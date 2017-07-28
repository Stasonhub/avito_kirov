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
