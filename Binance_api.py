import ccxt
import pandas as pd
import time
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
symbol = get_valid_input("수집할 종목을 입력하세요 (예: SOL/USDT): ", lambda x: '/' in x)

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
valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
timeframe = get_valid_input("수집할 봉의 종류를 입력하세요 (예: 1m, 5m, 1h, 1d): ", lambda x: x in valid_timeframes)

# 파일 경로 입력
file_path = get_valid_input("저장할 파일 경로를 입력하세요 (예: C:/Users/Username/Desktop/solana_1min_data.csv): ", lambda x: len(x) > 0)

# 입력 받은 날짜를 timestamp로 변환
start_timestamp = int(datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
end_timestamp = int(datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

# 바이낸스 API 설정
binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'timeout': 30000,  # 30초 타임아웃 설정
    'enableRateLimit': True,  # 레이트 리밋 사용
})

# 요청 가중치 추적 변수 초기화
used_weight = 0
weight_limit = 6000  # 분당 가중치 한도

# 데이터 수집 함수
def fetch_ohlcv(symbol, timeframe, since, limit=1000):
    global used_weight
    all_ohlcv = []
    while True:
        try:
            # 요청 가중치 확인
            if used_weight >= weight_limit:
                print("API 요청 가중치 한도에 도달했습니다. 1분 대기 중...")
                time.sleep(60)
                used_weight = 0  # 가중치 초기화

            new_ohlcv = binance.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            used_weight += 1  # 각 요청마다 가중치 증가 (기본 가중치 1로 가정)

            if not new_ohlcv:
                break
            since = new_ohlcv[-1][0] + 1
            all_ohlcv += new_ohlcv
            if len(new_ohlcv) < limit:
                break

            # 호출 제한을 준수하기 위해 대기
            time.sleep(1)
        except ccxt.NetworkError as e:
            print(f"Network error: {e}. Retrying in 1 minute...")
            time.sleep(60)
        except ccxt.ExchangeError as e:
            print(f"Exchange error: {e}. Retrying in 1 minute...")
            time.sleep(60)
        except ccxt.RequestTimeout as e:
            print(f"Request timeout: {e}. Retrying in 1 minute...")
            time.sleep(60)
    return all_ohlcv

# 데이터 수집
ohlcv_data = fetch_ohlcv(symbol, timeframe, start_timestamp)

# 수집된 데이터가 종료 날짜 이전까지인지 확인하고 자르기
ohlcv_data = [data for data in ohlcv_data if data[0] <= end_timestamp]

# 데이터프레임으로 변환
df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['timestamp'] = df['timestamp'].dt.strftime('%Y.%m.%d.%H.%M.%S')

# 데이터 저장
df.to_csv(file_path, index=False)

print(f"총 {len(df)} 개의 데이터가 {file_path} 경로에 저장되었습니다.")
