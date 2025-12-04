# === Импорт библиотек ===
from functools import wraps

from telebot import types
from pathlib import Path

# === Импорт функций ===
from functions.bot_instance import bot # Подключение бота
from functions.menu import open_menu # Главное меню бота
from functions.dbconn import conn
from functions.accutek_parse import load_pages, find_products, parse_keywords, render_products_message
from functions.shape_parse import shape_scrape
from functions.gtmaco_parse import gtmaco_scrape
from functions.aqualon_parse import aqualon_scrape
from functions.i18n import t, set_lang
from locales.keys import L

# === Глобальные переменные ===
PAGES_FILE = Path("utils/accutek_pages.txt")

# === Команда /start ===
@bot.message_handler(commands=['start'])
def wrapper(message):
    open_menu(message, message.from_user)

# === Кнопка "Тестовое подменю" ===
@bot.callback_query_handler(func=lambda call: call.data == "test_submenu")
def submenu(call):
    bot.answer_callback_query(call.id)
    submenu_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    submenu_hkb.add(btn_hidemsg)
    text = (f">_ Тестовое подменю ⌵\n\n"
            f"╭ Это тестовое подменю.\n"
            f"╰ Здесь может быть всё, что вашей душе угодно.\n\n")
    bot.send_message(call.message.chat.id, text, reply_markup=submenu_hkb)

# === Кнопка "Пункт в разработке" ===
@bot.callback_query_handler(func=lambda call: call.data == "btn_indev")
def btnindev(call):
    bot.answer_callback_query(call.id, text=t(L.FUNCINDEV, call.from_user.id))

# === Кнопка "Выбор языка" ===
@bot.callback_query_handler(func=lambda call: call.data == "change_lang")
def chlang(call):
    bot.answer_callback_query(call.id)
    # Удаляем сообщение, к которому прикреплена кнопка
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # убирает хендлеры
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    chlang_kb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsgom"
    )
    btn_en = types.InlineKeyboardButton(
        text="English",
        callback_data="enlang"
    )
    btn_ka = types.InlineKeyboardButton(
        text="ქართული",
        callback_data="kalang"
    )
    btn_ru = types.InlineKeyboardButton(
        text="Русский",
        callback_data="rulang"
    )
    chlang_kb.add(btn_ka)
    chlang_kb.add(btn_en)
    chlang_kb.add(btn_ru)
    chlang_kb.add(btn_hidemsg)
    text = (f"🌐 Change language ⌵\n\n"
            f"╭ Here you can change language of the bot.\n"
            f"╰ Now only KA, EN, RU available.\n\n")
    bot.send_message(call.message.chat.id, text, reply_markup=chlang_kb)

@bot.callback_query_handler(func=lambda call: call.data == "rulang")
def ruslang(call):
    bot.answer_callback_query(call.id, "Язык успешно изменён!")
    # Удаляем сообщение, к которому прикреплена кнопка
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # убирает хендлеры
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    set_lang(call.from_user.id, "ru")
    open_menu(call.message, call.from_user)

@bot.callback_query_handler(func=lambda call: call.data == "enlang")
def englang(call):
    bot.answer_callback_query(call.id, "Language successfully changed!")
    # Удаляем сообщение, к которому прикреплена кнопка
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # убирает хендлеры
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    set_lang(call.from_user.id, "en")
    open_menu(call.message, call.from_user)

@bot.callback_query_handler(func=lambda call: call.data == "kalang")
def karlang(call):
    bot.answer_callback_query(call.id, "ენა წარმატებით შეიცვალა!")
    # Удаляем сообщение, к которому прикреплена кнопка
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # убирает хендлеры
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    set_lang(call.from_user.id, "ka")
    open_menu(call.message, call.from_user)

# === Кнопка "Admin" ===
@bot.callback_query_handler(func=lambda call: call.data == "admincmdtext")
def admincmdtext(call):
    bot.answer_callback_query(call.id)
    admincmd_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    admincmd_hkb.add(btn_hidemsg)
    full_admincmd_text = (f'- /checkuser (userid)\n'
                          f'- /adduser (userid) (uname) (urole)\n'
                          f'- /setrole (userid) (urole)')
    bot.send_message(call.message.chat.id, full_admincmd_text, parse_mode="HTML",
                disable_web_page_preview=True, reply_markup=admincmd_hkb)

