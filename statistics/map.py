# coding: utf-8
import sqlite3
import numpy as np
from PIL import Image, ImageDraw
import matplotlib
import matplotlib.cm as cm

# левый верхний угол: 58.641435, 49.531718
# правый нижний угол: 58.543749, 49.732219
# x1 = 49.531718
# x2 = 49.732219
# y1 = 58.543749
# y2 = 58.641435
x1 = 49.4918632507324
x2 = 49.7948455810547
y1 = 58.5086219067302
y2 = 58.6868491270311

def coord_to_xy(lat, lon, w, h):
    x = (lon - x1) * w / (x2 - x1)
    y = (y2 - lat) * h / (y2 - y1)
    return (x, y)

def load_data():
    # загрузка данных из БД
    connection = sqlite3.connect('../avito.db')
    cursor = connection.cursor()
    cursor.execute('''
        select id, area, price, lat, lon
        from adverts
        where price > 100 and floor > 1''')
    data = np.array(cursor.fetchall()).astype(float)
    return data

def xy_from_coords(lat, lon):
    pass

if __name__ == '__main__':
    # загрузка данных из БД
    data = load_data()

    print('Загружено %d записей' % len(data))

    # image = Image.open('kirov.png')
    image = Image.open('map2_bw.png')

    draw = ImageDraw.Draw(image)
    size = 7
    min_square_price = 20000
    max_square_price = 60000

    for item in data:
        x, y = coord_to_xy(item[3], item[4], image.width, image.height)

        square_price = item[2] / item[1]
        val = (square_price - min_square_price) / (max_square_price - min_square_price)

        color = matplotlib.colors.rgb2hex(cm.rainbow(val))
        draw.ellipse((x-size,y-size,x+size,y+size), fill=color, outline=color)

    image.show()
    image.save('map.png')
