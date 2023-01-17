#!/usr/bin/env python

import sqlite3
from sqlite3 import Error
from datetime import datetime

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def db():
    database = r"/opt/bot/bot.db"

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    join_date text NOT NULL
                                ); """

    sql_create_urls_table = """CREATE TABLE IF NOT EXISTS urls (
                                    url text PRIMARY KEY,
                                    hostname text NOT NULL,
                                    issued_date text NOT NULL,
                                    used_count integer NOT NULL DEFAULT 0
                                );"""
    
    sql_create_user_url_table = """CREATE TABLE IF NOT EXISTS user_url (
                                    user integer NOT NULL,
                                    url integer NOT NULL,
                                    issued_date text NOT NULL,
                                    FOREIGN KEY (user) REFERENCES users (id),
                                    FOREIGN KEY (url) REFERENCES urls (id)
                                );"""

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_urls_table)
        create_table(conn, sql_create_user_url_table)
    else:
        print("Error! cannot create the database connection.")

def inc_url_used_count(conn, url):
    sql = "UPDATE urls SET used_count = used_count + 1 WHERE url = ?"
    cur = conn.cursor()
    cur.execute(sql, url)
    conn.commit()

def get_url_byzone(conn, zone):
    zone_reg="null"
    if zone == "NUR":
        zone_reg="scherehtznur"
    if zone == "HEL":
        zone_reg="scherehtzhel"
    if zone == "FLK":
        zone_reg="scherehtzflk"
    if zone == "ARVSHN":
        zone_reg=".shanbe"
    if zone == "ARVYEK":
        zone_reg="yekshanbe"
    if zone == "ARVDO":
        zone_reg="doshanbe"
    if zone == "ARVSE":
        zone_reg="seshanbe"
    if zone == "ARVCHAR":
        zone_reg="charshanbe"
    if zone == "ARVPANJ":
        zone_reg="panjshanbe"
    if zone == "ARVJOM":
        zone_reg="jome"
    sql = "SELECT url FROM urls WHERE hostname LIKE ? AND used_count < 50 ORDER BY used_count  ASC, RANDOM() limit 1"
    cur = conn.cursor()
    cur.execute(sql, ("%"+zone_reg+"%",))
    conn.commit()
    result = cur.fetchone()
    if result == None:
        return 0
    else:
        return result

def check_if_user_has_url(conn, id, zone):
    zone_reg="null"
    if zone == "NUR":
        zone_reg="scherehtznur"
    if zone == "HEL":
        zone_reg="scherehtzhel"
    if zone == "FLK":
        zone_reg="scherehtzflk"
    if zone == "ARVSHN":
        zone_reg=".shanbe"
    if zone == "ARVYEK":
        zone_reg="yekshanbe"
    if zone == "ARVDO":
        zone_reg="doshanbe"
    if zone == "ARVSE":
        zone_reg="seshanbe"
    if zone == "ARVCHAR":
        zone_reg="charshanbe"
    if zone == "ARVPANJ":
        zone_reg="panjshanbe"
    if zone == "ARVJOM":
        zone_reg="jome"
    sql = ''' SELECT user_url.url FROM user_url LEFT JOIN urls ON user_url.url = urls.url WHERE user_url.user = ? AND urls.hostname like ? '''
    cur = conn.cursor()
    cur.execute(sql, (id,"%"+zone_reg+"%"))
    conn.commit()
    if len(cur.fetchall()) == 0:
        return 0
    else:
        return cur.fetchone()

def select_user_byid(conn, id):
    sql = ''' SELECT id FROM users where id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
    if len(cur.fetchall()) == 0:
        return 0
    else:
        return cur.fetchone()

def get_user_url_by_id(conn, id):
    sql = ''' SELECT url FROM user_url where user = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
    sql_result=cur.fetchall()
    result=""
    if len(sql_result) != 0:
        return sql_result
    else:
        return 0

def insert_user(conn, user):
    select_id=select_user_byid(conn, user[0])
    if (select_id != user[0]) and (select_id == 0):
        sql = ''' INSERT INTO users(id, name, join_date)
                  VALUES(?, ?, ?) '''
        cur = conn.cursor()
        cur.execute(sql, user)
        conn.commit()
        return cur.lastrowid

def insert_user_url(conn, user, url):
    current_dateTime = datetime.now()
    user_url=[user, url, current_dateTime]
    sql = ''' INSERT INTO user_url(user, url, issued_date)
              VALUES(?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, user_url)
    conn.commit()
    return cur.lastrowid

import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
START_ROUTES, END_ROUTES = range(2)
# Callback data
keys = {
    "VPN" : "VPN",
    "DONATE" : "DONATE",
    "EURO" : "EURO",
    "TETHER" : "TETHER",
    "SERVER" : "SERVER",
    "ASK" : "ASK",
    "HELP" : "HELP",
    "STATUS" : "STATUS",
    # vpn regions
    "NUR" : "NUR",
    "FLK" : "FLK",
    "HEL" : "HEL",
    "ARV" : "ARV",
    "ARVSHN" : "ARVSHN",
    "ARVYEK" : "ARVYEK",
    "ARVDO" : "ARVDO",
    "ARVSE" : "ARVSE",
    "ARVCHAR" : "ARVCHAR",
    "ARVPANJ" : "ARVPANJ",
    "ARVJOM" : "ARVJOM",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    current_dateTime = datetime.now()
    database = r"/opt/bot/bot.db"
    conn = create_connection(database)
    user = [user.id, user.first_name , current_dateTime]
    insert_user(conn, user)
    keyboard = [
        [
            InlineKeyboardButton("میخوام کمک بکنم",       callback_data=keys['DONATE']),
            InlineKeyboardButton("میخوام فیلترشکن بگیرم", callback_data=keys['VPN']),
        ],
        [InlineKeyboardButton("وضعیت من چیه؟", callback_data=keys['STATUS'])],
        [InlineKeyboardButton("راهنمای استفاده", callback_data=keys['HELP'])],
        [InlineKeyboardButton("سوال داشتم", callback_data=keys['ASK'])],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    textMsg="""
