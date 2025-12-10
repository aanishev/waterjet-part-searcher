# i18n.py
from importlib import import_module
from functools import lru_cache
from typing import Any
from functions.dbconn import conn, cursor

DEFAULT_LANG = "en"         # дефолт на ваш вкус
SUPPORTED_LANGS = {"en", "ru", "ka"}

def db_get_user_lang(user_id: int | str) -> str | None:
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    rlang = cursor.fetchone()
    return str(rlang[0]) if rlang else None

def db_set_user_lang(user_id: int | str, lang: str) -> None:
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id,))
    conn.commit()
    pass
# ------------------------------------------------

@lru_cache(maxsize=None)
def load_locale_module(lang: str):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return import_module(f"locales.{lang}")

def get_user_lang(user_id: int | str) -> str:
    lang = db_get_user_lang(user_id)
    if not lang or lang not in SUPPORTED_LANGS:
        return DEFAULT_LANG
    return lang

def t_idx(idx: int, user_lang: str, **kwargs: Any) -> str:
    mod = load_locale_module(user_lang)
    arr = getattr(mod, "locale_text", [])
    try:
        s = arr[idx]
    except (IndexError, TypeError):
        fallback = load_locale_module(DEFAULT_LANG)
        arr_f = getattr(fallback, "locale_text", [])
        s = arr_f[idx] if idx < len(arr_f) else ""

    try:
        return s.format(**kwargs) if kwargs else s
    except (KeyError, ValueError, IndexError):
        return s


def t(idx: int, user_id: int | str, **kwargs: Any) -> str:
    return t_idx(idx, get_user_lang(user_id), **kwargs)

def set_lang(user_id: int | str, lang: str) -> bool:
    if lang not in SUPPORTED_LANGS:
        return False
    db_set_user_lang(user_id, lang)
    return True
