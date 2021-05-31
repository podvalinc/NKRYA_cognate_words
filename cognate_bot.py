import os
import telebot
from enum import Enum
from baseline import getEvristicCognate, init, getRoots, generate_bitmask_for_list, get_only_root

token = os.environ.get('AUTH_TOKEN')

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(token)


class UserContext(Enum):
    NONE = 0,
    ROOT = 1,
    COGNATE = 2


users = {}


@bot.middleware_handler
def register_user(message):
    users[message.from_user.id] = users.get(message.from_user.id, UserContext.NONE)


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
    btn_root = telebot.types.KeyboardButton('Найти корень слова🔎')
    btn_cognate = telebot.types.KeyboardButton('Является ли пара однокоренной?')
    markup.row(btn_root, btn_cognate)
    bot.send_message(message.from_user.id, """Добро пожаловать в бота для проекта НКРЯ 2.0 
    Этот бот может оценить возраст потенциального читателя для предложенного текста, выделить корень слова и узнать являются ли пара слов однокоренной.

Является ли пара однокоренной? определяет вероятность того, является ли пара слов однокоренной

"Найти корень слова🔎" определяет корень слова
""", reply_markup=markup)
    users[message.from_user.id] = UserContext.NONE


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, """Этот бот может оценить возраст потенциального читателя для предложенного текста, выделить корень слова и узнать являются ли пара слов однокоренной.

"Является ли пара однокоренной?" определяет, является ли пара слов однокоренной

"Найти корень слова🔎" определяет корень слова предложенного слова
""")
    users[message.from_user.id] = UserContext.NONE


@bot.message_handler(commands=['cognate'])
def cognate(message):
    bot.send_message(message.from_user.id, 'Отправь мне пару слов и я скажу тебе однокоренные они или нет!')
    users[message.from_user.id] = UserContext.COGNATE


@bot.message_handler(commands=['root'])
def root(message):
    bot.send_message(message.from_user.id, 'Отправь мне слово и я скажу тебе его корень!')
    users[message.from_user.id] = UserContext.ROOT


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_status = users[message.from_user.id]
    print(user_status)

    if user_status == UserContext.NONE:
        help(message)
    elif user_status == UserContext.ROOT:
        words = message.text.lower().split()
        if not words or len(words) != 1:
            bot.send_message(message.from_user.id, 'Отправь мне только одно слово')
            return
        word = words[0]
        roots = getRoots([word])
        bitmask = generate_bitmask_for_list(word, get_only_root(roots[0]))
        word_with_root_list = [word[i].upper() if v else word[i] for i, v in enumerate(bitmask)]
        bot.send_message(message.from_user.id, f'Большими буквами выделен корень слова\n{"".join(word_with_root_list)}')

    elif user_status == UserContext.COGNATE:
        words = message.text.lower().split()
        if not words or len(words) != 2:
            bot.send_message(message.from_user.id, 'Отправь мне пару слова')
            return

        word1, word2 = words
        if word1 == word2 or getEvristicCognate(word1, word2):
            bot.send_message(message.from_user.id, 'Однокоренные')
        else:
            bot.send_message(message.from_user.id, 'Неоднокоренные')


if __name__ == '__main__':
    init("models/morphemes-3-5-3-memo_dima.json")
    print("Start polling")
    bot.polling()
