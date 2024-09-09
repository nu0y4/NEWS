# https://uifs.sina.cn/api/flow?_ukey=i-interface-wap_api-layout_col&showcid=56260&col=56262&level=1%2C2&show_num=100&page=2&act=more&jsoncallback=callbackFunction&_=1719411573327
import json

import requests


def extract_titles(data):
    titles = []
    try:
        result = data.get('result', {})
        status = result.get('status', {})
        if status.get('code') == 0 and status.get('msg') == "success":
            data_list = result.get('data', {}).get('list', [])
            for item in data_list:
                title = item.get('title')
                if title:
                    titles.append(title)
    except Exception as e:
        print(f"Error occurred: {e}")
    return titles


data = requests.get(
    'https://uifs.sina.cn/api/flow?_ukey=i-interface-wap_api-layout_col&showcid=56260&col=56262&level=1%2C2&show_num=100&page=2&act=more&jsoncallback=callbackFunction&_=1719411573327').text
data = data[data.index('callbackFunction')+len(str('callbackFunction')):]
print(data)
print(extract_titles(json.loads(data)))
