import sqlite3

create_db_query = '''
CREATE TABLE IF NOT EXISTS adverts (
    id integer PRIMARY KEY AUTOINCREMENT,
    ad_id integer,
    rooms integer,
    area real,
    floor integer,
    floors integer,
    price integer,
    address text,
    comment text,
    url text,
    lat real,
    lon real
);
'''

class avito_db:
    def __construct__(self):
        self.connection = sqlite3.connect('avito.db')
        cursor = self.connection.cursor()
        cursor.executescript(create_db_query)
        self.connection.commit()

    def has_advert(self, url):
        cursor = self.connection.cursor()
        cursor.execute('select count(*) from adverts where (url='%s')' % url)
        count = int(cursor.fetchone()[0])
        return count > 0

    def add_advert(self, ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon):
        cursor = self.connection.cursor()
        cursor.execute('''
            insert into adverts (
                ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon)
            values(
                %d, %d, %.2f, %d, %d, %d, '%s', '%s', '%s', %.7f, %.7f)'''
            % (ad_id, rooms, area, floor, floors, price, address, comment, url, lat, lon))
        self.connection.commit()

    def remove_old_adverts(self, parsed_links):
        # список ссылок из БД
        cursor = self.connection.cursor()
        cursor.execute('select url from adverts')
        db_links = cursor.fetchall()

        # устаревшие ссылки: есть в БД, но не было в ссылках при парсинге
        old_links = [item for item in db_links if item not in parsed_links]

        # удаление устаревших ссылок
        for url in old_links:
            cursor.execute('delete from adverts where url=\'%s\'' % url)
        self.connection.commit

