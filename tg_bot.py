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
from datetime import datetime
import datetime

# Определение состояний
DATE_INPUT, COST_INPUT, BORROWER_NAME_INPUT, LENDER_NAME_INPUT = range(4)
BORROWER_ACCOUNT_INPUT, BORROWER_BANK_INPUT, BORROWER_BIK_INPUT, BORROWER_CORR_ACCOUNT_INPUT, BORROWER_INN_INPUT, BORROWER_KPP_INPUT = range(4, 10)
BORROWER_EMAIL_INPUT, BORROWER_ADDRESS_INPUT = range(10, 12)  # Новые состояния для email и адреса
LENDER_ACCOUNT_INPUT, LENDER_BANK_INPUT, LENDER_BIK_INPUT, LENDER_CORR_ACCOUNT_INPUT, LENDER_INN_INPUT, LENDER_OGRN_INPUT, LENDER_KPP_INPUT = range(12, 19)
LENDER_EMAIL_INPUT, LENDER_ADDRESS_INPUT = range(19, 21)  # Новые состояния для email и адреса займодателя

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

def is_valid_date(date_string: str) -> bool:
    try:
        datetime.datetime.strptime(date_string, "%d.%m.%Y")
        return True
    except ValueError:
        return False

async def date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_input_text = update.message.text
    if not is_valid_date(date_input_text):
        await update.message.reply_text("❌ Неверный формат даты. Пожалуйста, введите дату в формате DD.MM.YYYY:")
        return DATE_INPUT  # Остаёмся в состоянии DATE_INPUT

    contract_data['date'] = date_input_text
    await update.message.reply_text("Укажите сумму договора (стоимость) в рублях:")
    return COST_INPUT
    
def is_valid_cost(cost_string: str) -> bool:
    return cost_string.isdigit()

async def cost_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cost_input_text = update.message.text
    if not is_valid_cost(cost_input_text):
        await update.message.reply_text("❌ Пожалуйста, введите корректное числовое значение для суммы договора (стоимость) в рублях:")
        return COST_INPUT  # Остаёмся в состоянии COST_INPUT

    contract_data['cost'] = cost_input_text
    await update.message.reply_text("Введите ФИО или наименование заемщика:")
    return BORROWER_NAME_INPUT  

def is_valid_name(name_string: str) -> bool:
    # Проверяем, что длина строки больше 1
    return len(name_string) > 1

async def borrower_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    borrower_name = update.message.text
    if not is_valid_name(borrower_name):
        await update.message.reply_text("❌ Пожалуйста, введите корректное имя или наименование заемщика (должно содержать более одного символа):")
        return BORROWER_NAME_INPUT  # Остаёмся в состоянии BORROWER_NAME_INPUT

    contract_data['borrower_name'] = borrower_name
    await update.message.reply_text("Введите email заемщика:")
    return BORROWER_EMAIL_INPUT  # Переход к вводу email заемщика

EMAIL_REGEX = r'^(([^<>()[$.,;:\s@"]+(\.[^<>()[$.,;:\s@"]+)*)|(".+"))@(([^<>()[$.,;:\s@"]+\.)+[^<>()[$.,;:\s@"]{2,})'

async def borrower_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text
    if not re.match(EMAIL_REGEX, email):
        await update.message.reply_text("❌ Пожалуйста, введите корректный email заемщика:")
        return BORROWER_EMAIL_INPUT  # Остаёмся в состоянии BORROWER_EMAIL_INPUT

    contract_data['borrower_email'] = email
    await update.message.reply_text("Введите адрес заемщика:")
    return BORROWER_ADDRESS_INPUT  # Переход к вводу адреса заемщика

async def borrower_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_address'] = update.message.text
    await update.message.reply_text("Введите номер счета заемщика:")
    return BORROWER_ACCOUNT_INPUT

def is_valid_account_number(account_string: str) -> bool:
    # Проверяем, что строка состоит только из цифр и длина равна 20
    return account_string.isdigit() and len(account_string) == 20

async def borrower_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    borrower_account = update.message.text
    if not is_valid_account_number(borrower_account):
        await update.message.reply_text("❌ Пожалуйста, введите корректный номер счета заемщика (должен содержать ровно 20 цифр):")
        return BORROWER_ACCOUNT_INPUT  # Остаёмся в состоянии BORROWER_ACCOUNT_INPUT
    
    contract_data['borrower_account'] = borrower_account
    await update.message.reply_text("Введите банк получателя заемщика:")
    return BORROWER_BANK_INPUT

