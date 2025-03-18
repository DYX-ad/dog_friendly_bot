from sqlalchemy import text
from database import SessionLocal  # Импортируем SessionLocal
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

# Состояния
USERNAME, PHONE_NUMBER = range(2)

# Функция для запроса username
async def ask_username(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите ваш username:")  # Запрашиваем username
    return USERNAME  # Возвращаем состояние USERNAME для продолжения процесса

# Функция для получения username и перехода к телефону
async def get_username(update: Update, context: CallbackContext):
    username = update.message.text  # Получаем введенный username
    context.user_data['username'] = username  # Сохраняем username в контексте

    # Запрашиваем номер телефона
    await update.message.reply_text("Введите ваш номер телефона:")
    return PHONE_NUMBER  # Переходим к следующему состоянию — PHONE_NUMBER

# Функция для получения phone_number и сохранения данных
async def get_phone_number(update: Update, context: CallbackContext):
    phone_number = update.message.text
    username = context.user_data['username']  # Получаем username из контекста

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
    await update.message.reply_text("Гав! Гав! До новых встреч!")
    return ConversationHandler.END  # Завершаем разговор после сохранения данных

# Функция для обработки кнопки "Получить PRO"
async def handle_pro(update: Update, context: CallbackContext):
    query = update.callback_query  # Получаем объект callback_query
    await query.answer()  # Обязательно отвечаем на callback_query

    # Используем query.message для ответа
    await query.message.reply_text("Введите ваш username.")

    # Переход к запросу username
    return await ask_username(update, context)  # Используем await для правильного ожидания
