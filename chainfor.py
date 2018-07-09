# ##
import json
import time
import queue
import requests

from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlpools.sql import SQLHelper
from concurrent.futures import ThreadPoolExecutor

q_urls = queue.Queue()


def get_article_urls():
    """
    :return: 获取所有的文章url
    """
    page = 1
    urls = []
    print("开始获取文章url...")
    while True:
        if page == 5:
            return urls
        form_data = {
            "categoryId": '',
            "pageNo": page,
            "device_type": '',
        }
        res = requests.post(
            url='https://www.chainfor.com/home/list/news/data.do',
            data=form_data,
        )

        news = json.loads(res.text)
        news_list = news.get("list")

        if news_list:
            for news in news_list:
                article_id = news.get('id')
                article_url = 'https://www.chainfor.com/news/show/{}.html'.format(article_id)
                q_urls.put(article_url)

                if article_url not in urls:
                    urls.append(article_url)
        else:
            print("获取所有文章url完成,进行下一步,获取文章详细...")
            return urls
        page += 1
    return urls


def get_article():
    # ret = requests.get(url='https://www.chainfor.com/news/show/23239.html')
    ret = requests.get(url=q_urls.get())
    return ret.text


def parser(text):
    soup = BeautifulSoup(text, "html.parser")

    title = soup.find(name='h1', attrs={"class": "m-i-title"}).text
    body = soup.find(name='div', attrs={"class": "m-i-bd"})
    p = body.children

    contents = ''
    for tag in p:
        if isinstance(tag, Tag):
            img = tag.find(name='img', )
            if img:
                img_src = img.attrs['src']  # 获取文章内的图片url, 图片占用空间太大,没有下载
                contents += img_src + '\n'
            tag_text = tag.text
            contents += tag_text + '\n'

    return title, contents


def write_url_db():
    start_time = time.time()
    art_urls = get_article_urls()

    sql_handle = SQLHelper()
    sql_handle.add_many('insert into urls(url) VALUES(%s)', art_urls)
    end_time = time.time() - start_time

    print("url耗时", end_time)


def write_article_db():
    ct = time.time()
    while True:
        if not q_urls.empty():

            text = get_article()
            art_res = parser(text)
            sql_handle = SQLHelper()
            sql_handle.add_one('insert into articles(title, content) VALUES(%s,%s)', art_res)

        else:
            break
    ent = time.time() - ct
    print("文章写入耗时", ent)


write_url_db()
print("队列大小:", q_urls.qsize())

# write_article_db()
# print("duiliedaxiao", q_urls.qsize())


t = ThreadPoolExecutor(20)
for i in range(1, 21):
    t.submit(write_article_db, )
