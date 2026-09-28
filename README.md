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

## 3. 그래프 웹앱 — `index.html`

`data/closing_prices.csv`를 읽어 그래프로 보여 줍니다.

- 통화별 평가금액 합계와 전일 대비
- 종목 카드: 최근 종가, 등락률, 최근 30일 추이
- 수익률 비교 차트(기간 시작일 대비 %)와 종목별 종가 차트, 기간 선택(1개월~전체)
- 날짜별 종가 표

**GitHub Pages로 열기:** 저장소 Settings → Pages → Source를 `Deploy from a branch`, 브랜치 `main` / `/ (root)`로 저장하면
`https://<아이디>.github.io/<저장소>/` 주소에서 볼 수 있습니다. 매일 기록이 커밋되면 페이지도 자동으로 최신 데이터를 보여 줍니다.
(비공개 저장소의 Pages는 유료 플랜에서만 됩니다. 이 경우 아래처럼 로컬에서 열거나, 화면의 **CSV 불러오기**로 파일을 직접 여세요.)

**로컬에서 열기:**

```bash
python -m http.server 8000   # 저장소 폴더에서 실행 후 http://localhost:8000 접속
```

데이터 파일을 찾지 못하면 예시 데이터를 표시합니다.

## 4. 자동 실행

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