# === Кнопка "Парсинг Accutek" ===
@bot.callback_query_handler(func=lambda call: call.data == "parse_accutek")
def ask_keywords(call):
    bot.answer_callback_query(call.id)
    accutek_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    accutek_hkb.add(btn_hidemsg)
    msg = bot.send_message(call.message.chat.id, t(L.KWDINPUT, call.from_user.id), reply_markup=accutek_hkb)
    bot.register_next_step_handler(msg, lambda m: ac_search_products(m, msg))


def ac_search_products(message, msg):
    if message.text.strip() != "/start":
        kwm = message.text.strip()
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.delete_message(message.chat.id, message.id)
        pendingmsg = bot.send_message(message.chat.id, t(L.SEARCHING, message.from_user.id))
        accutek_pkb = types.InlineKeyboardMarkup()
        btn_hidemsg = types.InlineKeyboardButton(
            text=t(L.HIDEBTN, message.from_user.id),
            callback_data="hidemsg"
        )
        accutek_pkb.add(btn_hidemsg)
        pages = load_pages(PAGES_FILE)
        keywords = parse_keywords(kwm)
        products = find_products(pages, keywords)
        full_text = render_products_message(products)
        found_prod = t(L.FOUNDPROD, message.from_user.id)
        total_t = t(L.TOTALT, message.from_user.id)
        final_full_text = full_text.replace("Found products", found_prod).replace("Total count", total_t)
        if len(final_full_text) < 4096:
            bot.send_message(
                msg.chat.id,
                final_full_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=accutek_pkb,
            )
        else:
            send_long_html(bot, msg.chat.id, final_full_text, reply_markup=accutek_pkb)
        bot.delete_message(pendingmsg.chat.id, pendingmsg.message_id)
    else:
        open_menu(message, message.from_user)

# === Кнопка "Парсинг Shape" ===
@bot.callback_query_handler(func=lambda call: call.data == "parse_shape")
def ask_keywords(call):
    bot.answer_callback_query(call.id)
    shape_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    shape_hkb.add(btn_hidemsg)
    msg = bot.send_message(call.message.chat.id, t(L.KWDINPUT, call.from_user.id), reply_markup=shape_hkb)
    bot.register_next_step_handler(msg, lambda m: search_products(m, msg))


def search_products(message, msg):
    if message.text.strip() != "/start":
        kwm_shape = message.text.strip()
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.delete_message(message.chat.id, message.id)
        pendingmsg = bot.send_message(message.chat.id, t(L.SEARCHING, message.from_user.id))
        shape_pkb = types.InlineKeyboardMarkup()
        btn_hidemsg = types.InlineKeyboardButton(
            text=t(L.HIDEBTN, message.from_user.id),
            callback_data="hidemsg"
        )
        shape_pkb.add(btn_hidemsg)
        full_text = shape_scrape(kwm_shape)
        found_prod = t(L.FOUNDPROD, message.from_user.id)
        total_t = t(L.TOTALT, message.from_user.id)
        final_full_text = full_text.replace("Found products", found_prod).replace("Total count", total_t)
        if len(final_full_text) < 4096:
            bot.send_message(
                msg.chat.id,
                final_full_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=shape_pkb,
            )
        else:
            send_long_html(bot, msg.chat.id, final_full_text, reply_markup=shape_pkb)
        bot.delete_message(pendingmsg.chat.id, pendingmsg.message_id)
    else:
        open_menu(message, message.from_user)

# === Кнопка "Парсинг GTMACO" ===
@bot.callback_query_handler(func=lambda call: call.data == "parse_gtmaco")
def ask_keywords(call):
    bot.answer_callback_query(call.id)
    gtm_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    gtm_hkb.add(btn_hidemsg)
    msg = bot.send_message(call.message.chat.id, t(L.KWDINPUT, call.from_user.id), reply_markup=gtm_hkb)
    bot.register_next_step_handler(msg, lambda m: search_products_gtm(m, msg))


