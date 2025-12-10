import requests

def login_strato(username: str, password: str) -> requests.Session:
    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/142.0.0.0 Safari/537.36"
    })

    url = "https://shop.strato.de/epages/63239732.sf/en_GB/"
    params = {
        "ObjectPath": "/Shops/63239732/Categories"
    }

    payload = {
        "ChangeAction": "SaveLoginForm",
        "RegistrationObjectID": "16526533",
        "ErrorAction": "View",
        "ErrorObjectID": "16526548",
        "Origin": "NavBar",
        "Login": username,
        "Password": password,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url,
    }

    resp = session.post(url, params=params, data=payload, headers=headers)
    resp.raise_for_status()

    cookies = session.cookies.get_dict()

    if not any(k.startswith("SessionID") for k in cookies):
        raise RuntimeError("Strato login failed — SessionID cookie not found")

    return session
