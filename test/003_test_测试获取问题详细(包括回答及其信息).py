"""
    测试获取问题详细信息

    现遇到问题：无法进行翻页发送信息
"""

import requests
import threading
import time
import random
import json
import config.config
import db.PoolDB
from queue import Queue


# 读取并组合api进入队列
def get_q_api(q_api_queue):
    print("打开连接池，创建对象提取数据")
    conn = db.PoolDB.pool.connection()
    cursor = conn.cursor()
    num_api = 0
    sql = "select question_link_api from all_question_data"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    print("提取api成功，将api组合并且放入队列")
    for temp in data_list:
        q_api_queue.put(temp[0] + "?limit=20&offset=0&include=content,comment_count,voteup_count")
        num_api += 1
    print("读取成功")
    print("目前队列中有：" + str(num_api))
    print("断开连接池中一条数据连接")
    conn.close()


# def get_q_api_out(q_api_queue):
#     url = "https://www.zhihu.com/api/v4/questions/331301540/answers?limit=20&offset=0&include=content,comment_count,voteup_count"
#     q_api_queue.put(url)
#
class get_next_api_html(threading.Thread):
    def __init__(self, threadName, q_api_queue, all_q_api_queue):
        super(get_next_api_html, self).__init__()
        self.threadName = threadName
        self.q_api_queue = q_api_queue
        self.all_q_api_queue = all_q_api_queue
        self.url_list = []


    def run(self):
        print("开启" + self.threadName + "号线程" )

        # while not zero_parser_Exit:
        # try:
            # time.sleep(1)
        time.sleep(5)
        url_ss = self.q_api_queue.get(False)
        self.url_list.append(url_ss)
        # print("这里是还未进入循环的url_list：" + str(self.url_list))
        print("进入翻页parser")
        switch = True
        html = self.requests_url(url_ss)
        print("进入循环")
        while switch:
            FT = html["paging"]["is_end"]
            time.sleep(random.randint(2, 4))
            # print(FT)
            if FT == False:
                # print("此页爬取完成，开始爬取下一页，当前页数为:{0}".format(self.html_page))
                urls = html["paging"]["next"]
                html = self.requests_url(urls)
                # print("翻页成功，存入列表")
                self.url_list.append(urls)
            else:
                print("该页面无数据爬取结束！")
                # print(self.url_list)
                self.parser(self.url_list)
                # print(self.all_q_api_queue.qsize())
                switch = False
        print("结束" + self.threadName + "号线程" )

    # 根据api发送请求
    def requests_url(self, url):
        s = requests.session()
        s.keep_alive = False
        proxies = {"http://": str(self.get_proxy())}
        time.sleep(random.randint(3, 5))
        requests.packages.urllib3.disable_warnings()
        html_proto = requests.get(url, headers=config.config.headrs_other, verify=False, proxies=proxies, timeout=3)
        html_proto.encoding = 'utf-8'
        html_text = html_proto.text
        html = json.loads(html_text)
        return html

    def parser(self, url_list):
        self.all_q_api_queue.put(url_list)

    # 获取代理ip
    def get_proxy(self):
        items = {}
        response = requests.get("http://127.0.0.1:8000/?types=0&count=1&protocol=0").text
        protocol_list = json.loads(response)
        for i in protocol_list:
            items["ip"] = i[0]
            items["port"] = i[1]
        proxy = "http://" + str(items["ip"]) + ":" + str(items["port"])
        return proxy


