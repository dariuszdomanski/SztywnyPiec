# Sztywny Piec 2024

import json
import os
import sqlite3
import subprocess
import time


DATA_URL = 'https://192.168.1.20/json/all.json'
DB_PATH = '/mnt/d/GrafanaDataSource/temperature.db'
LOOP_PERIOD = 4


def fetch_data(url):
    try:
        result = subprocess.run(['curl', '-k', url], capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data['ds1'], data['ds2'], data['ds3']
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None


def save_to_db(ds1, ds2, ds3):
    try:
        if not os.access(DB_PATH, os.W_OK):
            raise PermissionError(f"Cannot write to database file: {DB_PATH}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Temperature (
                id INTEGER PRIMARY KEY,
                sensor TEXT NOT NULL,
                value REAL NOT NULL
            )
        ''')
        cursor.execute('DELETE FROM Temperature')
        cursor.execute('INSERT INTO Temperature (sensor, value) VALUES (?, ?)', ('ds1', ds1))
        cursor.execute('INSERT INTO Temperature (sensor, value) VALUES (?, ?)', ('ds2', ds2))
        cursor.execute('INSERT INTO Temperature (sensor, value) VALUES (?, ?)', ('ds3', ds3))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving data: {e}")


while True:
    ds1, ds2, ds3 = fetch_data(DATA_URL)
    if ds1 is not None and ds2 is not None and ds3 is not None:
        save_to_db(ds1, ds2, ds3)
    time.sleep(LOOP_PERIOD)
