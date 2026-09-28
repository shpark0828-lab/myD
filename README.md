# 내 주식 종가 기록

`stocks.csv`에 보유 종목을 적어 두면, 매일 종가를 가져와 `data/closing_prices.csv`에 누적 기록합니다.

## 1. 종목 입력 — `stocks.csv`

```csv
ticker,name,quantity
005930,삼성전자,10
000660,SK하이닉스,5
AAPL,Apple,3
```

| 열 | 설명 |
|---|---|
| `ticker` | 한국 주식은 6자리 종목코드(코스피/코스닥 자동 판별), 해외 주식은 야후 파이낸스 티커(`AAPL`, `TSLA`, `7203.T` 등) |
| `name` | 표시용 이름 (선택) |
| `quantity` | 보유 수량 (선택) — 적으면 평가금액도 계산 |

## 2. 결과

- `data/closing_prices.csv` — 날짜·종목별 종가, 전일대비(%), 통화, 수량, 평가금액 (엑셀로 바로 열림)
- `data/latest.md` — 종목별 최신 종가와 통화별 평가금액 합계

## 3. 자동 실행

`.github/workflows/daily-close.yml`이 평일 매일 오전 7시 13분(KST)에 실행되어 결과를 커밋합니다.
최근 7일치를 다시 가져오므로 하루 이틀 실행이 빠져도 자동으로 채워집니다.
과거 데이터를 한 번에 채우려면 GitHub → Actions → "매일 종가 기록" → **Run workflow**에서 기간(`3mo`, `1y` 등)을 입력하세요.

## 로컬 실행

```bash
pip install -r requirements.txt
python fetch_prices.py            # 최근 7일
python fetch_prices.py --period 1y
```

시세 출처: Yahoo Finance (`yfinance`)
