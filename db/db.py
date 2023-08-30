import sqlite3


class dbClient:

    def __init__(self, name):
        self.cur = None
        self.con = None
        self.name = name

    def new_db(self):
        script = """
                BEGIN;
                DROP TABLE IF EXISTS Orders;
                CREATE TABLE Orders (
                    id VARCHAR,
                    ticker VARCHAR,
                    type VARCHAR,
                    time TEXT,
                    quantity VARCHAR,
                    price REAL,
                    total REAL
                );
                PRIMARY KEY(id)
                COMMIT;
                """
        self.cur.executescript(script)

    def connect(self):
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

    def disconnect(self):
        self.con.close()

    def new_entry(self, order):
        self.cur.execute("INSERT INTO Orders VALUES(?, ?, ?, ?, ?, ?, ?)", order.id)
