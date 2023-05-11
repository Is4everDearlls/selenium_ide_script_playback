import json
import os
import re
import winreg
from typing import Dict, List, Union
from zipfile import ZipFile
import jsonpath
import requests
import urllib3


def json_data_extract(data: Union[Dict, List], expression: str):
    data = jsonpath.jsonpath(data, expression)
    return data[0] if data and len(data) == 1 else data


def json_data_reader(json_file):
    with open(json_file, encoding='utf-8') as f:
        return json.load(f)


def get_chrome_version():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Google\\Chrome\\BLBeacon')
        value, t = winreg.QueryValueEx(key, 'version')
        return re.compile(r'^[1-9]\d*\.\d*.\d*').findall(value)[0]
    except WindowsError:
        raise RuntimeWarning('没有找到chrome浏览器注册表信息')


def get_chromedriver_version():
    chromedriver_version_info = os.popen('chromedriver --version').read()
    try:
        version_info = chromedriver_version_info.split(' ')[1]
        version_info = ".".join(version_info.split(".")[:-1])
        return version_info
    except KeyError and Exception:
        raise RuntimeWarning('没有找到可用的chromedriver，请检查执行环境')


def update_chromedriver_version():
    chrome_version = get_chrome_version()
    chromedriver_version = get_chromedriver_version()
    if chrome_version != chromedriver_version:
        base_url = 'https://npm.taobao.org/mirrors/chromedriver/'
        url = f"{base_url}LATEST_RELEASE_{chrome_version}"
        latest_version = requests.get(url).text
        download_url = f"{base_url}{latest_version}/chromedriver_win32.zip"
        file = requests.get(download_url)
        with open("chromedriver.zip", 'wb') as zip_file:
            zip_file.write(file.content)
        f = ZipFile("chromedriver.zip", 'r')
        for file in f.namelist():
            f.extract(file)
        f.close()
        os.remove('chromedriver.zip')
        os.remove('LICENSE.chromedriver')
    return True


def url_replace(address: str, environmental: str):
    if not address:
        return None
    key = urllib3.get_host(address)[1]
    if '.' in key:
        key = key.split('.')[0]
    if '-' in key:
        key = key.split('-')[0]
    return address.replace(key, environmental)
