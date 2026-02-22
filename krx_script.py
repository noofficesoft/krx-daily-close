import requests
import pandas as pd
from io import BytesIO
from datetime import datetime
import json

today = datetime.now().strftime("%Y%m%d")

otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"

otp_params = {
    "mktId": "ALL",
    "trdDd": today,
    "money": "1",
    "csvxls_isNo": "false",
    "name": "fileDown",
    "url": "dbms/MDC/STAT/standard/MDCSTAT01501"
}

headers = {
    "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader",
    "User-Agent": "Mozilla/5.0"
}

otp = requests.post(otp_url, data=otp_params, headers=headers).text

download_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
res = requests.post(download_url, data={"code": otp}, headers=headers)

df = pd.read_csv(BytesIO(res.content), encoding="euc-kr")
df = df[["종목코드", "종가"]]
df["종목코드"] = df["종목코드"].astype(str).str.zfill(6)

result = {"date": today}

for _, row in df.iterrows():
    result[row["종목코드"]] = int(row["종가"])

with open("krx_close.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)
