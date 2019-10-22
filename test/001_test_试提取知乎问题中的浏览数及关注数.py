import requests
import configg
import faker
from lxml import etree


"""
    url: https://www.zhihu.com/question/303260259/answer/536752787


    关注数：//button[@type="button"]//strong[@class="NumberBoard-itemValue"]/text()


    浏览数：//div[@class="NumberBoard-item"]//strong[@class="NumberBoard-itemValue"]/text()
"""
# def get_ip

def main():
    headers = configg.headrs_other
    # print(headers)

    url = "https://www.zhihu.com/question/303260259/answer/536752787"


    # headers_com= faker.Factory().create("zh_CN").user_agent() # 获取云端的User_Agent
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"
    # }


    print(headers)
    html = requests.get(url = url, headers = headers, verify = False)
    htmls = html.text

    test_html = etree.HTML(htmls)

    test_text = test_html.xpath('//strong[@class="NumberBoard-itemValue"]/text()')

    print(test_text[0])
    print(type(test_text))





if __name__ == "__main__":
    main()
