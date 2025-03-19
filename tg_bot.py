from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Функции для обработки кнопок
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Хочу заключить договор конвертируемого займа", callback_data='offer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Я Telegram-бот для заключения договора конвертируемого займа. Как я могу вам помочь?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'offer':
        keyboard = [
            [InlineKeyboardButton("Ознакомлен с офертой", callback_data='consent')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="ЗДЕСЬ ДОЖНА БЫТЬ ОФЕРТА", reply_markup=reply_markup)

    elif query.data == 'consent':
        keyboard = [
            [InlineKeyboardButton("Даю согласие на обработку персональных данных", callback_data='disclaimer')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ", reply_markup=reply_markup)

    elif query.data == 'disclaimer':
        keyboard = [
            [InlineKeyboardButton("Ознакомлен", callback_data='final')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="ДИСКЛЕЙМЕРЫ ПО ИСПОЛЬЗОВАНИЮ СОЗДАННОГО ДОГОВОРА НЕ ПО НАЗНАЧЕНИЮ ИЛИ С ИЗМЕНЕННЫМИ УСЛОВИЯМИ", reply_markup=reply_markup)

    elif query.data == 'final':
        await query.edit_message_text(text="Спасибо за использование нашего бота!")

# Основная функция бота
def main():
    # Вставьте сюда ваш токен от BotFather
    TOKEN = "7607646604:AAGQoa_c_Soale1SLvuBtJDpaaaOHsUhUyw"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()
    print("Бот запущен!")

if __name__ == "__main__":
    main()