def is_valid_bik(bik_string: str) -> bool:
    # Проверяем, что строка состоит только из цифр и длина равна 9
    return bik_string.isdigit() and len(bik_string) == 9

def is_valid_corr_account(corr_account_string: str) -> bool:
    # Проверяем, что строка состоит только из цифр и длина равна 20
    return corr_account_string.isdigit() and len(corr_account_string) == 20

async def borrower_bank_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['borrower_bank'] = update.message.text
    await update.message.reply_text("Введите БИК банка получателя заемщика:")
    return BORROWER_BIK_INPUT

async def borrower_bik_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    borrower_bik = update.message.text
    if not is_valid_bik(borrower_bik):
        await update.message.reply_text("❌ Пожалуйста, введите корректный БИК (должен содержать ровно 9 цифр):")
        return BORROWER_BIK_INPUT  # Остаёмся в состоянии BORROWER_BIK_INPUT

    contract_data['borrower_bik'] = borrower_bik
    await update.message.reply_text("Введите корреспондентский счет заемщика:")
    return BORROWER_CORR_ACCOUNT_INPUT

async def borrower_corr_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    corr_account = update.message.text
    if not is_valid_corr_account(corr_account):
        await update.message.reply_text("❌ Пожалуйста, введите корректный корреспондентский счет (должен содержать ровно 20 цифр):")
        return BORROWER_CORR_ACCOUNT_INPUT  # Остаёмся в состоянии BORROWER_CORR_ACCOUNT_INPUT

    contract_data['borrower_corr_account'] = corr_account
    await update.message.reply_text("Введите ИНН заемщика:")
    return BORROWER_INN_INPUT

INN_REGEX = r'^\d{10}$|^\d{12}$'

async def borrower_inn_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    inn = update.message.text
    if not re.match(INN_REGEX, inn):
        await update.message.reply_text("❌ Пожалуйста, введите корректный ИНН (10 или 12 цифр):")
        return BORROWER_INN_INPUT  # Остаёмся в состоянии BORROWER_INN_INPUT

    contract_data['borrower_inn'] = inn
    await update.message.reply_text("Введите КПП заемщика:")
    return BORROWER_KPP_INPUT

async def borrower_kpp_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    kpp = update.message.text
    
    # Проверка на длину и содержание только цифр
    if len(kpp) != 9 or not kpp.isdigit():
        await update.message.reply_text("❌ Пожалуйста, введите корректный КПП (должен содержать 9 цифр):")
        return BORROWER_KPP_INPUT  # Остаёмся в состоянии BORROWER_KPP_INPUT

    contract_data['borrower_kpp'] = kpp
    await update.message.reply_text("Введите ФИО или наименование займодателя:")
    return LENDER_NAME_INPUT

def is_valid_name(name_string: str) -> bool:
    # Проверяем, что длина строки больше 1
    return len(name_string) > 1

async def lender_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lender_name = update.message.text
    if not is_valid_name(lender_name):
        await update.message.reply_text("❌ Пожалуйста, введите корректное имя или наименование займодателя (должно содержать более одного символа):")
        return LENDER_NAME_INPUT  # Остаёмся в состоянии LENDER_NAME_INPUT

    contract_data['lender_name'] = lender_name
    await update.message.reply_text("Введите email займодателя:")
    return LENDER_EMAIL_INPUT  # Переход к вводу email займодателя

async def lender_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text
    if not re.match(EMAIL_REGEX, email):
        await update.message.reply_text("❌ Пожалуйста, введите корректный email займодателя:")
        return LENDER_EMAIL_INPUT  # Остаёмся в состоянии LENDER_EMAIL_INPUT

    contract_data['lender_email'] = email
    await update.message.reply_text("Введите адрес займодателя:")
    return LENDER_ADDRESS_INPUT  # Переход к вводу адреса займодателя

async def lender_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_address'] = update.message.text
    await update.message.reply_text("Введите номер счета займодателя:")
    return LENDER_ACCOUNT_INPUT

def is_valid_account_number(account_string: str) -> bool:
    # Проверяем, что строка состоит только из цифр и длина равна 20
    return account_string.isdigit() and len(account_string) == 20

async def lender_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lender_account = update.message.text
    if not is_valid_account_number(lender_account):
        await update.message.reply_text("❌ Пожалуйста, введите корректный номер счета займодателя (должен содержать ровно 20 цифр):")
        return LENDER_ACCOUNT_INPUT  # Остаёмся в состоянии LENDER_ACCOUNT_INPUT

    contract_data['lender_account'] = lender_account
    await update.message.reply_text("Введите банк получателя займодателя:")
    return LENDER_BANK_INPUT

