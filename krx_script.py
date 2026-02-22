import requests
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import json
import os

def find_last_trading_day(max_retry=7):
    today = datetime.now()
    for i in range(1, max_retry + 1):
        date = (today - timedelta(days=i)).strftime("%Y%m%d")
        if fetch_data(date, test_only=True):
            return date
    return None

def fetch_data(target_date, test_only=False):
    otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
    otp_params = {
        "mktId": "ALL",
        "trdDd": target_date,
        "money": "1",
        "csvxls_isNo": "false",
        "name": "fileDown",
        "url": "dbms/MDC/STAT/standard/MDCSTAT01501"
    }

    headers = {
        "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        otp_res = requests.post(otp_url, data=otp_params, headers=headers, timeout=10)
        if otp_res.status_code != 200:
            return False

        download_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
        res = requests.post(download_url, data={"code": otp_res.text}, headers=headers, timeout=10)

        if not res.content or len(res.content) < 100:
            return False

        if test_only:
            return True

        df = pd.read_csv(BytesIO(res.content), encoding="euc-kr")
        df = df[["종목코드", "종가"]]
        df["종목코드"] = df["종목코드"].astype(str).str.zfill(6)

        result = {"date": target_date}
        for _, row in df.iterrows():
            result[row["종목코드"]] = int(row["종가"])

        with open("krx_close.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False)

        print("KRX JSON updated:", target_date)
        return True

    except Exception as e:
        print("Error:", e)
        return False

# ===============================
# 실행 로직
# ===============================

last_trading_day = find_last_trading_day()

if last_trading_day:
    success = fetch_data(last_trading_day)
    if not success:
        print("Data fetch failed. Keeping previous JSON.")
else:
    print("No trading day found in last 7 days. Keeping previous JSON.")
