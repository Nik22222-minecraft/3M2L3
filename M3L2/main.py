from logic import DB_Manager
from config import DATABASE

manager = DB_Manager(DATABASE)

# создаём таблицы и заполняем начальными значениями
manager.create_tables()
manager.default_insert()

# пример добавления проекта
project_data = [
    (1, "Бот-портфолио", "Хранит проекты и навыки", "https://example.com", 2, "portfolio.png")
]
manager.insert_project(project_data)

# проверим всё
print("\nПроекты:")
print(manager.get_projects(1))

print("\nНавыки:")
print(manager.get_skills())

print("\nСтатусы:")
print(manager.get_statuses())
