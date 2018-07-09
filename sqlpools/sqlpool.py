import pymysql
from DBUtils.PooledDB import PooledDB

POOL = PooledDB(
    creator=pymysql,
    maxconnections=4,
    mincached=2,
    maxcached=4,
    maxshared=4,
    blocking=True,
    maxusage=None,
    ping=0,
    host='127.0.0.1',
    port=3306,
    user='root',
    password='123456',
    database='chainfor',
    charset='utf8',
)

