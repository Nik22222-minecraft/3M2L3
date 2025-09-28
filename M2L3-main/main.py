import telebot
from telebot import types  # Import necessary classes for keyboard creation
from config import token
from collections import defaultdict # Задание 7 - испортируй команду defaultdict
from logic import quiz_questions

user_responses = {}
# Задание 8 - создай словарь points для сохранения количества очков пользователя
user_points = defaultdict(int) # Используем defaultdict для удобства

bot = telebot.TeleBot(token)

def send_question(chat_id):
    question_number = user_responses[chat_id] + 1 #Get the next question number
    if question_number in quiz_questions: #Added check if questions_number is in questions dict
        question = quiz_questions[question_number] # Get the question by question number
        bot.send_message(chat_id, question.text, reply_markup=question.gen_markup()) # Send text from the question object
    else:
        bot.send_message(chat_id, f"Вы ответили на все вопросы! Ваш счет: {user_points[chat_id]}")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data == "correct":
        bot.answer_callback_query(call.id, "Answer is correct")
        # Задание 9 - добавь очки пользователю за правильный ответ
        user_points[call.message.chat.id] += 1 # Add points to the user
    elif call.data == "wrong":
        bot.answer_callback_query(call.id,  "Answer is wrong")
      
    # Задание 5 - реализуй счетчик вопросов
    user_responses[call.message.chat.id] += 1 #Increment question counter

    # Задание 6 - отправь пользователю сообщение с количеством его набранных очков, если он ответил на все вопросы, а иначе отправь следующий вопрос
    question_number = user_responses[call.message.chat.id] + 1 #Get the next question number
    if question_number <= len(quiz_questions):  # Checking if the user has answered all questions
        send_question(call.message.chat.id)  # Sending next question
    else:
        bot.send_message(call.message.chat.id, f"Вы ответили на все вопросы! Ваш счет: {user_points[call.message.chat.id]}") # Sending the final score


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in user_responses.keys():
        user_responses[message.chat.id] = 0
        user_points[message.chat.id] = 0 # Initialize user points upon /start
        send_question(message.chat.id)


bot.infinity_polling()
