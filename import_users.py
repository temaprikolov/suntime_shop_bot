import csv
import sqlite3
from datetime import datetime
import os

def import_from_csv(csv_file='users.csv'):
    """Импорт пользователей из CSV файла"""
    
    # Подключаемся к базе данных бота
    db_path = 'data/database.db'
    
    if not os.path.exists(db_path):
        print("❌ База данных бота не найдена!")
        print("Сначала запустите бота хотя бы один раз")
        return
    
    if not os.path.exists(csv_file):
        print(f"❌ Файл {csv_file} не найден!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу если ее нет (на всякий случай)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        joined_at DATETIME,
        is_admin BOOLEAN DEFAULT 0
    )
    ''')
    
    users_imported = 0
    users_skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Адаптируйте названия колонок под ваш CSV файл
                user_id = int(row.get('user_id') or row.get('User ID') or row.get('id') or 0)
                username = row.get('username') or row.get('Username') or row.get('user') or ''
                first_name = row.get('first_name') or row.get('First Name') or row.get('Имя') or ''
                last_name = row.get('last_name') or row.get('Last Name') or row.get('Фамилия') or ''
                
                if not user_id:
                    print(f"⚠️ Пропущена строка без user_id: {row}")
                    users_skipped += 1
                    continue
                
                # Проверяем, есть ли уже такой пользователь
                cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
                if cursor.fetchone():
                    print(f"⚠️ Пользователь {user_id} уже существует, пропускаю")
                    users_skipped += 1
                    continue
                
                # Вставляем пользователя
                cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, joined_at, is_admin)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, datetime.now(), 0))
                
                users_imported += 1
                print(f"✅ Импортирован пользователь {user_id} ({username})")
                
            except Exception as e:
                print(f"❌ Ошибка при импорте строки {row}: {e}")
                users_skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Импорт завершен!")
    print(f"✅ Успешно импортировано: {users_imported}")
    print(f"⚠️ Пропущено: {users_skipped}")

if __name__ == "__main__":
    import_from_csv()
