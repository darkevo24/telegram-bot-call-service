from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

BTC_QR_CODE_IMAGE_PATH = "./btc.jpg"  # Replace with actual link to QR code image

# Your Bitcoin payment processor API endpoint and credentials
PAYMENT_PROCESSOR_API_URL = "https://api.cryptomus.com"
PAYMENT_PROCESSOR_API_KEY = ""

# Function to generate a new Bitcoin address for each transaction
def generate_new_btc_address():
    try:
        response = requests.post(f"{PAYMENT_PROCESSOR_API_URL}/generate_address", headers={"Authorization": f"Bearer {PAYMENT_PROCESSOR_API_KEY}"})
        if response.status_code == 200:
            return response.json()["address"]
        else:
            return None
    except Exception as e:
        print("Error generating BTC address:", e)
        return None

# Function to check payment status using the payment processor API
def check_payment_status(transaction_id):
    try:
        response = requests.get(f"{PAYMENT_PROCESSOR_API_URL}/check_payment_status/{transaction_id}", headers={"Authorization": f"Bearer {PAYMENT_PROCESSOR_API_KEY}"})
        if response.status_code == 200:
            return response.json()["status"]
        else:
            return None
    except Exception as e:
        print("Error checking payment status:", e)
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Purchase", callback_data='purchase')],
        [InlineKeyboardButton("Commands", callback_data='commands')],
        [InlineKeyboardButton("FAQs", callback_data='faqs')],
        [InlineKeyboardButton("How To", callback_data='howto')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose a section:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'purchase':
        purchase_keyboard = [
            [InlineKeyboardButton("2 DAY $125 [btc price] / $100", callback_data='purchase_2_days')],
            [InlineKeyboardButton("3 DAY $220 [btc price] / $170", callback_data='purchase_3_days')],
            [InlineKeyboardButton("1 WEEK $370 [btc price] / $350", callback_data='purchase_1_week')],
        ]
        purchase_reply_markup = InlineKeyboardMarkup(purchase_keyboard)
        await query.edit_message_text(text="🪙 We accept BTC\n\n👇 Select an option 👇", reply_markup=purchase_reply_markup)
    elif query.data == 'purchase_2_days':
        await send_payment_instructions(query, "2 days", "$100")
    elif query.data == 'purchase_3_days':
        await send_payment_instructions(query, "3 days", "$170")
    elif query.data == 'purchase_1_week':
        await send_payment_instructions(query, "1 week", "$350")
    elif query.data == 'commands':
        await query.edit_message_text(text=('Welcome to the Commands section. Here are the commands you can use:\n'
                                            '🔊 /otp - Capture Any Numeric OTP\n'
                                            '💳 /cc - Capture Card details\n'
                                            '🗣 /pgp - Transfers you to them\n'
                                            '🤖 /pgp1 - Transfers them to you after pressing 1\n'
                                            '🗣 /cpgp - Custom script pgp, transfers after pressing 1'))
    elif query.data == 'faqs':
        await query.edit_message_text(text="Welcome to the FAQs section. Here you can find common questions and answers.")
    elif query.data == 'howto':
        await query.edit_message_text(text="Welcome to the How To section. Here you can find tutorial on how to use the bot.")

async def send_payment_instructions(query, duration, amount):
    btc_address = generate_new_btc_address()
    if btc_address:
        keyboard = [
            [InlineKeyboardButton("Check Payment Status", callback_data='check_payment')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"Currency - BTC\n\n"
            f"Send {amount} to this address: {btc_address}\n\n"
            f"ℹ️ You will be granted a subscription for {duration} once the transaction reaches enough confirmations.\n"
            f"⚠️ This is a one-time payment address, please send money only once.\n"
            f"⚠️ Use High Network Fee ⚠️"
        )

        try:
            with open(BTC_QR_CODE_IMAGE_PATH, 'rb') as photo:
                await query.message.reply_photo(photo=photo, caption=message, reply_markup=reply_markup)
        except FileNotFoundError:
            await query.message.reply_text("The QR code image is not found, please check the file path.")
    else:
        await query.message.reply_text("Error generating Bitcoin address. Please try again later.")

async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Extract transaction ID from the update
    transaction_id = extract_transaction_id(update)

    if transaction_id:
        # Check payment status using the payment processor's API
        payment_status = check_payment_status(transaction_id)

        if payment_status:
            await update.callback_query.edit_message_text(text=payment_status)
        else:
            await update.callback_query.edit_message_text(text="Error checking payment status. Please try again later.")
    else:
        await update.callback_query.edit_message_text(text="Transaction ID not found.")

def extract_transaction_id(update: Update) -> str:
    # Extract the transaction ID from the update data
    # You'll need to adapt this based on how transaction IDs are structured in your system
    # For example, if the transaction ID is stored in the update's message text, you can extract it like this:
    try:
        transaction_id = update.message.text.split(":")[-1].strip()
        return transaction_id
    except Exception as e:
        print("Error extracting transaction ID:", e)
        return None

# Initialize the bot application
app = ApplicationBuilder().token("6989059213:AAHXL6gucjhr9vzHOCFTRA2ArvRB-cqSToU").build()

# Add command handler to start the bot
app.add_handler(CommandHandler("start", start))
# Add a callback query handler to handle button presses
app.add_handler(CallbackQueryHandler(button))

# Run the bot
if __name__ == '__main__':
    app.run_polling()
