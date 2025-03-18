import nest_asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters, \
    ConversationHandler
from pro import handle_pro, get_username, get_phone_number  # Импортируем функции из pro.py
from overpass_api import get_nearby_places  # Импортируем функцию для поиска мест

# Применяем nest-asyncio для работы с уже существующим циклом событий
nest_asyncio.apply()

# Ваш API токен для бота
API_TOKEN = "7496660100:AAHjiIEKB_kvfdEtNafVfefVtMP5UxoN3IE"

# Состояния для ConversationHandler
USERNAME, PHONE_NUMBER = range(2)


# Функция для команды /start
async def start(update: Update, context: CallbackContext):
    button = KeyboardButton("Отправить местоположение", request_location=True)
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Гав! Гав! Где ты?", reply_markup=reply_markup)


# Обработчик для текста (например, "Привет")
async def echo(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()  # Приводим к нижнему регистру для удобства

    if "привет" in user_message:
        # Запрос местоположения после приветствия
        button = KeyboardButton("Отправить местоположение", request_location=True)
        keyboard = [[button]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Гав! Гав! Где ты? Отправь мне своё местоположение!", reply_markup=reply_markup)

    elif "спасибо" in user_message:
        # Завершение взаимодействия
        await update.message.reply_text("Гав! Гав! Пока!")

    else:
        await update.message.reply_text(f"Вы написали: {user_message}")


# Функция для обработки получения местоположения
async def location(update: Update, context: CallbackContext):
    user_location = update.message.location  # Получаем местоположение пользователя
    location = (user_location.latitude, user_location.longitude)

    # Отправляем кнопки для выбора
    keyboard = [
        [InlineKeyboardButton("Кушать!", callback_data='cafe')],
        [InlineKeyboardButton("Отдыхать!", callback_data='hotel')],
        [InlineKeyboardButton("За подарками!", callback_data='petshop')]  # Новая кнопка для магазинов для животных
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что делаем?", reply_markup=reply_markup)

    # Сохраняем местоположение пользователя в контексте
    context.user_data["location"] = location


# Функция для обработки кнопок
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    location = context.user_data.get("location")

    if query.data == 'end':  # Обработка кнопки "Спасибо"
        await query.edit_message_text(text="Гав! Гав! Пока!")
        return  # Завершаем обработку для кнопки "Спасибо"

    if not location:
        await query.edit_message_text(text="Пожалуйста, отправьте ваше местоположение сначала.")
        return

    # Получаем ближайшие места в зависимости от выбранной категории
    places = []  # Добавляем переменную для places, чтобы избежать UnboundLocalError

    if query.data == 'cafe':
        places = get_nearby_places(location, "cafe")
        response = "Ммм, идем кушац! Ближайшие кафе:\n"
    elif query.data == 'hotel':
        places = get_nearby_places(location, "hotel")
        response = "Ооо! Отдыхаем! Ближайшие отели:\n"
    elif query.data == 'petshop':
        places = get_nearby_places(location, "petshop")
        response = "Гав! Гав! Ближайшие питомники (магазины для животных):\n"

    if not places:
        await query.edit_message_text(text="Извините, в этом радиусе не найдено подходящих мест.")
    else:
        # Показываем ближайшие места
        for place, lat, lon in places:
            response += f"{place}: \n"
            await query.message.reply_location(latitude=lat, longitude=lon)

        # После того как локации выведены, добавляем кнопки
        keyboard = [
            [InlineKeyboardButton("Спасибо", callback_data='end')],
            [InlineKeyboardButton("Получить PRO", callback_data='get_pro')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Обновляем текст сообщения и добавляем кнопки
        await query.edit_message_text(text=response, reply_markup=reply_markup)

    # Обработка кнопки "Получить PRO"
    if query.data == 'get_pro':
        # Переход к запросу данных пользователя (username и phone_number)
        await handle_pro(update, context)


async def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(CallbackQueryHandler(button))

    # Добавляем ConversationHandler для обработки ввода username и phone_number
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],  # Ожидаем ввод username
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_number)],
            # Ожидаем ввод phone_number
        },
        fallbacks=[],
    )
    application.add_handler(conversation_handler)

    await application.run_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
