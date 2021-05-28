# @Readability_test_bot
import telebot

# from books_n_kids import predict_text_class

bot = telebot.TeleBot('TELEGRAM_TOKEN')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Привет, отправь мне два слова и я скажу тебе, однокоренные они или нет')
    else:
        # result = predict_cognete_words(message.text)
        # bot.send_message(message.from_user.id, result)