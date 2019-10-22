import db.PoolDB
import re

def get_data():
    """
        从数据库中提取数据
    :return:
    """
    # 定义正则开始过滤html标签
    pat = re.compile('<[^>]+>',re.S)
    num = 0
    conn = db.PoolDB.pool.connection()
    cursor = conn.cursor()
    sql = "SELECT a_id,answer_content FROM question_info"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    dict_list = []
    # 打印从数据库提取数据
    for i in data_list:
        data_dict = {}
        data_dict['key'] = i[0]
        data_dict['value'] = pat.sub('', i[1])
        dict_list.append(data_dict)
        # print(a)

    import time
    import random
    # 开始更新sql语句
    for i in dict_list:
        sql_update = "UPDATE question_info SET answer_content = '{0}' WHERE a_id = {1}".format(i['value'], i['key'])
        # print(sql_update)
        time.sleep(0.5)
        cursor.execute(sql_update)
        conn.commit()
        print("{0}号问题除杂成功".format(i['key']))


def main():
    get_data()


if __name__ == "__main__":
    main()