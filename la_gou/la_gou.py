import re
import requests
import hashlib
from bs4 import BeautifulSoup


def password_md5(pwd):
    """
    :param pwd:
    :return: 把密码通过md5加密
    """
    assert not isinstance(pwd, int), (
        "密码不是数字"
    )
    v = "veenike"
    pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    ret = hashlib.md5(bytes(v + str(pwd) + v, encoding='utf-8')).hexdigest()
    return ret

print(password_md5("18518217651"))
def get_token():
    """
    :return:获取两个请求头
    """
    token = {}
    login_url = "https://passport.lagou.com/login/login.html"
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    }
    res = requests.get(
        url=login_url,
        headers=headers,
    )
    Forge_Token = re.findall(r"window.X_Anti_Forge_Token = '(.*)';", res.text)
    Forge_Code = re.findall(r"window.X_Anti_Forge_Code = '(.*)';", res.text)
    if Forge_Token:
        token["window.X_Anti_Forge_Token"] = Forge_Token[0]
    if Forge_Code:
        token["window.X_Anti_Forge_Code"] = Forge_Code[0]
    return token


def get_login_location():
    ret = requests.get(
        url='https://www.lagou.com/frontLogin.do',
        allow_redirects=False,
    )
    return ret.headers.get("Location")

# def get_dd():
#     ref = get_login_location()
#     ww = requests.get(
#         url=ref,
#         headers={
#             "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
#         }
#     )
#     c = ww.cookies.get_dict()
#     print(c)
#
# get_dd()

def contents(username, pwd):
    # r = requests.get(
    #     url="https://www.lagou.com"
    # )
    # cok = r.cookies.get_dict()
    # print(cok)
    pwd = password_md5(pwd)
    login_url = "https://passport.lagou.com/login/login.json"
    form_data = {
        "isValidate": 'true',
        "username": username,
        "password": pwd,
        "request_form_verifyCode": '',
        "submit": '',
    }
    header = {
        "Accept": 'application/json, text/javascript, */*; q=0.01',
        "Accept-Encoding": 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "Connection": 'keep-alive',
        "Content-Type": 'application/x-www-form-urlencoded; charset=UTF-8',
        "Host": 'passport.lagou.com',
        "Origin": "https://passport.lagou.com",
        "Content-Length": "111",
        "Referer": get_login_location(),
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        # "X-Requested-With": 'XMLHttpRequest',
    }
    token = get_token()
    header.update(token)
    ret = requests.post(
        url=login_url,
        data=form_data,
        headers=header,
    )
    return ret.text


def parser(text):
    soup = BeautifulSoup(text)


con = contents("18518217651", "18518217651")
print(con)

