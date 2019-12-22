from lxml import html,etree
import requests
import sqlite3
from sqlite3 import Error
from urllib.parse import urljoin

#insert content into database
def insert_into_db(data):
    conn = sqlite3.connect('IMDb.db')
    print("Connection Established")
    cursorObj = conn.cursor()
    cursorObj.execute("CREATE TABLE IF NOT EXISTS MYMOVIE(SERIAL INTEGER PRIMARY KEY, NAME TEXT, YEAR INT,DURATION TEXT,RATINGS INT)")
    try:
        cursorObj.executemany("INSERT OR IGNORE INTO MYMOVIE(SERIAL,NAME,YEAR,DURATION,RATINGS) VALUES(?,?,?,?,?)",data)
    except Error:
        print(Error)
    conn.commit()
    conn.close()
    print("Connection Close")

navurl = "https://www.imdb.com/search/title/?genres=crime&groups=top_1000&sort=user_rating,desc&ref_=adv_prv"
global stack
stack = []
stack.append(navurl)
#navigation function works for navigation one page to another 
def nav(navurl,stack):
    n = 0
    while True:
        resp = requests.get(url=navurl,headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"})
        tree = html.fromstring(html=resp.content)
        nav_lst = tree.xpath("//div[@class='nav']/div[2]/a/text()")
        titles = ''.join(tree.xpath("//div[@class='nav']/div[2]/span/text()")[0].split(' ')[2].split(','))
        nav = []
        if (n + 1) == round(int(titles)/50):
            break
        for i in nav_lst:
            for j in i.split(" "):
                nav.append(j)
        for i in nav:
            if i == 'Next':
                try:
                    navurl = urljoin(base=navurl,url=tree.xpath("//div[@class='nav']/div[2]/a/@href")[1])
                    stack.append(navurl)
                    n = n + 1
                except IndexError:
                    navurl = urljoin(base=navurl,url=tree.xpath("//div[@class='nav']/div[2]/a/@href")[0])
                    stack.append(navurl)
                    n = n + 1

all_info = [] # each page information stores in this list

def get(lst_items):
    try:
        return lst_items.pop(0)
    except IndexError:
        return ' '

#scrape function scrapes the required info
def scrape(stack):
    for url in stack:    
        resp = requests.get(url=url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"})
        tree = html.fromstring(html=resp.content)
        lst = tree.xpath("//div[@class='lister-list']/div[contains(@class,'mode-advanced')]")
        for lstitems in lst:
            info = (
                 get(lstitems.xpath(".//div[3]/h3/span[1]/text()")).split('.')[0],
                 get(lstitems.xpath(".//div[3]/h3/a/text()")),
                 get(lstitems.xpath(".//div[3]/h3/span[2]/text()")),
                 get(lstitems.xpath(".//div[3]/p[1]/span[@class='runtime']/text()")),
                 get(lstitems.xpath(".//div[3]/div[1]/div[1]/strong/text()"))
            )
            all_info.append(info)

nav(navurl,stack)
scrape(stack)
insert_into_db(all_info)
# # https://www.imdb.com/search/title/?genres=drama&groups=top_250&sort=user_rating,desc&ref_=adv_prv