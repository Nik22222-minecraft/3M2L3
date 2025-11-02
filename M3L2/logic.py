import sqlite3
from config import DATABASE

# --- Стандартные значения для инициализации ---
skills = [(_,) for _ in ['Python', 'SQL', 'API', 'Telegram', 'HTML', 'CSS', 'Flask']]
statuses = [(_,) for _ in [
    'На этапе проектирования',
    'В процессе разработки',
    'Разработан. Готов к использованию.',
    'Обновлен',
    'Завершен. Не поддерживается'
]]


class DB_Manager:
    def __init__(self, database):
        self.database = database

    # --- Создание таблиц ---
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                photo TEXT,
                status_id INTEGER,
                FOREIGN KEY(status_id) REFERENCES status(status_id)
            )''')

            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY,
                skill_name TEXT UNIQUE
            )''')

            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                project_id INTEGER,
                skill_id INTEGER,
                FOREIGN KEY(project_id) REFERENCES projects(project_id),
                FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
            )''')

            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY,
                status_name TEXT UNIQUE
            )''')

            conn.commit()

    # --- Универсальный метод для массового выполнения ---
    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    # --- Универсальный метод выборки ---
    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    # --- Проверка, пустая ли таблица ---
    def __is_table_empty(self, table_name):
        sql = f"SELECT COUNT(*) FROM {table_name}"
        result = self.__select_data(sql)
        return result[0][0] == 0

    # --- Заполнение таблиц по умолчанию ---
    def default_insert(self):
        if self.__is_table_empty("skills"):
            sql = 'INSERT INTO skills (skill_name) VALUES (?)'
            self.__executemany(sql, skills)
            print("✅ Навыки добавлены по умолчанию.")
        else:
            print("ℹ️ Таблица skills уже заполнена.")

        if self.__is_table_empty("status"):
            sql = 'INSERT INTO status (status_name) VALUES (?)'
            self.__executemany(sql, statuses)
            print("✅ Статусы добавлены по умолчанию.")
        else:
            print("ℹ️ Таблица status уже заполнена.")

    # --- Добавление проекта ---
    def insert_project(self, data):
        sql = '''INSERT INTO projects 
                 (user_id, project_name, description, url, status_id, photo)
                 VALUES (?, ?, ?, ?, ?, ?)'''
        self.__executemany(sql, data)
        print("📁 Проект(ы) добавлен(ы).")

    # --- Добавление навыка к проекту ---
    def insert_skill(self, user_id, project_name, skill):
        project = self.__select_data(
            "SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?",
            (project_name, user_id)
        )
        skill_res = self.__select_data(
            "SELECT skill_id FROM skills WHERE skill_name = ?",
            (skill,)
        )

        if not project or not skill_res:
            print("⚠️ Ошибка: проект или навык не найден.")
            return

        project_id = project[0][0]
        skill_id = skill_res[0][0]

        sql = 'INSERT OR IGNORE INTO project_skills VALUES (?, ?)'
        self.__executemany(sql, [(project_id, skill_id)])
        print(f"🧩 Навык '{skill}' добавлен к проекту '{project_name}'.")

    # --- Получение всех статусов ---
    def get_statuses(self):
        return self.__select_data("SELECT * FROM status")

    # --- Получение ID статуса по имени ---
    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        return res[0][0] if res else None

    # --- Получение проектов пользователя ---
    def get_projects(self, user_id):
        sql = "SELECT project_id, project_name, description FROM projects WHERE user_id = ?"
        return self.__select_data(sql, (user_id,))

    # --- Получение project_id по имени ---
    def get_project_id(self, project_name, user_id):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        res = self.__select_data(sql, (project_name, user_id))
        return res[0][0] if res else None

    # --- Получение всех навыков ---
    def get_skills(self):
        return self.__select_data('SELECT * FROM skills')

    # --- Получение навыков проекта ---
    def get_project_skills(self, project_name):
        sql = '''SELECT skill_name FROM projects 
                 JOIN project_skills ON projects.project_id = project_skills.project_id 
                 JOIN skills ON skills.skill_id = project_skills.skill_id 
                 WHERE project_name = ?'''
        res = self.__select_data(sql, (project_name,))
        return ', '.join([x[0] for x in res]) if res else "Нет навыков"

    # --- Получение информации о проекте ---
    def get_project_info(self, user_id, project_name):
        sql = '''SELECT project_name, description, url, photo, status_name FROM projects 
                 JOIN status ON status.status_id = projects.status_id 
                 WHERE project_name = ? AND user_id = ?'''
        return self.__select_data(sql, (project_name, user_id))

    # --- Обновление имени проекта ---
    def update_projects(self, project_id, new_name):
        sql = "UPDATE projects SET project_name = ? WHERE project_id = ?"
        self.__executemany(sql, [(new_name, project_id)])
        print(f"✏️ Проект с ID {project_id} переименован в '{new_name}'.")

    # --- Удаление проекта ---
    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])
        print(f"🗑 Проект с ID {project_id} удалён.")

    # --- Удаление связи проект-навык ---
    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM project_skills WHERE project_id = ? AND skill_id = ?"
        self.__executemany(sql, [(project_id, skill_id)])
        print(f"🗑 Удалена связь проект {project_id} ↔ навык {skill_id}.")

    # --- Удаление статуса ---
    def delete_status(self, status_id):
        sql = "DELETE FROM status WHERE status_id = ?"
        self.__executemany(sql, [(status_id,)])
        print(f"🗑 Статус с ID {status_id} удалён.")

    # --- Добавление нового навыка ---
    def add_skill(self, skill_name):
        sql = "INSERT OR IGNORE INTO skills (skill_name) VALUES (?)"
        self.__executemany(sql, [(skill_name,)])
        print(f"🆕 Навык '{skill_name}' добавлен.")

    # --- Обновление названия навыка ---
    def update_skill(self, skill_id, new_name):
        sql = "UPDATE skills SET skill_name = ? WHERE skill_id = ?"
        self.__executemany(sql, [(new_name, skill_id)])
        print(f"✏️ Навык с ID {skill_id} обновлён на '{new_name}'.")

    # --- Обновление статуса проекта ---
    def update_project_status(self, project_id, new_status_id):
        sql = "UPDATE projects SET status_id = ? WHERE project_id = ?"
        self.__executemany(sql, [(new_status_id, project_id)])
        print(f"🔄 Статус проекта с ID {project_id} обновлён.")


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()

    # Примеры тестов
    manager.add_skill("AI")
    manager.update_skill(1, "Python 3")
    manager.update_project_status(1, 2)
