#============================================================
#指定した範囲内の歩数データを取得するプログラム
#日付を広い範囲で選択するとtokenを失効するので小分けにして取得すること
#============================================================

#必要なライブラリーをインポート
import fitbit
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import date, timedelta
import datetime
import psycopg2

#fitbit apiを作動させるのに必要な環境変数をosから取得
CLIENT_ID = os.environ['FITBIT_CLIENT_ID']
CLIENT_SECRET = os.environ['FITBIT_CLIENT_SECRET']
ACCESS_TOKEN = os.environ['FITBIT_ACCESS_TOKEN']
REFRESH_TOKEN = os.environ['FITBIT_REFRESH_TOKEN']

#accesstokenの有効期限が切れていても自動取得させる関数定義
def refresh_cb(token_dict):
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    ACCESS_TOKEN = token_dict['access_token']
    REFRESH_TOKEN = token_dict['refresh_token']
    return token_dict

#refresh_cb=refresh_cbでaccess tokenを自動更新する
authd_client = fitbit.Fitbit(
    CLIENT_ID,
    CLIENT_SECRET,
    access_token=ACCESS_TOKEN,
    refresh_token=REFRESH_TOKEN,
    refresh_cb=refresh_cb
)

#DBに接続
conn = psycopg2.connect("host=127.0.0.1 port=5432 dbname=DataRecordApp-db user=root password=")
cur = conn.cursor()

#1日分 リクエスト回数24回/日
#=======================================
#GET_YEARとGET_MONTHに取得したい年月をいれる
#=======================================
GET_YEAR = "2019"
GET_MONTH = "12"

#=================================================================================
#range内の数値を変更し、取得したい日付の範囲を指定する。※リクエストが多いとtoken失効するので注意
#=================================================================================
for DAY in range(28, 32):
    if DAY < 10 :
        DATE =  GET_YEAR + "-" + GET_MONTH + "-" + "0" + str(DAY)
              
    else :
        DATE = GET_YEAR + "-" + GET_MONTH + "-"  + str(DAY)
        
    #stringdateカラムにいれるデータを作成
    string_date = GET_YEAR + "/" + GET_MONTH + "/" + str(DAY)
    
    #時間の取得
    for TIME in range(0, 24) :
        start_time = str(TIME) + ":00"
        end_time = str(TIME) + ":59"
        #ここでAPIを実行する
        data_sec = authd_client.intraday_time_series('activities/steps', base_date=DATE, detail_level='1min', start_time = start_time, end_time = end_time )
        #必要なデータ　をjsonから取得する
        hour_steps = data_sec['activities-steps'][0]['value']
        
        #timeカラム に入れるデータを作成
        record_time = DATE + " " +str(TIME) + ":00"
        record_time_with_timezone = record_time + ":00+09"
        #sql実行
        cur.execute("INSERT INTO fitbit_hoursteps(hour_steps, time, string_date) VALUES(%s,%s,%s)", (hour_steps, record_time_with_timezone, string_date))
        print("Now completed insert data time is " + str(TIME))
        TIME +=1
        #sqlにコミット 
    conn.commit()
    print(DATE + "committed")