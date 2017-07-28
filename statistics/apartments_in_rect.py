# coding: utf-8
# поиск квартир в заданном квадрате
import sqlite3
import numpy as np
import pyperclip

def load_data_from_db():
    connection = sqlite3.connect('../avito.db')
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


def select_by_id(id):
    connection = sqlite3.connect('../avito.db')
    cursor = connection.cursor()
    cursor.execute(\
        'select url, area, price, floor, floors, address\
        from adverts where id=%d' % id)
    return cursor.fetchall()[0]


if __name__ == '__main__':

    data = load_data_from_db()
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

        data = select_by_id(id)
        print('%3d. Площадь: %d, цена: %d (%d), этаж: %d/%d, адрес: %s' %\
            (number, data[1], data[2] / data[1],\
            data[2], data[3], data[4], data[5]), end='')
        
        # ссылка на квартиру - в буфер обмена
        pyperclip.copy(data[0])
        input('')

        number += 1
