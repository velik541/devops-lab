from flask import Flask, render_template
import psycopg2
import os
import time

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "devops_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret_pass")

def get_db_connection():
    # Функция для безопасного подключения к БД с повторными попытками
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2)
    raise Exception("Could not connect to the database")

def init_db():
    # Инициализация таблицы просмотров
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS page_views (
            id SERIAL PRIMARY KEY,
            view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Инициализируем базу данных при старте
try:
    init_db()
    db_available = True
except Exception as e:
    print(f"Database init failed: {e}")
    db_available = False

@app.route("/")
def home():
    db_status = "Connected successfully"
    visit_count = 0
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Записываем текущий визит
        cur.execute("INSERT INTO page_views DEFAULT VALUES;")
        conn.commit()
        
        # Считаем общее количество визитов
        cur.execute("SELECT COUNT(*) FROM page_views;")
        visit_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
    except Exception as e:
        db_status = f"Connection error: {e}"
        visit_count = "N/A"

    return render_template("index.html", db_status=db_status, visit_count=visit_count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)