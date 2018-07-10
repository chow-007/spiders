import hashlib
import requests
import re

from bs4 import BeautifulSoup

session = requests.session()
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}


# 第一步：对密码进行md5双重加密
def password_md5(pwd):
    """
    :param pwd:
    :return: 把密码通过md5双重加密
    """
    assert not isinstance(pwd, int), (
        "密码不是数字"
    )
    v = "veenike"
    pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    ret = hashlib.md5(bytes(v + str(pwd) + v, encoding='utf-8')).hexdigest()
    return ret


# 第二步：访问登陆页,拿到X_Anti_Forge_Token，X_Anti_Forge_Code
def get_header_token():
    """
    1、请求url:https://passport.lagou.com/login/login.html
    2、请求方法:GET
    3、请求头:
       User-agent
    :return:注意：Anti和Anit区别
    """
    url = 'https://passport.lagou.com/login/login.html'
    temp = {}
    r1 = session.get(url=url, headers=header)

    temp["X-Anit-Forge-Token"] = re.findall("X_Anti_Forge_Token = '(.*?)'", r1.text, re.S)[0]
    temp["X-Anit-Forge-Code"] = re.findall("X_Anti_Forge_Code = '(.*?)'", r1.text, re.S)[0]
    return temp


# 第三步：登陆
def login(username, password):
    """
    1、请求url:https://passport.lagou.com/login/login.json
    2、请求方法:POST
    3、请求头:
       cookie
       User-agent
       Referer:https://passport.lagou.com/login/login.html
       X-Anit-Forge-Code:
       X-Anit-Forge-Token:
       X-Requested-With:XMLHttpRequest
    4、请求体：
        isValidate:true
        username:用户名
        password:加密之后的密码
        request_form_verifyCode:''
        submit:''
    :param username:
    :param password:
    :return:
    """
    url = 'https://passport.lagou.com/login/login.json'
    headers = {
        'Referer': 'https://passport.lagou.com/login/login.html',
        'X-Requested-With': 'XMLHttpRequest'
    }
    headers.update(header)
    head_token = get_header_token()
    headers.update(head_token)
    form_data = {
        "isValidate": True,
        'username': username,
        'password': password_md5(password),
        'request_form_verifyCode': '',
        'submit': ''
    }
    r2 = session.post(url=url, headers=headers, data=form_data)


# 第四步：授权
def auth():
    """
    1、请求url:https://passport.lagou.com/grantServiceTicket/grant.html
    2、请求方法:GET
    3、请求头:
        User-agent
        Referer:https://passport.lagou.com/login/login.html
    :return:
    """
    url = 'https://passport.lagou.com/grantServiceTicket/grant.html'
    headers = {
        'Referer': 'https://passport.lagou.com/login/login.html',
    }
    headers.update(header)
    r3 = session.get(url=url, headers=headers)


# 第五步：验证
def is_auth(username):
    url = 'https://www.lagou.com/resume/myresume.html'
    r4 = session.get(url=url, headers=header)
    # print(r4.text)
    return username in r4.text


def run(username, password):
    login(username, password)
    auth()
    return is_auth(username)


# def get_record():
#     page = 1
#     while True:
#         url = 'https://www.lagou.com/message/msglist.json'
#         form_data = {
#             "queryType": '',
#             "pageNo": page
#         }
#         ret = session.post(url=url, headers=header, data=form_data)
#         import json
#         data = json.loads(ret.text)
#         data_list = data.get('content').get('data').get('postMessageInfo').get('result')
#         if data_list:
#             for info in data_list:
#                 content_str = info.get('content')
#                 content = json.loads(content_str)
#                 companyName = content.get('companyName')
#                 createTimeStr = content.get('createTimeStr')
#                 positionName = content.get('positionName')
#                 msg.append(companyName + "|" + positionName + "|" + createTimeStr)
#             page += 1
#             break
#         else:
#             return


def get_record(num):
    pageNo = num
    url = 'https://www.lagou.com/mycenter/delivery.html'
    params = {
        "tag": '-1',
        "r": '',
        "pageNo": pageNo
    }
    r = session.get(url=url, headers=header, params=params)
    return r.text


msg = []


def parser():
    num = 1
    while True:
        text = get_record(num)
        soup = BeautifulSoup(text, 'html.parser')
        div_tag_list = soup.find_all(name='div', attrs={"class": 'd_item'})
        if div_tag_list:
            for div in div_tag_list:
                a_tag = div.find(name='a', attrs={"class": 'd_job_link'})
                title = a_tag.attrs.get('title')

                div_company = div.find(name='div', attrs={"class": 'd_company'})
                a_tag2 = div_company.find(name='a')
                companyName = a_tag2.attrs.get('title')

                time = div.find(name='span', attrs={"class": 'd_time'}).get_text()
                msg.append(companyName + " | " + title + " | " + time)

            num += 1
        else:
            return


def save_msg():
    with open('msg_record.txt', 'w', encoding='utf-8') as f:
        for i in msg:
            f.write(i + '\n')


username = "xxxxxx"
password = "******"
if not run(username, password):
    raise ValueError("登录不成功")

parser()
save_msg()
