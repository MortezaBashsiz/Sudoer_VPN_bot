#!/usr/bin/env python

import sqlite3, csv, sys
from sqlite3 import Error
from datetime import datetime


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def main():
    csv_file= sys.argv[1] 
    database = r"/opt/bot/bot.db"
    con = create_connection(database)
    cur = con.cursor()
    current_dateTime = datetime.now()
    with open(csv_file) as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=';')
        cur.executemany("INSERT INTO urls (url, hostname, issued_date) VALUES (?, ?, DATETIME('now'))", csv_reader_object)
    con.commit()
    con.close()

if __name__ == "__main__":
    main()

