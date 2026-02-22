import requests
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import json

def get_target_date():
    # 오늘이 휴장일일 수 있으므로
    # 기본은 어제 날짜로 시도
    return (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

target_date = get_target_date()

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

otp_res = requests.post(otp_url, data=otp_params, headers=headers)

if otp_res.status_code != 200:
    raise Exception("OTP request failed")

otp = otp_res.text

download_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
res = requests.post(download_url, data={"code": otp}, headers=headers)

# 🔥 응답이 비어있는 경우 처리
if not res.content or len(res.content) < 100:
    print("KRX returned empty data. Possibly holiday.")
    exit(0)

try:
    df = pd.read_csv(BytesIO(res.content), encoding="euc-kr")
except Exception as e:
    print("CSV parsing failed:", e)
    exit(0)

df = df[["종목코드", "종가"]]
df["종목코드"] = df["종목코드"].astype(str).str.zfill(6)

result = {"date": target_date}

for _, row in df.iterrows():
    result[row["종목코드"]] = int(row["종가"])

with open("krx_close.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print("KRX JSON update completed:", target_date)
