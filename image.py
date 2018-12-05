import bs4
import urllib  
from urllib import request
from bs4 import BeautifulSoup as bs
from urllib.error import URLError, HTTPError
import xlwt
from xlwt import Workbook
import json
import requests
import time
import datetime
import os

def getRaceInfo(id,page):
    url='http://m.yundong.runnerbar.com/yd_mobile/share/album.json'
    para = {'activity_id':id,'page':page,'pageSize':100}
    header = {}
    r = requests.post(url,data=para,headers= header)
    json_r = r.json()
    parsed_json = json_r['album']['searchResultList']
    activity = {}
    items = []
    count = json_r['album']['activity_photo_count']
    for item in parsed_json:
        items.append(item)
    activity['items'] = items
    activity['count'] = count
    return activity


def startRace(id):
    row_index = 1001
    workbook = xlwt.Workbook(encoding = 'utf-8')
    try:
        activity = getRaceInfo(id,1)
        tempdata = activity['items']
        count = int(activity['count'])
        if count > 0:
            print(id,count)
            for i in range(1,int(count/100+2)):
                try:
                    data = getRaceInfo(id,i)['items']
                    for item in data:
                        print(item['url_hq'])
                        save_img(item['url_hq'],row_index,'book'+id)
                        row_index = row_index +1
                    print(row_index)
                except HTTPError as e:
                    print('Error code: ', e.code)
                except URLError as e:
                    print('Reason: ', e.reason)
                except Exception as e:
                    print('错误 ：',e)
    except Exception as e:
        print('错误 ：',e)


def save_img(img_url,file_name,file_path='book'):
    #保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    try:
        if not os.path.exists(file_path):
            print('文件夹',file_path,'不存在，重新建立')
            #os.mkdir(file_path)
            os.makedirs(file_path)
        #获得图片后缀
        file_suffix = os.path.splitext(img_url)[1]
        #拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path,os.sep,file_name,file_suffix)
       #下载图片，并保存到文件夹中
        urllib.request.urlretrieve(img_url,filename=filename)
    except IOError as e:
        print('文件操作失败',e)
    except HTTPError as e:
        print('Error code: ', e.code)
    except Exception as e:
        print('错误 ：',e)
# 0-100 10712 7376  10765
for i in range(7835,7836):
    startRace(str(i))