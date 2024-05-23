from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BTC_QR_CODE_IMAGE_PATH = "./btc.jpg"  # Replace with actual link to QR code image

# Function to start the bot and show the main menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Purchase", callback_data='purchase')],
        [InlineKeyboardButton("Commands", callback_data='commands')],
        [InlineKeyboardButton("FAQs", callback_data='faqs')],
        [InlineKeyboardButton("How To", callback_data='howto')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose a section:', reply_markup=reply_markup)

# Callback query handler for button presses
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'purchase':
        purchase_keyboard = [
            [InlineKeyboardButton("1 day | $50", callback_data='purchase_1_day')],
            [InlineKeyboardButton("1 week | $300", callback_data='purchase_1_week')],
            [InlineKeyboardButton("1 month | $750", callback_data='purchase_1_month')],
        ]
        purchase_reply_markup = InlineKeyboardMarkup(purchase_keyboard)
        await query.edit_message_text(text="🪙 We accept BTC\n\n👇 Select an option 👇", reply_markup=purchase_reply_markup)
    elif query.data == 'purchase_1_day':
        await send_payment_instructions(query, "1 day", "$50")
    elif query.data == 'purchase_1_week':
        await send_payment_instructions(query, "1 week", "$300")
    elif query.data == 'purchase_1_month':
        await send_payment_instructions(query, "1 month", "$750")
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
    keyboard = [
        [InlineKeyboardButton("Check Payment Status", callback_data='check_payment')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"Currency - BTC\n\n"
        # f"Send {amount} to this address:: {BTC_ADDRESS}\n\n"
        f"ℹ️ You will be granted a subscription for {duration} once the transaction reaches enough confirmations.\n"
        f"⚠️ This is a one-time payment address, please send money only once.\n"
        f"⚠️ Use High Network Fee ⚠️"
    )

    try:
        with open(BTC_QR_CODE_IMAGE_PATH, 'rb') as photo:
            await query.message.reply_photo(photo=photo, caption=message, reply_markup=reply_markup)
    except FileNotFoundError:
        await query.message.reply_text("The QR code image is not found, please check the file path.")

async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Dummy implementation of payment check
    # Here you would implement the actual logic to check the payment status from the blockchain or your backend service
    await update.callback_query.edit_message_text(text="Checking payment status...")

    # Simulate checking status
    # In real implementation, replace this with actual payment status check logic
    payment_status = "Payment Received! Subscription has been activated."

    await update.callback_query.edit_message_text(text=payment_status)

# Initialize the bot application
app = ApplicationBuilder().token("6989059213:AAHXL6gucjhr9vzHOCFTRA2ArvRB-cqSToU").build()

# Add command handler to start the bot
app.add_handler(CommandHandler("start", start))
# Add a callback query handler to handle button presses
app.add_handler(CallbackQueryHandler(button))

# Run the bot
if __name__ == '__main__':
    app.run_polling()
