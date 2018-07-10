import json
import queue
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from requests.cookies import RequestsCookieJar

q = queue.Queue()


def get_cookies(user, password):
    """
    使用selenium模拟登陆,获取cookies
    :return: cookies
    """
    try:
        browser = webdriver.Chrome()
        browser.get("https://www.zhaopin.com/")
        # 返回旧版,不喜欢智联招聘的新版本
        input_tag = browser.find_element_by_class_name("return-to-old")
        input_tag.click()
        # reach_window = browser.current_window_handle  # 此行代码用来定位当前页面
        input_tag_user = browser.find_element_by_id("loginname")
        input_tag_user.send_keys(user)
        input_tag_pwd = browser.find_element_by_id("password")
        input_tag_pwd.send_keys(password)
        input_tag_pwd.submit()
        cookies = browser.get_cookies()
        browser.close()
        return cookies
    except Exception as e:
        print(e)


def write_cookies(user, password):
    """
    把cookies写入文件,调试的时候,不用每次都登陆一次
    :return:
    """
    cookies = get_cookies(user, password)
    with open('cookie.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(cookies))


def read_cookies():
    """
    去文件读取cookies
    :return:
    """
    with open('cookie.txt', 'r', encoding='utf-8') as f:
        temp = f.read()
    return json.loads(temp)


def get_web_text(num):
    """
    获取网页内容
    :param num: 页码
    :return: 网页text内容
    """
    jar = RequestsCookieJar()
    for cookie in read_cookies():
        jar.set(cookie['name'], cookie['value'])
    form_data = {
        "tab": 0,
        "type": 1,
        "pageNum": num,
    }
    ret = requests.post(
        url="https://i.zhaopin.com/PositionRecord/jobpostrecord/_JobPostHistory",
        cookies=jar,
        data=form_data
    )
    return ret.text


def parser():
    """
    companyName: 公司名称
    title: 职位
    addressMoney: 地址和薪资
    循环爬取网页,一直到爬不到,终止本函数
    爬取的信息,放到队列里面
    :return:
    """
    companyName = ''
    title = ''
    addressMoney = ''
    num = 1
    while True:
        text = get_web_text(num)
        soup = BeautifulSoup(text, 'html.parser')
        div_tags = soup.find_all(name='div', attrs={"class": 'Pad20'})
        print(len(div_tags))
        if len(div_tags) == 0:
            return
        for div in div_tags:
            h2_tag = div.find(name='h2')
            if h2_tag:
                a_tag = h2_tag.find(name='a')
                if a_tag:
                    companyName = a_tag.get_text()
            div_info = div.find(name='div', attrs={"class": "fb_company_list_left"})
            if div_info:
                a_tag_title = div_info.find(name='a')
                if a_tag_title:
                    title = a_tag_title.get_text()
                p_tag = div_info.find(name='p')
                if p_tag:
                    addressMoney = p_tag.get_text().strip()
            q.put(companyName + ' | ' + title + ' | ' + addressMoney+'\n')
        num += 1


def write_job_post_record():
    """
    从队列里面取出爬取的信息,写入文件
    :return:
    """
    with open('jobPostRecord.txt', 'w', encoding='utf-8') as f:
        while True:
            if q.empty():
                break
            f.write(q.get())


user = 'xxxx'
password = 'xxxx'
# write_cookies(user, password)
parser()
write_job_post_record()
