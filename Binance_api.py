from binance.spot import Spot
import pandas as pd
import datetime

# 사용자 입력 유효성 검사 함수
def get_valid_input(prompt, validation_func):
    while True:
        value = input(prompt)
        if validation_func(value):
            return value
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

# API 키와 시크릿 키 입력
api_key = get_valid_input("API 키를 입력하세요: ", lambda x: len(x) > 0)
api_secret = get_valid_input("API 시크릿 키를 입력하세요: ", lambda x: len(x) > 0)

# 종목 입력
symbol = get_valid_input("수집할 종목을 입력하세요 (예: SOLUSDT): ", lambda x: x.isalnum())

# 날짜 입력 (형식 검사 포함)
def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

start_date = get_valid_input("데이터 수집 시작 날짜를 입력하세요 (예: 2023-07-11): ", is_valid_date)
end_date = get_valid_input("데이터 수집 종료 날짜를 입력하세요 (예: 2024-07-11): ", is_valid_date)

# 봉의 종류 입력 (기본적인 검사)
valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
timeframe = get_valid_input("수집할 봉의 종류를 입력하세요 (예: 1m, 5m, 1h, 1d): ", lambda x: x in valid_timeframes)

# 파일 경로 입력
file_path = get_valid_input("저장할 파일 경로를 입력하세요 (예: C:/Users/Username/Desktop/solana_1min_data.csv): ", lambda x: len(x) > 0)

# 클라이언트 설정
client = Spot(key=api_key, secret=api_secret)

# 데이터 수집 함수
def fetch_ohlcv(symbol, interval, start_str, end_str):
    klines = client.klines(symbol=symbol, interval=interval, startTime=start_str, endTime=end_str)
    return klines

# Unix 타임스탬프로 변환
start_timestamp = int(datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
end_timestamp = int(datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

# 데이터 수집
ohlcv_data = fetch_ohlcv(symbol, timeframe, start_timestamp, end_timestamp)

# 데이터프레임으로 변환
df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['timestamp'] = df['timestamp'].dt.strftime('%Y.%m.%d.%H.%M.%S')

# 열 순서 및 이름 재정렬
df = df[['timestamp', 'close', 'open', 'high', 'low', 'volume']]

# 데이터 저장
df.to_csv(file_path, index=False)

print(f"총 {len(df)} 개의 데이터가 {file_path} 경로에 저장되었습니다.")

