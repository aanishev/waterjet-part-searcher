from functions.aqualon_auth import login_aqualon
from config import AQUALON_PASSWORD, AQUALON_USERNAME
import requests
from bs4 import BeautifulSoup
import re
import re
from lxml import html
import httpx

_PREFIX_RE = re.compile(r"^\s*Gross\s*Price\s*:\s*", re.IGNORECASE)

def fetch_gross_price_bs(url: str, session: requests.Session, *, timeout: float = 10.0) -> str:
    r = session.get(url, timeout=timeout)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    span = soup.find("span", string=re.compile(r"\bGross\s*Price\s*:", re.IGNORECASE))
    if span:
        raw = span.get_text(" ", strip=True)
        return _PREFIX_RE.sub("", raw).strip()

    for sp in soup.find_all("span"):
        raw = sp.get_text(" ", strip=True)
        if re.search(r"\bGross\s*Price\s*:", raw, flags=re.IGNORECASE):
            return re.sub(r"\bGross\s*Price\s*:\s*", "", raw, flags=re.IGNORECASE).strip()

    return "Not found"

def parse_aqualon_search_results(json_data):
    html = json_data.get("d", "")
    soup = BeautifulSoup(html, "html.parser")

    results = []

    for ul in soup.select("ul.overlay-search-result"):
        for li in ul.select("li"):

            link = li.select_one("a")
            if not link:
                continue
            href_raw = link.get("href", "").strip()
            href = "https://www.aqualonwaterjet.se" + href_raw

            title_el = link.select_one("p.title")
            title = title_el.get_text(strip=True) if title_el else ""

            sku_el = link.select_one(".sku")
            if sku_el:
                sku_text = sku_el.get_text(" ", strip=True)
                artno = sku_text.replace("ArtNr:", "").replace("ArtNr :", "").strip()
            else:
                artno = ""

            price_el = link.select_one(".price")
            if price_el:
                price_text = price_el.get_text(" ", strip=True)
                if ":" in price_text:
                    price = price_text.split(":", 1)[1].strip()
                else:
                    price = price_text
            else:
                price = ""

            results.append((href, title, artno, price))

    return results

def aqualon_search(session: requests.Session, search_term: str):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.aqualonwaterjet.se",
        "Referer": "https://www.aqualonwaterjet.se/en/products",
    }

    payload = {
        "searchTerm": search_term
    }

    resp = session.post("https://www.aqualonwaterjet.se/Template/Output/Search.asmx/SearchProducts", json=payload, headers=headers)
    resp.raise_for_status()

    return resp.json()   # возвращаем JSON

def aqualon_scrape(keywords: str):
    session_log = login_aqualon(AQUALON_USERNAME, AQUALON_PASSWORD)
    products = parse_aqualon_search_results(aqualon_search(session_log, keywords))
    full_text = f'╭  Found products:\n'
    for href, title, artno, price in products:
        gross = fetch_gross_price_bs(href, session_log)
        full_text += f'├  <a href="{href}">{title} ({artno})</a> - {price} (Gross - {gross})\n'
    full_text += f'╰  Total count: {len(products)}\n'
    return str(full_text)

