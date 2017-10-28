# -*- coding:utf-8 -*-
from config import *
import re
import pymysql
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


URL = BJ_URL

db = pymysql.connect(host="localhost",user="testuser01",password="test123",db="house_price", charset='utf8mb4')
cursor = db.cursor()

def get_district_list():
    url = URL + "/house/s/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            districts = soup.select('li#quyu_name a')
            districts.pop(0)
            for district in districts:
                yield {
                    'link': district['href'],
                    'name': district.get_text().encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(html)[0])
                }
        else:
            print("Can't got 200 when request URL")
    except RequestException:
        print("Request Failed")
        return None


def get_block_list(district):
    url = URL + district['link']
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            blocks = soup.select('div.quyu ol li a')
            for block in blocks:
                yield {
                    'link': block['href'],
                    'block_name': block.get_text().encode('ISO-8859-1').decode(requests.utils.get_encodings_from_content(html)[0]),
                    'district_name': district['name']
                }
        else:
            print("Can't got 200 when request URL")
    except RequestException:
        print("Request Failed")
        return None


def get_house_list_of_block(block):
    url = URL + block['link']
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            total_count_text = soup.select_one('a#allUrl span').get_text()
            digit_pattern = re.compile(r'\d+')
            total_count = int(digit_pattern.search(total_count_text).group())
            if total_count == 0:
                yield None
            else:
                if total_count > 20:
                    house_list = soup.select('div#newhouse_loupai_list ul li div div.nlc_details')
                    page_count = (total_count // 20) + 1
                    page_range = range(2, page_count)
                    for page_index in page_range:
                        url_page = url + '/b9%d' % page_index
                        response = requests.get(url_page, headers=headers)
                        if response.status_code == 200:
                            html = response.text
                            soup_page = BeautifulSoup(html, 'lxml')
                            house_list += soup_page.select('div#newhouse_loupai_list ul li div div.nlc_details')
                        else:
                            print("Got page %d data failed! " % page_index)
                else:
                        house_list = soup.select('div#newhouse_loupai_list ul li div div.nlc_details')
                for house in house_list:
                    key_pattern = re.compile(r'(?<=http://)\w+(?=\.fang)')
                    house_key = key_pattern.search(house.select_one('div.nlcd_name a')['href']).group()
                    try:
                        house_name = house.select_one('div.nlcd_name a').get_text().encode(response.encoding).decode(
                            requests.utils.get_encodings_from_content(html)[0]).strip()
                    except:
                        house_name = "生僻字，名字获取失败！"
                    try:
                        house_address = house.select_one('div.address a')['title'].encode(response.encoding).decode(
                            requests.utils.get_encodings_from_content(html)[0])
                        patter_loc = re.compile(r'(?<=\[).+(?=\])')
                        if patter_loc.search(house_address):
                            location = patter_loc.search(house_address).group()
                        else:
                            location = '-'
                    except:
                        house_address = "生僻字，地址获取失败！"
                    if house.select_one('div.nhouse_price span'):
                        house_price_text = house.select_one('div.nhouse_price span').get_text().encode(response.encoding).decode(requests.utils.get_encodings_from_content(html)[0])
                        if house_price_text == '价格待定':
                            house_price = 0
                        else:
                            house_price_unit_text = house.select_one('div.nhouse_price em').get_text()
                            if house_price_unit_text == 'ÍòÔª/Ì×Æð':
                                house_price = -int(digit_pattern.search(house_price_text).group())
                            else:
                                house_price = int(digit_pattern.search(house_price_text).group())
                        yield {
                            'house_key': house_key,
                            'name': house_name,
                            'address': house_address,
                            'price': house_price,
                            'district_name': block['district_name'],
                            'block_name': block['block_name'],
                            'location': location
                        }
                    else:
                        yield None
        else:
            print("Can't got 200 when request URL")
    except RequestException:
        print("Request Failed")
        return None


def store_house_price_data_in_db(house):
    sel_sql = "SELECT * FROM bj_new_house_price \
       WHERE house_key =  \"%s\"" % (house['house_key'])
    try:
        # 执行sql语句
        cursor.execute(sel_sql)
        # 执行sql语句
        result = cursor.fetchall()
    except:
        print("Failed to fetch data")

    if result.__len__() == 0:
        sql = "INSERT INTO bj_new_house_price \
                    (house_key, name, district_name, block_name, address, price, location) \
                 VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %d, \"%s\")" % \
              (house['house_key'], house['name'], house['district_name'], house['block_name'], house['address'], house['price'], house['location'])

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            db.commit()
            print("House data of {0} ADDED to DB table new_house_price!".format(house['house_key']))
        except pymysql.DatabaseError:
            # 发生错误时回滚
            print(Exception)
            db.rollback()
    else:
        print("This house {0} ALREADY EXISTED!!!".format(house['house_key']))


def main():
    try:
        for dis in get_district_list():
            if dis:
                for block in get_block_list(dis):
                    if block:
                        for house in get_house_list_of_block(block):
                            if house:
                                print(house)
                                store_house_price_data_in_db(house)
            else:
                print("This distric is empty!")
    finally:
        db.close()


if __name__ == '__main__':
    main()