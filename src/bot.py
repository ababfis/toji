import telebot
from telebot import types
import random
import setings
import datetime
import json

bot = telebot.TeleBot(setings.BOT_TOKEN)

# Словари для хранения данных пользователей и цитат
user_data = {}
quotes = {}
bad_w = set()
rare_tea_list = ['спринг мелоди', 'китайский', 'чёрный чай']

@bot.message_handler(func=lambda message: message.text and message.text.lower() == 'кто я?')
def information(message: types.Message):
    global rare_tea_list

    user = message.from_user
    user_id = str(user.id)
    add_user(user)

    user_stats = user_data[user_id]
    msg = user_stats['messages']

    if set(rare_tea_list).issubset(set(user_stats['rare_tea'])):
        main_status = 'Эксперт по чаю (китаец)'
    elif len(user_stats['rare_tea']) >= 5:
        main_status = 'Чайный мастер'
    elif user_stats['tea_drink'] >= 2000:
        main_status = 'Любитель чая'
    elif user_stats['tea_drink'] >= 1:
        main_status = 'Новичoк'

    else:
        main_status = 'Бездарь'

    second_status = user_stats.get('second_status', 'ну типо ну хз')
    rewards = ', '.join(user_stats['rewards'] if user_stats['rewards'] else 'net nagrad')
    rare_tea = ', '.join(user_stats['rare_tea'] if user_stats['rare_tea'] else 'net tea')
    response = (
        f"👤 Имя: {user_stats['name']}\n"
        f"📊 Сообщений сегодня: {msg['by_day'].get(datetime.datetime.now().strftime('%Y-%m-%d'), 0)}\n"
        f"📊 Сообщений за неделю: {msg['by_week'].get(str(datetime.datetime.now().isocalendar()[1]), 0)}\n"
        f"📊 Сообщений за месяц: {msg['by_month'].get(str(datetime.datetime.now().month), 0)}\n"
        f"📊 Всего сообщений: {msg['total']}\n"
        f"🥇 Королевский клич: {main_status}\n"
        f"🥈 ЗВАНИИЕЕЕЕЕ: {second_status}\n"
        f"🏆 Награды: {rewards}\n"
        f"🍵 Выпито чая: {user_stats['tea_drink']} мл\n"
        f"🌟 Редкие чаи: {rare_tea}"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['info'])
def info(message: types.Message):
    commands = '''
Mои команды:\n
1. Вероятность (рандомный факт) - бот в ответ говорит что такой-то факт (столько-то процентов что правда) 
2. Кто? (рандомный ник из группы "я думаю {рандомный пользователь} ответ на вопрос)
3. Эдит (Отправка рандомного видоса)
4. Бан (удаление из группы пользователя)
5. /info - все команды бота
6. Расстрелять ({пользователь который выбрал команду} расстрелял как гитлера {пользователь которого указали})
7. Тодзи лох
8. Кто я: Выводит информацию про пользователя. 
9. Наградить/Снять награду (Только администратор группы можеть или награждать или снимать награды с человека, пересылкой сообщения от этого человека и написать какая награду ему присваивает. Также только администратор моржет снять награду)
10.  пака лох (если кто то отравляет гиф или видео бот отправляет гиф без текста)
11. выпить чай: ты випил чая!
12. /q (создает цитату из сообщения на которое ответили команой оно нумируется можно посмотреть все цитаты и потом по номеру выводить любую из них)
13. избить (пользователь) избил (пользовател на которого сообщение ответ) 
14. тодзи включи музыку)
'''
    bot.send_message(message.chat.id, commands)

# Функции для загрузки и сохранения данных
def load_user_data():
    global user_data
    try:
        with open('user_data.json', 'r', encoding='utf-8') as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}
    
    # Инициализация отсутствующих ключей для всех пользователей
    # for data in user_data.values():
    #     data.setdefault('name', 'nn')
    #     data.setdefault('tea_drink', 0)
    #     data.setdefault('kettle_failed', 30)

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

def load_bad_words():
    global bad_w
    try:
        with open('bad_words.txt', 'r', encoding='utf-8') as file:
            for i in file:
                word = i.strip().lower()
                if word:
                    bad_w.add(word)
    except  FileNotFoundError:
        bad_w = set()


# Функция для добавления пользователя
def add_user(user):
    user_id = str(user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user.first_name or 'nn',
            'username': user.username,
            'tea_drink': 0,
            'kettle_failed': 100,
            'messages': {
                'total': 0,
                'by_day': {},
                'by_week': {},
                'by_month': {}
            },
            'bad_word_count': 0,
            'rare_tea': [],
            'main_status': None,
            'second_status': None,
            'rewards': [],
            'last_tea_time': None
        }


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
            if random.randint(1, 100) <= 1:
                global rare_tea_list
                rare_tea = random.choice(rare_tea_list)
                user_info['rare_tea'].append(rare_tea)
                response = f'ТЕБЕ ПОПАЛСЯ РЕДКИЙ ЧАЙ {rare_tea}'
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

