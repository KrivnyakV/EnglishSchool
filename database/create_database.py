import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
#Подгружаем переменные окружения
load_dotenv()

# Подключение к серверу PostgreSQL с помощью psycopg2 DBAPI
engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

print(engine)


Base = declarative_base()
metadata = Base.metadata


# metadata.clear()

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer(), primary_key=True)
    title = Column(String(200), nullable=False)
    about = Column(Text(),  nullable=False)
    image = Column(Text(), nullable=True)
    date = Column(Text(), default=datetime.now, onupdate=datetime.now)


class Users(Base):
    __tablename__ = 'users'

    email = Column(String(30), nullable=False, primary_key=True)
    password = Column(String(150), nullable=False)
    Name = Column(String(20), nullable=False)
    Surname = Column(String(20), nullable=False)
    Patronymic = Column(String(20), nullable=False)
    Role = Column(String(20), nullable=False)
    ActiveCourse = Column(Text, nullable=True)
    AdminCourse = Column(Text, nullable=True)




class Directing(Base):

    __tablename__ ='directing'

    id = Column(Integer(), primary_key=True)
    title = Column(String(40), nullable=False)
    about = Column(Text(), nullable=False)
    image = Column(Text(), nullable=True)


class Courses(Base):

    __tablename__ ='Courses'

    id = Column(Integer(), primary_key=True)
    id_direction = Column(String(40), nullable=False)
    all = Column(Text(), nullable=False)



# #Создаём таблицы в базе данных если они не созданы
# metadata.create_all(engine)
#
# engine.connect()
