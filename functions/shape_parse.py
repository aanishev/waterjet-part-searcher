from functions.shape_auth import shape_login
from config import SHAPE_PASSWORD, SHAPE_USERNAME
from bs4 import BeautifulSoup

BASE_URL = "https://shop.shapeprocessautomation.com"

def shape_scrape(keyword: str):
    search_page = "https://shop.shapeprocessautomation.com/catalog/search?productListParentType=0&sectionId=21&total=242&ExactTextSearch=False&UniqueNodeIdentifier=&ErpProductsOnly=False&listvalue=" + str(keyword).replace(" ", "+") + "&RelationType=4%20Virtual&search=" + str(keyword).replace(" ", "+") + "&SelectedListTypeModel=Grid&sortBy=&PageSize=1000&page=1&TotalPages=21&SelectedListTypeModel=Grid"
    session = shape_login(SHAPE_USERNAME, SHAPE_PASSWORD)
    resp = session.get(search_page)
    resp.raise_for_status()

    window_locat = resp.text.find("window.location = '")
    if window_locat != -1:
        href_fragm = resp.text[window_locat:window_locat + 200]
        prod_page = "https://shop.shapeprocessautomation.com" + href_fragm[19:href_fragm.find(";") - 1]
        resp = session.get(prod_page)
        resp.raise_for_status()
        productinfo = parse_shape_product_page(resp.text)
        full_text = (f'╭  Found products:\n'
                    f'├  <a href="{prod_page}">{productinfo[0]} ({productinfo[1]})</a> - {productinfo[2]} (Gross - {productinfo[3]})\n'
                    f'╰  Total count: 1\n')
        return str(full_text)
    else:
        products = parse_shape_products(resp.text)
        full_text = f'╭  Found products:\n'
        for href, title, stockcode, price, grprice in products:
            hrefinal = "https://shop.shapeprocessautomation.com" + href
            full_text += f'├  <a href="{hrefinal}">{title} ({stockcode})</a> - {price} (Gross - {grprice})\n'
        full_text += f'╰  Total count: {len(products)}\n'
        return str(full_text)

def parse_shape_product_page(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # 1. Title
    title_el = soup.select_one("h1.page-header")
    title = title_el.get_text(strip=True) if title_el else ""

    # 2. Stock code
    stock_el = soup.select_one('p[aria-label="Stock code"] strong')
    stockcode = stock_el.get_text(strip=True) if stock_el else ""

    # 3. Цена netprice
    price_el = soup.select_one("h2.product-netprice")
    if price_el:
        full_price = " ".join(price_el.stripped_strings)
        price = full_price.split("/")[0].strip()
    else:
        price = ""

    # 4. Цена gross
    grprice_el = soup.select_one("p.product-grossprice")
    if grprice_el:
        full_grprice = " ".join(grprice_el.stripped_strings)
        grprice = full_grprice.split("/")[0].strip()
    else:
        grprice = ""


    # возвращаем в том же формате, что и для списка
    return title, stockcode, price, grprice

def parse_shape_products(html: str):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for item in soup.select("li.product.type-erp"):
        # 1. Ссылка + заголовок
        # сначала ищем именно заголовок
        title_link = item.select_one("h3.hover-product-title a.js-product-detail")
        if not title_link:
            # fallback: вдруг верстка отличается
            title_link = item.select_one("h3 a, a.js-product-detail")
        if not title_link:
            # если вообще не нашли ссылку с названием — пропускаем товар
            continue
        href = (title_link.get("href") or "").strip()
        title = title_link.get_text(strip=True)
        # 2. Stockcode
        stock_el = item.select_one("p.field-stockcode")
        stockcode = stock_el.get_text(strip=True) if stock_el else ""
        # 3. Цена
        price_el = item.select_one("h4.product-netprice")
        if price_el:
            full_price = " ".join(price_el.stripped_strings)
            price = full_price.split("/")[0].strip()
        else:
            price = ""
        # 4. Цена gross
        grprice_el = item.select_one("p.product-grossprice")
        if grprice_el:
            full_grprice = " ".join(grprice_el.stripped_strings)
            grprice = full_grprice.split("/")[0].strip()
        else:
            grprice = ""
        results.append((href, title, stockcode, price, grprice))
    return results
