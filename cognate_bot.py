# @Readability_test_bot
import telebot
from baseline import getEvristicCognate, init
# from books_n_kids import predict_text_class

bot = telebot.TeleBot('1790787625:AAGY4fc0kyIiuiNhxUtTMnOqjZ8oSq3NXgM')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Привет, отправь мне два слова и я скажу тебе, однокоренные они или нет')
    else:
        
        words = message.text.lower().split()
        if not words or len(words) != 2:
            bot.send_message(message.from_user.id, 'Привет, отправь мне два слова')
            return
        
        word1, word2 = words
        if (word1 == word2 or getEvristicCognate(word1, word2)):
            bot.send_message(message.from_user.id, 'Однокоренные')
        else:
            bot.send_message(message.from_user.id, 'Неоднокоренные')
        # result = predict_cognete_words(message.text)
        # bot.send_message(message.from_user.id, result)

if __name__ == '__main__':
    init("models/morphemes-3-5-3-memo_dima.json")
    print("Хуй")
    bot.polling()