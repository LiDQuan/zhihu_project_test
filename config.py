"""
    配置文件
    headers_list:请求头列表
    mysql_config:mysql本地连接配置
    mysql_in_id:获取id根据id插入数据库的sql语句
    mysql_update_id:根据id进行sql数据库更新其余字段的语句
    * mysql_out_sql:从数据库中获取数据的语句，可以根据获取数据的不同而自行修改
"""
import random
import pymysql
"""
    请求头列表，可以自行往里面添加请求头，以列表的形式
"""
headers_list = [
    # Opera
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"},
    {"User-Agent": "Opera/8.0 (Windows NT 5.1; U; en)"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50"},
    # chrome
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"},
    # maxthon浏览器
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36"},
    # UC浏览器
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36"},
]
# 这里的随机user-agent停用，改用Faker一个随机生成user-agent的库，但是faker太老了，不适用于知乎
headrs_other = random.choice(headers_list)




"""
   数据库连接信息
"""
conn = pymysql.connect(
    host = 'localhost',
    port = 3306,
    db = 'python4',
    user = 'root',
    passwd = '123456',
    charset = 'utf8'
)

conn_zhidao_formal_a = pymysql.connect(
    host = 'localhost',
    port = 3306,
    db = 'python4',
    user = 'root',
    passwd = '123456',
    charset = 'utf8'
)

test_items = {
    'id': '1115709898426009339',
    'answerer': '如果喜欢请深爱',
    'date_list': '2017-10-27',
    'questions': '南宁初级会计培训哪个好',
    'questions_add': '',
    'comment_best':'高顿的初级会计职称和会计实操都不错，一个是理论基础，一个是基本会计上岗技能！还有中级会计职称，注册会计师（cpa）以及ACCA！',
    'comment_common': ''
}


# 当连接错误数超过多少时重新ip池，修改该值,默认值200
upIPPORT_NUM = 200






#测试
if __name__ =="__main__":
    print(headrs_other)
