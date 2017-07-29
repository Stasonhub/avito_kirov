# coding: utf-8
# поиск квартир в заданном квадрате
import sqlite3
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt
import pyperclip


def load_data_from_db(db_name):
    connection = sqlite3.connect('../' + db_name)
    cursor = connection.cursor()
    cursor.execute('''
        select id, area, price, lat, lon
        from adverts
        where price > 0 and price < 2000000 and floor > 1''')
    data = np.array(cursor.fetchall()).astype(float)
    return data


def filter_by_coordinates(data, left_top_coordinates, right_bottom_coordinates):
    return np.array([item for item in data if
        item[3] >= right_bottom_coordinates[0] and
        item[3] <= left_top_coordinates[0] and
        item[4] >= left_top_coordinates[1] and
        item[4] <= right_bottom_coordinates[1]])


Apartment = namedtuple(\
    'Apartment', ['area', 'floor', 'floors', 'price', 'address', 'url'])

def select_by_id(db_name, id):
    connection = sqlite3.connect('../' + db_name)
    cursor = connection.cursor()
    cursor.execute(\
        'select url, area, price, floor, floors, address\
        from adverts where id=%d' % id)

    data = cursor.fetchall()[0]
    apartment = Apartment(url=data[0], area=data[1], price=data[2],\
        floor=data[3], floors=data[4], address=data[5])
    
    return apartment


if __name__ == '__main__':

    postfix = ['sdam/na_dlitelnyy_srok', 'prodam/vtorichka', 'prodam/novostroyka']
    choice = int(input('Выбор: сдам = 0, вторичка = 1, новостройка = 2: '))
    db_name = postfix[choice].replace('/', '_') + '.db'

    data = load_data_from_db(db_name)
    print('Загружено квартир: %d' % len(data))

    # ввод координат интересующего квадрата
    left_top_coordinates =\
        np.array(input('Координаты левого верхнего угла: ').split(','), float)
    right_bottom_coordinates =\
        np.array(input('Координаты правого нижнего угла: ').split(','), float)

    # фильтрация по координатам
    data = filter_by_coordinates(\
        data, left_top_coordinates, right_bottom_coordinates)
    print('Квартир после фильтрации по координатам: %d' % len(data))

    # гистограмма стоимости за квадратный метр
    plt.hist(data[:,2] / data[:,1], bins=30)
    plt.grid()
    plt.show()

    # вычисление средней стоимости метра в указанном квадрате
    square_meter_mean = np.mean(data[:,2] / data[:,1])
    std = np.std(data[:,2] / data[:,1])
    print('Средняя стоимость кв. метра: %d руб.' % square_meter_mean)
    print('Диапазон цен за метр: %d - %d руб.'\
        % (round(square_meter_mean - std), round(square_meter_mean + std)))
    
    # список id квартир, отсортированных по удалённости от средней цены
    indexes = np.argsort(np.abs(square_meter_mean - data[:,2] / data[:,1]))
    ids = data[indexes,0]

    number = int(input('Перейти к объявлению №'))

    # вывод найденных квартир на экран
    for id in ids[number:]:

        apt = select_by_id(db_name, id)

        meter_price = apt.price / apt.area
        diff_percent = 100 * (meter_price / square_meter_mean - 1)

        print('%3d. Площадь: %d, цена: %d [%+.1f%%] (%.3f млн.), этаж: %d/%d, адрес: %s' %\
            (number, apt.area, meter_price, diff_percent, apt.price / 1000000,\
            apt.floor, apt.floors, apt.address), end='')
        
        # ссылка на квартиру - в буфер обмена
        pyperclip.copy(apt.url)
        input('')

        number += 1
