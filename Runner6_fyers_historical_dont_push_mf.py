from dotenv import load_dotenv
from fyers_apiv3 import fyersModel
# from fyers_api import accessToken
import os
import pandas as pd
import datetime

load_dotenv()

appId = os.getenv("APP_ID")
appSecret = os.getenv("APP_SECRET")
redirectUrl =  os.getenv("REDIRECT_URL")

def get_access_token():
    if not os.path.exists('access_token.txt'):
        session=fyersModel.SessionModel(client_id=appId,
        secret_key=appSecret,redirect_uri=redirectUrl, 
        response_type="code", grant_type="authorization_code")

        response = session.generate_authcode()  
        print("Login Url", response)

        auth_code = input("Enter Auth Code : ")
        session.set_token(auth_code)
        # this will generate accessToken
        access_token = session.generate_token()['access_token']
        with open("access_token.txt", 'w') as f:
            f.write(access_token)

    else:
        with open("access_token.txt", 'r') as f:
            access_token = f.read()
    
    print(access_token)
    return access_token

# accessToken = get_access_token()

fyers = fyersModel.FyersModel(client_id=appId, token=get_access_token(), log_path="./logs")

# data = {"symbol":"NSE:SBIN-EQ","resolution":"D","date_format":"0","range_from":"1622097600","range_to":"1622097685","cont_flag":"1"}

# NSE:SBIN-EQ
# Data API
# https://api-docs.fyers.in/docs/index.html#tag/Data-Api/paths/~1DataApi/post

def historical_bydate(symbol, sd, ed, interval):
    data = {"symbol":symbol,"resolution":interval,"date_format":"1","range_from":str(sd),"range_to":str(ed),"cont_flag":"1"}
    # data = {
    # "symbol":"NSE:SBIN-EQ",
    # "resolution":"D",
    # "date_format":"1",
    # "cont_flag":"1"
    # }
    nx = fyers.history(data)
    cols = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
    # print(nx.keys()) #prints keys
    df = pd.DataFrame.from_dict(nx['candles'])
    df.columns = cols
    df['datetime'] = pd.to_datetime(df['datetime'], unit = "s")
    df['datetime'] = df['datetime'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
    # df['datetime'] = df['datetime'].dt.tz_localize('None')
    df = df.set_index('datetime')
    df['realtime'] = df.index.tz_localize(None)
    return df
    print("Done")

# historical_bydate('NSE:SBIN-EQ', '2023-06-14', '2023-06-15', '2')


sd = datetime.date(2024,1,1)
# enddate = datetime.date(2023,12,31)
enddate = datetime.datetime.now().date()
df = pd.DataFrame()

n = abs((sd - enddate).days)
ab = None

# upto 366 days for 1D Resolution
itercount = 0
while ab == None:
    days = 365
    # if n > 366:
    #     days = 365
    # else:
    #     days = n

    if n < days or itercount == 0:
        sd = (enddate - datetime.timedelta(n))
    else:
        sd = (sd + datetime.timedelta(days))

    itercount = itercount + 1
    # ed = (sd + datetime.timedelta(days = 365 if n > 366 else n)).strftime("%Y-%m-%d")
    ed_str = (sd + datetime.timedelta(days)).strftime("%Y-%m-%d")
    sd_str = sd.strftime("%Y-%m-%d")
    # dx = historical_bydate("NSE:NIFTY200MOMENTM30-INDEX", sd, ed, "D")
    # dx = historical_bydate("NSE:ITC-EQ", sd, ed, "D")
    # dx = historical_bydate("NSE:HINDPETRO-EQ", sd, ed, "2")
    dx = historical_bydate("NSE:NIFTY50-INDEX", sd_str, ed_str, "D")
    # dx = historical_bydate("NSE:GOLDBEES-EQ", sd_str, ed_str, "D")
    # dx = historical_bydate("NSE:GOLDBEES-EQ", sd, ed, "D")
    # dx = historical_bydate("NSE:NIFTY200MOMENTM30-INDEX", sd, ed, "D")
    # df = df.append(dx)
    df = pd.concat([df, dx], ignore_index=True)

    n = n - days if n > days else n - n
    print(n)
    if n == 0:
        ab = "done"

df['realtime'] = pd.to_datetime(df['realtime'])     # step 1
df = df.set_index('realtime')                       # step 2
df.index = df.index.date                            # step 3 set only date as index
df = df.sort_index()                                # optional: recommended
df.to_csv("./historical_data/NIFTY200MOMENTM30_1D_055_zzz.csv")

# Setting up fyers api
# https://www.youtube.com/watch?v=J5GhpB574XM
# Websockets
# https://www.youtube.com/watch?v=K2lzFEkwldw
# MaticAlgos 1 min data scrap
# https://www.youtube.com/watch?v=BJvTASV9Y0o

# Github document,
# https://github.com/FyersDev/fyers-api-sample-code/blob/sample_v3/v3/python/login/get_access_token.py
# Fyers api documentation, has websockets as well
# https://myapi.fyers.in/docsv3#tag/Data-Api/paths/~1DataApi/post
# Github POSTMAN Collection
# https://github.com/FyersDev/fyers-api-sample-code/tree/sample_v3/v3