def search_products_gtm(message, msg):
    if message.text.strip() != "/start":
        kwm_gtm = message.text.strip()
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.delete_message(message.chat.id, message.id)
        pendingmsg = bot.send_message(message.chat.id, t(L.SEARCHING, message.from_user.id))
        gtm_pkb = types.InlineKeyboardMarkup()
        btn_hidemsg = types.InlineKeyboardButton(
            text=t(L.HIDEBTN, message.from_user.id),
            callback_data="hidemsg"
        )
        gtm_pkb.add(btn_hidemsg)
        full_text = gtmaco_scrape(kwm_gtm)
        found_prod = t(L.FOUNDPROD, message.from_user.id)
        total_t = t(L.TOTALT, message.from_user.id)
        final_full_text = full_text.replace("Found products", found_prod).replace("Total count", total_t)
        if len(final_full_text) < 4096:
            bot.send_message(
                msg.chat.id,
                final_full_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=gtm_pkb,
            )
        else:
            send_long_html(bot, msg.chat.id, final_full_text, reply_markup=gtm_pkb)
        bot.delete_message(pendingmsg.chat.id, pendingmsg.message_id)
    else:
        open_menu(message, message.from_user)

# === Кнопка "Парсинг Aqualon" ===
@bot.callback_query_handler(func=lambda call: call.data == "parse_aqualon")
def ask_keywords(call):
    bot.answer_callback_query(call.id)
    aql_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    aql_hkb.add(btn_hidemsg)
    msg = bot.send_message(call.message.chat.id, t(L.KWDINPUT, call.from_user.id), reply_markup=aql_hkb)
    bot.register_next_step_handler(msg, lambda m: search_products_aql(m, msg))


def search_products_aql(message, msg):
    if message.text.strip() != "/start":
        kwm_aql = message.text.strip()
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.delete_message(message.chat.id, message.id)
        pendingmsg = bot.send_message(message.chat.id, t(L.SEARCHING, message.from_user.id))
        aql_pkb = types.InlineKeyboardMarkup()
        btn_hidemsg = types.InlineKeyboardButton(
            text=t(L.HIDEBTN, message.from_user.id),
            callback_data="hidemsg"
        )
        aql_pkb.add(btn_hidemsg)
        full_text = aqualon_scrape(kwm_aql)
        found_prod = t(L.FOUNDPROD, message.from_user.id)
        total_t = t(L.TOTALT, message.from_user.id)
        final_full_text = full_text.replace("Found products", found_prod).replace("Total count", total_t)
        if len(final_full_text) < 4096:
            bot.send_message(
                msg.chat.id,
                final_full_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=aql_pkb,
            )
        else:
            send_long_html(bot, msg.chat.id, final_full_text, reply_markup=aql_pkb)
        bot.delete_message(pendingmsg.chat.id, pendingmsg.message_id)
    else:
        open_menu(message, message.from_user)

# === Кнопка "Глобальный поиск" ===
@bot.callback_query_handler(func=lambda call: call.data == "global_search")
def ask_keywords(call):
    bot.answer_callback_query(call.id)
    glb_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, call.from_user.id),
        callback_data="hidemsg"
    )
    glb_hkb.add(btn_hidemsg)
    msg = bot.send_message(call.message.chat.id, t(L.KWDINPUT, call.from_user.id), reply_markup=glb_hkb)
    bot.register_next_step_handler(msg, lambda m: search_products_glb(m, msg))


