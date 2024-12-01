import telebot
from telebot import types
import random
import db, setings
import datetime
import json

bot = telebot.TeleBot(setings.BOT_TOKEN)
quotes = {}
user_data = {}
tea_stats = {}

def load_user_data():
    global user_data
    try:
        with open('user_data.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}

def save_user_data():
    with open('user_data.json', 'w', encoding='utf-8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)

def load_quotes():
    global quotes
    try:
        with open('quotes.json', 'r', encoding='utf-8') as file:
            quotes = json.load(file)
    except FileNotFoundError:
        quotes = {}

def save_quotes():
    with open('quotes.json', 'w', encoding='utf-8') as file:
        json.dump(quotes, file, ensure_ascii=False, indent=4)


def add_user(chat_id, user):
    global user_data 
    if chat_id not in user_data:
        user_data[chat_id] = []

    if not any(x['id'] == user.id for x in user_data[chat_id]):
        user_data[chat_id].append({'id': user.id, 'name': user.first_name or 'nn'}) 



@bot.my_chat_member_handler()

def drink_tea(chat_id, user_id, user_name):
    global tea_stats
    if chat_id not in tea_stats:
        tea_stats[chat_id] = {}

    if user_id not in tea_stats[chat_id]:
        tea_stats[chat_id][user_id] = {
            'name': user_name,
            'tea_drink': 0,
            'kettle_failed': 30
        }
    if tea_stats[chat_id][user_id]['kettle_failed'] > 0:
        if random.randint(1, 100) <= 25:
            tea_stats[chat_id][user_id]['kettle_failed'] -= 1
            if tea_stats[chat_id][user_id]['kettle_failed'] == 0:
                return f'ТЫ БЫЛ ИЗБРАННИКОМ! ВСЕ ДУМАЛИ ТЫ БУДЕШЬ ЗАЩИЩАТЬ НАС ОТ ЖЕНЩИН А НЕ ПРИМКНЕШЬ К НИМ!'
            return f'чайник не вскипел🤬смотри что бы девушки не появилось. осталось не выпетых чаев: {tea_stats[chat_id][user_id]['kettle_failed']}'
        
        tea_amount = random.randint(1, 300)
        tea_stats[chat_id][user_id]['tea_drink'] += tea_amount
        if tea_amount <= 150:
            return (
                f'ты випил {tea_amount} чая \nвыпито чая всего: {tea_stats[chat_id][user_id]['tea_drink']}\nосталось не выпитых чаев: {tea_stats[chat_id][user_id]['kettle_failed']}'
            )
        else:
            return (
                f' ОМАГАД ТЫ ВИПИЛ АЖ {tea_amount} Л ЧАЯ!!!\nвыпито чая всего: {tea_stats[chat_id][user_id]['tea_drink']}\nосталось не выпитых чаев: {tea_stats[chat_id][user_id]['kettle_failed']}'
            )
    else:
        return f'тебе уже нет смысла пить чай ситх...'

@bot.message_handler(func=lambda message: message.text.lower() == 'выпить чай')
def tea(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.username
    response = drink_tea(chat_id, user_id, user_name)
    bot.reply_to(message, response)

# @bot.message_handler(func=lambda message: True)
# def save_user(message:types.Message):
#     chat_id = message.chat.id
#     user = message.from_user
#     add_user(chat_id, user)

@bot.my_chat_member_handler()
def check_admin(message:types.ChatMemberUpdated):
    if message.chat.type in ['group', 'supergroup']:
        old_status = message.old_chat_member.status
        new_status = message.new_chat_member.status
        if old_status != 'administrator' and new_status == 'administrator':
            bot.send_message(chat_id=message.chat.id, text= 'МУ ХА ХА ХА ХА Я ТЕПЕРЬ АДМИН Я ВАС КАК ГОДЖО РАТАТАТААТААТТ\nА ЧТО БЫ УЗНАТЬ ВСЕ МОИ ВИДЫ РАССТРЕЛА НАПИШИ /info')
    
@bot.message_handler(content_types=['video', 'animation'])
def media(message: types.Message):
    gif = r'src\GIF\video_2024-11-17_11-43-49.mp4'
    with open(gif, '+rb') as file:
        bot.send_animation(message.chat.id, file)

@bot.message_handler(func=lambda message:True, content_types=['text', 'sticker', 'photo', 'video', 'audio', 'document', 'location', 'contact', 'video_note', 'voice'])
def all_message_handler(message:types.Message):
    user_id = str(message.chat.id)
    today = datetime.date.today()
    week = datetime.date.today().isocalendar()[1]
    month = datetime.date.today().month
    user_info = 


@bot.message_handler(commands=['q'])
def quotes_chat(message: types.Message):
    chat_id = message.chat.id
    if message.reply_to_message:
        if chat_id not in quotes:
            quotes[chat_id] = []
        quot = message.reply_to_message.text
        quotes[chat_id].append(quot)
        bot.reply_to(message, f'цитата сохранена под номером {len(quotes[chat_id])}')
    elif len(message.text.split()) > 1:
        try:
            a, num = message.text.split()
            num = int(num) - 1
            if chat_id in quotes and 0 <= num <len(quotes[chat_id]):
                selected_q = quotes[chat_id][num]
                bot.reply_to(message, f'{selected_q}')
            else:
                bot.reply_to(message, 'цитата не найдена')
        except (ValueError, IndexError):
            bot.reply_to(message, f'у тебя аутизм? вот формат гений: /q <номер> (например, /q 2).')
    else:
        if chat_id in quotes and quotes[chat_id]:
            response = "\n".join([f"{i + 1}. {quote}" for i, quote in enumerate(quotes[chat_id])])
            bot.reply_to(message, f"Сохранённые цитаты:\n{response}")
        else:
            bot.reply_to(message, "Нет сохранённых цитат.")

bot.polling()