class get_html(threading.Thread):
    def __init__(self, threadName, all_q_api_queue, get_html_queue, lock):
        super(get_html, self).__init__()
        self.threadName = threadName
        self.all_q_api_queue = all_q_api_queue
        self.get_html_queue = get_html_queue
        self.lock = lock

    def run(self):
        print("开启" + self.threadName + "号线程" )
        while not first_parser_Exit:
            try:
                time.sleep(3)
                # print("进入get_html页面")
                # print("this is all_q_api_queue.qsize：" + str(self.all_q_api_queue.qsize()) + "\t" + str(self.threadName))
                url_list = self.all_q_api_queue.get(False)
                # print("这个是在get_html线程中的url_list:" + url_list)
                for i in url_list:
                    self.parser(i)
            except:
                pass
        print("结束" + self.threadName + "号线程" )

    # 获取代理ip
    def get_proxy(self):
        items = {}
        response = requests.get("http://127.0.0.1:8000/?types=0&count=1&protocol=0").text
        protocol_list = json.loads(response)
        for i in protocol_list:
            items["ip"] = i[0]
            items["port"] = i[1]
        proxy = "http://" + str(items["ip"]) + ":" + str(items["port"])
        return proxy

    def parser(self, url):
        print("进入给api发送请求模块，并且返回json代码")
        proxies = {"http://": str(self.get_proxy())}
        time.sleep(random.randint(3, 5))
        requests.packages.urllib3.disable_warnings()
        html_proto = requests.get(url, headers=config.config.headrs_other, verify=False, proxies=proxies, timeout=3)
        html_proto.encoding = 'utf-8'
        html_text = html_proto.text
        html = json.loads(html_text)
        self.get_html_queue.put(html)
        self.lock.acquire()
        global num_
        num_ += 1
        print("已存入{0}条html数据".format(num_))
        self.lock.release()


class parser_html(threading.Thread):
    def __init__(self, threadName, get_html_queue, items_queue):
        super(parser_html, self).__init__()
        self.threadName = threadName
        self.get_html_queue = get_html_queue
        self.items_queue = items_queue
        self.html_page = 0
        self.switch = True


    def run(self):
        print("开启" + self.threadName + "号线程" )
        while not secount_parser_Exit:
            try:
                time.sleep(10)
                html = self.get_html_queue.get(False)
                time.sleep(random.randint(1, 2))
                self.parser(html)
            except:
                pass
        print("结束" + self.threadName + "号线程" )

    def parser(self, html):
        # print("zizizi进入解析界面")
        # print(html["data"])
        for temp in html["data"]:
            print(temp)
            items = {}
            time.sleep(random.randint(1,2))
            items["q_id"] = temp["question"]["id"]
            items["question_name"] = temp["question"]["title"]
            items["a_id"] = temp["id"]
            items["voteup_count"] = temp["voteup_count"]
            items["comment_count"] = temp["comment_count"]
            items["answer_count"] = html["paging"]["totals"]
            items["answer_content"] = temp["content"]
            items["question_link"] = "https://www.zhihu.com/question/" + str(temp["question"]["id"])
            items["author_name"] = temp["author"]["name"]
            items["author_healine"] = temp["author"]["headline"]
            items["author_url_token"] = temp["author"]["url_token"]
            # 测试
            # print(items)
            # print("将数据放入items")
            self.items_queue.put(items)
            # print("items数据成功")


class pymysql_save(threading.Thread):
    def __init__(self, threadName, items_queue, lock2):
        super(pymysql_save, self).__init__()
        self.threadName = threadName
        self.items_queue = items_queue
        self.lock2 = lock2
        # self.num_b = 0

    def run(self):
        print("开启" + self.threadName + "号线程" )
        while not three_parser_Exit:
            try:
            # print("ll")
                time.sleep(3)
                print(self.items_queue.qsize())
                items = self.items_queue.get(False)
                self.parser(items)
            except:
                pass
        print("结束" + self.threadName + "号线程" )


    def parser(self, items):
        print("进入存储函数")
        conn = db.PoolDB.pool.connection()
        cursor = conn.cursor()
        sql_select = "select count(*) from question_info where a_id = '%d' " % (int(items["a_id"]))
        sql_insert = """insert into question_info (q_id, question_name, a_id, voteup_count, comment_count, answer_count, answer_content, question_link, author_name, author_healine, author_url_token)
                     VALUE ('%d', '%s', '%d', '%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s')""" % (int(items["q_id"]), items["question_name"], int(items["a_id"]), int(items["voteup_count"]), int(items["comment_count"]),int(items["answer_count"]), items["answer_content"], items["question_link"], items["author_name"],items["author_healine"], items["author_url_token"])
        cursor.execute(sql_select)
        return_count = cursor.fetchall()
        if return_count[0][0] == 0:
            cursor.execute(sql_insert)
            conn.commit()
            self.lock2.acquire()
            print("数据插入成功")
            global num_b
            num_b += 1
            print("目前为止插入成功:{0}条".format(num_b))
            self.lock2.release()
        elif return_count[0][0] > 0:
            print(items["a_id"])
            print("该条数据，数据库中已存在，插入失败。。")
        conn.close()



