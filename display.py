from config import configWeather,configSpotify
from datetime import datetime
import requests
import time

from PIL import Image,ImageDraw,ImageFont

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


def createDisplay():
    WIDTH = 128
    HEIGHT = 160
    SPEED_HZ = 4000000

    DC = 24
    RST = 25
    SPI_PORT = 0
    SPI_DEVIDE = 0

    disp = TFT.ST7735(
        DC,
        rst=RST,
        spi=SPI.SpiDev(
            SPI_PORT,
            SPI_DEVIDE,
            max_speed_hz=SPEED_HZ))
    
    disp.begin()
    return disp

def clearDisplay(disp):
    disp.clear((0,0,0))

def drawRotatedText(image,text,position,angle,font,fill=(255,255,255)):
    draw=ImageDraw.Draw(image)
    width,height = draw.textsize(text, font=font)
    textimage = Image.new('RGBA',(width,height),(0,0,0,0))
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0),text,font=font,fill=fill)
    rotated = textimage.rotate(angle,expand=1)
    image.paste(rotated,position,rotated)

def showDisplay(disp):
    clearDisplay(disp)
    font=ImageFont.truetype('fonts/Arial.ttf',20)
    drawRotatedText(disp.buffer,"TESTE2",(110,36),270,font,fill=(255,255,255))
    disp.display()

def showWeather(disp,weather):
    print(weather['temp'])
    clearDisplay(disp)
    font=ImageFont.truetype('fonts/Arial.ttf',15)
    drawRotatedText(disp.buffer,"Temperatura:",(115,30),270,font,fill=(255,255,255))
    font=ImageFont.truetype('fonts/Arial.ttf',30)
    drawRotatedText(disp.buffer,str(weather['temp'])+"°C",(60,30),270,font,fill=(255,255,255))
    disp.display()


def main():
    disp = createDisplay()
    # now = getDate()
    weather = getWeather()
    # spotify = getSpotify()
    showDisplay(disp)
    time.sleep(1)
    showWeather(disp,weather)
    # disp = createDisplay()
    # clearDisplay(disp)

if __name__ == '__main__':
    main()
    