from asyncio import open_connection
from ctypes.wintypes import POINT
from pickle import GLOBAL
import sqlite3
from typing import Type
from unicodedata import name
from urllib.request import urlopen
import requests
import traceback
from telegram.ext import *
try:
    conn = sqlite3.connect('KURZONA.db', check_same_thread=False) 
    cursor = conn.cursor()
    print("Подключение")
    
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
    traceback.print_exc()
#finally:
#    if (conn):
#        conn.close()
#        print("Соединение с SQLite закрыто")
#это наша функция для получения адреса по координатам
def get_address_from_coords(coords):
    
    PARAMS = {
        "apikey": "token",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }

    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        global adress_str
        adress_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        return adress_str

    except Exception as e:
        return "I can't find the address\n\nPlease turn on the location and repeat"

# Старт бота
def start_command(update, context):
    name = update.message.chat.first_name
    update.message.reply_text("Привет, " + name)
    update.message.reply_text("Поделитесь фото")
    print('start_command ')


# Запрос фото и сохранинение
def image_handler(update, context):
    file = update.message.photo[3].file_id
    global photo
    obj = context.bot.get_file(file)
    photo = obj['file_id'] + ".jpg"
    update.message.reply_text("Изображение принято")
    update.message.reply_text('Скинь геопозицию\n'
                                '\n1. Нажми на "скрепку"\n'
                                '2. Ннажми на "Геопозиция"\n'
                                '3. Включи локацию на смартфоне\n'
                                '4. Подожди пока обработается и напишет приблитительную точность'
                                '5. Отправляй!')
    print(photo)
#Эта функция будет использоваться, если пользователь послал в бота любой текст


def text(update, context):
    coords = update.message.text
    adress_str = get_address_from_coords(coords)
    update.message.reply_text(adress_str)

#Эта функция будет использоваться, если пользователь послал локацию.
def location(update, context):
    message = update.message
    global current_position
    current_position = (message.location.longitude, message.location.latitude)
    q = message.location
    print( q)
    global coords
    coords = f"{current_position[0]},{current_position[1]}"
    print(current_position)
    print(coords)
    adress_str = get_address_from_coords(coords)
    

    update.message.reply_text(adress_str)
    update.message.reply_text('Нажми → /save ← , чтобы СОХНРАНИТЬ\n'
                            'Или\n'
                            'Отправь НОВОЕ ФОТО')
    print(adress_str)
    

def download (update, context):
    try:
        sqlite3.connect('KURZONA.db', check_same_thread=False) 
        cursor.execute("""INSERT INTO kurzona
                              (coords, adress, photo)
                              VALUES
                              (?, ?, ?)""", (str(coords),str(adress_str), (str([photo])),))
                              
        conn.commit()


        print("Запись успешно вставлена   в таблицу ")
     
        update.message.reply_text('Saved) \n'
            '\n Чтобы добавить новую крточку - ПРИШЛИ ФОТО')
       
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    #finally:
    #    if sqlite_connection:
    #        sqlite_connection.close()
    #        print("Соединение с SQLite закрыто"))
    
#Это основная функция, где запускается наш бот  
def main():
    print('начало')
    updater = Updater("token", use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start",  start_command))
    dispatcher.add_handler(CommandHandler("save", download  ))
    dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, text))  
    dispatcher.add_handler(MessageHandler(Filters.location, location))
    updater.start_polling()
    updater.idle()
    

main()
