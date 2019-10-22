"""
    用于读取数据库中的数据
"""

import pymysql
import db.PoolDB

'''
    list : return api_list
'''
# 提取答案id存入列表并返回
def get_a_id():
    api_list = []
    print("打开连接池，创建对象提取数据")
    conn = db.PoolDB.pool.connection()
    cursor = conn.cursor()
    sql = "select question_link_api from all_question_data"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    print("提取api成功，将api组合并且放入列表并返回")
    for temp in data_list:
        api_list.append(temp[0] + "?limit=20&offset=0&include=content,comment_count,voteup_count")
    # print("读取成功")
    # print("目前列表中有：" + str(len(api_list)))
    # print("断开连接池中一条数据连接")
    conn.close()
    return api_list

def get_q_api(q_api_queue):
    print("打开连接池，创建对象提取数据")
    conn = db.PoolDB.pool.connection()
    cursor = conn.cursor()
    num_api = 0
    sql = "select question_link_api from all_question_data"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    print("提取api成功，将api放入队列")
    for temp in data_list:
        # print(temp[0] + "?limit=5&offset=0&include=content,comment_count,voteup_count")
        q_api_queue.put(temp[0])
        num_api += 1
    print("读取成功")
    print("目前队列中有：" + str(num_api))
    print("断开连接池中一条数据连接")
    conn.close()

if __name__ == "__main__":
    get_a_id()
    # a = get_a_id()
    # for i in a:
    #     print(a)