def search_products_glb(message, msg):
    if message.text.strip() != "/start":
        kwm_glb = message.text.strip()
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.delete_message(message.chat.id, message.id)
        pendingmsg = bot.send_message(message.chat.id, t(L.SEARCHING, message.from_user.id))
        glb_pkb = types.InlineKeyboardMarkup()
        btn_hidemsg = types.InlineKeyboardButton(
            text=t(L.HIDEBTN, message.from_user.id),
            callback_data="hidemsg"
        )
        glb_pkb.add(btn_hidemsg)
        pages = load_pages(PAGES_FILE)
        keywords = parse_keywords(kwm_glb)
        products = find_products(pages, keywords)
        found_prod = t(L.FOUNDPROD, message.from_user.id)
        total_t = t(L.TOTALT, message.from_user.id)
        full_text_acc = render_products_message(products).replace("Found products", found_prod + " (Accutek)").replace("Total count", total_t + " (Accutek)") + "\n"
        full_text_shape = shape_scrape(kwm_glb).replace("Found products", found_prod + " (Shape)").replace("Total count", total_t + " (Shape)") + "\n"
        full_text_gtm = gtmaco_scrape(kwm_glb).replace("Found products", found_prod + " (GTMACO)").replace("Total count", total_t + " (GTMACO)") + "\n"
        full_text_aql = aqualon_scrape(kwm_glb).replace("Found products", found_prod + " (Aqualon)").replace("Total count", total_t + " (Aqualon)") + "\n"
        final_full_text = full_text_acc + full_text_shape + full_text_gtm + full_text_aql
        if len(final_full_text) < 4096:
            bot.send_message(
                msg.chat.id,
                final_full_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=glb_pkb,
            )
        else:
            send_long_html(bot, msg.chat.id, final_full_text, reply_markup=glb_pkb)
        bot.delete_message(pendingmsg.chat.id, pendingmsg.message_id)
    else:
        open_menu(message, message.from_user)


# === Функция для отправки больших сообщ-й раздельно
MAX_LEN = 4096

def send_long_html(argbot, chat_id, text, reply_markup=None):
    lines = text.split("\n")
    chunk = ""

    for line in lines:
        # +1 за '\n'
        if len(chunk) + len(line) + 1 > MAX_LEN:
            argbot.send_message(
                chat_id,
                chunk,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=reply_markup,
            )
            chunk = ""

        chunk += line + "\n"

    if chunk.strip():
        argbot.send_message(
            chat_id,
            chunk,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=reply_markup,
        )

# === Callback для скрытия сообщения от бота ===
@bot.callback_query_handler(func=lambda call: call.data == "hidemsg")
def hidemessage(call):
    # Обязательно закрываем "часики" на кнопке
    bot.answer_callback_query(call.id)
    # Удаляем сообщение, к которому прикреплена кнопка
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # убирает хендлеры
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

# === Callback для скрытия сообщения от бота и открытия меню ===
@bot.callback_query_handler(func=lambda call: call.data == "hidemsgom")
def hidemessage(call):
    # Обязательно закрываем "часики" на кнопке
    bot.answer_callback_query(call.id)
    # Удаляем сообщение, к которому прикреплена кнопка
    bot.delete_message(call.message.chat.id, call.message.message_id)
    # убирает хендлеры
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    # открывает меню
    open_menu(call.message, call.from_user)

# === Администраторские функции и команды ===
def get_user(user_id: int):
    cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone()


def get_user_role(user_id: int) -> str | None:
    row = get_user(user_id)
    return row[2] if row else None


def is_admin(user_id: int) -> bool:
    return get_user_role(user_id) == "Administrator"

def admin_only(handler):
    """Декоратор для команд только для админов."""
    @wraps(handler)
    def wrapper_ao(message):
        admonly_hkb = types.InlineKeyboardMarkup()
        btn_hidemsg = types.InlineKeyboardButton(
            text=t(L.HIDEBTN, message.from_user.id),
            callback_data="hidemsg"
        )
        admonly_hkb.add(btn_hidemsg)
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "⛔ {t(L.YOUDONTHAVEPERM, message.from_user.id)}", reply_markup=admonly_hkb)
            return
        return handler(message)
    return wrapper_ao

