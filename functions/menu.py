# === Импорт библиотек ===
from telebot import types

# === Импорт файла конфигурации ===
from config import branch

# === Импорт функций ===
from functions.bot_instance import bot
from functions.dbconn import cursor
from functions.usermanipulations import get_or_create_user
from functions.i18n import t
from locales.keys import L

# === Открытие главного меню ===
def open_menu(message, user):
    # === Принимаем запросы только из чатов с пользователями, игнорируя группы и каналы ===
    if message.chat.type != "private":
        return

    # === Манипуляции с пользователем ===
    get_or_create_user(user)

    # === Получаем имя ===
    cursor.execute("SELECT uname FROM users WHERE user_id=?", (user.id,))
    uname = cursor.fetchone()[0]

    # === Получаем роль ===
    cursor.execute("SELECT urole FROM users WHERE user_id=?", (user.id,))
    urole = cursor.fetchone()[0]
    rolename = urole
    if rolename == "Administrator":
        rolename = t(L.ADM, user.id)
    elif rolename == "Manager":
        rolename = t(L.MAN, user.id)
    else:
        rolename = t(L.GUEST, user.id)
    # === Клавиатура ===
    menu_mkb = types.InlineKeyboardMarkup()
    btn_accutek = types.InlineKeyboardButton(
        text="🔎 Accutek",
        callback_data="parse_accutek"
    )
    btn_shape = types.InlineKeyboardButton(
        text="🔎 Shape",
        callback_data="parse_shape"
    )
    btn_aqualon = types.InlineKeyboardButton(
        text="🔎 Aqualon",
        callback_data="parse_aqualon"
    )
    btn_gtmaco = types.InlineKeyboardButton(
        text="🔎 GTMACO",
        callback_data="parse_gtmaco"
    )
    btn_allfi = types.InlineKeyboardButton(
        text="🔎 Allfi",
        callback_data="parse_allfi"
    )
    btn_admincmd = types.InlineKeyboardButton(
        text=">_ Admin",
        callback_data="admincmdtext"
    )
    btn_glb = types.InlineKeyboardButton(
        text="🔎 Global",
        callback_data="global_search"
    )
    btn_sysadmin = types.InlineKeyboardButton(
        text=t(L.SYSADMIN, user.id),
        url=f"tg://resolve?domain=@aanishev"
    )
    btn_chlang = types.InlineKeyboardButton(
        text=t(L.CHLANG, user.id),
        callback_data="change_lang"
    )

    # === Текст для зарегистрированных пользователей ===
    text = ''
    if branch == "main":
        text += t(L.MENU, user.id)
    else:
        text += t(L.MENUDEV, user.id)
    text += (f"╭ {t(L.UNAME, user.id)}: {uname}\n"
             f"╰ {t(L.UROLE, user.id)}: {rolename}\n\n")

    # === Текст для новых пользователей
    guesttext = ''
    if branch == "main":
        guesttext += t(L.MENU, user.id)
    else:
        guesttext += t(L.MENUDEV, user.id)
    guesttext += (f"╭ {t(L.UNAME, user.id)}: {uname}\n"
                  f"╰ {t(L.UROLE, user.id)}: {rolename}\n\n"
                  f"⚠️ {t(L.SYSADMINWARN, user.id)}")


    if urole == 'Manager' or urole == 'Administrator':
        menu_mkb.row(btn_accutek, btn_shape)
        menu_mkb.row(btn_aqualon, btn_gtmaco)
        menu_mkb.row(btn_allfi, btn_glb)
        if urole == 'Administrator':
            menu_mkb.add(btn_admincmd)
        menu_mkb.add(btn_chlang)
        caption = text
    else:
        menu_mkb.add(btn_sysadmin)
        menu_mkb.add(btn_chlang)
        caption = guesttext

    # === Отправка сообщения ===
    bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=menu_mkb)