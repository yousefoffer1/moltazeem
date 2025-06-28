import os
import json
from datetime import datetime, timedelta
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def get_default_status():
    return {
        "اذكار_الصباح": False,
        "ورد_القرآن": False,
        "اذكار_المساء": False,
        "قيام_الليل": False
    }

def get_user_file(user_id):
    return f"user_{user_id}.json"

def load_user_data(user_id):
    file_path = get_user_file(user_id)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_user_data(user_id, data):
    file_path = get_user_file(user_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_status_text(status):
    today = datetime.now().strftime("%Y-%m-%d")
    today_status = status.get(today, get_default_status())
    return (
        f"📆 جدول عباداتك ليوم {today}:\n\n"
        f"☀️ أذكار الصباح: {'✅' if today_status['اذكار_الصباح'] else '❌'}\n"
        f"📖 وِرد القرآن: {'✅' if today_status['ورد_القرآن'] else '❌'}\n"
        f"🌙 أذكار المساء: {'✅' if today_status['اذكار_المساء'] else '❌'}\n"
        f"🌌 قيام الليل: {'✅' if today_status['قيام_الليل'] else '❌'}"
    )

def get_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ أذكار الصباح", callback_data="اذكار_الصباح"),
        InlineKeyboardButton("✅ وِرد القرآن", callback_data="ورد_القرآن")
    )
    keyboard.row(
        InlineKeyboardButton("✅ أذكار المساء", callback_data="اذكار_المساء"),
        InlineKeyboardButton("✅ قيام الليل", callback_data="قيام_الليل")
    )
    return keyboard

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📋 جدول اليوم"))
    keyboard.add(KeyboardButton("📆 سجل الأسبوع"))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    status = load_user_data(user_id)
    text = get_status_text(status)
    welcome_message = (
        "*اهلا بيك ي كتكوت في بوت ملتزم 😍*\n\n"
        "*لو بتتكاسل في أداء العبادات البوت هيساعدك تنتظم ان شاءالله 🤲*\n\n"
        "*كل الل عليك لما تخلص عبادة من العبادات تدوس ع علامة صح قصادها ✅*\n\n"
        "*وكمان فيه سجل اسبوعي تقدر تشوف فيه العبادات اللي عملتها واللي قصرت فيها 🗓️*\n\n"
        "*وكمان فيه تذكير اشعارات دايما بالعبادات  عشان متكسلش ي كتكوت 🔔*"
    )
    bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown")
    bot.send_message(message.chat.id, text, reply_markup=get_keyboard())
    bot.send_message(message.chat.id, "اختر من القائمة:", reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.text == "📋 جدول اليوم")
def handle_daily_status(message):
    user_id = message.from_user.id
    status = load_user_data(user_id)
    text = get_status_text(status)
    bot.send_message(message.chat.id, text, reply_markup=get_keyboard())

@bot.message_handler(func=lambda message: message.text == "📆 سجل الأسبوع")
def handle_weekly_log(message):
    user_id = message.from_user.id
    status = load_user_data(user_id)

    arabic_days = {
        "Saturday": "السبت",
        "Sunday": "الأحد",
        "Monday": "الإثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الأربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة"
    }

    response = "🗓️ *سجل الأسبوع الأخير:*\n\n"
    response += "*📅 اليوم* | ☀️ صباح | 📖 قرآن | 🌙 مساء | 🌌 قيام\n"
    response += "─" * 40 + "\n"

    for i in range(6, -1, -1):
        date_obj = datetime.now() - timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        weekday_en = date_obj.strftime("%A")
        weekday_ar = arabic_days.get(weekday_en, weekday_en)
        day_status = status.get(date_str, get_default_status())
        row = (
            f"{weekday_ar} | "
            f"{'✅' if day_status['اذكار_الصباح'] else '❌'} | "
            f"{'✅' if day_status['ورد_القرآن'] else '❌'} | "
            f"{'✅' if day_status['اذكار_المساء'] else '❌'} | "
            f"{'✅' if day_status['قيام_الليل'] else '❌'}"
        )
        response += row + "\n"

    bot.send_message(message.chat.id, response, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    status = load_user_data(user_id)
    action = call.data
    today = datetime.now().strftime("%Y-%m-%d")
    day_status = status.get(today, get_default_status())

    if day_status.get(action):
        bot.answer_callback_query(call.id, text="تم مسبقًا ✅")
        return

    day_status[action] = True
    status[today] = day_status
    save_user_data(user_id, status)

    new_text = get_status_text(status)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=new_text,
        reply_markup=get_keyboard()
    )

    responses = {
        "اذكار_الصباح": "شطور يا جميل كده انت انهاردة هتبقى في حفظ الله ويومك هيبقى مليان بركه 😍",
        "ورد_القرآن": "ربنا يحفظك بالقرآن يا جميل ويجعله شفيعك يوم القيامة 🤲😍",
        "اذكار_المساء": "ربنا يحفظك يا جميل من كل سوء 😍",
        "قيام_الليل": "كده تنام وانت مطمن يا جميل وإن شاء الله ربنا يحققلك كل دعوة دعيتها 🤲😍"
    }

    if action in responses:
        bot.send_message(user_id, responses[action])

if __name__ == "__main__":
    print("البوت شغّال ✅")
    bot.polling()