from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ❗ HARD-CODED TOKEN (NOT RECOMMENDED FOR PRODUCTION)
BOT_TOKEN = "8575760556:AAEKxmRf8acr1a7k6Fx4d0BZa39d04AukB8"

TEMPLATE = """🚦 Traffic Violation Notice 🚦
Immediate Action Required

Vehicle Number: {{vehicle}}

Dear Vehicle Owner,

We wish to inform you that a traffic violation has been recorded against your vehicle for jumping a red signal.

Violation: Traffic Light Break
Amount Payable: ₹4500

Please take necessary action.
"""

# In-memory user session storage
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📂 Upload a .txt or .csv file\n\n"
        "Format:\n"
        "phone,vehicle\n\n"
        "Example:\n"
        "9428791606,GJ03HL4878"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = (await file.download_as_bytearray()).decode("utf-8")

    records = []
    for line in content.splitlines():
        if "," not in line:
            continue
        phone, vehicle = line.split(",", 1)
        phone = phone.strip()
        vehicle = vehicle.strip()
        if phone.isdigit() and len(phone) == 10:
            records.append((phone, vehicle))

    if not records:
        await update.message.reply_text("❌ No valid records found.")
        return

    user_data_store[update.effective_user.id] = {
        "records": records,
        "index": 0
    }

    await send_next(update, context)

async def send_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = user_data_store.get(user_id)

    if not data:
        await update.effective_message.reply_text("❗ Upload a file first.")
        return

    index = data["index"]
    total = len(data["records"])

    if index >= total:
        await update.effective_message.reply_text("✅ All messages completed.")
        return

    phone, vehicle = data["records"][index]
    data["index"] += 1

    # 1️⃣ Send phone number only
    await update.effective_message.reply_text(phone)

    # 2️⃣ Send message with vehicle number
    msg = TEMPLATE.replace("{{vehicle}}", vehicle)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"▶️ Next ({data['index']}/{total})", callback_data="next")]
    ])

    await update.effective_message.reply_text(msg, reply_markup=keyboard)

async def next_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_next(update, context)

async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_next(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(next_button))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()