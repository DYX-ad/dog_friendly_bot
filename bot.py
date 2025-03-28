import logging
import re

from sqlalchemy import text
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext,
                          CallbackQueryHandler)

from database import SessionLocal
from overpass_api import get_nearby_places

from config import API_TOKEN

# Включаем логирование
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
USERNAME, PHONE_NUMBER = range(2)

CHOICE_END = 'end'
CHOICE_CAFE = 'cafe'


# Функция для команды /start
async def start(update: Update, context: CallbackContext):
    # Создаем клавиатуру с двумя кнопками
    keyboard = [
        [KeyboardButton("начать прогулку", request_location=True)],
        [KeyboardButton("стать членом стаи")],
        [KeyboardButton("покинуть стаю")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Отправляем сообщение с кнопками
    await update.message.reply_text("Гав! Гав!",
                                    reply_markup=reply_markup)

# Обработчик для текста (например, "Привет")
async def echo(update: Update, context: CallbackContext):
    user_message = update.message.text.lower()  # Приводим к нижнему регистру для удобства

    if "привет" in user_message:
        await update.message.reply_text("Гав тебе, человече! Используй /start , чтобы начать взаимодействие!")

    elif "спасибо" in user_message:
        await update.message.reply_text("Гав! Обращайся! Используй /start , чтобы вновь начать взаимодействие!")

    else:
        await update.message.reply_text(f"Гав! Не понимаю тебя! Попробуй /start ")


# Функция для обработки получения местоположения
async def location(update: Update, context: CallbackContext):
    user_location = update.message.location  # Получаем местоположение пользователя
    location = (user_location.latitude, user_location.longitude)


# Обработчик для кнопки "Зарегистрироваться"
async def register(update: Update, context: CallbackContext):
    await update.message.reply_text("Какая у тебя кличка?")
    return USERNAME  # Переходим в состояние GET_NAME


# Функция для получения username и перехода к телефону
async def get_username(update: Update, context: CallbackContext):
    username = update.message.text  # Получаем введенный username
    context.user_data['username'] = username  # Сохраняем username в контексте

    # Запрашиваем номер телефона
    await update.message.reply_text("А какой твой номер телефона?")
    return PHONE_NUMBER  # Переходим к следующему состоянию — PHONE_NUMBER

# Функция для получения phone_number и сохранения данных
async def get_phone_number(update: Update, context: CallbackContext):
    phone_number = update.message.text
    username = context.user_data['username']  # Получаем username из контекста

    # Проверка, что введен номер телефона, состоящий только из цифр
    if not re.match(r"^\d{10}$", phone_number):  # Проверяем, что номер состоит из 10 цифр
        await update.message.reply_text("Упс! Кажись ты ввел не 10 цифр как надо... Попробуй-ка еще раз!")
        return PHONE_NUMBER  # Повторный запрос номера телефона

    # Сохраняем данные в базу данных через SQL
    db = SessionLocal()  # Создаем сессию для работы с базой
    try:
        query = text("INSERT INTO users (username, phone_number) VALUES (:username, :phone_number)")
        db.execute(query, {"username": username, "phone_number": phone_number})
        db.commit()  # Подтверждаем изменения
        print(f"Пользователь {username} с номером {phone_number} был добавлен.")
    except Exception as e:
        db.rollback()
        await update.message.reply_text(f"Ошибка при сохранении данных: {e}")
        return ConversationHandler.END  # Завершаем диалог в случае ошибки

    # Завершаем сеанс
    await update.message.reply_text(f"Гав, {context.user_data['username']}! До новых встреч!")
    return ConversationHandler.END  # Завершаем разговор после сохранения данных


# Функция для удаления пользователя из базы данных
async def delete_user(update: Update, context: CallbackContext):
    # Запрашиваем номер телефона для удаления пользователя
    await update.message.reply_text("Введите ваш номер телефона, чтобы покинуть стаю:")
    return PHONE_NUMBER  # Переходим к следующему состоянию, запрос телефона

# Функция для получения номера телефона при покидании стаи
async def handle_delete_phone(update: Update, context: CallbackContext):
    phone_number = update.message.text.strip()  # Получаем номер телефона и убираем лишние пробелы

    # Проверка на правильность номера телефона
    if not re.match(r"^\d{10}$", phone_number):  # Проверяем, что номер состоит из 10 цифр
        await update.message.reply_text("Упс! Кажись ты ввел не 10 цифр как надо... Попробуй-ка еще раз!")
        return PHONE_NUMBER  # Повторный запрос номера телефона

    # Проверяем, есть ли пользователь с таким номером телефона
    db = SessionLocal()
    try:
        query = text("SELECT * FROM users WHERE phone_number = :phone_number")
        result = db.execute(query, {"phone_number": phone_number}).fetchone()

        if result:
            # Удаляем пользователя из базы данных по номеру телефона
            query = text("DELETE FROM users WHERE phone_number = :phone_number")
            db.execute(query, {"phone_number": phone_number})
            db.commit()

            # Очищаем данные пользователя из контекста
            context.user_data.clear()

            await update.message.reply_text(f"Ты покинул стаю. Надеюсь, до новых встреч!")

        else:
            await update.message.reply_text("Хитрец! Ты не был в стае!")

    except Exception as e:
        db.rollback()
        await update.message.reply_text(f"Ошибка при удалении данных: {e}")
        return ConversationHandler.END  # Завершаем диалог в случае ошибки

    return ConversationHandler.END  # Завершаем разговор после успешного удаления


# Обработчик для отмены регистрации
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Может в следующий раз!")
    context.user_data.clear()  # Очищаем данные пользователя
    return ConversationHandler.END  # Завершаем диалог


# Обработчик для получения локации
async def location(update: Update, context: CallbackContext):
    user_location = update.message.location
    await update.message.reply_text(f"Далеко ты забрался! Широта: {user_location.latitude}, Долгота: {user_location.longitude}")

    # Отправляем кнопки для выбора
    keyboard = [
        [InlineKeyboardButton("Кушать!", callback_data='cafe')],
        [InlineKeyboardButton("Отдыхать!", callback_data='hotel')],
        [InlineKeyboardButton("Игрушки и вкусняшками!", callback_data='petshop')]  # Новая кнопка для магазинов для животных
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что делаем?", reply_markup=reply_markup)

    # Сохраняем местоположение пользователя в контексте
    context.user_data["location"] = (user_location.latitude, user_location.longitude)





# Обработчик для inline-кнопок
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_location = context.user_data.get("location")

    # Получаем выбор пользователя
    choice = query.data

    if choice == CHOICE_END:  # Обработка кнопки "Спасибо"
        await query.edit_message_text(text="Гав! Гав! Пока!")
        return  # Завершаем обработку для кнопки "Спасибо"

    if not user_location:
        await query.edit_message_text(text="Пожалуйста, отправьте ваше местоположение сначала.")
        return

    # Получаем ближайшие места в зависимости от выбранной категории
    places = []  # Добавляем переменную для places, чтобы избежать UnboundLocalError

    if choice == 'cafe':
        places = get_nearby_places(user_location, "cafe")
        response = "Ммм, идем кушац! Ближайшие кафе:\n"
    elif choice == 'hotel':
        places = get_nearby_places(user_location, "hotel")
        response = "Ооо! Отдыхаем! Ближайшие отели:\n"
    elif choice == 'petshop':
        places = get_nearby_places(user_location, "petshop")
        response = "Ты купишь мне вкусную косточку и новый мячик? Ближайшие petshop-ы:\n"

    if not places:
        await query.edit_message_text(text="Чет ничего рядом нет")
    else:
        # Показываем ближайшие места
        for place, lat, lon in places:
            response += f"{place}: \n"
            await query.message.reply_location(latitude=lat, longitude=lon)

        # После того как локации выведены, добавляем кнопки
        keyboard = [
            [InlineKeyboardButton("Спасибо", callback_data=CHOICE_END)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Обновляем текст сообщения и добавляем кнопки
        await query.edit_message_text(text=response, reply_markup=reply_markup)





def main():
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(["стать членом стаи"]), register),
                      MessageHandler(filters.Text(["покинуть стаю"]), delete_user)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username),
                       MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_phone)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_number),
                           MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )





    application.add_handler(conv_handler)

    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(delete_user, pattern="^delete_user$"))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()