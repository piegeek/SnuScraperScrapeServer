import json
import requests
import sys
from threading import Thread
from copy import deepcopy
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

SITE_URL = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'

with open('Params.txt', 'r', encoding='utf-8') as f:
    params = json.loads(f.read())

def fetch(url, lecture_code):
    payload = deepcopy(params)
    
    payload['srchCond'] = '1'
    payload['srchSbjtCd'] = str(lecture_code)
    payload['workType'] = 'S'

    try:
        res = requests.post(url, data=payload, timeout=10)
        return res
    except requests.exceptions.RequestException as RequestException:
        return None

def parse(response, lecture_number):    
    soup = BeautifulSoup(response.content, 'html.parser')
    data = soup.findAll('td', { 'rowspan': True })

    find_data = []

    for i in range(len(data[1:])):
        if i % 15 == 14:            
            find_data.append(int(data[i].getText()))
    
    try: 
        return find_data[lecture_number - 1]
    except IndexError:
        return None


@app.route('/lectures/<lecture_code>/<lecture_number>', methods=['GET'])
def scrape(lecture_code, lecture_number):
    
    res = fetch(SITE_URL, str(lecture_code))
    if res == None:
        return jsonify(status=400, error_msg='강좌를 못 찾았습니다')
    
    updated_number = parse(res, int(lecture_number))
    if updated_number == None:
        return jsonify(status=400, error_msg='강좌를 못 찾았습니다')
    else:
        return jsonify(status=200, updated_number=updated_number)


if __name__ == "__main__":
    try:
        if sys.argv[1] == '-debug':
            app.run(debug=True)
    except IndexError:
        print('Run with gunicorn or with the "-debug" option.')