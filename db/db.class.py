"""
    数据库操作类
"""


import pymysql
from DBUtils.PooledDB import PooledDB
from config import config


class Db(object):
    def __init__(self, db_host, db_port, db_name, db_user, db_passwd, charset):
        self.conn = PooledDB(
            creator=pymysql,
            maxconnections=10,  # 连接池允许的最大连接数， 0和none表示没有限制
            mincached=2,  # 初始化时，连接池至少创建的空闲连接，0表示不创建
            maxcached=5,  # 连接池空闲的最多连接数，0和none表示不限制
            blocking=True,  # 连接池中如果没有可用共享连接后是否阻塞等待，True表示等待，反之则为报错弹出
            host= db_host,
            port=int(db_port),
            user= db_user,
            passwd= db_passwd,
            database= db_name,
            charset= charset
        ).connection()
        self.cursor = self.conn.cursor()

    # 新增数据
    def db_insert(self, tableName, dataDict):
        str_field = ""
        str_value = ""
        for filed,value in dataDict.items():
            str_field += "`" + filed + "`,"
            if (type(value) == type("kkk")):
                str_value += "'" + str(value) + "'" + ","
            elif(type(value) == type(123)):
                str_value += str(value) + ","
        sql = "INSERT INTO `"+ tableName +"`(" + str_field[:-1] + ")VALUE(" + str_value[:-1] + ")"
        self.cursor.execute(sql)
        self.conn.commit()
        get_rows = self.cursor.rowcount
        if get_rows == 1 :
            return True
        else:
            return False
        # print(str_value)

    # 更新数据
    def db_updata(self):
        pass;

    # 提取数据 return 元组
    def db_getdata(self, tableName, field):
        sql = "SELECT " + field + " FROM " + tableName;
        print(sql)
        self.cursor.execute(sql)
        data_tuple= self.cursor.fetchall()
        return data_tuple

    # 删除数据
    def db_deldata(self):
        pass;

    # 查询数据
    def db_selectdata(self):
        pass;

    # 回收数据库资源
    def __del__(self):
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    datadict = {
        "q_id": 283194995,
        "question_name": "毕业两年如何做自己的职业规划？",
        "focus_count": 112,
        "view_count": 44927,
        "question_link": "https://www.zhihu.com/question/283194995",
        "question_link_api": "https://www.zhihu.com/api/v4/questions/283194995/answers",
        "created_time": "2018-06-30 14:31:08"
    }
    db = Db('127.0.0.1', 3306, 'zhihu_get_data', 'root', '123456', 'utf8')
    print(db.db_insert("test_table", datadict))
    # tuple = db.db_getdata("all_question_data", "question_link_api")
