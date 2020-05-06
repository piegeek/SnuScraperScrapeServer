import json
import requests
import sys
from copy import deepcopy
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

SITE_URL = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'

with open('Params.txt', 'r', encoding='utf-8') as f:
    params = json.loads(f.read())

def get_data(url, lecture_code, lecture_number):
    max_page_num = (lecture_number // 10) + 1
    start = max_page_num - 2 if max_page_num > 2 else 1
    
    for i in range(start, max_page_num + 1):
        res = fetch(url, lecture_code, i)
        if res != None:
            found_data = parse(res, lecture_number)
            if found_data != None:
                return found_data
        else:
            break
    return None


def fetch(url, lecture_code, page_num):
    payload = deepcopy(params)

    payload['srchCond'] = '0'
    payload['srchSbjtCd'] = str(lecture_code)
    payload['workType'] = 'S'
    payload['pageNo'] = str(page_num)

    try:
        res = requests.post(url, data=payload, timeout=10)
        return res
    except requests.exceptions.RequestException as RequestException:
        return None

def parse(response, lecture_number):    
    soup = BeautifulSoup(response.content, 'html.parser')
    data = soup.findAll('td', { 'rowspan': True })

    for i in range(len(data[1:])):
        if i % 15 == 14:            
            if int(data[i - 6].getText()) == lecture_number:
                found_data = int(data[i].getText())
                return found_data
    return None

@app.route('/')
def main():
    return jsonify(status=200)

@app.route('/lectures/<lecture_code>/<lecture_number>', methods=['GET'])
def scrape(lecture_code, lecture_number):
    
    # res = fetch(SITE_URL, str(lecture_code), int(lecture_number))
    # if res == None:
    #     return jsonify(status=400, error_msg='강좌를 못 찾았습니다')
    
    # updated_number = parse(res, int(lecture_number))
    # if updated_number == None:
    #     return jsonify(status=400, error_msg='강좌를 못 찾았습니다')
    # else:
    #     return jsonify(status=200, updated_number=updated_number)

    updated_number = get_data(SITE_URL, str(lecture_code), int(lecture_number))
    if updated_number == None:
        return jsonify(status=400, error_msg='강좌를 못 찾았습니다')
    else:
        return jsonify(status=200, updated_number=updated_number)


if __name__ == "__main__":
    try:
        if sys.argv[1] == '--debug':
            app.run(debug=True)
    except IndexError:
        print('Run with gunicorn or with the "--debug" option.')