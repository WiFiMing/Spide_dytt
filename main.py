#coding:utf-8
"""
爬取电影天堂页面下的最新电影（https://dytt8.net/html/gndy/dyzz/index.html）
"""
import requests
from lxml import etree
import re
from tqdm import tqdm
from random import randint
import time
# 导入自定义函数
from output import TXTwriter

class dytt:
    def __init__(self):
        # 设置默认的请求头方式
        User_Agents = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        ]
        random_agent = User_Agents[randint(0, len(User_Agents) - 1)]
        # 随机获取UA，否则会被服务器限制访问
        # 参考网址https://blog.csdn.net/ztf312/article/details/87919027
        self.headers = {
            'User-Agent': random_agent,
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://dytt8.net/',
            'Cookie': '37cs_user=37cs92449963518; UM_distinctid=171b0c35b10330-0df265d993b43e-b383f66-dbe48-171b0c35b11'\
                     '2dc; bz_finger=dfb8b8db51880fe7cb3c6fd4b23a2f8a; 37cs_pidx=3; 37cs_show=253%2C75%2C76; XLA_CI=0a'\
                     'a67cb3e94d242397be0ff14e49c727; CNZZDATA1260535040=518604271-1587804667-https%253A%252F%252Fcn.b'\
                     'ing.com%252F%7C1588143975; cscpvrich5041_fidx=3',
        }
        self.proxies = {"https": "http://127.0.0.1:27000", }

    def parse_url(self, url):
        # 将输入的url地址进行请求和转换为xpath可识别格式
        # response = requests.get(url, headers=self.headers, proxies=self.proxies)
        response = requests.get(url, headers=self.headers)
        response.encoding = 'gb2312'
        parser = etree.HTMLParser(encoding='gb2312')
        html = etree.HTML(response.content.decode('gb2312', errors='ignore'), parser=parser)  # 解码（gb2312，从网页可查知）为字符串
        # html = etree.HTML(response.content)  # 也可以不用解码，正常显示
        return html

    def get_page_num(self):
        # 获取总共页码数量
        ori_url = 'https://dytt8.net/html/gndy/dyzz/index.html'
        html = self.parse_url(ori_url)  # 转换为xpath可以解析的格式
        # print(etree.tostring(html, encoding='gb2312').decode('gbk'))
        # 使用//text()进行提取，其中含页数的内容位于列表中第二项
        result = html.xpath('//div[@class="co_content8"]/div//text()')[1]
        # 页数包含在字符串中，使用正则表达式提取
        page_num = re.match('.*?(\d+).*?', result).group(1)
        return int(page_num)

    def get_content_url(self):
        # 根据观察规律构造目录url，以便进一步提取各目录中电影url
        page_num = self.get_page_num()
        content_urls = []
        for per in range(1, page_num+1):  # 从1 - page_num
            content_url = 'https://dytt8.net/html/gndy/dyzz/list_23_' + str(per) + '.html'
            content_urls.append(content_url)

        return content_urls

    def input_page(self):
        # 输入开始页码（start_page）和结束页码（end_page）
        page_num = self.get_page_num()
        print('-'*100)
        print('2020年新片精品网页部分总共有 %d 页'%(page_num))

        # 输入起止页码（start_page, end_page）
        while True:
            # 输入起止页码，要求：1.整数； 2.开始页码数不大于（小于等于）结束页码数
            try:
                start_page = int(input('请输出开始页码：'))
                end_page = int(input('请输入结束页码：'))
            except ValueError:
                # 要求1：整数
                print('起止页码数字必须为整数，请重新输入：')
            else:
                # 要求2：开始页码小于等于结束页码，否则重新输入
                if start_page > end_page:
                    print('开始页码必须小于或等于结束页码，请重新输入：')
                else:
                    break  # 符合两个要求，结束循环

        return [start_page, end_page]

    def get_movie_url(self, start_page, end_page):
        # 电影url地址位于目录下的一个属性中，获取所有电影的url地址
        movie_urls = []
        print('准备提取第%d——%d目录页中的电影链接地址：'%(start_page, end_page))
        content_urls = self.get_content_url()[start_page-1:end_page]  # 目录页的url，可以进一步提取其中movie的url
        for per_url in tqdm(content_urls):
            selector = self.parse_url(per_url)
            content_movie_urls = selector.xpath('//a[@class="ulink"]/@href')  # 获取目录网页中的电影url
            for index in range(len(content_movie_urls)):
                # 添加域名，组成url
                content_movie_urls[index] = 'https://dytt8.net/' + content_movie_urls[index]
            movie_urls.extend(content_movie_urls)
            # 进行间隔停顿，防止请求过快
            time.sleep(2)  # 1~2s之间变化

        print('共获取到%d个电影链接地址'%(len(movie_urls)))
        return movie_urls

    def movie_info(self, per_url):
        # 获取电影信息，包括名称（title）、海报（poster_url）、类别（kind）、上映日期（release_date）、豆瓣评分（score）、导演（director）、主演（actors）
        # 其中主演部分人数较多，暂时只选取了第一个

        # 进行初始化，防止没有爬取到相关信息而报错
        title = ''
        poster_url = ''
        kind = ''
        release_date = ''
        score = ''
        director = ''
        actors = ''

        selector = self.parse_url(per_url)

        title = selector.xpath('//div[@class="title_all"]//h1/font/text()')[0]  # 电影名称
        poster_url = selector.xpath('//div[@id="Zoom"]//img/@src')[0]  # 电影海报url

        lists = selector.xpath('//div[@id="Zoom"]//text()')  # 爬取所有有关数据（上映时间、主演等）
        for info in lists:
            if '类　　别' in info:
                kind = info[6:].strip()
            elif '语　　言' in info:
                language = info[6:].strip()
            elif '上映日期' in info:
                release_date = info[6:].strip()
            elif '豆瓣评分' in info:
                score = info[6:].strip()
            elif '导　　演' in info:
                director = info[6:].strip()
            elif '主　　演' in info:
                actors = info[6:].strip()  # 主演较多，只添加了一个
            else:
                pass

        movie_info = {
            'title': title,
            'poster_url': poster_url,
            'kind': kind,
            'language': language,
            'release_date': release_date,
            'score': score,
            'director': director,
            'actors': actors,
        }

        return movie_info

    def start(self):
        print('-'*100)
        print('开始获取电影url地址信息')
        input_page = self.input_page() # 输入要提取的起止页码
        print('-'*100)
        movie_urls = self.get_movie_url(input_page[0], input_page[1])
        # movie_urls = ['https://dytt8.net//html/gndy/dyzz/20200423/59954.html']
        print('电影url地址获取完毕')

        print('-'*100)
        print('开始读取电影相关信息并写入txt文件')
        write = TXTwriter()
        for per_url in tqdm(movie_urls):
            movie_info = self.movie_info(per_url)
            write.write_out('电影.txt', movie_info)

            # 进行停顿，防止爬取过快
            time.sleep(2)

if __name__ == '__main__':
    spide = dytt()
    spide.start()