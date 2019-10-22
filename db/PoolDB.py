"""
    用于数据库连接池工具包
    作为块级代码
"""

import pymysql
from DBUtils.PooledDB import PooledDB


# 连接池对象一般只初始化一次，可以作为块级代码确保使用，即：

pool = PooledDB(
    creator = pymysql,
    maxconnections = 10, # 连接池允许的最大连接数， 0和none表示没有限制
    mincached = 2, # 初始化时，连接池至少创建的空闲连接，0表示不创建
    maxcached = 5, # 连接池空闲的最多连接数，0和none表示不限制
    blocking = True, # 连接池中如果没有可用共享连接后是否阻塞等待，True表示等待，反之则为报错弹出
    host = '127.0.0.1',
    port = 3306,
    user = 'root',
    passwd = '123456',
    database = 'zhihu_get_data',
    charset = 'utf8mb4'
)

