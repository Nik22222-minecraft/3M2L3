import telebot
from telebot import types  # Import necessary classes for keyboard creation

class Question:

    def __init__(self, text, answer_id, *options):
        self.__text = text
        self.__answer_id = answer_id
        self.options = options

    # Задание 1 - Создай геттер для получения текста вопроса
    @property
    def text(self):  # Corrected getter name to 'text' for simplicity
        return self.__text

    def gen_markup(self):
        # Задание 3 - Создай метод для генерации Inline клавиатуры
        markup = types.InlineKeyboardMarkup()
        markup.row_width = len(self.options)

        for i, option in enumerate(self.options):
            if i == self.__answer_id:
                markup.add(types.InlineKeyboardButton(option, callback_data='correct'))
            else:
                markup.add(types.InlineKeyboardButton(option, callback_data='wrong'))

        return markup

# Задание 4 - заполни словарь своими вопросами
quiz_questions = {
    1: Question("Что котики делают, когда никто их не видит?", 1, "Спят", "Пишут мемы"),
    2: Question("Как котики выражают свою любовь?", 0, "Громким мурлыканием", "Отправляют фото на Instagram", "Гавкают"),
    3: Question("Какие книги котики любят читать?", 3, "Обретение вашего внутреннего урр-мирения", "Тайм-менеджмент или как выделить 18 часов в день для сна", "101 способ уснуть на 5 минут раньше, чем хозяин", "Пособие по управлению людьми"),
    4: Question("Любимая игра котиков?", 2, "Прятки", "Догонялки", "Охота на лазерную указку"),
    5: Question("Что котики говорят во сне?", 1, "Мур-мур", "Ня-ня", "Гав-гав"),
    6: Question("Самый большой страх котиков?", 0, "Пылесос", "Собака", "Вода"),
    7: Question("Что любят есть котики?", 2, "Тортики", "Конфеты", "Рыбку"),
    8: Question("Как котики будят хозяина?", 1, "Кричат", "Скидывают вещи со стола", "Кусают"),
    9: Question("Самое любимое место для сна?", 0, "Коробка", "Кровать", "Диван"),
    10: Question("Какое умение у котиков самое главное?", 3, "Лазить по деревьям", "Ловить мышей", "Петь", "Быть милыми")
}