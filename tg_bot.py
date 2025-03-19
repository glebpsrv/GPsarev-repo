from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ваш Telegram-бот. Как я могу вам помочь?")

# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = f"Вы написали: {user_message}"  # Простой ответ
    await update.message.reply_text(response)

# Функция для команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start - Запуск бота\n/help - Получить помощь")

# Основная функция бота
def main():
    # Вставьте сюда ваш токен от BotFather
    TOKEN = "7607646604:AAGQoa_c_Soale1SLvuBtJDpaaaOHsUhUyw"

    # Создаем ApplicationBuilder и связываем его с вашим токеном бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчик текста
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling()
    print("Бот запущен!")

if __name__ == "__main__":
    main()