درود

با توجه به اینکه محدودیت منابع داریم، لطفا به نکات زیر توجه کنید تا بتونیم همین فرمون رو بریم جلو و فیلترشکن‌ها رو پایدارتر بکنیم

۱. لطفا ابتدا تلاش کنید از لینکهای خارجی استفاده کنید. حتما هر سه منطقه خارجی رو چندین بار امتحان کنید، یعنی هرکدام را وصل کنید ببینید کار میکنه یا نه، اگه کار کرد که هیچی اگ کار نکرد قطع و وصل کنید و این کار را تا ۵ یا ۶ بار انجام بدید و اگر در این صورت کار نکرد برید روی لینکهای داخلی
۲. فقط و فقط در صورتی که از لینکهای خارجی نتیجه مطلوب نگرفتید برید سراغ لینکهای داخلی
۳. از لینکهای داخلی فقط برای جاهایی که فیلتره استفاده کنید مثلا برای یوتیوب و وقتی که میخواید آپارات بگیرید خاموشش کنید
۴. این فیلترشکن با کمکهای مالی که جمع شده نگهداری میشه و بدون کمکهای مالی خاموش خواهد شد و اگر امکانش براتون هست همراهی کنید اگر هم که امکانش براتون نیست اشکالی نداره این فی
لترشکنها برای شماست و امیدوارم که بتونم نگهش دارم
۵. سعی کنید به اندازه نیاز ضروریتون مصرف کنید و از اصرافش بپرهیزید
۶. به موارد بالا توجه کنید تا بتونیم برای همیشه داشته باشیم
    """

    await update.message.reply_text(textMsg, reply_markup=reply_markup)
    return START_ROUTES

async def vpn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("ایران - داخلی", callback_data=keys['ARV']),
        ],
        [    
            InlineKeyboardButton("آلمان - نورنبرگ", callback_data=f"vpn:{keys['NUR']}"),
        ],
        [
            InlineKeyboardButton("آلمان - فالکنشتاین", callback_data=f"vpn:{keys['FLK']}"),
            InlineKeyboardButton("فنلاند - هلسینکی", callback_data=f"vpn:{keys['HEL']}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="دوس داری توی کدوم منطقه باشه ؟", reply_markup=reply_markup
    )
    return START_ROUTES

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result=""
    database = r"/opt/bot/bot.db"
    conn = create_connection(database)
    user = update.callback_query.from_user
    query = update.callback_query
    region = query.data.split(':')[1]
    user_url = check_if_user_has_url(conn, user.id, region)
    
    if user_url == 0:
        url = get_url_byzone(conn, region)
        if url == 0:
            result="متاسفانه این منطقه ظرفیتش تکمیل شده لطفا جاهای دیگه رو امتحان کن"
            await update.callback_query.message.reply_text(result)
        else:
            inc_url_used_count(conn, url)
            insert_user_url(conn, user.id, url[0])
            result=f"""
            مقدار url پایین رو کپی کنید و در برنامه اضافه بکنید
            """
            await update.callback_query.message.reply_text(result)
            result=f"{url[0]}"
            await update.callback_query.message.reply_text(result)
    else:
        result="تو قبلا از این منطقه فیلترشکن گرفتی برای اینکه ببینیش از منوی اصلی گزینه (وضعیت من چیه؟) رو انتخاب کن"
        await update.callback_query.message.reply_text(result)

async def arv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("شنبه", callback_data=f"vpn:{keys['ARVSHN']}"),
            InlineKeyboardButton("یک شنبه", callback_data=f"vpn:{keys['ARVYEK']}"),
            InlineKeyboardButton("دو شنبه", callback_data=f"vpn:{keys['ARVDO']}"),
        ],
        [    
            InlineKeyboardButton("سه شنبه", callback_data=f"vpn:{keys['ARVSE']}"),
            InlineKeyboardButton("چهار شنبه", callback_data=f"vpn:{keys['ARVCHAR']}"),
            InlineKeyboardButton("پنج شنبه", callback_data=f"vpn:{keys['ARVPANJ']}"),
        ],
        [
            InlineKeyboardButton("جمعه", callback_data=f"vpn:{keys['ARVJOM']}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="روزتو انتخاب کن", reply_markup=reply_markup
    )
    return START_ROUTES


async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("دونیت با پول", callback_data=keys['EURO']),
            InlineKeyboardButton("دونیت با کریپتو", callback_data=keys['TETHER']),
            InlineKeyboardButton("دونیت با سرور", callback_data=keys['SERVER']),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="چطوری میخوای دونیت بکنی؟", reply_markup=reply_markup
    )
    return START_ROUTES

async def euro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text="""
    هرچقدر که دوست داشتی میتونی بآ آدرس زیر برام دونیت کنی
    خیلی ممنونم که ازم حمایت میکنی

    https://www.buymeacoffee.com/Bashsiz

    """
    await update.callback_query.message.reply_text(text)

async def tether(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text="""
    اینا هم برای کمک با کریپتو هست
    مرسی

    Tether: TRasnfQrKdZ2dNZsPxJ2oyxSw9Mj1z3XVS

    Dogecoin: D9eKyR4c2vymXaF1pfZqgSE4meBj4JGfbk

    """
    await update.callback_query.message.reply_text(text)

async def server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text="""
    اگه دوست داری خودت سرور بگیری و دونیت کنی بآ آیدی زیر بهم پیام بده تا باهم صحبت کنیم
    @MortezaBashsiz
    """
    await update.callback_query.message.reply_text(text)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text="""
    توی آدرس زیر یه ویدیو گذاشتم که باهاش میتونی راحت فیلترشکنت رو تنظیم کنی
    https://t.me/sudoer_grp/615
    یه نگاه بنداز اگه نشد بهم با آیدی زیر پیام بده و مشکلت رو مطرح بکن
    @MortezaBashsiz
    """
    await update.callback_query.message.reply_text(text)

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text="اگه سوالی داری که با راهنما نتونستی حلش کنی به آیدی من @MortezaBashsiz پیام بده"
    await update.callback_query.message.reply_text(text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user
    database = r"/opt/bot/bot.db"
    conn = create_connection(database)
    urls = get_user_url_by_id(conn, user.id)
    query = update.callback_query
    text=f"""
    فیلترشکنهای زیر برای توست
    """
    await update.callback_query.message.reply_text(text)
    for url in urls:
        text=f"{url[0]}"
        await update.callback_query.message.reply_text(text)

def main() -> None:
    application = Application.builder().token("numbernumbernumber:stringstringstringstring:").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                
                CallbackQueryHandler(get_config, pattern="^vpn:"),
                CallbackQueryHandler(arv, pattern="^{}$".format(keys['ARV'])),
                
                CallbackQueryHandler(vpn, pattern="^{}$".format(keys['VPN'])),
                CallbackQueryHandler(donate, pattern="^{}$".format(keys['DONATE'])),
                CallbackQueryHandler(tether, pattern="^{}$".format(keys['TETHER'])),
                CallbackQueryHandler(server, pattern="^{}$".format(keys['SERVER'])),
                CallbackQueryHandler(euro, pattern="^{}$".format(keys['EURO'])),
                CallbackQueryHandler(ask, pattern="^{}$".format(keys['ASK'])),
                CallbackQueryHandler(help, pattern="^{}$".format(keys['HELP'])),
                CallbackQueryHandler(status, pattern="^{}$".format(keys['STATUS'])),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()



if __name__ == "__main__":
    db()
    main()
