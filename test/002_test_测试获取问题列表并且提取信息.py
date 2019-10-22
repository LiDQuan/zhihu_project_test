"""
    测试获取问题列表并且提取信息

"""
import os
import pymysql
import random
import requests
import json
import config.config
import time
from lxml import etree
import datetime


class get_questionList(object):
    # 初始化变量
    def __init__(self, keyword):
        self.keyword = keyword
        self.num_ = 0

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

    # 时间戳的转化
    def get_time(self, time):
        t = datetime.datetime.fromtimestamp(time)
        return t

    # 解析网页返回所需信息，问题id，问题标题，问题组合链接网址，问题的API组合，以及再次发送请求并且返回的浏览数以及关注数，提问时间
    def requests_parse(self, html):
        # items = {}
        # items["id"] = html["data"][0]["object"]
        # # items["question_name"] = html["data"][0]["object"]["title"]
        # print(items)

        for temp in html["data"]:
            if temp["type"] == "search_result":
                if temp["object"]["type"] == "answer":
                    url = "https://www.zhihu.com/question/" + str(temp["object"]["question"]["id"])
                    proxies = {"http://": str(self.get_proxy())}
                    time.sleep(2)
                    requests.packages.urllib3.disable_warnings()
                    get_html = requests.get(url, headers=config.config.headrs_other, verify=False, proxies=proxies).text
                    htmls = etree.HTML(get_html)
                    VF_count_list = htmls.xpath('//strong[@class="NumberBoard-itemValue"]/text()')
                    items = {}
                    items["q_id"] = temp["object"]["question"]["id"]
                    items["question_name"] = temp["object"]["question"]["name"]
                    items["question_name"] = str(items["question_name"]).replace("<em>", "").replace("</em>", "").replace("em", "").replace("\u003c", "")
                    items["focus_count"] = VF_count_list[0]
                    items["focus_count"] = str(items["focus_count"]).replace(",","")
                    items["view_count"] = VF_count_list[1]
                    items["view_count"] = str(items["view_count"]).replace(",", "")
                    items["question_link"] = "https://www.zhihu.com/question/" + str(temp["object"]["question"]["id"])
                    items["question_link_api"] = "https://www.zhihu.com/api/v4/questions/" + str(temp["object"]["question"]["id"]) + "/answers"
                    items["created_time"] = self.get_time(int(temp["object"]["created_time"]))
                    print(items["q_id"]+ "\t" + items["question_name"])
                    self.Save_items(items)

    # 根据api发送请求
    def requests_url(self, url):
        proxies = {"http://" : str(self.get_proxy())}
        time.sleep(random.randint(3,5))
        requests.packages.urllib3.disable_warnings()
        html_proto = requests.get(url, headers = config.config.headrs_other, verify = False, proxies = proxies, timeout = 3)
        html_proto.encoding = 'utf-8'
        html_text = html_proto.text
        html = json.loads(html_text)
        return html

    # 判断网页里面是否有内容
    def Judge_content(self, html):
        if html["paging"]["is_end"] == False:
            print("该页面有数据，送去解析！")
            return True
        elif html["paging"]["is_end"] == True:
            print("该页面无数据爬取结束！")
            return False

    # 把数据保存到数据库
    """
        可优化，一步到位，判断数据库中有无改该数据，如果有该数据则不插入，如果无则进行插入；
        无需使用下列中判断语句
    """
    def Save_items(self, items):
        """
            将items存入数据库
        """
        '''
            方法1
                缺点：会录入重复数据
        '''
        # try:
        #     cursors.execute(
        #         "insert into tmm_question(q_id, question_name, focus_count, view_count, question_link, question_link_api, created_time) VALUE ('%d', '%s', '%s', '%s', '%s', '%s', '%s')" % (
        #             int(items["q_id"]), items["question_name"], items["focus_count"], items["view_count"], items["question_link"], items["question_link_api"], items["created_time"])
        #     )
        #     print("数据插入成功!!!")
        #     self.num_ = self.num_ + 1
        #     print("目前为止插入成功:{0}条".format(self.num_))
        # except Exception as e:
        #     print("id重复，继续执行!!")
        # conn.commit()

        '''
            方法2：
                加入if判断，过程复杂
        '''
        sql_select = "select count(*) from all_question_data where q_id = '%d' " % (int(items["q_id"]))
        sql_insert = """insert into all_question_data(q_id, question_name, focus_count, view_count, question_link, question_link_api, created_time) 
                        VALUE ('%d', '%s', '%d', '%d', '%s', '%s', '%s')"""% (int(items["q_id"]), items["question_name"], int(items["focus_count"]), int(items["view_count"]), items["question_link"], items["question_link_api"], items["created_time"])
        cursors.execute(sql_select)
        return_count = cursors.fetchall()
        if return_count[0][0] == 0:
            cursors.execute(sql_insert)
            conn.commit()
            print("数据插入成功")
            self.num_ = self.num_ + 1
            print("目前为止插入成功:{0}条".format(self.num_))
        elif return_count[0][0] > 0:
            print("该条数据，数据库中已存在，插入失败。。")

    # 主函数
    def main(self):
        html_page = 0
        switch = True
        url ="http://www.zhihu.com/api/v4/search_v3?q=" + str(self.keyword) + "&offset=0&limit=20"
        # print(url)
        while(switch):
            html = self.requests_url(url)
            FT = self.Judge_content(html)
            if FT == True:
                self.requests_parse(html)
                print("此页爬取完成，开始爬取下一页，当前页数为:{0}".format(html_page))
                url = html["paging"]["next"]
                html_page += 20
                print(url)
            elif FT == False:
                print("该页面无数据爬取结束！")
                switch = False






if __name__ == "__main__":
    conn = config.config.conn
    cursors = conn.cursor()

    newdata = get_questionList("职业规划")
    newdata.main()
    # print(a)

    cursors.close()
    conn.close()