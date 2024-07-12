from binance.spot import Spot
import pandas as pd
import datetime
import time

# 입력값 설정
API_KEY = "YOUR_API_KEY_HERE"
API_SECRET = "YOUR_API_SECRET_HERE"
SYMBOL = "SOLUSDT"  # 수집할 종목 (예: 'SOLUSDT', 'BTCUSDT' 등)
START_DATE = "2023-07-11"  # 데이터 수집 시작 날짜 (형식: 'YYYY-MM-DD')
END_DATE = "2024-07-11"  # 데이터 수집 종료 날짜 (형식: 'YYYY-MM-DD')
TIMEFRAME = "1m"  # 수집할 봉의 종류 (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M 중 선택)
FILE_PATH = "C:/Users/krkr5/OneDrive/바탕 화면/project/Crypto_data/dava_csv/solana_data.csv"  # 저장할 파일 경로


def date_to_timestamp(date_str):
    return int(datetime.datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)


def call_api(client, symbol, interval, start_time, end_time):
    try:
        klines = client.klines(
            symbol=symbol,
            interval=interval,
            startTime=start_time,
            endTime=end_time,
            limit=1000
        )
        return klines
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return []


def process_klines(klines):
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
               'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(klines, columns=columns)
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    df['number_of_trades'] = df['number_of_trades'].astype(int)
    return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]


def collect_data(client, symbol, timeframe, start_date, end_date):
    start_time = date_to_timestamp(start_date)
    end_time = date_to_timestamp(end_date)
    all_data = []

    while start_time < end_time:
        next_end = min(start_time + (1000 * 60 * 1000), end_time)
        klines = call_api(client, symbol, timeframe, start_time, next_end)

        if klines:
            all_data.extend(klines)
            print(f"수집된 데이터: {len(klines)}개 ({datetime.datetime.fromtimestamp(start_time / 1000)})")
        else:
            print(f"데이터 수집 실패: {datetime.datetime.fromtimestamp(start_time / 1000)}")

        start_time = next_end
        time.sleep(2)  # API 호출 제한 고려

    return process_klines(all_data)


def save_data(df, file_path):
    df.to_csv(file_path, index=False)
    print(f"총 {len(df)} 개의 데이터가 {file_path} 경로에 저장되었습니다.")


def main():
    #client = Spot(api_key=API_KEY, api_secret=API_SECRET)
    client = Spot()

    print("데이터 수집 시작...")
    start_time = time.time()

    df = collect_data(client, SYMBOL, TIMEFRAME, START_DATE, END_DATE)

    end_time = time.time()
    print(f"데이터 수집 완료. 소요 시간: {end_time - start_time:.2f} 초")

    save_data(df, FILE_PATH)


if __name__ == "__main__":
    main()