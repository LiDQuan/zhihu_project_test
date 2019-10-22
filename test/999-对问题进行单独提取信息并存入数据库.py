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
    print("提取api成功，将api放入队列")
    for temp in data_list:
        # print(temp[0] + "?limit=5&offset=0&include=content,comment_count,voteup_count")
        q_api_queue.put(temp[0])
        num_api += 1
    print("读取成功")
    print("目前队列中有：" + str(num_api))
    print("断开连接池中一条数据连接")
    conn.close()

class get_next_api_html(threading.Thread):
    def __init__(self, threadName, q_api_queue, all_q_api_queue):
        super(get_next_api_html, self).__init__()
        self.threadName = threadName
        self.q_api_queue = q_api_queue
        self.all_q_api_queue = all_q_api_queue

    def run(self):
        print("开启" + self.threadName + "号线程" )
        while not zero_parser_Exit:
            url_ss = self.q_api_queue.get(False)
            offset = 0
            html = self.requests_url(url_ss)
            while(offset <= html["paging"]["totals"]):
                url = url_ss + "?limit=5&offset="+ str(offset) +"&include=content,comment_count,voteup_count"
                self.parser(url)
                # 结束条件
                offset += 5
        print("结束" + self.threadName + "号线程" )

    # 根据api发送请求
    def requests_url(self, url):
        s = requests.session()
        s.keep_alive = False
        proxies = {"http://": str(self.get_proxy())}
        time.sleep(random.randint(1, 5))
        requests.packages.urllib3.disable_warnings()
        html_proto = requests.get(url, headers=config.config.headrs_other, verify=False, proxies=proxies, timeout=(3, 7))
        # print("响应码:" + str(html_proto.status_code) + "\t该url为\t" +url)
        html_proto.encoding = 'utf-8'
        html_text = html_proto.text
        html = json.loads(html_text)
        return html

    # 将url列表存入子api队列中
    def parser(self, url):
        self.all_q_api_queue.put(url)

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

    # 让程序休眠
    def sleep_time(self, start_time, end_time):
        time.sleep(random.randint(start_time, end_time))

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
            time.sleep(3)
            url = self.all_q_api_queue.get(False)
            self.parser(url)
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
        html_proto = requests.get(url, headers=config.config.headrs_other, verify=False, proxies=proxies, timeout=(3,7))
        if(html_proto.status_code != 200):
            self.parser(url)
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
        # self.switch = True

    def run(self):
        print("开启" + self.threadName + "号线程" )
        while not secount_parser_Exit:
            time.sleep(random.randint(2, 6))
            html = self.get_html_queue.get(False)
            time.sleep(random.randint(1, 2))
            self.parser(html)
        print("结束" + self.threadName + "号线程" )

    def parser(self, html):
        # print("zizizi进入解析界面")
        # print(html["data"])
        for temp in html["data"]:
            # print(temp)
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
            print(items)
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
            time.sleep(3)
            print(self.items_queue.qsize())
            items = self.items_queue.get(False)
            self.parser(items)
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

    # 爬虫翻页、网页解析、解析爬虫以及储存线程数，最好是2的倍数
    crwal_num = 64
    html_num = 24
    parser_num = 18
    save_num = 8        # 连接池只设置了10，这里设置8保证不会溢出
    # 线程列表
    zero_crwal = []
    first_crwal = []
    second_crwal = []
    pymsql_crwal = []

    # 一个个爬虫来，先开始的是翻页爬虫，并且将翻页后的url存入all_q_api_queue中
    get_q_api(q_api_queue)
    for i in range(1, crwal_num):
        zero_crwal.append("翻页爬虫" +str(i))

    zero_switch = []
    for threadName in zero_crwal:
        thread = get_next_api_html(threadName, q_api_queue, all_q_api_queue)
        thread.start()
        zero_switch.append(thread)

    # 等待队列为空，翻页线程退出循环
    while not q_api_queue.empty():
        pass

    print("q_api_queue为空")


    for thread in zero_switch:
        thread.join()
        print("翻页结束，开始进入页面解析")

    # 开始进入解析页面，即为，发送请求，并且解析成html页面
    for i in range(1, html_num):
        first_crwal.append("网页爬虫" + str(i))

    first_switch = []
    for threadName in first_crwal:
        thread = get_html(threadName, all_q_api_queue, get_html_queue, lock)
        thread.start()
        first_switch.append(thread)
    while not all_q_api_queue.empty():
        pass

    print("all_q_api_queue为空")

    global first_parser_Exit
    first_parser_Exit = True

    for thread in first_switch:
        thread.join()
        print("传输api(q_api_queue)队列为空---------------->结束")

    for i in range(1, parser_num):
        second_crwal.append("解析爬虫" + str(i))
    second_parser_switch = []
    for threadName in second_crwal:
        thread = parser_html(threadName, get_html_queue, items_queue)
        thread.start()
        second_parser_switch.append(thread)

    while not get_html_queue.empty():
        pass

    global secount_parser_Exit
    secount_parser_Exit = True

    for thread in second_parser_switch:
        thread.join()
        print("已经将所有items存入items_queue队列中(get_html_queue)")



    for i in range(1, save_num):
        pymsql_crwal.append("储存爬虫" +str(i))

    pymysql_list = []
    for threadName in pymsql_crwal:
        thread = pymysql_save(threadName, items_queue, lock2)
        thread.start()
        pymysql_list.append(thread)

    while not items_queue.empty():
        pass

    global three_parser_Exit
    three_parser_Exit = True

    for thread in pymysql_list:
        thread.join()
        print("储存结束")
    print("储存线程结束，程序结束")

if __name__ == "__main__":
    main()