from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
from urllib.parse import urljoin
from html import escape

import httpx
from bs4 import BeautifulSoup, Tag


PAGES_FILE = Path("../utils/accutek_pages.txt")


@dataclass(frozen=True)
class Product:
    title: str
    price: str
    url: str
    source_page: str
    desc: str

def parse_keywords(raw: str) -> list[str]:
    return [t for t in re.split(r"[,\s]+", raw.strip()) if t]

def find_products(pages: list[str], keywords: list[str]) -> list[Product]:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(scrape_all(pages, keywords))
    else:
        raise RuntimeError(
            "Нельзя вызвать find_products() внутри уже работающего event loop. "
            "Используйте await a_find_products(...)."
        )

def load_pages(file_path: Path) -> List[str]:
    if not file_path.exists():
        raise FileNotFoundError(
            f'Не найден файл "{file_path}". Создайте его в корне проекта и укажите по одному URL на строку.'
        )
    urls: List[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    if not urls:
        raise ValueError(f'Файл "{file_path}" пуст. Добавьте хотя бы один URL.')
    return urls


async def fetch(client: httpx.AsyncClient, url: str, *, attempts: int = 3, timeout_s: float = 20.0) -> Optional[str]:
    last_err: Optional[Exception] = None
    for attempt in range(1, attempts + 1):
        try:
            resp = await client.get(url, timeout=timeout_s, follow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ProductScraper/1.0; +https://example.com/bot)"
            })
            resp.raise_for_status()
            # Отбрасываем бинарные/не-HTML
            ctype = resp.headers.get("content-type", "").lower()
            if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
                return None
            return resp.text
        except Exception as e:  # noqa: BLE001
            last_err = e
            await asyncio.sleep(min(2 ** attempt, 5))
    print(f"[warn] Не удалось загрузить {url}: {last_err}")
    return None


def _text(el: Optional[Tag]) -> str:
    return " ".join(el.stripped_strings) if el else ""


def extract_products(html: str, base_url: str, keywords: list[str]) -> List[Product]:
    soup = BeautifulSoup(html, "lxml")
    results: List[Product] = []
    kw_tokens = [k.casefold() for k in keywords if k.strip()]
    desc = ""
    desc_cf = ""

    for ul in soup.select("ul.woo-entry-inner.clr"):
        for woo_desc in ul.select("li.woo-desc"):
            desc = _text(woo_desc)
            desc_cf = desc.casefold()
        for li_title in ul.select("li.title"):
            a = li_title.select_one("h2 a, h3 a, a")
            if not a:
                continue

            title = _text(a)
            title_cf = title.casefold()
            title_hit = bool(title) and all(tok in title_cf for tok in kw_tokens)
            desc_hit = bool(desc) and all(tok in desc_cf for tok in kw_tokens)
            if not (title_hit or desc_hit):
                continue

            price_li = None
            for sib in li_title.find_next_siblings():
                if isinstance(sib, Tag) and sib.name == "li" and "price-wrap" in (sib.get("class") or []):
                    price_li = sib
                    break

            if price_li:
                bdi = price_li.select_one("bdi")
                if bdi:
                    price_text = _text(bdi)
                else:
                    price_text = _text(price_li.select_one(".price, ins, del, span, strong"))
            else:
                near_price = li_title.find_next(["bdi", "span"], class_=lambda c: c and "price" in " ".join(c)) \
                             or li_title.find_next("bdi")
                price_text = _text(near_price)

            price_text = re.sub(r"\s+", " ", price_text).strip() or "—"

            href = a.get("href") or ""
            full_url = urljoin(base_url, href)
            results.append(Product(title=title, price=price_text, url=full_url, source_page=base_url, desc = desc))

    unique: dict[Tuple[str, str], Product] = {}
    for p in results:
        key = (p.title, p.url)
        unique[key] = p
    return list(unique.values())


async def scrape_all(pages: Iterable[str], keywords: list[str]) -> List[Product]:
    products: List[Product] = []
    limits_obj = httpx.Limits(max_connections=10, max_keepalive_connections=10)  # ваш совместимый шим для httpx
    timeout = httpx.Timeout(30.0)

    client_kwargs = dict(http2=True, timeout=timeout)
    if limits_obj is not None:
        client_kwargs["limits"] = limits_obj

    async with httpx.AsyncClient(**client_kwargs) as client:
        htmls = await asyncio.gather(*(fetch(client, url) for url in pages))

    for url, html in zip(pages, htmls, strict=False):
        if not html:
            continue
        products.extend(extract_products(html, url, keywords))
    return products

def render_products_message(products: list[Product]) -> str:
    seen_urls: set[str] = set()
    unique_products: list[Product] = []
    for p in products:
        if p.url in seen_urls:
            continue
        seen_urls.add(p.url)
        unique_products.append(p)
    # --------------------------------------------------------------

    lines: list[str] = ["╭  Found products:"]

    if not unique_products:
        lines.append("╰  Total count: 0\n")
        return "\n".join(lines)

    for p in unique_products:
        title_html = escape(p.title, quote=True)
        url_html = escape(p.url, quote=True)
        price_html = escape(p.price, quote=True) if p.price else "—"
        lines.append(f'├  <a href="{url_html}">{title_html}</a> - {price_html}')

    lines.append(f"╰  Total count: {len(unique_products)}\n")
    return "\n".join(lines)
