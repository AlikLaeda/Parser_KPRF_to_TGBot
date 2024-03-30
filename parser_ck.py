# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import time
import io

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

# парсим статью в ЦК КПРФ и ищем там ключевые слова из word_list
def search_lub_ck(url_st):
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
    main_text = soup.find("div", class_="content").text.lower()

# ищем в тексте каждое слово из word_list и возвращаем его
    found_in_list = False
    for search_word in word_list:
        if main_text.find(search_word)!=-1: found_in_list = True
    return found_in_list


# парсинг новых новостей с КПРФ kprf.ru
def update_news_ck():
# В news_dict.json сохранены все имеющиеся новости за последнее время
    with io.open("news_dict.json", encoding='utf-8') as file:
        news_dict = json.load(file)
    
# Удаляем из словаря новости старше 30 дней (примерно, без учёта часовых поясов)
    Older_news = []
    for One_news in news_dict:
#        if time.time() - time.mktime(time.strptime(One_news["article_date"], '%d.%m.%Y')) > 2592000:
        if time.time() - news_dict[One_news]["article_date"] > 2592000:
# Из словаря нельзя удалять записи, пока он в for'е, а то наступит неожиданный конец.
# Сохраняем удаляемые новасти в специальный список.
            Older_news.append(One_news)
# И только теперь удаляем.
    for One_news in Older_news:
        news_dict.pop(One_news)

# Словарь только для новых новостей 
    fresh_dict = {}

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    url= "https://kprf.ru/"
    
    try: 
        r = requests.get(url=url, headers=headers)
    except requests.exceptions.ConnectTimeout:
        return fresh_dict
    soup = BeautifulSoup(r.text, "lxml")
    
    try:
        announces_cards = soup.find("div", id="announcement").find_all("a")
    except Exception: 
        print(time.ctime(time.time()) + " - no announces")


    for announce in announces_cards:
        announce_link = announce.get("href")
        announce_id = announce_link[1:].split("/")[-1].split(".")[0]
        announce_link = url[:-1] + announce_link
        
# Если новости с таким ид ещё нет в словаре
        if announce_id in news_dict:
            continue
        else:
            announce_title = "Анонс: " + announce.previous_sibling.previous_sibling.previous_sibling.previous_sibling.text
            announce_date = time.time()
            announce_desc = announce.text
            announce_image = ""
# Добавляем анонс в словарь, чтобы в следующий раз его не обрабатывать                
            news_dict[announce_id] = {
                "article_date": announce_date,
                "article_title": announce_title,
                "article_desc": announce_desc,
                "article_link": announce_link,
                "article_image": announce_image
            }

# Записываем в словарь свежих новостей
            fresh_dict[announce_id] = {
                "article_date": announce_date,
                "article_title": announce_title,
                "article_desc": announce_desc,
                "article_link": announce_link,
                "article_image": announce_image
            }


# Избавляемся от тех мест супа, где есть тэги, одноименные новостным карточкам
    soup.find("div", id="announcement").decompose()
    soup.find("div", id="submenu").decompose()
    soup.find("div", class_="advbanners").decompose()

# Достаём карточки новостей и перебираем их
    articles_cards = soup.find_all("div", class_="item")
    for article in articles_cards:

# Достаём из карточки ID новости и ссылку на статью
        article_link = article.find("a").get("href")
        article_id = article_link[1:].split("/")[-1].split(".")[0]
        article_link = url[:-1] + article_link

        
# Если новости с таким ид ещё нет в словаре
        if article_id in news_dict:
            continue
        else:

# Достаём из карточки заголовок новости, дату и ссылку на картинку
            article_title = article.text.strip()
            article_date = time.time()
            article_image = url[:-1] + article.find("a").get("style").split("(")[1].split(")")[0]
            article_desc = article_title

# Добавляем новость в словарь, чтобы в следующий раз её не обрабатывать
            news_dict[article_id] = {
                "article_date": article_date,
                "article_title": article_title,
                "article_desc": article_desc,
                "article_link": article_link,
                "article_image": article_image
            }
    
# Вызываем функцию поиска ключевых слов внутри статьи
            if search_lub_ck(article_link):

# Записываем в словарь свежих новостей только те, что содержат хоть 1 слово
                fresh_dict[article_id] = {
                    "article_date": article_date,
                    "article_title": article_title,
                    "article_desc": article_desc,
                    "article_link": article_link,
                    "article_image": article_image
                }
                

# Сохраняем словарь всех новостей обратно в файл                
    with io.open("news_dict.json", "w", encoding='utf-8') as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)    

# Возвращаем словарь свежих новостей
    return fresh_dict

if __name__ == "__main__":
    print(update_news_ck())

