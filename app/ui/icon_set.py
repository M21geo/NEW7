"""Icons offered for categories: plain Material icons ('عادية') and colourful 3D-style emoji ('مجسمة'), by group."""

PLAIN = {
    "طعام": ["restaurant", "fastfood", "local_pizza", "lunch_dining", "set_meal", "bakery_dining", "icecream", "cake",
             "local_cafe", "local_bar", "kitchen", "emoji_food_beverage"],
    "مواصلات": ["directions_car", "local_taxi", "directions_bus", "train", "flight", "two_wheeler", "pedal_bike",
                "local_gas_station", "local_parking", "directions_boat", "car_repair", "build"],
    "بيت": ["home", "bolt", "water_drop", "wifi", "tv", "chair", "bed", "cleaning_services", "lightbulb", "key",
            "local_laundry_service", "yard"],
    "صحة": ["favorite", "local_hospital", "medication", "medical_services", "vaccines", "healing", "fitness_center",
            "spa", "self_improvement", "psychology", "face", "sports_gymnastics"],
    "تسوق": ["shopping_bag", "shopping_cart", "store", "checkroom", "diamond", "card_giftcard", "watch", "phone_android",
             "laptop", "headphones", "brush", "toys"],
    "ترفيه": ["sports_esports", "movie", "music_note", "sports_soccer", "beach_access", "celebration", "theater_comedy",
              "palette", "menu_book", "camera_alt", "casino", "park"],
    "مال": ["payments", "savings", "account_balance", "credit_card", "work", "trending_up", "receipt_long",
            "attach_money", "request_quote", "volunteer_activism", "currency_exchange", "paid"],
    "أخرى": ["school", "pets", "child_care", "call", "mail", "mosque", "star", "bookmark", "category", "groups",
             "language", "cruelty_free"],
}

EMOJI = {
    "طعام": "🍔 🍕 🍟 🌮 🍗 🥩 🍣 🍜 🥗 🍎 🥖 🍰 🍩 ☕ 🧋 🥤 🍽️ 🛒 🥛 🍳 🍫 🍉 🥙 🍚".split(),
    "مواصلات": "🚗 🚕 🚌 🚇 🚲 🛵 🏍️ ⛽ 🛣️ ✈️ 🚢 🚂 🚖 🅿️ 🔧 🛞".split(),
    "بيت": "🏠 🛋️ 💡 🔌 🚿 🧹 🧺 🔑 🛏️ 📺 🧯 🪑 🌡️ 💧 📶 🗑️ 🧼 🪴".split(),
    "صحة": "💊 🩺 🏥 🦷 🩹 💉 🧴 😷 🧘 🏋️ 👓 🩸 🧠 ❤️‍🩹".split(),
    "تسوق": "🛍️ 👕 👗 👟 👜 💄 🎁 💍 ⌚ 📱 💻 🎧 🧸 👶 🕶️ 👔".split(),
    "ترفيه": "🎮 🎬 🎵 🎤 🎭 🎨 📚 🎟️ ⚽ 🏀 🏖️ 🎂 🎉 🎡 🎳 🧩 🏕️ 🎣".split(),
    "مال": "💰 💵 💳 🏦 📈 💼 🧾 💸 🪙 💎 🤝 📊 🧮 🏧".split(),
    "أخرى": "⭐ ❤️ 🔥 🐶 🐱 🌿 🎓 📞 ✉️ 🕌 🌙 🎗️ 🤲 🐑 🧿 🕋 👨‍👩‍👧 🐓".split(),
}

GROUPS = list(PLAIN)
