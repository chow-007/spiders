import pymysql

from .sqlpool import POOL


class SQLHelper(object):
    @staticmethod
    def open():
        conn = POOL.connection()
        cursor = conn.cursor()
        return conn, cursor

    @staticmethod
    def close(conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def fetch_one(cls, sql, args):
        conn, cursor = cls.open()
        cursor.execute(sql, args)
        obj = cursor.fetchone()
        cls.close(conn, cursor)
        return obj

    @classmethod
    def fetch_all(cls, sql, args):
        conn, cursor = cls.open()
        cursor.execute(sql, args)
        obj = cursor.fetchall()
        cls.close(conn, cursor)
        return obj

    @classmethod
    def add_one(cls, sql, args):
        """
        :param sql: "INSERT INTO USER1(name, age) VALUES (%s, %s);"
        :param args:username = "zhou",   age = 18
        :return:
        """
        conn, cursor = cls.open()
        cursor.execute(sql, args)
        conn.commit()
        cls.close(conn, cursor)

    @classmethod
    def add_many(cls, sql, args):
        """
        :param sql:"INSERT INTO USER1(name, age) VALUES (%s, %s);"
        :param args:[("zhou", 18), ("zhi", 20), ("long", 21)]
        :return:
        """
        conn, cursor = cls.open()
        cursor.executemany(sql, args)
        conn.commit()
        cls.close(conn, cursor)

