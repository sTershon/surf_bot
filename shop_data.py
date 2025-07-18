# shop_data.py

WEAPON_SHOP = [
    {"name": "🗡 Меч новичка", "price": 100, "damage": 10},
    {"name": "🏹 Лук охотника", "price": 150, "damage": 12},
    {"name": "🔥 Огненный меч", "price": 300, "damage": 20},
]

ARMOR_SHOP = [
    {"name": "🛡 Кожаная броня", "price": 80, "defense": 5},
    {"name": "🔰 Железная броня", "price": 200, "defense": 10},
    {"name": "⚔️ Броня воина", "price": 400, "defense": 20},
]

POTION_SHOP = [
    {
        "name": "🧪 Зелье брони",
        "price": 50,
        "effect": {
            "armor_boost": 2,
            "duration": 3  # в боях
        }
    },
    {
        "name": "❤️ Зелье лечения",
        "price": 40,
        "effect": {
            "hp": 30
        }
    }
]