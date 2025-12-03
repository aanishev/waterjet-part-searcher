import requests
import re


BASE_URL = "https://shop.shapeprocessautomation.com"
LOGIN_PAGE_URL = BASE_URL + "/User/Login"   # поставь тот, который у тебя реально работает
AUTH_URL = BASE_URL + "/User/Authenticate"


def shape_login(username: str, password: str) -> requests.Session:
    """Логинится на Shape и возвращает готовую Session с cookies."""

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
    })

    # 1. GET логин-страницы (или фрагмента, откуда берётся токен)
    resp = session.get(LOGIN_PAGE_URL)
    resp.raise_for_status()
    html = resp.text

    # 2. Ищем токен в HTML
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', html)
    verification_token = (
        m.group(1) if m else session.cookies.get("__RequestVerificationToken")
    )
    if not verification_token:
        raise RuntimeError("Не нашёл __RequestVerificationToken")

    # 3. Собираем payload как в DevTools
    payload = {
        "__RequestVerificationToken": verification_token,
        "ReturnUrl": "/",
        "KeepBasket": "False",
        "User.UserName": username,
        "User.Password": password,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": LOGIN_PAGE_URL,
        "X-Requested-With": "XMLHttpRequest",
    }

    # 4. POST авторизации
    auth_resp = session.post(AUTH_URL, data=payload, headers=headers)
    auth_resp.raise_for_status()

    # можно проверять клиентский JSON в ответе
    # но часто достаточно просто куки
    if "PT_OnlineBusiness_Authentication" not in session.cookies.get_dict():
        raise RuntimeError("Логин не удался!")

    return session
