import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.aqualonwaterjet.se"
LOGIN_URL = BASE_URL + "/en/sign-in/"


def login_aqualon(username: str, password: str) -> requests.Session:
    session = requests.Session()

    # Настоящий браузерный заголовок
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/142.0.0.0 Safari/537.36"
    })

    # 1) GET login page → cookies + hidden ASP.NET fields
    resp = session.get(LOGIN_URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    def val(name):
        el = soup.find("input", {"name": name})
        return el["value"] if el and "value" in el.attrs else ""

    # Вытаскиваем все обязательные скрытые поля
    viewstate       = val("__VIEWSTATE")
    eventvalidation = val("__EVENTVALIDATION")
    eventtarget     = val("__EVENTTARGET")
    eventargument   = val("__EVENTARGUMENT")
    viewstategen    = val("__VIEWSTATEGENERATOR")

    # + твои реальные поля из payload:
    # ct100$ContentPlaceHolder1$tbxLogin
    # ct100$ContentPlaceHolder1$tbxPassword
    # ct100$ContentPlaceHolder1$cbRemember
    # ct100$ContentPlaceHolder1$loginButton
    # ct100$langHf

    payload = {
        "__EVENTTARGET":      eventtarget,
        "__EVENTARGUMENT":    eventargument or "",
        "__VIEWSTATE":        viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION":  eventvalidation,

        "ctl00$ContentPlaceHolder1$tbxLogin":    username,
        "ctl00$ContentPlaceHolder1$tbxPassword": password,
        "ctl00$ContentPlaceHolder1$cbRemember":  "on",    # как в DevTools
        "ctl00$ContentPlaceHolder1$loginButton": "Login", # обязательно
        "ctl00$langHf": "2",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": LOGIN_URL,
    }

    # 2) POST авторизация
    login_resp = session.post(LOGIN_URL, data=payload, headers=headers, allow_redirects=False)

    # Сервер вернёт 302 → Location: /en/products
    if login_resp.status_code != 302:
        raise RuntimeError("Login failed (no 302 redirect).")

    if "Set-Cookie" not in str(login_resp.headers):
        raise RuntimeError("Login failed: no cookies returned.")

    return session