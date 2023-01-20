import threading
import telebot
import base64
import json
import sqlite3


#admins = [260723447]

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

bot = telebot.TeleBot("token token token token token", parse_mode=None)

text="""
درود

اطلاع‌رسانی

سپاس فراوان

"""
id="260723447"

database = r"/opt/bot/bot.db"
conn = create_connection(database)
sql = ''' SELECT id FROM users '''
cur = conn.cursor()
cur.execute(sql)
conn.commit()
users=cur.fetchall()
 

bot.send_message(id,text)
input("OK??")


for id in list(users):
    try:
        bot.send_message(id[0],text)
        print("sucess id:",id[0])
    except Exception as e:
        print("id:",id[0],"\n", e)
        sql = ''' DELETE FROM users where id=? '''
        cur = conn.cursor()
        cur.execute(sql, (id[0],))
        conn.commit()
