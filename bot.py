import nest_asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters
from search_cafe import get_nearby_cafes
from search_hotel import get_nearby_hotels
from search_park import get_nearby_parks

# Применяем nest-asyncio для работы с уже существующим циклом событий
nest_asyncio.apply()

# Мой API токен для бота
API_TOKEN = "7496660100:AAHjiIEKB_kvfdEtNafVfefVtMP5UxoN3IE"

# Храним отправленные координаты мест
sent_locations = set()  # Множество для хранения уникальных мест (по координатам)


# Функция для команды /start
async def start(update: Update, context: CallbackContext):
    # Используем KeyboardButton для запроса местоположения
    button = KeyboardButton("Отправить местоположение", request_location=True)
    keyboard = [[button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Гав гав! Напиши 'Привет', и я помогу найти ближайшие места!",
                                    reply_markup=reply_markup)


# Функция для обработки текста (например, "Привет")
async def echo(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()  # Приводим к нижнему регистру для удобства

    if "привет" in user_message:
        # Запрос местоположения после приветствия
        button = KeyboardButton("Отправить местоположение", request_location=True)
        keyboard = [[button]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Гав гав! Отправь мне своё местоположение, и я подберу ближайшие места!",
                                        reply_markup=reply_markup)

    elif "спасибо" in user_message:
        # Завершение взаимодействия
        await update.message.reply_text("Пожалуйста! Если понадоблюсь, напиши снова! Пока!")

    else:
        await update.message.reply_text(f"Вы написали: {user_message}")


# Функция для обработки получения местоположения
async def location(update: Update, context: CallbackContext):
    user_location = update.message.location  # Получаем местоположение пользователя
    location = (user_location.latitude, user_location.longitude)

    # Отправляем кнопки для выбора
    keyboard = [
        [InlineKeyboardButton("Кушац!", callback_data='cafe')],
        [InlineKeyboardButton("Спац!", callback_data='hotel')],
        [InlineKeyboardButton("Гуляц!", callback_data='park')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите, что вам нужно:", reply_markup=reply_markup)

    # Сохраняем местоположение пользователя в контексте
    context.user_data["location"] = location


# Функция для обработки кнопок
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Получаем местоположение пользователя
    location = context.user_data.get("location")

    if not location:
        await query.edit_message_text(text="Пожалуйста, отправьте ваше местоположение сначала.")
        return

    # Функция для поиска с расширяющимся радиусом
    def find_places_within_radius(place_type, location):
        radius = 1000  # Начальный радиус 1 км
        if place_type == 'cafe':
            places = get_nearby_cafes(location, radius)
        elif place_type == 'hotel':
            places = get_nearby_hotels(location, radius)
        elif place_type == 'park':
            places = get_nearby_parks(location, radius)

        if not places:
            radius = 3000  # Расширяем до 3 км
            if place_type == 'cafe':
                places = get_nearby_cafes(location, radius)
            elif place_type == 'hotel':
                places = get_nearby_hotels(location, radius)
            elif place_type == 'park':
                places = get_nearby_parks(location, radius)

        if not places:
            radius = 5000  # Расширяем до 5 км
            if place_type == 'cafe':
                places = get_nearby_cafes(location, radius)
            elif place_type == 'hotel':
                places = get_nearby_hotels(location, radius)
            elif place_type == 'park':
                places = get_nearby_parks(location, radius)

        return places

    # Выводим уникальные локации
    places = find_places_within_radius(query.data, location)
    response = ""
    sent_count = 0

    for place in places:
        # Проверяем, что место содержит все необходимые данные
        if len(place) != 4:
            continue  # Пропускаем если данные неполные

        name, category, lat, lon = place  # Распаковываем данные

        # Если место уже было отправлено, пропускаем его
        if (lat, lon) in sent_locations:
            continue

        # Если место уникальное, отправляем его
        response += f"{category}: {name}\n"
        sent_locations.add((lat, lon))  # Добавляем в множество отправленных мест
        await query.message.reply_location(latitude=lat, longitude=lon)
        sent_count += 1

        if sent_count >= 3:  # Останавливаем, если отправили 3 места
            break

    # Если не было уникальных мест, сообщаем пользователю
    if sent_count == 0:
        response = "Извините, в этом радиусе не найдено подходящих мест."

    await query.edit_message_text(text=response)


async def main():
    # Создаем объект Application и передаем токен
    application = Application.builder().token(API_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))  # Обработчик для команды /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))  # Обработчик для текста
    application.add_handler(MessageHandler(filters.LOCATION, location))  # Обработчик для местоположения
    application.add_handler(CallbackQueryHandler(button))  # Обработчик для кнопок

    # Запускаем бота
    await application.run_polling()


# Запуск бота
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())  # Запуск через asyncio.run() с использованием nest-asyncio
