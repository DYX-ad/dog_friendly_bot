#Вынести функцию save_user_to_db в отдельный файл, чтобы избежать циклического импорта.

from sqlalchemy.orm import Session
from sqlalchemy import text

# Функция для сохранения данных пользователя в базу
def save_user_to_db(db: Session, username: str, phone_number: str):
    query = text("INSERT INTO users (username, phone_number) VALUES (:username, :phone_number)")
    db.execute(query, {"username": username, "phone_number": phone_number})
    db.commit()  # Подтверждаем изменения

