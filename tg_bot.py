from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from docx import Document
import re

# Определение состояний
DATE_INPUT, COST_INPUT, TERM_INPUT = range(3)

# Хранилище данных
contract_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Хочу заключить договор конвертируемого займа", callback_data='offer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я Telegram-бот для заключения договора конвертируемого займа. Как я могу вам помочь?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            [InlineKeyboardButton("Да", callback_data='percent_yes')],
            [InlineKeyboardButton("Нет", callback_data='percent_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Заем будет процентный?", reply_markup=reply_markup)

    elif query.data == 'percent_yes':
        await query.edit_message_text(
            text="Вы выбрали процентный заем.\nВведите дату договора в формате DD.MM.YYYY:"
        )
        return DATE_INPUT

    elif query.data == 'percent_no':
        await query.edit_message_text(text="Вы выбрали беспроцентный заем. Спасибо за использование нашего бота!")
        return ConversationHandler.END

async def date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['date'] = update.message.text
    await update.message.reply_text("Укажите сумму договора (стоимость) в рублях:")
    return COST_INPUT

async def cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['cost'] = update.message.text
    await update.message.reply_text("Введите срок действия договора в днях:")
    return TERM_INPUT

async def term_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['term'] = update.message.text
    doc_path = generate_contract(contract_data)
    with open(doc_path, 'rb') as doc_file:
        await update.message.reply_document(doc_file)
    await update.message.reply_text("Спасибо! Ваш договор успешно создан.", reply_markup=None)
    return ConversationHandler.END

def generate_contract(data) -> str:
    template_path = r"C:\Users\User\Desktop\hse\template.docx"
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for key, value in data.items():
            if f"{{{{{key}}}}}" in paragraph.text:
                paragraph.text = re.sub(f"{{{{{key}}}}}", value, paragraph.text)
    file_name = "contract_filled.docx"
    doc.save(file_name)
    return file_name

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text("📄 Создание договора отменено. Используйте команду /start, чтобы начать заново.", reply_markup=None)
    return ConversationHandler.END

def main() -> None:
    TOKEN = "7607646604:AAGQoa_c_Soale1SLvuBtJDpaaaOHsUhUyw"
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_input)],
            COST_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_input)],
            TERM_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, term_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
