from bs4 import BeautifulSoup

from functions.allfi_auth import allfi_login
from config import ALLFI_USERNAME, ALLFI_PASSWORD

def get_allfi_html(kwm: str):
    session = allfi_login(ALLFI_USERNAME, ALLFI_PASSWORD)
    searchurl = f"https://allfiwaterjetparts.com/en/products,2?search={kwm}"
    resp = session.get(searchurl)
    resp.raise_for_status()
    return resp.text

def allfi_parser(html: str, kwm: str):
    soup = BeautifulSoup(html, "html.parser")

    results = []

    for item in soup.select("div.product-item"):
        # 0. Link
        href_el = item.select_one("a.covered-link")
        href_addition = href_el.get("href") if href_el else ""
        href = f"https://allfiwaterjetparts.com/en/{href_addition}"

        # 1. Title
        title_el = item.select_one("h2.product-name")
        title = title_el.get_text(strip=True) if title_el else ""

        # 2. Stock
        stock_el = item.select_one("h2.product-code")
        stock = stock_el.get_text(strip=True) if stock_el else ""

        # 3. Price
        price_el = item.select_one("p.price")
        price = price_el.get_text(strip=True) if price_el else ""

        results.append((href, title, stock, price))
    return results

def allfi_scrape(kwm: str):
    products = allfi_parser(get_allfi_html(kwm), kwm)
    full_text = f'╭  Found products:\n'
    for href, title, stock, price in products:
        full_text += f'├  <a href="{href}">{title} ({stock})</a> - {price}\n'
    full_text += f'╰  Total count: {len(products)}\n'
    return str(full_text)
