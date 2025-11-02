import os
from logic import DB_Manager
from config import *
from telebot import TeleBot, types

bot = TeleBot(TOKEN)
manager = DB_Manager(DATABASE)

cancel_button = "🚫 Отмена"
hideBoard = types.ReplyKeyboardRemove()


# --- Вспомогательные функции ---
def cansel(message):
    bot.send_message(message.chat.id, "❗ Чтобы посмотреть команды, используй /info", reply_markup=hideBoard)

def no_projects(message):
    bot.send_message(message.chat.id, "📭 У тебя пока нет проектов!\nДобавь их с помощью команды /new_project")

def gen_inline_markup(rows):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(types.InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(types.KeyboardButton(row))
    markup.add(types.KeyboardButton(cancel_button))
    return markup


# Словарь редактируемых полей проекта
attributes_of_projects = {
    "📛 Имя проекта": ["Введите новое имя проекта", "project_name"],
    "📝 Описание": ["Введите новое описание проекта", "description"],
    "🔗 Ссылка": ["Введите новую ссылку на проект", "url"],
    "📊 Статус": ["Выберите новый статус задачи", "status_id"]
}


# --- Информация о проекте ---
def info_project(message, user_id, project_name):
    info = manager.get_project_info(user_id, project_name)[0]
    project_name, description, url, photo, status_name = info
    skills = manager.get_project_skills(project_name)
    if not skills:
        skills = "Навыки пока не добавлены"

    text = f"""✨ <b>{project_name}</b>

📝 Описание: {description}
🔗 Ссылка: {url}
📊 Статус: {status_name}
💪 Навыки: {skills}"""

    if photo:
        bot.send_photo(message.chat.id, photo, caption=text, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, text, parse_mode="HTML")


# --- Команды ---
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "👋 Привет! Я — бот-портфолио!\nПомогу тебе хранить информацию о проектах 💼")
    info(message)

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, """
📖 <b>Команды бота:</b>

🆕 /new_project — добавить новый проект  
💪 /skills — добавить навыки к проекту  
📁 /projects — посмотреть список проектов  
🗑️ /delete — удалить проект  
✏️ /update_projects — обновить информацию о проекте  
ℹ️ Просто напиши название проекта — и я покажу все его данные!

🚫 В любой момент можно нажать "Отмена", чтобы выйти.
""", parse_mode="HTML")


# --- Добавление проекта ---
@bot.message_handler(commands=['new_project'])
def add_project(message):
    bot.send_message(message.chat.id, "🆕 Введи название нового проекта:")
    bot.register_next_step_handler(message, name_project)

def name_project(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "📸 Отправь фото проекта (или напиши 'нет'):")
    bot.register_next_step_handler(message, photo_project, data=data)

def photo_project(message, data):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        data.append(file_id)
    elif message.text and message.text.lower() == 'нет':
        data.append(None)
    else:
        bot.send_message(message.chat.id, "⚠️ Отправь фото или напиши 'нет'.")
        bot.register_next_step_handler(message, photo_project, data=data)
        return

    bot.send_message(message.chat.id, "🔗 Введи ссылку на проект:")
    bot.register_next_step_handler(message, link_project, data=data)

def link_project(message, data):
    data.append(message.text)
    statuses_rows = manager.get_statuses()             # [(id, name), ...]
    statuses = [x[1] for x in statuses_rows]           # имена для показа
    bot.send_message(message.chat.id, "📊 Выбери текущий статус проекта:", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_project, data=data, statuses_rows=statuses_rows)

def callback_project(message, data, statuses_rows):
    status_name = message.text
    if status_name == cancel_button:
        cansel(message)
        return

    valid_names = [r[1] for r in statuses_rows]
    if status_name not in valid_names:
        bot.send_message(message.chat.id, "⚠️ Выбери статус из списка:", reply_markup=gen_markup(valid_names))
        bot.register_next_step_handler(message, callback_project, data=data, statuses_rows=statuses_rows)
        return

    status_id = next(r[0] for r in statuses_rows if r[1] == status_name)
    user_id, name, photo, url = data
    description = None
    project_data = [(user_id, name, description, url, status_id, photo)]
    manager.insert_project(project_data)
    bot.send_message(message.chat.id, "✅ Проект успешно сохранён!")