zero_parser_Exit = False
first_parser_Exit = False
secount_parser_Exit = False
three_parser_Exit = False
# first_Exit = False
# second_Exit = False
# three_Exit = False
num_ = 0
num_b = 0
def main():

    # 创建锁
    lock = threading.Lock()
    lock2 = threading.Lock()

    # 创建所需队列
    q_api_queue = Queue()
    all_q_api_queue = Queue()
    get_html_queue = Queue()
    items_queue = Queue()
    # 从数据库中提取所需api并且放入队列
    get_q_api(q_api_queue)


    # 休息三秒
    print("休息三秒，三秒后开始发送请求并且解析")
    time.sleep(3)

    # 爬虫、网页、解析爬虫以及储存线程数，最好是2的倍数
    crwal_num = 6
    html_num = 6
    parser_num = 6
    save_num = 8        # 连接池只设置了10，这里设置8保证不会溢出
    # 线程列表
    first_crwal = []
    second_crwal = []
    zero_crwal = []
    pymsql_crwal = []

    for i in range(1, crwal_num):
        zero_crwal.append("翻页爬虫" +str(i))
    for i in range(1, html_num):
        first_crwal.append("网页爬虫" + str(i))
    for i in range(1, parser_num):
        second_crwal.append("解析爬虫" + str(i))
    for i in range(1, save_num):
        pymsql_crwal.append("储存线程" + str(i))



    zero_switch = []
    for threadName in zero_crwal:
        thread = get_next_api_html(threadName, q_api_queue, all_q_api_queue)
        thread.start()
        zero_switch.append(thread)


    first_switch = []
    for threadName in first_crwal:
        thread = get_html(threadName, all_q_api_queue, get_html_queue, lock)
        # time.sleep(3)
        thread.start()
        first_switch.append(thread)

    second_parser_switch = []
    for threadName in second_crwal:
        thread = parser_html(threadName, get_html_queue, items_queue)
        # time.sleep(3)
        thread.start()
        second_parser_switch.append(thread)


    # 第二种方法
    # 等待队列为空，采集线程退出循环
    while not q_api_queue.empty():
        pass

    print("q_api_queue为空")

    global zero_parser_Exit
    zero_parser_Exit = True

    for thread in zero_switch:
        thread.join()
        print("翻页结束，开始进入页面解析")


    while not all_q_api_queue.empty():
        pass

    print("all_q_api_queue为空")


    global first_parser_Exit
    first_parser_Exit = True

    for thread in first_switch:
        thread.join()
        print("传输api(q_api_queue)队列为空---------------->结束")



    while not get_html_queue.empty():
        pass

    global secount_parser_Exit
    secount_parser_Exit = True

    for thread in second_parser_switch:
        thread.join()
        print("已经将所有items存入items_queue队列中(get_html_queue)")

    a = pymysql_save("测试存储1", items_queue, lock2)
    a1 = pymysql_save("测试存储2", items_queue, lock2)
    a2 = pymysql_save("测试存储3", items_queue, lock2)
    a.start()
    a1.start()
    a2.start()


    pymysql_list = []
    for threadName in pymysql_list:
        thread = pymysql_save(threadName, items_queue, lock2)
        thread.start()
        pymsql_crwal.append(thread)


    while not items_queue.empty():
        pass

    global three_parser_Exit
    three_parser_Exit = True

    for thread in pymsql_crwal:
        thread.join()
        print("储存结束")
    print("储存线程结束，程序结束")


if __name__ == "__main__":
    # 打开数据库连接
    # conn = config.conn
    # cursor = conn.cursor()

    main()

    # 关闭数据库连接
    # cursor.close()
    # conn.close()