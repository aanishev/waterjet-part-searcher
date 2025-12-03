import re
from functions.gtmaco_auth import login_strato
from config import GTMACO_PASSWORD, GTMACO_USERNAME
from bs4 import BeautifulSoup

def gtmaco_scrape(search_string: str):
    search_page = "https://shop.strato.de/epages/63239732.sf/sec7119fe35cb/?ObjectID=16526533&ViewAction=FacetedSearchProducts&FocusReference=RemoteSearch_NavBarLeft_1&SearchString=" + search_string
    session = login_strato(GTMACO_USERNAME, GTMACO_PASSWORD)
    resp = session.get(search_page)
    resp.raise_for_status()
    products = parse_gtmaco_products(resp.text)
    full_text = f'╭  Found products:\n'
    for href, title, prodno, oemno, price in products:
        full_text += f'├  <a href="{href}">{title} ({oemno})</a> - {price}\n'
    full_text += f'╰  Total count: {len(products)}\n'
    return str(full_text)

def parse_gtmaco_products(html: str):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    # один товар = один <td> с div.InfoArea
    product_blocks = soup.select("td > div.InfoArea")

    for block in product_blocks:
        # 1. Ссылка и заголовок
        # внутри h3 находится <a href="?ObjectPath=/Shops/63239732/Products/7060-12">...</a>
        link = block.select_one("h3 a")
        if not link:
            # запасной вариант – любой ссылочный продуктовый href
            link = block.select_one("a[href*='/Products/']")
        if not link:
            continue  # без ссылки товар неинтересен

        href_raw = (link.get("href") or "").strip()
        href = "http://gtmaco-shop.eu/epages/63239732.sf/en_GB/" + href_raw
        title = link.get_text(strip=True)

        # 2. Product №
        prod_el = block.select_one("span.ProductNo")
        if prod_el:
            prod_text = prod_el.get_text(strip=True)
            # "Product no.: 7060-12" -> "7060-12"
            prodno = prod_text.replace("Product no.:", "").strip()
        else:
            prodno = ""

        # 3. OEM №
        desc_el = block.select_one("div.Description")
        if desc_el:
            desc_text = desc_el.get_text(strip=True) if desc_el else ""
            # "OEM# 85567, A2260012" -> "85567, A2260012"
            oemno = re.sub(r"^OEM[#\s:]*", "", desc_text, flags=re.I).strip()
        else:
            oemno = ""

        # 4. Цена
        price_el = block.select_one("p.price-value")
        if price_el:
            # "83.30 € *" -> "83.30 €"
            price_text = " ".join(price_el.stripped_strings)
            price_text = price_text.replace("*", "").strip()
            price = price_text
        else:
            price = ""
        results.append((href, title, prodno, oemno, price))
    return results