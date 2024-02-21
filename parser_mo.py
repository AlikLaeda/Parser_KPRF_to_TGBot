# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json

from cleaner import news_remover

# список слов, если статья не содержит, хотя бы одного из них,
# то она не пройдёт дальше в результат поиска. В список старых 
# статей попадёт.
# Использовать только нижний регистр. 
# Случайное положительное срабатывание приемлемо.
word_list=[
    'люберц',
    'люберец',
    'люберч',
    'котельник',
    'котельнич',
    'дзержинск',
    'лыткарин',
    'томилин',
    'красков',
    'малаховк',
    'малаховск'
]

# функция использовалась один раз для первого парсинга
def get_first_news():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    url= "https://mkkprf.ru/"
    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    articles_cards = soup.find_all("div", class_="index-news")
    news_dict = {}
    for article in articles_cards:
        # print(article, "\n * \n")
        article_title = article.find("a").text
        article_link = article.find("a").get("href")
        article_id = article_link[1:].split("-")[0]
        article_link = url[:-1] + article_link
        article_date = article.find("span", class_="arg idate").text
        article_image = article.find("img").get("src")[2:-2]

        article.h3.decompose()
        article.p.decompose()
        article.find("div", class_="headinfo").decompose()
        article_desc = article.text

        news_dict[article_id] = {
            "article_date": article_date,
            "article_title": article_title,
            "article_desc": article_desc,
            "article_link": article_link,
            "article_image": article_image
        }
    with open("news_dict.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)


# парсим статью в МО КПРФ и поиск там ключевых слов из word_list
def search_lub_mo(url_st):
# 
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url=url_st, headers=headers)
    except:
        return True
    soup = BeautifulSoup(r.text, "lxml")

# достаём текст статьи и сразу переводим в нижний регистр
    main_text = soup.find("div", class_="maincont").text.lower()

# ищем в тексте каждое слово из word_list и возвращаем его
    found_in_list = False
    for search_word in word_list:
        if main_text.find(search_word)!=-1: found_in_list = True
    return found_in_list

#
# парсинг новых новостей с КПРФ МО mkkprf.ru
#

def update_news_mo():
# В news_dict.json сохранены все имеющиеся новости за последнее время
    with open("news_dict.json") as file:
        news_dict = json.load(file)

# Удаляем старые новости
    news_remover(news_dict=news_dict)

# Словарь только для новых новостей 
    fresh_dict = {}

# Делаем запрос, устанавливаем параметры запроса, делаем из этого суп
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    url= "https://mkkprf.ru/"
    try: 
        r = requests.get(url=url, headers=headers)
    except requests.exceptions.ConnectTimeout:
        return fresh_dict
    soup = BeautifulSoup(r.text, "lxml")

# Достаём карточки новостей и перебираем их
    articles_cards = soup.find_all("div", class_="index-news")
    for article in articles_cards:

# Достаём из карточки ID новости и ссылку на статью
        article_link = article.find("a").get("href")
        article_id = article_link[1:].split("-")[0]
        article_link = url[:-1] + article_link

        
# Если новости с таким ид ещё нет в словаре
        if article_id in news_dict:
            continue
        else:

# Достаём из карточки заголовок новости дату и ссылку на картинку            
            article_title = article.find("a").text
            article_date = article.find("span", class_="arg idate").text
            article_image = article.find("img").get("src")[2:-2]

# У краткого содержания нет спечального тэга, очищаем карточку 
# от лишних тэгов, чтобы добраться до текста
            article.h3.decompose()
            article.p.decompose()
            article.find("div", class_="headinfo").decompose()
            article_desc = article.text

# Добавляем новость в словарь, чбы в следующий раз её не обрабатывать
            news_dict[article_id] = {
                "article_date": article_date,
                "article_title": article_title,
                "article_desc": article_desc,
                "article_link": article_link,
                "article_image": article_image
            }
    
# Вызываем функцию поиска ключевых слов внутри статьи
            if search_lub_mo(article_link):

# Записываем в словарь свежих новостей только те, что содержат хоть 1 слово
                fresh_dict[article_id] = {
                    "article_date": article_date,
                    "article_title": article_title,
                    "article_desc": article_desc,
                    "article_link": article_link,
                    "article_image": article_image
                }

# Сохраняем словарь всех новостей обратно в файл                
    with open("news_dict.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)    

# Возвращаем словарь свежих новостей
    return fresh_dict

if __name__ == "__main__":
    print(update_news_mo())