async def lender_bank_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_bank'] = update.message.text
    await update.message.reply_text("Введите БИК банка получателя займодателя:")
    return LENDER_BIK_INPUT

def is_valid_bik(bik_string: str) -> bool:
    # Проверяем, что строка состоит только из цифр и длина равна 9
    return bik_string.isdigit() and len(bik_string) == 9

async def lender_bank_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contract_data['lender_bank'] = update.message.text
    await update.message.reply_text("Введите БИК банка получателя займодателя:")
    return LENDER_BIK_INPUT

async def lender_bik_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lender_bik = update.message.text
    if not is_valid_bik(lender_bik):
        await update.message.reply_text("❌ Пожалуйста, введите корректный БИК (должен содержать ровно 9 цифр):")
        return LENDER_BIK_INPUT  # Остаёмся в состоянии LENDER_BIK_INPUT

    contract_data['lender_bik'] = lender_bik
    await update.message.reply_text("Введите корреспондентский счет займодателя:")
    return LENDER_CORR_ACCOUNT_INPUT

def is_valid_ogrn(ogrn_string: str) -> bool:
    # Проверяем, что строка состоит только из цифр и длина равна 13 или 15
    return ogrn_string.isdigit() and (len(ogrn_string) == 13 or len(ogrn_string) == 15)

async def lender_corr_account_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    corr_account = update.message.text
    if not is_valid_corr_account(corr_account):
        await update.message.reply_text("❌ Пожалуйста, введите корректный корреспондентский счет (должен содержать ровно 20 цифр):")
        return LENDER_CORR_ACCOUNT_INPUT  # Остаёмся в состоянии LENDER_CORR_ACCOUNT_INPUT

    contract_data['lender_corr_account'] = corr_account
    await update.message.reply_text("Введите ИНН займодателя:")
    return LENDER_INN_INPUT  # Переход к вводу ИНН

async def lender_inn_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    inn = update.message.text
    if not re.match(INN_REGEX, inn):
        await update.message.reply_text("❌ Пожалуйста, введите корректный ИНН (10 или 12 цифр):")
        return LENDER_INN_INPUT  # Остаёмся в состоянии LENDER_INN_INPUT

    contract_data['lender_inn'] = inn
    await update.message.reply_text("Введите ОГРН займодателя:")
    return LENDER_OGRN_INPUT  # Переход к вводу ОГРН

async def lender_ogrn_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ogrn = update.message.text
    
    # Получаем длину ИНН
    inn_length = len(contract_data.get('lender_inn', ''))
    
    # Условная проверка длины ОГРН
    if (inn_length == 10 and len(ogrn) != 13) or (inn_length == 12 and len(ogrn) != 15):
        await update.message.reply_text("❌ Для ЮЛ ОГРН должна содержать 13 цифр, Для ИП ОГРНИП должен содержать 15 цифр.")
        return LENDER_OGRN_INPUT  # Остаёмся в состоянии LENDER_OGRN_INPUT

    if not is_valid_ogrn(ogrn):
        await update.message.reply_text("❌ Пожалуйста, введите корректный ОГРН (должен содержать 13 или 15 цифр):")
        return LENDER_OGRN_INPUT  # Остаёмся в состоянии LENDER_OGRN_INPUT

    contract_data['lender_ogrn'] = ogrn
    await update.message.reply_text("Введите КПП займодателя:")
    return LENDER_KPP_INPUT  # Переход к вводу КПП

async def lender_kpp_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    kpp = update.message.text
    
    # Проверка на длину и содержание только цифр
    if len(kpp) != 9 or not kpp.isdigit():
        await update.message.reply_text("❌ Пожалуйста, введите корректный КПП (должен содержать 9 цифр):")
        return LENDER_KPP_INPUT  # Остаёмся в состоянии LENDER_KPP_INPUT

    contract_data['lender_kpp'] = kpp
    await update.message.reply_text("Спасибо! Ваши данные успешно сохранены. Ожидайте формирования документа")

    # Определяем путь к шаблону в зависимости от типа займа
    if 'percent' in contract_data and contract_data['percent'] == 'yes':
        template_path = r"C:\Users\User\Desktop\hse\template.docx"
    else:
        template_path = r"C:\Users\User\Desktop\hse\template_no_proc.docx"
    
    doc_path = generate_contract(contract_data, template_path)
    with open(doc_path, 'rb') as doc_file:
        await update.message.reply_document(doc_file)
    await update.message.reply_text("Ваш договор успешно создан!", reply_markup=None)
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
            LENDER_OGRN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lender_ogrn_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()