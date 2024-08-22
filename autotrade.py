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

def get_current_status():
    orderbook = pyupbit.get_orderbook(ticker="KRW-ETH")
    current_time = orderbook['timestamp']  # 호가창 시간을  받는다. 
    eth_balance = 0
    krw_balance = 0
    eth_avg_buy_price = 0
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == "ETH":
            eth_balance = b['balance']    # 코인 보유량
            eth_avg_buy_price = b['avg_buy_price']
        if b['currency'] == "KRW":
            krw_balance = b['balance']    # 원화 보유량

    # 현재 정보들을 전부 담는다. 
    current_status = {'current_time': current_time, 'orderbook': orderbook, 'eth_balance': eth_balance, 'krw_balance': krw_balance, 'eth_avg_buy_price': eth_avg_buy_price}
    return json.dumps(current_status)  # json으로 바꿔서 보낸다. 

# 코인 데이터 30일 치와 24시간 데이터를 가져온다. 
def fetch_and_prepare_data():
    # Fetch data
    df_daily = pyupbit.get_ohlcv("KRW-ETH", "day", count=30)
    df_hourly = pyupbit.get_ohlcv("KRW-ETH", interval="minute60", count=24)

    # Define a helper function to add indicators
    def add_indicators(df):
        # Moving Averages
        df['SMA_10'] = ta.sma(df['close'], length=10)
        df['EMA_10'] = ta.ema(df['close'], length=10)

        # RSI
        df['RSI_14'] = ta.rsi(df['close'], length=14)

        # Stochastic Oscillator
        stoch = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3, smooth_k=3)
        df = df.join(stoch)

        # MACD
        ema_fast = df['close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

        # Bollinger Bands
        df['Middle_Band'] = df['close'].rolling(window=20).mean()
        # Calculate the standard deviation of closing prices over the last 20 days
        std_dev = df['close'].rolling(window=20).std()
        # Calculate the upper band (Middle Band + 2 * Standard Deviation)
        df['Upper_Band'] = df['Middle_Band'] + (std_dev * 2)
        # Calculate the lower band (Middle Band - 2 * Standard Deviation)
        df['Lower_Band'] = df['Middle_Band'] - (std_dev * 2)

        return df

    # Add indicators to both dataframes
    df_daily = add_indicators(df_daily)
    df_hourly = add_indicators(df_hourly)

    combined_df = pd.concat([df_daily, df_hourly], keys=['daily', 'hourly'])
    combined_data = combined_df.to_json(orient='split')

    # make combined data as string and print length
    print(len(combined_data))

    return json.dumps(combined_data)

# instructions.md 파일을 불러온다. 
def get_instructions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred while reading the file:", e)

def analyze_data_with_gpt4(data_json):
    instructions_path = "instructions.md"
    try:
        instructions = get_instructions(instructions_path)
        if not instructions:
            print("No instructions found.")
            return None

        # 현재 상태를 받아온다. 
        current_status = get_current_status()
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": instructions}, # gpt에  md 파일을 보낸다. 
                {"role": "user", "content": data_json},   # 시장 데이터 받는다.
                {"role": "user", "content": current_status}  # 현재 상태를 받는다. json데이터 2개가 gpt에 보내진다
            ],
            response_format={"type":"json_object"}  # 이걸 추가하면 응답이 json 형태로만 온다. 
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyzing data with GPT-4: {e}")
        return None

# 매수
def execute_buy():
    print("Attempting to buy ETH...")
    try:
        krw = upbit.get_balance("KRW")
        if krw > 5000:
            result = upbit.buy_market_order("KRW-ETH", krw*0.9995)
            print("Buy order successful:", result)
    except Exception as e:
        print(f"Failed to execute buy order: {e}")

# 매도
def execute_sell():
    print("Attempting to sell ETH...")
    try:
        eth = upbit.get_balance("ETH")
        current_price = pyupbit.get_orderbook(ticker="KRW-ETH")['orderbook_units'][0]["ask_price"]
        # 5000 원 이상이면 구매한다. 
        if current_price*eth > 5000:
            result = upbit.sell_market_order("KRW-ETH", eth)
            print("Sell order successful:", result)
    except Exception as e:
        print(f"Failed to execute sell order: {e}")

def make_decision_and_execute():
    print("Making decision and executing...")
    data_json = fetch_and_prepare_data()
    advice = analyze_data_with_gpt4(data_json) # gpt로부터 투자조언을 받는다. 

    try:
        decision = json.loads(advice)
        print(decision)
        if decision.get('decision') == "buy":
            execute_buy()
        elif decision.get('decision') == "sell":
            execute_sell()
    except Exception as e:
        print(f"Failed to parse the advice as JSON: {e}")

if __name__ == "__main__":
    make_decision_and_execute()
    schedule.every().hour.at(":01").do(make_decision_and_execute)

    # 매시각을 확인한다.
    while True:
        schedule.run_pending()
        time.sleep(1)