#7885233281:AAFOUDvwhCa1Fx6m415JqBnh61ls_CO-Xe0
import telebot
import json
import os
import time
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from shop_data import WEAPON_SHOP, ARMOR_SHOP, POTION_SHOP



TOKEN = '7885233281:AAFOUDvwhCa1Fx6m415JqBnh61ls_CO-Xe0'
bot = telebot.TeleBot(TOKEN)

WORK_COOLDOWN = 300  # 5 минут в секундах

selected_item_for_use = {}


################# BUSSINESS ################

BUSINESS_LIST = [
    {"id": 1, "name": "🥦 Овощная лавка", "price": 500, "income": 50},
    {"id": 2, "name": "🛡 Магазин брони", "price": 1000, "income": 120},
    {"id": 3, "name": "🧪 Аптека", "price": 1500, "income": 180},
]

BUSINESS_COOLDOWN = 300  # 5 минут



################  SHOP ################
SHOP_ITEMS = [
    {"name": "🍎 Яблоко", "price": 20, "effect": "heal", "value": 10},
    {"name": "🥪 Бутерброд", "price": 50, "effect": "heal", "value": 25},
    {"name": "🧪 Зелье здоровья", "price": 100, "effect": "heal", "value": 50}
]

################ LOCATION ################
LOCATIONS = [
    "🌳 Деревня",
    "🏙 Город",
    "🏔 Горы",
    "🌋 Вулкан"
]
################ MONSTERS #############
MONSTERS = [
    {"name": "🐀 Гиганская Крыса", "hp": 20, "damage": 5, "reward": 10, "xp": 5},
    {"name": "🕷 Паук", "hp": 30, "damage": 8, "reward": 20, "xp": 10},
    {"name": "🧟 Зомби", "hp": 50, "damage": 12, "reward": 30, "xp": 20},
    {"name": "🐉 Маленький Дракон", "hp": 100, "damage": 20, "reward": 100, "xp": 50}
]

# MISSIONS 

MISSIONS = [
    {
        "id": 1,
        "title": "⚔️ Победи 3 монстров",
        "type": "kill_monsters",
        "goal": 3,
        "reward": {"coins": 100, "xp": 20}
    },
    {
        "id": 2,
        "title": "💰 Заработай 200 монет",
        "type": "earn_money",
        "goal": 200,
        "reward": {"coins": 50, "xp": 10}
    },
    {
        "id": 3,
        "title": "🛠 Выполни 5 работ",
        "type": "do_work",
        "goal": 5,
        "reward": {"coins": 80, "xp": 15}
    }
]

# ДОСТИЖЕНИЕ

ACHIEVEMENTS = [
    {
        "id": 1,
        "title": "🗡 Первый бой",
        "type": "kill_monsters",
        "goal": 1,
        "reward": {"coins": 20, "xp": 5}
    },
    {
        "id": 2,
        "title": "💰 Богач",
        "type": "earn_money_total",
        "goal": 1100,
        "reward": {"coins": 50, "xp": 10}
    },
    {
        "id": 3,
        "title": "🎯 Работяга",
        "type": "do_work_total",
        "goal": 10,
        "reward": {"coins": 30, "xp": 8}
    }
]




