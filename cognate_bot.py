import os
import telebot
from enum import Enum
from baseline import getEvristicCognate, init, getRoots, generate_bitmask_for_list, get_only_root
from logger import save_cognate

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
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn_root = telebot.types.KeyboardButton('Найти корень слова')
    btn_cognate = telebot.types.KeyboardButton('Является ли пара однокоренной?')
    markup.row(btn_root, btn_cognate)
    bot.send_message(message.from_user.id, """Добро пожаловать в бота для проекта НКРЯ 2.0 
Этот бот может оценить возраст потенциального читателя для предложенного текста, выделить корень слова и узнать являются ли пара слов однокоренной.

"Является ли пара однокоренной?" определяет, является ли пара слов однокоренной

"Найти корень слова" определяет корень слова предложенного слова
""", reply_markup=markup)
    users[message.from_user.id] = UserContext.NONE


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, """Этот бот может оценить возраст потенциального читателя для предложенного текста, выделить корень слова и узнать являются ли пара слов однокоренной.

"Является ли пара однокоренной?" определяет, является ли пара слов однокоренной

"Найти корень слова" определяет корень слова предложенного слова
""")
    users[message.from_user.id] = UserContext.NONE


@bot.message_handler(regexp='Является ли пара однокоренной?')
def cognate(message):
    bot.send_message(message.from_user.id, 'Отправь мне пару слов и я скажу тебе однокоренные они или нет!')
    users[message.from_user.id] = UserContext.COGNATE


@bot.message_handler(regexp='Найти корень слова')
def root(message):
    bot.send_message(message.from_user.id, 'Отправь мне слово и я скажу тебе его корень!')
    users[message.from_user.id] = UserContext.ROOT


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_status = users.get(message.from_user.id, UserContext.NONE)
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

        # btn_incorrect = telebot.types.InlineKeyboardButton(text="Тут ошибка", callback_data=f'error-root_{word}')
        # btn_correct = telebot.types.InlineKeyboardButton(text="Все верно", callback_data=f'correct-root_{word}')
        # btn_markup = telebot.types.InlineKeyboardMarkup()
        # btn_markup.add(btn_correct, btn_incorrect)
        bot.send_message(message.from_user.id, f'Большими буквами выделен корень слова\n{"".join(word_with_root_list)}')

    elif user_status == UserContext.COGNATE:
        words = message.text.lower().split()
        if not words or len(words) != 2:
            bot.send_message(message.from_user.id, 'Отправь мне пару слов')
            return

        word1, word2 = words
        btn_incorrect = telebot.types.InlineKeyboardButton(text="Тут ошибка",
                                                           callback_data=f'error-cognate_{word1}&{word2}')
        btn_correct = telebot.types.InlineKeyboardButton(text="Все верно",
                                                         callback_data=f'correct-cognate_{word1}&{word2}')
        btn_markup = telebot.types.InlineKeyboardMarkup()
        btn_markup.add(btn_correct, btn_incorrect)
        if word1 == word2 or getEvristicCognate(word1, word2):
            bot.send_message(message.from_user.id, 'Однокоренные', reply_markup=btn_markup)
        else:
            bot.send_message(message.from_user.id, 'Неоднокоренные', reply_markup=btn_markup)


def root_handler(query, data):
    pass


inline_handlers = {
    "error-root": root_handler,
    "correct-root": root_handler,
    "error-cognate": lambda x, y: save_cognate(*y.split('&'), status=False),
    "correct-cognate": lambda x, y: save_cognate(*y.split('&'), status=True),
}


@bot.callback_query_handler(func=lambda call: True)
def query_text(inline_query):
    query_type, query_data = inline_query.data.split("_", 1)
    if query_type in inline_handlers:
        inline_handlers[query_type](inline_query, query_data)

    bot.answer_callback_query(inline_query.id, "Спасибо за ваш отзыв")
    bot.edit_message_reply_markup(inline_query.message.chat.id, inline_query.message.id)


if __name__ == '__main__':
    init("models/morphemes-3-5-3-memo_dima.json")
    print("Start polling")
    bot.polling()
