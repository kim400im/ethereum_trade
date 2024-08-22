import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import pyupbit
import pandas as pd
import pandas_ta as ta
import json
import schedule
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
upbit = pyupbit.Upbit(os.getenv("UPBIT_ACCESS_KEY"), os.getenv("UPBIT_SECRET_KEY"))

# openai 키 확인용
# completion = client.chat.completions.create(
#     model= "gpt-3.5-turbo",
#     messages=[
#         {
#             "role" : "system",
#             "content": "you are a helpful assistant",
#         },
#         {
#             "role": "user",
#             "content":"Hello!"
#         }
#     ]
# )

# print(completion.choices[0].message.content)

krw = upbit.get_balance(ticker="KRW")
print(f"KRW BAlance: {krw}")
bit = upbit.get_balance(ticker='BTC')
print(bit)

df_daily = pyupbit.get_ohlcv("KRW-BTC", "day", count=30)
df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=24)
print(df_daily)

# 데이터 형식이 판다스이다. 
print(type(df_daily))
