# coding: utf-8
# зависимость стоимости от площади для квартир, расположенных в центре города
import sqlite3
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import pyperclip

id=0
area=1
price=2
Lat=3
Lon=4
dis=5

accepted_streets = ['урицкого', 'красноармейская', 'володарского', 'свободы',
    'казанская', 'октябрьский', 'люксембург', 'либкнехта', 'труда', 'воровского',
    'маклина', 'горького', 'герцена', 'горбачева', 'маркса', 'дерендяева',
    'спасская', 'московская', 'преображенская', 'пятницкая', 'ленина', 'мопра']

def load_data():
    # загрузка данных из БД
    connection = sqlite3.connect('../avito.db')
    cursor = connection.cursor()
    cursor.execute('''
        select id, area, price, lat, lon, address
        from adverts
        where price > 0 and floor > 1''')
    data = np.array(cursor.fetchall())

    # фильтрация по интересующим улицам
    filtered_data = []
    for item in data:
        for street in accepted_streets:
            if street.lower() in item[5].lower():
                filtered_data.append(item)
                break

    data = np.array(filtered_data)[:, :5].astype(float)
    return data

def distance(A, B):
    return 1000 * np.sqrt(np.sum(np.power(A - B, 2)))


if __name__ == '__main__':
    # загрузка данных из БД
    data = load_data()

    # гистограмма цен за кв. метр
    square_price = data[:,2] / data[:,1]
    plt.hist(square_price, bins=50)
    plt.grid()
    plt.show()

    # столбец с расстоянием от центра города
    # center = np.array([58.600422, 49.651881])
    # dist = []
    # for item in data:
    #     lat = item[Lat]
    #     lon = item[Lon]
    #     d = distance(center, np.array([lat, lon]))
    #     dist.append(d)
    # dist = np.array(dist).reshape((-1, 1))
    # data = np.c_[data, dist]

    # фильтрация записей: отбрасываем квартиры с нулевой ценой
    # и расстоянием от центра более distance_threshold единиц
    # distance_threshold = 50
    # data = data[np.array(data[:, dis] <= distance_threshold), :]

    # построение точечного графика
    x = np.matrix(data[:, area]).reshape((-1, 1))
    y = np.matrix(data[:, price]).reshape((-1, 1))
    plt.plot(x, y, 'b.')

    # построение линейной модели
    model = linear_model.LinearRegression()
    model.fit(x, y)
    theta = [model.intercept_[0], model.coef_[0][0]]
    x_ = np.linspace(np.min(x), np.max(x), 100)
    h_x = theta[0] + x_ * theta[1]
    plt.plot(x_, h_x, 'r-')
    plt.show()

    # поиск квартир, максимально удалённых от гипотезы и меньшее неё
    # пробегаем по всем объявлениям
    # вносим в ids id объявления и расстояние от цены до гипотетической цены
    # сортируем по увеличению разности
    # выводим ссылки по id тех объявлений, которые первые в списке
    ids = []
    for item in data:
        h_x = theta[0] + item[area] * theta[1]
        dist = item[price] - h_x
        ids.append([item[id], dist])
    ids = np.array(ids)
    # ids = ids[np.argsort(ids[:,1])]
    ids = ids[(-ids[:,1]).argsort()]

    connection = sqlite3.connect('../avito.db')
    cursor = connection.cursor()

    # копирование в буфер обмена ссылки на страницу
    print('Обнаружено %d квартир с указанными параметрами' % len(ids))
    number = int(input('Перейти к объявлению № '))

    for item in ids[number:]:

        cursor.execute('select url, area, price, floor, address from adverts where id=%d' % item[0])
        data = cursor.fetchall()[0]
        
        # ссылка на квартиру - в буфер обмена
        pyperclip.copy(data[0])
        print('%03d. Площадь: %d, цена: %d, этаж: %d, адрес: %s' % (number, data[1], data[2], data[3], data[4]), end='')
        input('')

        number += 1