# --- Добавление навыков ---
@bot.message_handler(commands=['skills'])
def skill_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "💼 Выбери проект:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)

def skill_project(message, projects):
    project_name = message.text
    if project_name == cancel_button:
        cansel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "⚠️ Нет такого проекта!", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects)
        return
    skills = [x[1] for x in manager.get_skills()]
    bot.send_message(message.chat.id, "💪 Выбери навык:", reply_markup=gen_markup(skills))
    bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)

def set_skill(message, project_name, skills):
    skill = message.text
    user_id = message.from_user.id
    if skill == cancel_button:
        cansel(message)
        return
    if skill not in skills:
        bot.send_message(message.chat.id, "⚠️ Неверный навык, выбери из списка:", reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills)
        return
    manager.insert_skill(user_id, project_name, skill)
    bot.send_message(message.chat.id, f"✅ Навык <b>{skill}</b> добавлен к проекту <b>{project_name}</b>!", parse_mode="HTML")


# --- Просмотр проектов ---
@bot.message_handler(commands=['projects'])
def get_projects(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"📌 {x[2]}" for x in projects])
        bot.send_message(message.chat.id, f"📁 Твои проекты:\n\n{text}", reply_markup=gen_inline_markup([x[2] for x in projects]))
    else:
        no_projects(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    project_name = call.data
    info_project(call.message, call.from_user.id, project_name)


# --- Удаление проекта ---
@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "🗑️ Выбери проект для удаления:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
    else:
        no_projects(message)

def delete_project(message, projects):
    project = message.text
    user_id = message.from_user.id
    if project == cancel_button:
        cansel(message)
        return
    if project not in projects:
        bot.send_message(message.chat.id, "⚠️ Такого проекта нет. Попробуй снова:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f"🗑️ Проект <b>{project}</b> удалён!", parse_mode="HTML")


# --- Обновление данных проекта ---
@bot.message_handler(commands=['update_projects'])
def update_project(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "✏️ Выбери проект для изменения:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
    else:
        no_projects(message)

def update_project_step_2(message, projects):
    project_name = message.text
    if project_name == cancel_button:
        cansel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "⚠️ Ошибка! Попробуй снова:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
        return
    bot.send_message(message.chat.id, "Что хочешь изменить?", reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)

def update_project_step_3(message, project_name):
    attribute = message.text
    reply_markup = None
    if attribute == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "⚠️ Ошибка! Попробуй снова:", reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    elif attribute == "📊 Статус":
        rows = manager.get_statuses()
        reply_markup = gen_markup([x[1] for x in rows])
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup=reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attributes_of_projects[attribute][1])

def update_project_step_4(message, project_name, attribute):
    update_info = message.text
    if attribute == "status_id":
        rows = manager.get_statuses()
        names = [x[1] for x in rows]
        if update_info in names:
            update_info = next(x[0] for x in rows if x[1] == update_info)
        elif update_info == cancel_button:
            cansel(message)
            return
        else:
            bot.send_message(message.chat.id, "⚠️ Неверный статус! Попробуй снова:", reply_markup=gen_markup(names))
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, project_name, user_id)
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "✅ Изменения успешно внесены!")


# --- Обработка текста (название проекта) ---
@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    projects = [x[2] for x in manager.get_projects(user_id)]
    project = message.text
    if project in projects:
        info_project(message, user_id, project)
        return
    bot.reply_to(message, "❓ Не понял запрос. Напиши /info, чтобы узнать, что я умею.")


# --- Запуск ---
if __name__ == '__main__':
    bot.infinity_polling()
