import requests
from bs4 import BeautifulSoup

BASE_URL = "https://allfiwaterjetparts.com"
LOGIN_URL = BASE_URL + "/en/login,16"

def allfi_login(email: str, password: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/143.0.0.0 Safari/537.36",
    })

    r = s.get(LOGIN_URL)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    csrf_el = soup.find("input", {"name": "__csrf"})
    if not csrf_el or not csrf_el.get("value"):
        csrf_el = soup.find("input", {"name": "_csrf"})

    csrf = csrf_el["value"]

    payload = {
        "__csrf": csrf,
        "__action": "Customer/Login",
        "email": email,
        "password": password,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": BASE_URL,
        "Referer": LOGIN_URL,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
    }

    resp = s.post(LOGIN_URL, data=payload, headers=headers)
    resp.raise_for_status()

    return s
