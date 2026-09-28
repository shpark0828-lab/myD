"""stocks.csv 에 적은 종목들의 종가를 가져와 data/closing_prices.csv 에 누적 저장한다.

사용법:
    python fetch_prices.py              # 최근 7일치 종가를 가져와 빠진 날짜까지 채움
    python fetch_prices.py --period 3mo # 과거 3개월치 한 번에 채우기 (1mo, 6mo, 1y ...)
"""

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
STOCKS_FILE = ROOT / "stocks.csv"
DATA_FILE = ROOT / "data" / "closing_prices.csv"
SUMMARY_FILE = ROOT / "data" / "latest.md"

FIELDS = ["date", "ticker", "name", "close", "change_pct", "currency", "quantity", "value"]


def load_stocks():
    with open(STOCKS_FILE, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("ticker") or "").strip()]
    for r in rows:
        r["ticker"] = r["ticker"].strip().upper()
        r["name"] = (r.get("name") or "").strip() or r["ticker"]
        q = (r.get("quantity") or "").strip()
        r["quantity"] = float(q) if q else None
    return rows


def yahoo_candidates(ticker):
    """한국 종목코드(6자리 숫자)는 코스피(.KS) → 코스닥(.KQ) 순으로 시도한다."""
    if re.fullmatch(r"\d{6}", ticker):
        return [f"{ticker}.KS", f"{ticker}.KQ"]
    return [ticker]


def fetch_history(ticker, period):
    """[(date 'YYYY-MM-DD', close float)], currency 를 반환한다."""
    import yfinance as yf

    for symbol in yahoo_candidates(ticker):
        t = yf.Ticker(symbol)
        hist = t.history(period=period, auto_adjust=False)
        if hist.empty:
            continue
        closes = [(idx.strftime("%Y-%m-%d"), float(c)) for idx, c in hist["Close"].dropna().items()]
        try:
            currency = t.fast_info.get("currency") or ""
        except Exception:
            currency = ""
        return closes, currency
    return [], ""


def load_records():
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, encoding="utf-8-sig") as f:
        return {(r["date"], r["ticker"]): r for r in csv.DictReader(f)}


def save_records(records):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(records.values(), key=lambda r: (r["date"], r["ticker"]))
    # utf-8-sig: 엑셀에서 열어도 한글이 깨지지 않도록 BOM 포함
    with open(DATA_FILE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def fmt_num(x, digits=2):
    s = f"{x:,.{digits}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def update(stocks, period, fetch=fetch_history):
    records = load_records()
    failed = []
    for s in stocks:
        closes, currency = fetch(s["ticker"], period)
        if not closes:
            failed.append(s["ticker"])
            continue
        prev = None
        for date, close in closes:
            change = (close / prev - 1) * 100 if prev else None
            prev = close
            qty = s["quantity"]
            records[(date, s["ticker"])] = {
                "date": date,
                "ticker": s["ticker"],
                "name": s["name"],
                "close": round(close, 4),
                "change_pct": round(change, 2) if change is not None else "",
                "currency": currency,
                "quantity": f"{qty:g}" if qty is not None else "",
                "value": round(close * qty, 2) if qty is not None else "",
            }
    # 가져온 기간의 첫날은 전일 대비를 계산할 수 없으므로, 저장된 이전 종가로 보충
    by_ticker = {}
    for key in sorted(records):
        r = records[key]
        last = by_ticker.get(r["ticker"])
        if r["change_pct"] in ("", None) and last is not None:
            r["change_pct"] = round((float(r["close"]) / float(last) - 1) * 100, 2)
        by_ticker[r["ticker"]] = r["close"]
    save_records(records)
    return records, failed


def write_summary(records, stocks):
    latest = {}
    for (date, ticker), r in records.items():
        if ticker not in latest or date > latest[ticker]["date"]:
            latest[ticker] = r
    lines = [
        "# 보유 종목 최근 종가",
        "",
        "| 종목 | 코드 | 기준일 | 종가 | 전일대비 | 수량 | 평가금액 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    totals = {}
    for s in stocks:
        r = latest.get(s["ticker"])
        if not r:
            continue
        chg = f"{float(r['change_pct']):+.2f}%" if r["change_pct"] not in ("", None) else "-"
        val = f"{fmt_num(float(r['value']))} {r['currency']}" if r["value"] not in ("", None) else "-"
        if r["value"] not in ("", None):
            totals[r["currency"]] = totals.get(r["currency"], 0) + float(r["value"])
        lines.append(
            f"| {r['name']} | {r['ticker']} | {r['date']} | {fmt_num(float(r['close']))} {r['currency']} "
            f"| {chg} | {r['quantity'] or '-'} | {val} |"
        )
    if totals:
        lines += ["", "**통화별 평가금액 합계:** " + ", ".join(f"{fmt_num(v)} {c}" for c, v in totals.items())]
    SUMMARY_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="보유 종목 종가 기록")
    parser.add_argument("--period", default="7d", help="가져올 기간 (예: 7d, 1mo, 3mo, 1y). 기본 7d")
    args = parser.parse_args()

    stocks = load_stocks()
    if not stocks:
        sys.exit("stocks.csv 에 종목이 없습니다.")
    records, failed = update(stocks, args.period)
    write_summary(records, stocks)
    print(SUMMARY_FILE.read_text(encoding="utf-8"))
    if failed:
        print(f"가져오지 못한 종목: {', '.join(failed)}", file=sys.stderr)
        if len(failed) == len(stocks):
            sys.exit(1)


if __name__ == "__main__":
    main()
