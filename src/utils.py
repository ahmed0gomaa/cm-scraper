import json
import re

import requests
from bs4 import BeautifulSoup

s = None


def authenticate():
    global s
    s = requests.Session()

    params = {"login": None}
    headers = {"DNT": "1", "Sec-GPC": "1"}

    r = s.get("https://chessmood.com/", params=params, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    token = soup.select('form > input[name=_token]')[0].get('value')

    credentials = json.load(open('../credentials.json'))
    user = credentials['user']
    password = credentials['pass']
    data = {"_token": token, "email": user, "password": password, "remember": "1"}
    q = s.post("https://chessmood.com/login", data=data)

    nsoup = BeautifulSoup(q.content, 'html.parser')
    csrf_token = nsoup.select('meta[name=csrf-token]')[0].get('content')
    headers={"X-CSRF-TOKEN": csrf_token, "X-Requested-With": "XMLHttpRequest", "DNT": "1", "Sec-GPC": "1"}

    result = s.post("https://chessmood.com/check-user-auth", data={"_token": csrf_token}, headers=headers)
    print(result.content)
    return s



def get_courses():
    assert(s is not None)
    r = s.get('https://chessmood.com/courses')

    root_html = r.content
    BeautifulSoup(root_html, 'html.parser')
    soup = BeautifulSoup(root_html, 'html.parser')
    links = soup.head
    what = links.find_all('script')[5]

    js = json.loads(what.contents[0])
    links_list = js['itemListElement']
    links_posta = [entry['url'] for entry in links_list]
    return links_posta


def get_soup(url, headers=None):
    assert(s is not None)
    r = s.get(url, headers=headers)
    return BeautifulSoup(r.content, 'html.parser')


def monospace(line):
    line = line.strip()
    line = re.sub('\s+', ' ', line)
    line = re.sub('/', ' ', line)
    return line

