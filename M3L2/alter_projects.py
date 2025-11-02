import sqlite3
from config import DATABASE

# Подключение к базе данных
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Название таблицы
table_name = 'projects'

# Название нового столбца и его тип данных
new_column_name = 'photo'
new_column_type = 'TEXT'

# Выполнение запроса на добавление столбца
try:
    alter_query = f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_column_type}"
    cursor.execute(alter_query)
    print("✅ Столбец 'photo' успешно добавлен в таблицу projects.")
except sqlite3.OperationalError:
    print("ℹ️ Столбец 'photo' уже существует — ничего менять не нужно.")

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