@bot.message_handler(commands=['setrole'])
@admin_only
def cmd_setrole(message):
    setrole_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, message.from_user.id),
        callback_data="hidemsg"
    )
    setrole_hkb.add(btn_hidemsg)
    try:
        _, user_id_str, role = message.text.strip().split(maxsplit=2)
        target_id = int(user_id_str)
    except ValueError:
        bot.reply_to(message, f"{t(L.USE, message.from_user.id)}: /setrole (user_id) (Guest | Manager | Administrator)", reply_markup=setrole_hkb)
        return

    role = role.capitalize()
    if role not in ("Guest", "Administrator", "Manager"):
        bot.reply_to(message, f"{t(L.ROLESHOULDBE, message.from_user.id)}", reply_markup=setrole_hkb)
        return

    # проверим, есть ли уже такой пользователь
    if not get_user(target_id):
        bot.reply_to(message, f"{t(L.USER, message.from_user.id)} {target_id} {t(L.NOEXISTS, message.from_user.id)}", reply_markup=setrole_hkb)
        return

    conn.execute("UPDATE users SET urole = ? WHERE user_id = ?", (role, target_id))
    conn.commit()
    bot.reply_to(message, f"{t(L.USERROLE, message.from_user.id)} {target_id} {t(L.CHANGEDTO, message.from_user.id)} {role}.", reply_markup=setrole_hkb)

@bot.message_handler(commands=['adduser'])
@admin_only
def cmd_adduser(message):
    adduser_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, message.from_user.id),
        callback_data="hidemsg"
    )
    adduser_hkb.add(btn_hidemsg)
    try:
        _, user_id_str, uname, role = message.text.strip().split(maxsplit=3)
        user_id = int(user_id_str)
    except ValueError:
        bot.reply_to(message, f"{t(L.USE, message.from_user.id)}: /adduser (user_id) (uname) (Guest | Manager | Administrator)", reply_markup=adduser_hkb)
        return

    role = role.capitalize()
    if role not in ("Guest", "Administrator", "Manager"):
        bot.reply_to(message, f"{t(L.ROLESHOULDBE, message.from_user.id)}", reply_markup=adduser_hkb)
        return

    if get_user(user_id):
        bot.reply_to(message, f"{t(L.USER, message.from_user.id)} {user_id} {t(L.EXISTS, message.from_user.id)}.", reply_markup=adduser_hkb)
        return

    conn.execute(
        "INSERT INTO users(user_id, uname, urole, lang) VALUES (?, ?, ?, 'en')",
        (user_id, uname, role),
    )
    conn.commit()
    bot.reply_to(message, f"{t(L.USER, message.from_user.id)} {user_id} ({uname}) {t(L.ADDEDWITHROLE, message.from_user.id)} {role}, lang=en.", reply_markup=adduser_hkb)

@bot.message_handler(commands=['sendall'])
@admin_only
def cmd_sendall(message):
    sendall_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, message.from_user.id),
        callback_data="hidemsg"
    )
    sendall_hkb.add(btn_hidemsg)
    try:
        _, text_str = message.text.strip().split(maxsplit=1)
    except ValueError:
        bot.reply_to(message, f"{t(L.USE, message.from_user.id)}: /sendall (text)", reply_markup=sendall_hkb)
        return

    rows = conn.execute("SELECT user_id FROM users").fetchall()

    # Если нужно получить список только значений
    user_ids = [row[0] for row in rows]

    for user_id in user_ids:
        bot.send_message(user_id, text_str)

    bot.reply_to(message, f"Sent successfully!", reply_markup=sendall_hkb)


@bot.message_handler(commands=['checkuser'])
@admin_only
def cmd_checkuser(message):
    checkuser_hkb = types.InlineKeyboardMarkup()
    btn_hidemsg = types.InlineKeyboardButton(
        text=t(L.HIDEBTN, message.from_user.id),
        callback_data="hidemsg"
    )
    checkuser_hkb.add(btn_hidemsg)
    try:
        _, user_id_str = message.text.strip().split(maxsplit=1)
        user_id = int(user_id_str)
    except ValueError:
        bot.reply_to(message, f"{t(L.USE, message.from_user.id)}: /checkuser (user_id)", reply_markup=checkuser_hkb)
        return

    row = get_user(user_id)
    if not row:
        bot.reply_to(message, f"{t(L.NOINBASE, message.from_user.id)}{user_id}.", reply_markup=checkuser_hkb)
        return

    bot.reply_to(
        message,
        f"Найден:\n"
        f"user_id: {row[0]}\n"
        f"uname: {row[1]}\n"
        f"urole: {row[2]}\n"
        f"lang: {row[3]}", reply_markup=checkuser_hkb
    )


# === Запуск ===
print("The bot is started...")
bot.infinity_polling()
