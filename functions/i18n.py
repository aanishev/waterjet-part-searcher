# i18n.py
from importlib import import_module
from functools import lru_cache
from typing import Any
from functions.dbconn import conn, cursor

DEFAULT_LANG = "en"         # дефолт на ваш вкус
SUPPORTED_LANGS = {"en", "ru", "ka"}

# ---- ЗАГЛУШКИ БД (замените на ваши функции) ----
def db_get_user_lang(user_id: int | str) -> str | None:
    """
    Возвращает код языка из БД ('en'/'ru'/'ka') или None, если не найден.
    Реализуйте как SELECT lang FROM users WHERE user_id = ?.
    """
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    rlang = cursor.fetchone()
    return str(rlang[0]) if rlang else None

def db_set_user_lang(user_id: int | str, lang: str) -> None:
    """
    Обновляет язык пользователя в БД.
    Реализуйте как UPDATE users SET lang=? WHERE user_id=? (или INSERT).
    """
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id,))
    conn.commit()
    pass
# ------------------------------------------------

@lru_cache(maxsize=None)
def load_locale_module(lang: str):
    """
    Кэшируем импорт локали: locales/<lang>.py должен содержать locale_text: list[str]
    """
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return import_module(f"locales.{lang}")

def get_user_lang(user_id: int | str) -> str:
    lang = db_get_user_lang(user_id)
    if not lang or lang not in SUPPORTED_LANGS:
        return DEFAULT_LANG
    return lang

def t_idx(idx: int, user_lang: str, **kwargs: Any) -> str:
    """
    Возвращает строку по индексу для заданного языка.
    Позволяет делать подстановки через format(**kwargs).
    """
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
    """
    Удобный враппер: сам достаёт язык пользователя по user_id.
    """
    return t_idx(idx, get_user_lang(user_id), **kwargs)

def set_lang(user_id: int | str, lang: str) -> bool:
    """
    Сохраняет язык, если поддерживается. Возвращает True/False.
    """
    if lang not in SUPPORTED_LANGS:
        return False
    db_set_user_lang(user_id, lang)
    return True
