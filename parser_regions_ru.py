# 
# Модуль парсит новостной сайт regions.ru - вытаскивает 
# новости с первой страницы раздела "новости" заданного
# города.
#
# Новости сохраняются списком в json-файл, чтобы 
# не повторяться. Чтобы не пропускать новости надо 
# запускать модуль не реже раза в день.

import requests
from bs4 import BeautifulSoup
import json
import time

# Функция преобразует дату из строки со словами "Сегодня" и "Вчера"
# или вида ДД.ММ, 
# а ещё время вида ЧЧ:ММ 
# в дату-время в секундах с начала эпохи.
# Устанавливается год даже если сегодня январь, а новость декабрьская.
#
def str_to_time(time_str):
    # Записываем текущее время в секундах и вычитаем время от начала
    # суток, чтобы было время 00:00:00
    current_day = time.mktime(time.localtime())
    current_day -= time.localtime(current_day).tm_hour * 3600
    current_day -= time.localtime(current_day).tm_min * 60
    current_day -= time.localtime(current_day).tm_sec
#    curr_yday = (time.localtime().tm_yday - 1) * 86400

    # Если вместо даты стоят слова "Сегодня" или "Вчера" то
    # присваиваем секунды сего или вчерашнего дня.
    if time_str.count('Сегодня'):
        date = current_day
    elif time_str.count('Вчера'):
        date = current_day - 86400
#        date = time.strftime("%d.%m ", time.gmtime(current_day - 86400))

    # Если стоит дата, то высчитываем и присваиваем секунды дня года из
    # даты вида 'ДД.ММ' из начала строки. Пока без года.
    else:
        date = (time.strptime(time_str[:5], '%d.%m').tm_yday - 1) * 86400
#        time.mktime(time.strptime("2024", '%Y'))

        # Если сейчас январь, а статья декабрьская, то прибавляем секунды 
        # прошлого года.
        if (time_str[3:5] == '12') & (time.localtime(current_day).tm_mon == 1):
            current_year = time.localtime(current_day).tm_year
            date += time.mktime(time.strptime(str(current_year - 1), '%Y'))
            
        # А обычно прибавляем секунды этого года.
        else:
            current_year = time.localtime(current_day).tm_year
            date += time.mktime(time.strptime(str(current_year), '%Y'))

    # Время вида ЧЧ:ММ из конца строки пересчитываем в секунды и прибавляем.         
    date += (int(time_str[-5:-3]) * 3600) + (int(time_str[-2:]) * 60)
    return date
#    

# 86400 день
# год
# Основная функция модуля принимает string название города 
# латиницей, из адресной строки сайта. На выходе - dict 
# новостей с ключами из уникальных индетификаторов сайта
# и словарём:
# Дата и время.
# Название новости.
# Категория.
# Ссылка на статью.
# Ссылка на картинку.
# Текст статьи.
def parse_regions_ru(sity):
    url = "https://regions.ru/"+sity+"/news"
    response = requests.get(url)
    print(type(response))
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'lxml')
    soup.find('div', class_='zone-left').decompose()
    articles = soup.find_all("div", class_="story article")
    for art in articles:
        pass




if __name__ == "__main__":
#    parse_regions_ru("kotelniki")
    print(time.localtime(str_to_time("Сегодня в 00:03")))
    print(time.localtime(str_to_time("Вчера в 11:28")))
    print(time.localtime(str_to_time("19.02 в 23:40")))

    

    