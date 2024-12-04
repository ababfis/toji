import telebot
from telebot import types
import random
import setings
import datetime
import json

bot = telebot.TeleBot(setings.BOT_TOKEN)

# Словари для хранения данных пользователей и цитат
user_data = {}
quotes = []

# Функции для загрузки и сохранения данных
def load_user_data():
    global user_data
    try:
        with open('user_data.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}
    
    # Инициализация отсутствующих ключей для всех пользователей
    for data in user_data.values():
        data.setdefault('name', 'nn')
        data.setdefault('tea_drink', 0)
        data.setdefault('kettle_failed', 30)

def save_user_data():
    with open('user_data.json', 'w', encoding='utf-8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)

def load_quotes():
    global quotes
    try:
        with open('quotes.json', 'r', encoding='utf-8') as file:
            quotes = json.load(file)
    except FileNotFoundError:
        quotes = []

def save_quotes():
    with open('quotes.json', 'w', encoding='utf-8') as file:
        json.dump(quotes, file, ensure_ascii=False, indent=4)

# Функция для добавления пользователя
def add_user(user):
    user_id = str(user.id)
    user_data.setdefault(user_id, {})
    user_data[user_id].setdefault('name', user.first_name or 'nn')
    user_data[user_id].setdefault('tea_drink', 0)
    user_data[user_id].setdefault('kettle_failed', 30)

# Обработка статуса бота в чате
@bot.my_chat_member_handler()
def check_admin(message: types.ChatMemberUpdated):
    if message.chat.type in ['group', 'supergroup']:
        old_status = message.old_chat_member.status
        new_status = message.new_chat_member.status
        if old_status != 'administrator' and new_status == 'administrator':
            bot.send_message(chat_id=message.chat.id, text='Всем привет! Я теперь администратор этого чата.\nНапишите /info, чтобы узнать мои команды.')

#Обработка запроса команды "Выпить чай"
@bot.message_handler(func=lambda message: message.text and message.text.lower() == 'выпить чай')
def tea(message: types.Message):
    user = message.from_user
    user_id = str(user.id)
    add_user(user)

    user_info = user_data[user_id]

    if user_info['kettle_failed'] > 0:
        if random.randint(1, 100) <= 25:
            user_info['kettle_failed'] -= 1
            if user_info['kettle_failed'] == 0:
                response = 'ТЫ БЫЛ ИЗБРАННИКОМ! ВСЕ ДУМАЛИ, ЧТО ТЫ БУДЕШЬ ЗАЩИЩАТЬ НАС ОТ ЖЕНЩИН, А НЕ ПРИМКНЕШЬ К НИМ!'
            else:
                response = f'Чайник не вскипел 🤬 Смотри, чтобы девушка не появилась. Осталось не выпитых чаёв: {user_info["kettle_failed"]}'
        else:
            tea_amount = random.randint(1, 300)
            user_info['tea_drink'] += tea_amount
            if tea_amount <= 150:
                response = (
                    f'Ты выпил {tea_amount} чая\nВыпито чая всего: {user_info["tea_drink"]}\nОсталось не выпитых чаёв: {user_info["kettle_failed"]}'
                )
            else:
                response = (
                    f'ОМАГАД ТЫ ВЫПИЛ АЖ {tea_amount} Л ЧАЯ!!!\nВыпито чая всего: {user_info["tea_drink"]}\nОсталось не выпитых чаёв: {user_info["kettle_failed"]}'
                )
    else:
        response = 'Тебе уже нет смысла пить чай, ситх...'

    bot.reply_to(message, response)
    save_user_data()


# Обработка функции отправки гифки
@bot.message_handler(content_types=['video', 'animation'])
def media(message: types.Message):
    gif = r'src\GIF\video_2024-11-17_11-43-49.mp4'
    try:
        with open(gif, 'rb') as file:
            bot.send_animation(message.chat.id, file)
    except Exception as e:
        print(f"Ошибка отправки гифки: {e}")

# Обработка любого сообщения и изменение количества сообщений отправленных пользователем
@bot.message_handler(func=lambda message: True, content_types=['text', 'sticker', 'photo', 'video', 'audio', 'document', 'location', 'contact', 'video_note', 'voice'])
def all_message_handler(message: types.Message):
    user = message.from_user
    user_id = str(user.id)
    add_user(user)

    user_info = user_data[user_id]
    today = datetime.date.today()
    week = datetime.date.today().isocalendar()[1]
    month = datetime.date.today().month


# Обработчик команды "/q" для работы с цитатами
@bot.message_handler(commands=['q'])
def quotes_chat(message: types.Message):
    if message.reply_to_message:
        quot = message.reply_to_message.text
        quotes.append(quot)
        bot.reply_to(message, f'Цитата сохранена под номером {len(quotes)}')
        save_quotes()
    elif len(message.text.split()) > 1:
        try:
            _, num = message.text.split()
            num = int(num) - 1
            if 0 <= num < len(quotes):
                selected_q = quotes[num]
                bot.reply_to(message, f'{selected_q}')
            else:
                bot.reply_to(message, 'Цитата не найдена')
        except (ValueError, IndexError):
            bot.reply_to(message, 'Неверный формат команды. Вот правильный формат: /q <номер> (например, /q 2).')
    else:
        if quotes:
            response = "\n".join([f"{i + 1}. {quote}" for i, quote in enumerate(quotes)])
            bot.reply_to(message, f"Сохранённые цитаты:\n{response}")
        else:
            bot.reply_to(message, "Нет сохранённых цитат.")

# Запуск бота
if __name__ == '__main__':
    load_user_data()
    load_quotes()
    bot.polling()