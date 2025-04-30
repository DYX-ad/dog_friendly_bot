from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Настроим строку подключения
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание объекта engine для взаимодействия с базой данных
engine = create_engine(DATABASE_URL, echo=True)

# Создание базового класса для моделей
Base = declarative_base()

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Модель для таблицы пользователей
class User(Base):
    __tablename__ = "users"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Первичный ключ
    username = Column(String, index=True)  # Столбец для username
    phone_number = Column(String)  # Столбец для номера телефона


# Создание всех таблиц в базе данных
def create_db():
    Base.metadata.create_all(bind=engine)