def all_message_handler(messages: list):
    for message in messages:
        if not message.from_user:
            continue
    
        user = message.from_user
        user_id = str(user.id)
        add_user(user)
        
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        week = now.isocalendar()[1]
        month = now.month
        
        user_info = user_data[user_id]
        msg_stats  = user_info['messages']
        msg_stats['total'] += 1

        msg_stats['by_day'].setdefault(today, 0)
        msg_stats['by_day'][today] += 1

        msg_stats['by_month'].setdefault(str(month), 0)
        msg_stats['by_month'][str(month)] += 1

        msg_stats['by_week'].setdefault(str(week), 0)
        msg_stats['by_week'][str(week)] += 1

        if message.text:
            text = message.text.lower()
            text_word = text.split()
     
            for word in text_word:
                if word in bad_w:
                    user_info['bad_word_count'] += 1
                    if user_info['bad_word_count'] >= 3:
                        #прописать позже секонд статус
                        break
                    break
    save_user_data()


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

def is_admin(chat_id, user_id ):
    admins = bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)

@bot.message_handler(func=lambda message:message.text and message.text.lower().startswith('тодзи наградить'))
def nagradit(message: types.Message):
    if is_admin(message.chat.id, message.from_user.id):
        try:
            commands_part = message.text.split()
            if len(commands_part) < 3:
                bot.reply_to(message, 'неправильно написал бож🙄 нада так: тодзи наградить (имя этого немоща) (название награды)' )
                return
            # ['тодзи', 'наградить', '@username,' 'награда']
            username = commands_part[2].strip('@')
            reward_name = commands_part[3].strip()
            if not reward_name:
                bot.reply_to(message, 'да ты конченный? все я психушку вызываю НЕ ПУСТУЮ НАГРАДУ ДАВАЙ Я ТЕБЯ ВОДУХОМ НАГРАЖУ ПАРАЛЕЛИПИПИД')
                return
            user_to_reward = find_user_by_username(message.chat.id, username) 
            if user_to_reward == None:
                bot.send_message(message.chat.id, 'нету его пусть он мне чет напишет и тогда окей')
                return

            user_id = str(user_to_reward.id)
            user_info = user_data.setdefault(user_id, {})
            rewards = user_info.setdefault('rewards', [])

            if len(rewards) >= 5:
                bot.reply_to(message, f'этот немощь {user_to_reward.first_name} имеет максимум наград сначала удали одну а потом добавляй еще')

            else:
                rewards.append(reward_name)
                save_user_data()
                bot.reply_to(message, f'этот немощь {user_to_reward.first_name} получил нагдаду {reward_name}')
            
        except Exception as e:
            bot.reply_to(message, f'произошли некоторые технические шоколадки типо вот: {e}')
    else:
        bot.reply_to(message, f'ахахаха какой то рапик хочет дать награду хотя у него не хватает социал кредита ')

@bot.message_handler(func=lambda message:message.text and message.text.lower().startswith('тодзи снять награду'))
def nagradit(message: types.Message):
    if is_admin(message.chat.id, message.from_user.id):
        try:
            command_parts = message.text.split()
    
            if len(command_parts) < 3:
                bot.reply_to(message, 'неправильно написал бож🙄 нада так: тодзи снять награду (имя этого немоща) (название награды)' )
                return
                
            username = command_parts[3].strip('@')
            reward_name = command_parts[4:].strip()

            if not reward_name:
                bot.reply_to(message, 'да ты конченный? все я психушку вызываю НЕ ПУСТУЮ НАГРАДУ ДАВАЙ Я ТЕБЯ ВОДУХОМ НАГРАЖУ ПАРАЛЕЛИПИПИД')
                return
                
            user_to_reward = find_user_by_username(message.chat.id, username) 
            if user_to_reward == None:
                bot.send_message(message.chat.id, 'нету его пусть он мне чет напишет и тогда окей')
                return   
            
            user_id = str(user_to_reward.id)
            user_info = user_data.get(user_id, {})
            rewards = user_info.get('rewards', [])

            if reward_name in rewards:
                rewards.remove(reward_name)
                bot.reply_to(message, f'ну типо убрал')
            
            else:
                bot.reply_to(message, f'такой награды у этого немоща нету')

        except Exception as e:
            bot.reply_to(message, f'ну кароче опять технические шоколадки типо {e}')

    else:
        bot.reply_to(message, f'ахаха у этого рапика даже что бы дать награду кредита не хватила а он снять хочет ты кто такой вообще????')

def find_user_by_username(chat_id, username):
    """
    Ищет пользователя в чате по его username.
    """
    members = bot.get_chat_administrators(chat_id)#TODO сделать поиск по базе данных
    for member in members:
        if member.user.username and member.user.username.lower() == username.lower():
            return member.user
    return None

# Запуск бота
if __name__ == '__main__':
    load_user_data()
    load_quotes()
    load_bad_words()
    bot.set_update_listener(all_message_handler)
    bot.polling()