

import requests
from bs4 import BeautifulSoup
import re
import time
import random
import csv


class Login(object):
    def __init__(self):
        self.headers = {
            'Referer':'https://seekingalpha.com/account/login',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        }
        self.login_url = 'https://seekingalpha.com/account/login'
        self.post_url = 'https://seekingalpha.com/account/orthodox_login'
        self.logined_url = 'https://seekingalpha.com/symbol/KO/earnings/transcripts'
        self.session = requests.Session()

    def login(self, email, password):
        post_data = {
            'slugs[]':'en_US', 
            'rt':'5edf110be2fc4cecb32637fc421111e2', 
            'user[url_source]': 'https://seekingalpha.com/account/login',
            'user[location_source]': 'orthodox_login',
            'user[email]': email,
            'user[password]': password
            }
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        if response.status_code == 200:
            print(200)
    
        response = self.session.get(self.logined_url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content,'lxml')
            soup.find_all("a", "dashboard-article-link")
            b = soup.find_all('li','symbol_item')
            for li in b:
                div = li.find('div','symbol_article')
                a = div.find('a')
                title = re.match('.*?Transcript', a.string, re.I)
                if title:
                    #link_list.append('https://seekingalpha.com'+a.get('href'))
                    #date = a.next_sibling.contents[-2]
                    #website = 'https://seekingalpha.com'+ a.get('href')
                    print(1)

#if __name__=="__main__":
login = Login()
login.login(email='dongge.zhou@outlook.com', password='ZdgLh1218*')




def get_one(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
}
    html = requests.get(url, headers = headers)
    if html.status_code == 200:
        return html.content
    else: None   


#path = '193284-quiksilver-inc-f1q10-earnings-call-transcript.html'
#htmlfile = open(path, 'r', encoding='utf-8')
#htmlhandle = htmlfile.read()


# get a list of each transcript's website# 
url_main = ("https://seekingalpha.com/earnings/earnings-call-transcripts")
soup1 = BeautifulSoup(get_one(url_main),'lxml')
print(type(soup1))
soup1.find_all("a", "dashboard-article-link")
for a in soup1.find_all("a", "dashboard-article-link"):
    title = re.match('^.*?\sQ(\d)\s(\d{4}).*?Transcript$', a.string, re.S)
    if title:
        tic = a.parent.next_sibling.next_sibling.find('a').string
        Q = title.group(1)
        year = title.group(2)
        website = 'https://seekingalpha.com/'+ a.get('href')
        print(tic, Q, year, website)
        
    
        with open('all_company.csv','a') as csvfile:
            fieldnames=['tic','year','Q','website']
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writerow({'tic':tic, 'year':year, 'Q':Q, 'website':website})
    else: continue