import requests
from os import environ
import datetime



def get_weather(lat: float, lon: float):
    try:
        r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=RU&appid={environ["WEATHER"]}')
        data = r.json()
        return f'Погода: {data["weather"][0]["description"]}\n' \
        f'Сейчас температура: {data["main"]["temp"]}C°\n' \
        f'Скорость ветра: {data["wind"]["speed"]} м/с\n' \
        f'Влажность: {data["main"]["humidity"]}%\n' \
        f'Давление: {data["main"]["pressure"]} мм\n' \
        f'Восход: {datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S")}\n' \
        f'Закат: {datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")}'
    except Exception as err:
        return 'Ошибка: {err}'