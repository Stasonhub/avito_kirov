import urllib.request
from bs4 import BeautifulSoup
import re
import time
import sqlite3
import random
from random import shuffle

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'


def sleep():
    time.sleep(random.randrange(100, 120) / 10)

def parse_page(url):
    request_ok = False
    while not request_ok:
        try:
            req = urllib.request.Request(url, data=None, headers={'User-Agent': user_agent})
            with urllib.request.urlopen(req) as response:
                web_page = response.read()
            request_ok = True
        except urllib.error.URLError as exception:
            print('Server exception. Wait for a time...')
            sleep()
    return BeautifulSoup(web_page, 'html.parser')

def tag_text(doc, selector, index=0):
    items = doc.select(selector)
    if len(items) > 0:
        return items[index].decode_contents().strip()
    return ''

def extract_by_regexp(regexp, string, default):
    result = re.findall(regexp, string)
    if len(result):
        return result[0]
    return default    

def feature(doc, type):
    tags = doc.select('ul li.item-params-list-item')
    features = {}
    for item in [tag.text.strip().split(': ') for tag in tags]:
        features[item[0]] = item[1]
    return features[type]

def create_db(db_name):
    with open('avito_sqlite_create.sql', 'r') as script:
        sql = script.read()
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.executescript(sql)
    conn.commit()
    return conn

def already_in_db(connection, url):
    cursor = connection.cursor()
    cursor.execute('''select count(*) from adverts where (url='%s')''' % url)
    count = int(cursor.fetchone()[0])
    return count > 0

def remove_old_adverts(parsed_links, connection):
    # писок ссылок из БД
    cursor = connection.cursor()
    cursor.execute('select url from adverts')
    db_links = cursor.fetchall()

    # устаревшие ссылки: есть в БД, но не было в ссылках при парсинге
    old_links = [item for item in db_links if item not in parsed_links]

    # удаление устаревших ссылок
    for url in old_links:
        cursor.execute('delete from adverts where url=\'%s\'' % url)
    connection.commit

def add_advert(connection, ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon):
    cursor = connection.cursor()
    cursor.execute('''
        insert into adverts (
            ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon)
        values(
            %d, %d, %.2f, %d, %d, %d, '%s', '%s', '%s', %.7f, %.7f)'''
        % (ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon))
    connection.commit()

avito_url = 'https://www.avito.ru/kirovskaya_oblast_kirov/kvartiry/'
postfix = ['sdam/na_dlitelnyy_srok', 'prodam/vtorichka', 'prodam/novostroyka']

choice = int(input('Выбор: сдам = 0, вторичка = 1, новостройка = 2: '))
db_name = postfix[choice].replace('/', '_') + '.db'

# подключение к БД
connection = create_db(db_name)

all_links = []

for page in range(1, 101):

    print('page %d' % page)

    doc = parse_page(avito_url + postfix[choice] + '?p=' + str(page))

    links = doc.select('a.item-description-title-link')
    shuffle(links)
    
    for link in links:
        url = 'https://www.avito.ru' + link.get('href')

        all_links.append(url)

        # если ссылка присутствует в БД, пропускаем её
        if (already_in_db(connection, url)):
            print('Ссылка уже присутствует в БД')
            continue

        # случайная задержка перед парсингом нового объявления
        time.sleep(random.random() * 5)

        doc = parse_page(url)
        
        # идентификатор объявления
        ad_id = tag_text(doc, 'div.title-info-metadata-item')
        ad_id = int(extract_by_regexp('\d+', ad_id, 0))

        # число комнат
        rooms = feature(doc, 'Количество комнат')
        rooms = int(extract_by_regexp('\d+', rooms, 1))

        # площадь
        area = feature(doc, 'Общая площадь')
        area = float(extract_by_regexp('\d+\.?\d*', area, 0.0))

        # этаж
        floor = feature(doc, 'Этаж')
        floor = int(extract_by_regexp('\d+', floor, 0))

        # этажей
        floors = feature(doc, 'Этажей в доме')
        floors = int(extract_by_regexp('\d+', floors, 0))

        # стоимость
        price = tag_text(doc, 'span.price-value-string.js-price-value-string')
        price = int(extract_by_regexp('[\d ]+', price.replace(' ', ''), '0'))
        
        # адрес
        address = tag_text(doc, 'span[itemprop="streetAddress"]')

        # комментарий
        comment = tag_text(doc, 'div.item-description-text p').replace('\'', '').replace('\"', '')

        # координаты
        map_tag = doc.select('div.b-search-map.expanded.item-map-wrapper.js-item-map-wrapper')[0]
        lat = float(extract_by_regexp('\d+\.?\d*', map_tag.get('data-map-lat'), 0))
        lon = float(extract_by_regexp('\d+\.?\d*', map_tag.get('data-map-lon'), 0))

        # занесение данных в БД
        add_advert(connection, ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon)

        print('Добавлено объявление ' + str(ad_id))

# удаление всех ссылок из БД, которые не встретились
# при парсинге - это устаревшие объявления
remove_old_adverts(all_links, connection)

print('Скрипт успешно завершён')
