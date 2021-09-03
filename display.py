from config import configWeather
from config import configSpotify
from datetime import datetime
import requests
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

def getDate():
    now = datetime.now()
    nowHour = now.strftime('%H:%M:%S')
    nowDate = now.strftime('%d/%m/%Y')
    data = {
        "nowHour":nowHour,
        "nowDate":nowDate
    }
    return data

def getWeather():
    link = 'https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&exclude=minutely&appid=%s&lang=pt_br&units=metric'% (configWeather['lat'],configWeather['long'],configWeather['key'])
    response = requests.get(link)
    json_resp = response.json()
    temp = json_resp['current']['temp']
    feels = json_resp['current']['feels_like']
    data = {
        "temp":temp,
        "feels":feels
    }
    return data

def getSpotify():
    link = "https://api.spotify.com/v1/me/player/currently-playing"
    token = configSpotify['key']
    response = requests.get(
        link,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    if response.status_code == 200:
        json_resp = response.json()
        artists = [artist for artist in json_resp['item']['artists']]
        artists_names = ', '.join([artist['name'] for artist in artists])
        music = json_resp['item']['name']
        playing = json_resp['is_playing']
        data = {
            "artists":artists_names,
            "music":music,
            "playing":playing
        }
        return data
    else:
        return False

def main():
    now = getDate()
    weather = getWeather()
    spotify = getSpotify()

if __name__ == '__main__':
    main()
    