# -*- coding:utf-8 -*-
import re
import pymysql
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

def get_district_list():
    url = "http://newhouse.cd.fang.com/house/s/"
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
    url = "http://newhouse.cd.fang.com" + district['link']
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
    url = "http://newhouse.cd.fang.com" + block['link']
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
            total_count_text = soup.select_one('a#allUrl span').get_text()
            digit_pattern = re.compile(r'\d+')
            total_count = int(digit_pattern.search(total_count_text).group())
            if total_count == 0:
                yield None
            house_list = soup.select('div#newhouse_loupai_list ul li div div.nlc_details')
            for house in house_list:
                house_name = house.select_one('div.nlcd_name').get_text()
                house_address = house.select_one('div.address a')['title']
                house_price_text = house.select_one('div.nhouse_price span').get_text().encode('ISO-8859-1').decode(
                        requests.utils.get_encodings_from_content(html)[0])
                if house_price_text == '价格待定':
                    yield None
                else:
                    house_price = int(digit_pattern.search(house_price_text).group())
                    yield {
                        'name': house_name,
                        'address': house_address,
                        'price': house_price,
                        'district_name': block['district_name'],
                        'block_name': block['block_name']
                    }
        else:
            print("Can't got 200 when request URL")
    except RequestException:
        print("Request Failed")
        return None


def main():
    for dis in get_district_list():
        for block in get_block_list(dis):
            print(block)




if __name__ == '__main__':
    main()