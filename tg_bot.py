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
DATE_INPUT, COST_INPUT, BORROWER_NAME_INPUT, LENDER_NAME_INPUT = range(4)
BORROWER_ACCOUNT_INPUT, BORROWER_BANK_INPUT, BORROWER_BIK_INPUT, BORROWER_CORR_ACCOUNT_INPUT, BORROWER_INN_INPUT, BORROWER_KPP_INPUT = range(4, 10)
BORROWER_EMAIL_INPUT, BORROWER_ADDRESS_INPUT = range(10, 12)  # Новые состояния для email и адреса
LENDER_ACCOUNT_INPUT, LENDER_BANK_INPUT, LENDER_BIK_INPUT, LENDER_CORR_ACCOUNT_INPUT, LENDER_INN_INPUT, LENDER_KPP_INPUT = range(12, 18)
LENDER_EMAIL_INPUT, LENDER_ADDRESS_INPUT = range(18, 20)  # Новые состояния для email и адреса займодателя

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
        contract_data['percent'] = 'yes'  # Сохраняем информацию о процентном займе
        await query.edit_message_text(
            text="Вы выбрали процентный заем.\nВведите дату договора в формате DD.MM.YYYY:"
        )
        return DATE_INPUT

    elif query.data == 'percent_no':
        contract_data['percent'] = 'no'  # Сохраняем информацию о беспроцентном займе
        await query.edit_message_text(text="Вы выбрали беспроцентный заем. Пожалуйста, введите дату договора в формате DD.MM.YYYY:")
        return DATE_INPUT  # Переход к вводу даты для беспроцентного займа

async def date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['date'] = update.message.text
    await update.message.reply_text("Укажите сумму договора (стоимость) в рублях:")
    return COST_INPUT

async def cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['cost'] = update.message.text
    await update.message.reply_text("Введите ФИО или наименование заемщика:")
    return BORROWER_NAME_INPUT  

async def borrower_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_name'] = update.message.text
    await update.message.reply_text("Введите email заемщика:")
    return BORROWER_EMAIL_INPUT  # Переход к вводу email заемщика

async def borrower_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_email'] = update.message.text
    await update.message.reply_text("Введите адрес заемщика:")
    return BORROWER_ADDRESS_INPUT  # Переход к вводу адреса заемщика

async def borrower_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_address'] = update.message.text
    await update.message.reply_text("Введите номер счета заемщика:")
    return BORROWER_ACCOUNT_INPUT

async def borrower_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_account'] = update.message.text
    await update.message.reply_text("Введите банк получателя заемщика:")
    return BORROWER_BANK_INPUT

async def borrower_bank_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_bank'] = update.message.text
    await update.message.reply_text("Введите БИК банка получателя заемщика:")
    return BORROWER_BIK_INPUT

async def borrower_bik_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_bik'] = update.message.text
    await update.message.reply_text("Введите корреспондентский счет заемщика:")
    return BORROWER_CORR_ACCOUNT_INPUT

async def borrower_corr_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_corr_account'] = update.message.text
    await update.message.reply_text("Введите ИНН заемщика:")
    return BORROWER_INN_INPUT

async def borrower_inn_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_inn'] = update.message.text
    await update.message.reply_text("Введите КПП заемщика:")
    return BORROWER_KPP_INPUT

async def borrower_kpp_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_kpp'] = update.message.text
    await update.message.reply_text("Введите ФИО или наименование займодателя:")
    return LENDER_NAME_INPUT

async def lender_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_name'] = update.message.text
    await update.message.reply_text("Введите email займодателя:")
    return LENDER_EMAIL_INPUT  # Переход к вводу email займодателя

async def lender_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_email'] = update.message.text
    await update.message.reply_text("Введите адрес займодателя:")
    return LENDER_ADDRESS_INPUT  # Переход к вводу адреса займодателя

async def lender_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_address'] = update.message.text
    await update.message.reply_text("Введите номер счета займодателя:")
    return LENDER_ACCOUNT_INPUT

async def lender_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_account'] = update.message.text
    await update.message.reply_text("Введите банк получателя займодателя:")
    return LENDER_BANK_INPUT

async def lender_bank_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_bank'] = update.message.text
    await update.message.reply_text("Введите БИК банка получателя займодателя:")
    return LENDER_BIK_INPUT

async def lender_bik_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_bik'] = update.message.text
    await update.message.reply_text("Введите корреспондентский счет займодателя:")
    return LENDER_CORR_ACCOUNT_INPUT

async def lender_corr_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_corr_account'] = update.message.text
    await update.message.reply_text("Введите ИНН займодателя:")
    return LENDER_INN_INPUT

async def lender_inn_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_inn'] = update.message.text
    await update.message.reply_text("Введите КПП займодателя:")
    return LENDER_KPP_INPUT

async def lender_kpp_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_kpp'] = update.message.text
    # Определяем путь к шаблону в зависимости от типа займа
    if 'percent' in contract_data and contract_data['percent'] == 'yes':
        template_path = r"C:\Users\User\Desktop\hse\template.docx"
    else:
        template_path = r"C:\Users\User\Desktop\hse\template_no_proc.docx"
    
    doc_path = generate_contract(contract_data, template_path)
    with open(doc_path, 'rb') as doc_file:
        await update.message.reply_document(doc_file)
    await update.message.reply_text("Спасибо! Ваш договор успешно создан.", reply_markup=None)
    return ConversationHandler.END

def generate_contract(data, template_path) -> str:
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
            BORROWER_NAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_name_input)],
            BORROWER_EMAIL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_email_input)],
            BORROWER_ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_address_input)],
            BORROWER_ACCOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_account_input)],
            BORROWER_BANK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_bank_input)],
            BORROWER_BIK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_bik_input)],
            BORROWER_CORR_ACCOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_corr_account_input)],
            BORROWER_INN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_inn_input)],
            BORROWER_KPP_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, borrower_kpp_input)],
            LENDER_NAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_name_input)],
            LENDER_EMAIL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_email_input)],
            LENDER_ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_address_input)],
            LENDER_ACCOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_account_input)],
            LENDER_BANK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_bank_input)],
            LENDER_BIK_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_bik_input)],
            LENDER_CORR_ACCOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_corr_account_input)],
            LENDER_INN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_inn_input)],
            LENDER_KPP_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_kpp_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()