@bot.message_handler(func=lambda message: message.text == "🎯 Использовать")
def select_item_to_use(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user or not user.get("inventory"):
        bot.send_message(message.chat.id, "🎒 У тебя нет предметов для использования.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item_name in user["inventory"].keys():
        markup.add(item_name)
    markup.add("⬅️ Назад")
    bot.send_message(message.chat.id, "Выбери предмет для использования:", reply_markup=markup)
    selected_item_for_use[user_id] = True  # Пометим, что он в режиме использования

@bot.message_handler(func=lambda message: str(message.from_user.id) in selected_item_for_use)
def handle_inventory_use(message):
    user_id = str(message.from_user.id)
    if user_id not in selected_item_for_use:
        return  # не в режиме использования

    item_name = message.text
    users = load_users()
    user = users.get(user_id)

    if item_name not in user["inventory"]:
        bot.send_message(message.chat.id, "❌ У тебя нет такого предмета.")
        return

    
    # Применяем эффекты зелий
    from shop_data import POTION_SHOP
    potion = next((p for p in POTION_SHOP if p["name"] == item_name), None)
    if not potion:
        bot.send_message(message.chat.id, "❌ Этот предмет нельзя использовать.")
        return

    effect = potion["effect"]
    if "hp" in effect:
        user["hp"] = min(100, user["hp"] + effect["hp"])
        bot.send_message(message.chat.id, f"🧪 Ты использовал {item_name} и восстановил {effect['hp']} HP.")
    elif "armor_boost" in effect:
        if "effects" not in user:
            user["effects"] = {}
        user["effects"]["armor_boost"] = {
            "value": effect["armor_boost"],
            "turns": effect["duration"]
        }
        bot.send_message(
            message.chat.id,
            f"🛡 Ты использовал {item_name}.\nТвоя броня увеличена на {effect['armor_boost']} на {effect['duration']} боёв!"
        )
    else:
        bot.send_message(message.chat.id, f"✅ Ты использовал {item_name}, эффект применён.")

    

    # Уменьшаем количество
    user["inventory"][item_name] -= 1
    if user["inventory"][item_name] <= 0:
        del user["inventory"][item_name]

    save_users(users)
    del selected_item_for_use[user_id]

    # Возвращаем в инвентарь
    inventory(message)

@bot.message_handler(commands=['menu'])
def menu(message):
    send_main_menu(message.chat.id)

def send_main_actions(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧙 Профиль", "⚔️ Бой", "💼 Работа")
    markup.add("🎯 Миссия", "🎒 Инвентарь", "🛍 Магазин")
    markup.add("🎁 Бонус дня")
    markup.add("⬅️ Назад")
    bot.send_message(chat_id, "📦 Основные действия:", reply_markup=markup)

def send_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📦 Основные", "🧰 Вспомогательные")
    bot.send_message(chat_id, "🔘 Главное меню:", reply_markup=markup)

def send_support_actions(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📜 Путеводитель", "🏅 Достижения", "👥 Клан")
    markup.add("🤝 Друзья", "💸 Передать монеты")
    markup.add("⚔️ Магазин снаряжения")
    markup.add("⬅️ Назад")
    bot.send_message(chat_id, "🧰 Вспомогательные функции:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text

    # Главное меню
    if text == "📦 Основные":
        send_main_actions(message.chat.id)
    elif text == "🧰 Вспомогательные":
        send_support_actions(message.chat.id)
    elif text == "⬅️ Назад":
        send_main_menu(message.chat.id)

    # Основные
    elif text == "🧙 Профиль":
        profile(message)
    elif text == "⚔️ Бой":
        fight(message)
    elif text == "⚔️ Магазин снаряжения":
        open_equipment_shop(message)
    elif text == "🗡 Оружие":
        show_weapon_shop(message)
    elif text == "🛡 Броня":
        show_armor_shop(message)
    elif text == "🍷 Зелья":
        show_potions(message)
    elif text == "💼 Работа":
        work(message)
    elif text == "🎁 Бонус дня":
        daily_bonus(message)
    elif text == "🎯 Миссия":
        mission(message)
    elif text == "🎒 Инвентарь":
        inventory(message)
    elif text == "🛍 Магазин":
        open_shop_menu(message)
    elif text in [item["name"] for item in WEAPON_SHOP]:
        buy_equipment(message, text, "weapon")
    elif text in [item["name"] for item in ARMOR_SHOP]:
        buy_equipment(message, text, "armor")
    elif text in [p["name"] for p in POTION_SHOP]:
        buy_potion(message, text)

    # Вспомогательные
    elif text == "📜 Путеводитель":
        help(message)
    elif text == "🏅 Достижения":
        show_achievements(message)
    elif text == "👥 Клан":
        clan_info(message)
    elif text == "🤝 Друзья":
        show_friends(message)
    elif text == "💸 Передать монеты":
        bot.send_message(message.chat.id, "Используй команду /pay ID сумма")

    # Обработка покупки из магазина
    elif text in [item["name"] for item in SHOP_ITEMS]:
        buy_named_item(message, text)

def buy_equipment(message, item_name, category):
    users = load_users()
    user_id = str(message.from_user.id)

    shop_list = WEAPON_SHOP if category == "weapon" else ARMOR_SHOP
    item = next((i for i in shop_list if i["name"] == item_name), None)

    if not item:
        bot.send_message(message.chat.id, "❌ Предмет не найден.")
        return

    user = users.get(user_id)
    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if "equipment" not in user:
        user["equipment"] = {"armor": None, "weapon": None}

    if user["coins"] < item["price"]:
        bot.send_message(message.chat.id, "💸 Недостаточно монет!")
        return

    user["coins"] -= item["price"]
    user["equipment"][category] = item_name

    save_users(users)
    bot.send_message(message.chat.id, f"✅ Ты экипировал {item_name}!")


def fight(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    monster_hp = 50
    monster_damage = 20

    # Защита от брони
    defense = 0
    equipped_armor = user.get("equipment", {}).get("armor")
    for armor in ARMOR_SHOP:
        if armor["name"] == equipped_armor:
            defense = armor.get("defense", 0)

    user_hp = user["hp"]

    while monster_hp > 0 and user_hp > 0:
        monster_hp -= 15  # Игрок атакует
        if monster_hp > 0:
            user_hp -= max(0, monster_damage - defense)  # Монстр атакует

    result = ""
    if user_hp > 0:
        user["hp"] = user_hp
        user["coins"] += 50
        user["stats"]["kills"] += 1
        result = "🏆 Ты победил монстра и получил 50 монет!"
    else:
        user["hp"] = 0
        result = "💀 Ты проиграл монстру!"

    save_users(users)
    bot.send_message(message.chat.id, result)


def buy_named_item(message, item_name):
    users = load_users()
    user_id = str(message.from_user.id)

    item = next((i for i in SHOP_ITEMS if i["name"] == item_name), None)
    if not item:
        bot.send_message(message.chat.id, "❌ Товар не найден.")
        return

    user = users.get(user_id)
    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if user["coins"] < item["price"]:
        bot.send_message(message.chat.id, "💸 Недостаточно монет!")
        return

    user["coins"] -= item["price"]
    user["hp"] = min(100, user["hp"] + item["value"])
    save_users(users)

    bot.send_message(message.chat.id, f"✅ Ты купил {item['name']} и восстановил {item['value']} HP.")


def check_achievements(user, message):
    for a in ACHIEVEMENTS:
        if a["id"] in user["achievements"]:
            continue

        if a["type"] == "kill_monsters" and user["stats"]["kills"] >= a["goal"]:
            unlock_achievement(user, message, a)
        elif a["type"] == "earn_money_total" and user["stats"]["money_earned"] >= a["goal"]:
            unlock_achievement(user, message, a)
        elif a["type"] == "do_work_total" and user["stats"]["work_done"] >= a["goal"]:
            unlock_achievement(user, message, a)

def unlock_achievement(user, message, achievement):
    user["achievements"].append(achievement["id"])
    user["coins"] += achievement["reward"]["coins"]
    user["xp"] += achievement["reward"]["xp"]
    bot.send_message(
        message.chat.id,
        f"🏆 Достижение получено: <b>{achievement['title']}</b>!\n"
        f"🎁 Награда: {achievement['reward']['coins']} монет, {achievement['reward']['xp']} XP",
        parse_mode="HTML"
    )

def deposit_ready(bank_data):
    if bank_data["amount"] == 0 or bank_data["timestamp"] == 0:
        return False
    return (time.time() - bank_data["timestamp"]) >= 3 * 60 * 60  # 3 часа

def load_clans():
    try:
        with open("clans.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_clans(data):
    with open("clans.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Загрузка данных
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def show_potions(message):
    from shop_data import POTION_SHOP
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for potion in POTION_SHOP:
        markup.add(potion["name"])
    markup.add("⬅️ Назад")
    bot.send_message(message.chat.id, "🍷 Зелья в продаже:", reply_markup=markup)

def buy_potion(message, potion_name):
    from shop_data import POTION_SHOP
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    potion = next((p for p in POTION_SHOP if p["name"] == potion_name), None)
    if not potion:
        bot.send_message(message.chat.id, "❌ Зелье не найдено.")
        return

    if user["coins"] < potion["price"]:
        bot.send_message(message.chat.id, "💸 Недостаточно монет!")
        return

    user["coins"] -= potion["price"]
    user["inventory"][potion_name] = user["inventory"].get(potion_name, 0) + 1
    save_users(users)
    bot.send_message(message.chat.id, f"✅ Ты купил {potion_name}. Оно добавлено в инвентарь.")

def open_equipment_shop(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🗡 Оружие", "🛡 Броня")
    markup.add("⬅️ Назад")
    bot.send_message(message.chat.id, "⚔️ Выбери категорию снаряжения:", reply_markup=markup)

def open_shop_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🗡 Оружие", "🛡 Броня", "🍷 Зелья")
    markup.add("⬅️ Назад")
    bot.send_message(message.chat.id, "Выбери категорию:", reply_markup=markup)

def show_weapon_shop(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in WEAPON_SHOP:
        markup.add(item["name"])
    markup.add("⬅️ Назад")
    bot.send_message(message.chat.id, "🔪 Выбери оружие для покупки:", reply_markup=markup)

def show_armor_shop(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item in ARMOR_SHOP:
        markup.add(item["name"])
    markup.add("⬅️ Назад")
    bot.send_message(message.chat.id, "🛡 Выбери броню для покупки:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🛡 Броня")
def show_armors(message):
    from shop_data import ARMORS
    text = "🛡 Доступная броня:\n"
    for a in ARMORS:
        text += f"{a['name']} — {a['price']} монет, Защита: {a['defense']}\n"
    bot.send_message(message.chat.id, text)



@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "name": message.from_user.first_name,
            "level": 1,
            "xp": 0,
            "coins": 100,
            "hp": 100,
            "location": "Начальная деревня",
            "inventory": {},
            "bank": {
                "amount": 0,
                "clan_id": [],
                "timestamp": 0
            },
            "achievements": [],
            "stats": {
                "kills": 0,
                "work_done": 0,
                "money_earned": 0
            },
            "friends": [],
            "pending_friends": [],
            "last_daily_bonus": 0,
            "equipment": {
                "armor": None,
                "weapon": None
            },
            "effects": {},
        }
        save_users(users)
        send_main_menu(message.chat.id)  # ✅ Показываем клавиатуру только при регистрации
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Ты начал своё приключение! 🗺️\nПодробнее о боте /help")
    else:
        bot.send_message(message.chat.id, "Ты уже зарегистрирован в игре!")

@bot.message_handler(commands=['profile'])
def profile(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return
    user = users[user_id]
    ach_done = len(user.get("achievements", []))

    user = users[user_id]
    text = (
        f"🧙 Профиль игрока {user['name']}\n"
        f"🏅 Уровень: {user['level']}\n"
        f"💥 Опыт: {user['xp']}\n"
        f"💰 Монеты: {user['coins']}\n"
        f"❤️ Здоровье: {user['hp']}\n"
        f"📍 Локация: {user['location']}\n"
        f"🏆 Достижений: {ach_done}/{len(ACHIEVEMENTS)}\n"
        f"🛡 Броня: {user['equipment'].get('armor', 'Нет')}\n"
        f"⚔️ Оружие: {user['equipment'].get('weapon', 'Нет')}\n"
        
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['help'])
def help(message):
    text = (
        "📖 *Путеводитель по игре*\n\n"
        "Добро пожаловать в RPG мир! Вот что ты можешь делать:\n\n"
        "🧍‍♂️ /profile – посмотреть свой профиль\n"
        "🏗 /work – работать и зарабатывать монеты\n"
        "🛒 /shop – магазин с товарами\n"
        "⚔️ /fight – сразиться с монстром\n"
        "🎒 /inventory – твой рюкзак\n"
        "🧭 /travel – путешествовать в другие локации\n"
        "👥 /mission – Квесты\n"
        "👥 /buy – купить товар\n"
        "👥 /deposit – положить деньги на депозит\n"
        "👥 /withdraw – снять полностью деньги с депозита\n"
        "👥 /bank – посмотреть сумму депозита\n"
        "👥 /buy – купить товар\n"
        "👥 /achievements – посмотреть свои достижения \n"
        "👥 /go – отправиться путешествовать\n"
        "👥 /use – использовать предмет с инвенторя\n"
        "📈 /top – топ игроков по уровню\n"
        "📘 /help – показать это меню\n\n"
        "🎯 Цель игры – прокачаться, заработать и победить боссов!\n"
        "Удачи, герой! 🏆"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['work'])
def work(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Сначала зарегистрируйся через /start")
        return

    user = users[user_id]
    now = int(time.time())

    last_work = user.get("last_work", 0)
    if now - last_work < WORK_COOLDOWN:
        remaining = WORK_COOLDOWN - (now - last_work)
        minutes = remaining // 60
        seconds = remaining % 60
        bot.send_message(message.chat.id, f"⏳ Ты устал. Попробуй снова через {minutes} мин {seconds} сек.")
        return

    # Выдаем награду
    earned_coins = 50
    earned_xp = 10
    user["coins"] += earned_coins
    user["xp"] += earned_xp
    user["last_work"] = now

    # Повышение уровня (если нужно)
    level_up(user)

    save_users(users)
    bot.send_message(
        message.chat.id,
        f"💼 Ты поработал и заработал:\n💰 {earned_coins} монет\n✨ {earned_xp} опыта"
    )

def level_up(user):
    xp = user["xp"]
    level = user["level"]
    next_level_xp = level * 100

    if xp >= next_level_xp:
        user["level"] += 1
        user["xp"] = xp - next_level_xp

# SHOP 

@bot.message_handler(commands=['shop'])
def shop(message):
    text = "<b>🛒 Магазин предметов:</b>\n\n"
    for idx, item in enumerate(SHOP_ITEMS, start=1):
        text += f"{idx}. {item['name']} — {item['price']} монет\n"
    text += "\nЧтобы купить, напиши: /buy Номер_предмета (например, /buy 1)"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['buy'])
def buy(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Введи /start.")
        return

    args = message.text.split(' ', 1)
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, "Пиши: /buy Номер_предмета (например, /buy 1)")
        return

    item_index = int(args[1]) - 1  # -1 потому что нумерация с 0

    if not (0 <= item_index < len(SHOP_ITEMS)):
        bot.send_message(message.chat.id, "❌ Нет предмета с таким номером.")
        return

    item = SHOP_ITEMS[item_index]
    user = users[user_id]

    if user["coins"] < item["price"]:
        bot.send_message(message.chat.id, "💸 Недостаточно монет!")
        return

    user["coins"] -= item["price"]
    user["hp"] = min(user["hp"] + item["value"], 100)

    # ✅ Добавляем в инвентарь
    inventory = user.setdefault("inventory", {})  # создаём, если ещё нет
    item_name = item["name"]
    inventory[item_name] = inventory.get(item_name, 0) + 1

    save_users(users)
    bot.send_message(
        message.chat.id,
        f"✅ Ты купил {item['name']} и восстановил {item['value']} HP!"
    )


# TRAVEL

@bot.message_handler(commands=['travel'])
def travel(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    text = "<b>🧭 Доступные локации:</b>\n\n"
    for idx, location in enumerate(LOCATIONS, start=1):
        text += f"{idx}. {location}\n"
    text += "\nЧтобы переместиться, напиши: /go Номер_локации"

    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['go'])
def go(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    args = message.text.split(' ', 1)
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, "Пиши: /go Номер_локации (например, /go 2)")
        return

    loc_index = int(args[1]) - 1
    if not (0 <= loc_index < len(LOCATIONS)):
        bot.send_message(message.chat.id, "❌ Нет локации с таким номером.")
        return

    users[user_id]["location"] = LOCATIONS[loc_index]
    save_users(users)

    bot.send_message(message.chat.id, f"✅ Ты переместился в {LOCATIONS[loc_index]}")

#### INVENTORY 

@bot.message_handler(commands=['inventory'])
def inventory(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user or not user.get("inventory"):
        bot.send_message(message.chat.id, "🎒 Инвентарь пуст.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item_name, count in user["inventory"].items():
        markup.add(f"{item_name} x{count}")
    markup.add("🎯 Использовать", "⬅️ Назад")
    bot.send_message(message.chat.id, "🎒 Ваш инвентарь:", reply_markup=markup)

@bot.message_handler(commands=['use'])
def use_item(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Введи /start.")
        return

    user = users[user_id]
    inventory = user.get("inventory", {})

    args = message.text.split(' ', 1)
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, "Пиши: /use Номер_предмета (например, /use 1)")
        return

    item_index = int(args[1]) - 1
    inventory_list = list(inventory.items())

    if not (0 <= item_index < len(inventory_list)):
        bot.send_message(message.chat.id, "❌ Неверный номер предмета.")
        return

    item_name, count = inventory_list[item_index]

    # Найти предмет в SHOP_ITEMS по имени
    item_data = next((item for item in SHOP_ITEMS if item["name"] == item_name), None)
    if not item_data:
        bot.send_message(message.chat.id, "❌ Ошибка: предмет не найден.")
        return

    # Применяем эффект
    if item_data["effect"] == "heal":
        heal = item_data["value"]
        user["hp"] = min(user["hp"] + heal, 100)
        bot.send_message(message.chat.id, f"🧪 Ты использовал {item_name} и восстановил {heal} HP!")
    else:
        bot.send_message(message.chat.id, f"Ты использовал {item_name}, но пока эффект не реализован.")

    # Уменьшаем количество
    if count > 1:
        inventory[item_name] -= 1
    else:
        del inventory[item_name]

    save_users(users)

#### FIGHT 

@bot.message_handler(commands=['fight'])
def fight(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    user = users[user_id]

    # Проверка на миссию
    mission = None
    if user.get("mission") and user["mission"].get("id") is not None:
        mission = next((m for m in MISSIONS if m["id"] == user["mission"]["id"]), None)
        if mission and mission["type"] == "kill_monsters":
            user["mission"]["progress"] += 1
            if user["mission"]["progress"] >= mission["goal"]:
                user["coins"] += mission["reward"]["coins"]
                user["xp"] += mission["reward"]["xp"]
                bot.send_message(
                    message.chat.id,
                    f"✅ Миссия '{mission['title']}' выполнена!\n🎁 Награда: {mission['reward']['coins']} монет, {mission['reward']['xp']} XP"
                )
                user["mission"] = {"id": None, "progress": 0}

    if user["hp"] <= 0:
        bot.send_message(message.chat.id, "😵 Ты слишком слаб. Вылечись перед боем.")
        return

    monster = random.choice(MONSTERS)
    monster_hp = monster["hp"]
    player_hp = user["hp"]

    while player_hp > 0 and monster_hp > 0:
        monster_hp -= 15  # фиксированный урон от игрока
        if monster_hp > 0:
            player_hp -= monster["damage"]

    if player_hp > 0:
        user["coins"] += monster["reward"]
        user["xp"] += monster["xp"]
        user["hp"] = player_hp
        level_up(user)
        save_users(users)
        bot.send_message(
            message.chat.id,
            f"⚔️ Ты победил {monster['name']}!\n"
            f"💰 Монеты: +{monster['reward']}\n"
            f"✨ Опыт: +{monster['xp']}\n"
            f"❤️ Осталось HP: {player_hp}"
        )
    else:
        user["hp"] = 0
        save_users(users)
        bot.send_message(
            message.chat.id,
            f"💀 Ты пал в бою с {monster['name']}...\n"
            f"❤️ Твоё здоровье теперь 0. Используй /inventory или /shop, чтобы восстановиться."
        )

# DEPOSIT 


@bot.message_handler(commands=['deposit'])
def deposit(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, "Пиши: /deposit сумма (например, /deposit 100)")
        return

    amount = int(args[1])
    user = users[user_id]

    if user["coins"] < amount or amount <= 0:
        bot.send_message(message.chat.id, "❌ Недостаточно монет.")
        return

    user["coins"] -= amount
    user["bank"]["amount"] = amount
    user["bank"]["timestamp"] = time.time()

    save_users(users)
    bot.send_message(message.chat.id, f"🏦 Ты положил {amount} монет на депозит. Через 3 часа получишь x2!")

@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    user = users[user_id]
    bank = user["bank"]

    if bank["amount"] == 0:
        bot.send_message(message.chat.id, "💼 У тебя нет активного депозита.")
        return

    if deposit_ready(bank):
        reward = bank["amount"] * 2
        bot.send_message(message.chat.id, f"💸 Ты снял {reward} монет с депозита (x2 за ожидание)!")
    else:
        reward = bank["amount"]
        bot.send_message(message.chat.id, f"💰 Ты досрочно снял {reward} монет (без бонуса).")

    user["coins"] += reward
    user["bank"] = {"amount": 0, "timestamp": 0}
    save_users(users)

@bot.message_handler(commands=['bank'])
def bank_info(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    user = users[user_id]

    # ✅ создаём банк, если его нет
    if "bank" not in user:
        user["bank"] = {"amount": 0, "timestamp": 0}
        save_users(users)

    bank = user["bank"]

    if bank["amount"] == 0:
        bot.send_message(message.chat.id, "🏦 У тебя нет активного вклада.")
    else:
        remaining = max(0, int(3 * 60 * 60 - (time.time() - bank["timestamp"])))
        minutes = remaining // 60
        bot.send_message(
            message.chat.id,
            f"🏦 В банке: {bank['amount']} монет.\nДо x2: {minutes} минут."
        )

################ CLAN ############

@bot.message_handler(commands=['clan_create'])
def clan_create(message):
    users = load_users()
    clans = load_clans()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if users[user_id].get("clan_id"):
        bot.send_message(message.chat.id, "Ты уже в клане.")
        return

    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Пиши: /clan_create Название")
        return

    name = args[1].strip()
    clan_id = user_id  # уникальный ID клана = ID создателя

    if clan_id in clans:
        bot.send_message(message.chat.id, "Клан с таким ID уже есть.")
        return

    clans[clan_id] = {
        "name": name,
        "owner": user_id,
        "members": [user_id],
        "xp": 0,
        "level": 1,
        "tasks": [],
        "chat": []
    }
    users[user_id]["clan_id"] = clan_id

    save_clans(clans)
    save_users(users)
    bot.send_message(message.chat.id, f"🏰 Клан '{name}' создан! Твой ID: {clan_id}")


@bot.message_handler(commands=['clan_join'])
def clan_join(message):
    users = load_users()
    clans = load_clans()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if users[user_id].get("clan_id"):
        bot.send_message(message.chat.id, "Ты уже в клане.")
        return

    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Пиши: /clan_join ID_клана")
        return

    clan_id = args[1].strip()
    if clan_id not in clans:
        bot.send_message(message.chat.id, "❌ Клан не найден.")
        return

    clans[clan_id]["members"].append(user_id)
    users[user_id]["clan_id"] = clan_id

    save_clans(clans)
    save_users(users)
    bot.send_message(message.chat.id, f"✅ Ты вступил в клан {clans[clan_id]['name']}")

@bot.message_handler(commands=['clan'])
def clan_info(message):
    users = load_users()
    clans = load_clans()
    user_id = str(message.from_user.id)

    if user_id not in users or not users[user_id].get("clan_id"):
        bot.send_message(message.chat.id, "Ты не в клане.")
        return

    clan_id = users[user_id]["clan_id"]
    clan = clans.get(clan_id)

    if not clan:
        bot.send_message(message.chat.id, "Клан не найден.")
        return

    bot.send_message(
        message.chat.id,
        f"🏰 Клан: {clan['name']}\n👑 Лидер: {clan['owner']}\n👥 Участников: {len(clan['members'])}"
    )


@bot.message_handler(commands=['clan_leave'])
def clan_leave(message):
    users = load_users()
    clans = load_clans()
    user_id = str(message.from_user.id)

    if user_id not in users or not users[user_id].get("clan_id"):
        bot.send_message(message.chat.id, "Ты не в клане.")
        return

    clan_id = users[user_id]["clan_id"]
    clan = clans.get(clan_id)

    if clan:
        clan["members"].remove(user_id)
        if user_id == clan["owner"]:
            # Удаляем клан, если владелец вышел
            del clans[clan_id]
            bot.send_message(message.chat.id, f"❌ Клан '{clan['name']}' был распущен.")
        else:
            bot.send_message(message.chat.id, "🚪 Ты покинул клан.")

    users[user_id]["clan_id"] = None
    save_clans(clans)
    save_users(users)


# MISSIONS

@bot.message_handler(commands=['mission'])
def mission(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if "mission" not in user:
        user["mission"] = {"id": None, "progress": 0}

    if user["mission"]["id"] is not None:
        # Показываем текущую миссию
        mission = next((m for m in MISSIONS if m["id"] == user["mission"]["id"]), None)
        if mission:
            bot.send_message(
                message.chat.id,
                f"🎯 Текущая миссия:\n{mission['title']}\nПрогресс: {user['mission']['progress']}/{mission['goal']}"
            )
        else:
            user["mission"] = {"id": None, "progress": 0}
    else:
        # Предлагаем выбрать миссию
        text = "📜 Доступные миссии:\n"
        for m in MISSIONS:
            text += f"{m['id']}. {m['title']} (награда: {m['reward']['coins']} монет, {m['reward']['xp']} XP)\n"
        text += "\nНапиши /take_mission [номер], чтобы начать миссию."
        bot.send_message(message.chat.id, text)

    save_users(users)

@bot.message_handler(commands=['take_mission'])
def take_mission(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if user["mission"]["id"] is not None:
        bot.send_message(message.chat.id, "У тебя уже есть активная миссия. Заверши её сначала.")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, "Пиши: /take_mission [номер миссии]")
        return

    mission_id = int(args[1])
    mission = next((m for m in MISSIONS if m["id"] == mission_id), None)

    if not mission:
        bot.send_message(message.chat.id, "❌ Такой миссии нет.")
        return

    user["mission"] = {"id": mission_id, "progress": 0}
    save_users(users)
    bot.send_message(message.chat.id, f"🎯 Миссия начата: {mission['title']}")

@bot.message_handler(commands=['achievements'])
def show_achievements(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    user = users[user_id]
    
    # Если у старых пользователей нет этих полей — создаём
    if "achievements" not in user:
        user["achievements"] = []
    if "stats" not in user:
        user["stats"] = {
            "kills": 0,
            "work_done": 0,
            "money_earned": 0
        }

    completed = user["achievements"]
    text = "🏆 Твои достижения:\n\n"

    for a in ACHIEVEMENTS:
        status = "✅" if a["id"] in completed else "❌"
        text += f"{status} {a['title']}\n"

    bot.send_message(message.chat.id, text)

# FRIENDS 

@bot.message_handler(commands=['addfriend'])
def add_friend(message):
    users = load_users()
    user_id = str(message.from_user.id)
    args = message.text.split()

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if len(args) != 2:
        bot.send_message(message.chat.id, "Используй: /addfriend ID_игрока")
        return

    target_id = args[1]
    if target_id == user_id:
        bot.send_message(message.chat.id, "Ты не можешь добавить себя.")
        return

    if target_id not in users:
        bot.send_message(message.chat.id, "Такого игрока не существует.")
        return

    users[target_id].setdefault("pending_friends", [])
    if user_id in users[target_id]["pending_friends"]:
        bot.send_message(message.chat.id, "Ты уже отправил заявку этому игроку.")
        return

    users[target_id]["pending_friends"].append(user_id)
    save_users(users)

    bot.send_message(message.chat.id, f"✅ Заявка отправлена игроку {users[target_id]['name']} (ID: {target_id})")

    # 🔘 Inline кнопки
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
    )

    try:
        bot.send_message(
            int(target_id),
            f"📩 Игрок {users[user_id]['name']} (ID: {user_id}) хочет добавить тебя в друзья.",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка отправки: {e}")

@bot.message_handler(commands=['acceptfriend'])
def accept_friend(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "Используй: /acceptfriend ID_игрока")
        return

    requester_id = args[1]

    if requester_id not in users:
        bot.send_message(message.chat.id, "Игрок не найден.")
        return

    # Инициализируем списки если отсутствуют
    users[user_id].setdefault("friends", [])
    users[user_id].setdefault("pending_friends", [])
    users[requester_id].setdefault("friends", [])

    if requester_id not in users[user_id]["pending_friends"]:
        bot.send_message(message.chat.id, "Нет заявки от этого игрока.")
        return

    users[user_id]["pending_friends"].remove(requester_id)
    users[user_id]["friends"].append(requester_id)
    users[requester_id]["friends"].append(user_id)
    save_users(users)

    bot.send_message(message.chat.id, f"✅ Игрок {users[requester_id]['name']} добавлен в друзья.")
    try:
        bot.send_message(int(requester_id), f"🎉 {users[user_id]['name']} принял твою заявку в друзья!")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

@bot.message_handler(commands=['friends'])
def show_friends(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    friend_ids = users[user_id].get("friends", [])
    if not friend_ids:
        bot.send_message(message.chat.id, "У тебя пока нет друзей. Добавь их через /addfriend ID")
        return

    text = "👥 Твои друзья:\n"
    for fid in friend_ids:
        name = users.get(fid, {}).get("name", "Неизвестно")
        text += f"• {name} (ID: {fid})\n"

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['pay'])
def pay_friend(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "Используй: /pay ID_друга сумма")
        return

    target_id, amount_str = args[1], args[2]

    if not amount_str.isdigit():
        bot.send_message(message.chat.id, "Сумма должна быть числом.")
        return

    amount = int(amount_str)

    if target_id not in users:
        bot.send_message(message.chat.id, "Игрок не найден.")
        return

    if target_id not in users[user_id].get("friends", []):
        bot.send_message(message.chat.id, "Ты можешь передавать монеты только друзьям.")
        return

    if users[user_id]["coins"] < amount:
        bot.send_message(message.chat.id, "Недостаточно монет.")
        return

    users[user_id]["coins"] -= amount
    users[target_id]["coins"] += amount
    save_users(users)

    bot.send_message(message.chat.id, f"✅ Ты отправил {amount} монет игроку {users[target_id]['name']} (ID: {target_id})")



# КЛАНОВЫЙ ЧАТ 

@bot.message_handler(commands=['clanchat'])
def clan_chat(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    user = users[user_id]
    clan_id = user.get("clan_id")

    if not clan_id:
        bot.send_message(message.chat.id, "Ты не состоишь в клане.")
        return

    text_parts = message.text.split(' ', 1)
    if len(text_parts) < 2:
        bot.send_message(message.chat.id, "Пиши так: /clanchat Твое сообщение")
        return

    chat_text = text_parts[1]
    sender_name = user["name"]

    # Рассылаем всем участникам этого клана
    for uid, u in users.items():
        if u.get("clan_id") == clan_id and uid != user_id:
            try:
                bot.send_message(int(uid), f"💬 Клановый чат от {sender_name} (ID: {user_id}):\n{chat_text}")
            except Exception as e:
                print(f"Ошибка отправки клан-чата для {uid}: {e}")

    bot.send_message(message.chat.id, "📨 Сообщение отправлено в клан!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_") or call.data.startswith("reject_"))
def handle_friend_response(call):
    users = load_users()
    user_id = str(call.from_user.id)
    parts = call.data.split("_")
    action = parts[0]
    requester_id = parts[-1]  # последний элемент — ID

    if user_id not in users or requester_id not in users:
        bot.answer_callback_query(call.id, "Ошибка данных.")
        return

    users[user_id].setdefault("pending_friends", [])
    users[user_id].setdefault("friends", [])
    users[requester_id].setdefault("friends", [])

    if requester_id not in users[user_id]["pending_friends"]:
        bot.answer_callback_query(call.id, "Нет такой заявки.")
        return

    if action == "accept":
        users[user_id]["pending_friends"].remove(requester_id)
        users[user_id]["friends"].append(requester_id)
        users[requester_id]["friends"].append(user_id)

        save_users(users)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🎉 Заявка в друзья принята!"
        )
        try:
            bot.send_message(int(requester_id), f"✅ {users[user_id]['name']} добавил тебя в друзья!")
        except:
            pass

    elif action == "reject":
        users[user_id]["pending_friends"].remove(requester_id)
        save_users(users)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ Заявка отклонена."
        )
        try:
            bot.send_message(int(requester_id), f"❌ {users[user_id]['name']} отклонил твою заявку.")
        except:
            pass

# ДУЭЛИ 

@bot.message_handler(commands=['duel'])
def duel(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. /start")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "Используй: /duel ID_игрока")
        return

    opponent_id = args[1].lstrip("@")

    if opponent_id == user_id:
        bot.send_message(message.chat.id, "Ты не можешь вызвать себя.")
        return

    if opponent_id not in users:
        bot.send_message(message.chat.id, "Такой игрок не найден.")
        return

    # Сохраняем в user временно заявку
    users[opponent_id]["duel_request"] = user_id
    save_users(users)

    # Отправляем кнопки
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Принять", callback_data=f"accept_duel_{user_id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_duel_{user_id}")
    )

    try:
        bot.send_message(int(opponent_id), f"⚔️ {users[user_id]['name']} вызывает тебя на дуэль!", reply_markup=markup)
        bot.send_message(message.chat.id, "Заявка на дуэль отправлена.")
    except:
        bot.send_message(message.chat.id, "❌ Не удалось отправить сообщение противнику.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_duel_") or call.data.startswith("reject_duel_"))
def handle_duel_response(call):
    users = load_users()
    defender_id = str(call.from_user.id)
    parts = call.data.split("_")
    action = parts[0]     # "accept" или "reject"
    attacker_id = parts[2]

    if attacker_id not in users or defender_id not in users:
        bot.answer_callback_query(call.id, "Игроки не найдены.")
        return

    # 🛡 Проверим, есть ли вообще заявка
    if users[defender_id].get("duel_request") != attacker_id:
        bot.answer_callback_query(call.id, "❌ У вас нет заявки от этого игрока.")
        return

    attacker = users[attacker_id]
    defender = users[defender_id]

    if action == "accept":
        # удалим заявку
        users[defender_id]["duel_request"] = None

        attacker_hp = attacker["hp"]
        defender_hp = defender["hp"]

        if attacker_hp <= 0 or defender_hp <= 0:
            bot.send_message(defender_id, "У кого-то из вас 0 HP. Дуэль невозможна.")
            return

        while attacker_hp > 0 and defender_hp > 0:
            defender_hp -= 15
            if defender_hp > 0:
                attacker_hp -= 15

        result_text = ""
        if attacker_hp > 0:
            attacker["hp"] = attacker_hp
            defender["hp"] = 0
            attacker["coins"] += 100
            defender["coins"] = max(0, defender["coins"] - 50)
            result_text = f"🏆 {attacker['name']} победил в дуэли!\n💰 +100 монет\n💀 {defender['name']} проиграл и потерял 50 монет."
        else:
            defender["hp"] = defender_hp
            attacker["hp"] = 0
            defender["coins"] += 100
            attacker["coins"] = max(0, attacker["coins"] - 50)
            result_text = f"🏆 {defender['name']} победил в дуэли!\n💰 +100 монет\n💀 {attacker['name']} проиграл и потерял 50 монет."

        save_users(users)

        bot.send_message(defender_id, result_text)
        bot.send_message(attacker_id, result_text)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ Дуэль завершена!")
    else:
        users[defender_id]["duel_request"] = None  # удалим и при отклонении
        save_users(users)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❌ Дуэль отклонена.")
        try:
            bot.send_message(int(attacker_id), f"❌ {defender['name']} отклонил дуэль.")
        except:
            pass

# BONUS ONE DAY
@bot.message_handler(commands=['daily'])
def daily_bonus(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    user = users[user_id]
    now = int(time.time())

    if now - user.get("last_daily_bonus", 0) < 86400:  # 24 часа = 86400 секунд
        remaining = 86400 - (now - user["last_daily_bonus"])
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        bot.send_message(message.chat.id, f"🎁 Ты уже получал ежедневный бонус. Попробуй снова через {hours} ч. {minutes} мин.")
        return

    coins = random.randint(50, 150)
    xp = random.randint(10, 50)

    user["coins"] += coins
    user["xp"] += xp
    user["last_daily_bonus"] = now

    save_users(users)

    bot.send_message(
        message.chat.id,
        f"🎁 Ты получил ежедневный бонус!\n💰 Монеты: +{coins}\n✨ Опыт: +{xp}"
    )

@bot.message_handler(commands=['business'])
def business_menu(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Напиши /start.")
        return

    business = user.get("business")
    if business:
        last = user.get("last_business_income", 0)
        wait = BUSINESS_COOLDOWN - int(time.time() - last)
        msg = f"🏭 У тебя бизнес: {business['name']}\n💰 Доход: {business['income']} монет каждые 5 минут\n"

        if wait <= 0:
            msg += "🟢 Доход доступен. Напиши /collect"
        else:
            minutes = wait // 60
            seconds = wait % 60
            msg += f"⏳ Доход через {minutes} мин {seconds} сек"

        msg += "\n\n🔻 Напиши /sell_business чтобы продать"
        bot.send_message(message.chat.id, msg)
    else:
        text = "📦 Доступные бизнесы:\n"
        for b in BUSINESS_LIST:
            text += f"{b['id']}. {b['name']} — {b['price']} монет, доход: {b['income']} / 5 мин\n"
        text += "\nНапиши: /buy_business [номер]"
        bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['buy_business'])
def buy_business(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return

    if user.get("business"):
        bot.send_message(message.chat.id, "❌ У тебя уже есть бизнес.")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, "Пиши: /buy_business [номер]")
        return

    b_id = int(args[1])
    business = next((b for b in BUSINESS_LIST if b["id"] == b_id), None)
    if not business:
        bot.send_message(message.chat.id, "❌ Такого бизнеса нет.")
        return

    if user["coins"] < business["price"]:
        bot.send_message(message.chat.id, "💸 Недостаточно монет.")
        return

    user["coins"] -= business["price"]
    user["business"] = business
    user["last_business_income"] = time.time()
    save_users(users)
    bot.send_message(message.chat.id, f"✅ Ты купил бизнес: {business['name']}")

@bot.message_handler(commands=['collect'])
def collect_business_income(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user or "business" not in user:
        bot.send_message(message.chat.id, "❌ У тебя нет бизнеса.")
        return

    last = user.get("last_business_income", 0)
    now = time.time()

    if now - last < BUSINESS_COOLDOWN:
        wait = int(BUSINESS_COOLDOWN - (now - last))
        minutes = wait // 60
        seconds = wait % 60
        bot.send_message(message.chat.id, f"⏳ Доход будет через {minutes} мин {seconds} сек.")
        return

    income = user["business"]["income"]
    user["coins"] += income
    user["last_business_income"] = now
    save_users(users)

    bot.send_message(message.chat.id, f"💰 Ты получил {income} монет от бизнеса.")


@bot.message_handler(commands=['sell_business'])
def sell_business(message):
    users = load_users()
    user_id = str(message.from_user.id)
    user = users.get(user_id)

    if not user or "business" not in user:
        bot.send_message(message.chat.id, "У тебя нет бизнеса.")
        return

    refund = user["business"]["price"] // 2
    user["coins"] += refund
    user.pop("business")
    user.pop("last_business_income", None)

    save_users(users)
    bot.send_message(message.chat.id, f"🧾 Ты продал бизнес и получил {refund} монет.")


bot.polling()
