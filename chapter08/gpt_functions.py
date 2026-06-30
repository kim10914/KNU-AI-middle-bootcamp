from datetime import datetime
import pytz
import yfinance as yf

# 주어진 타임존의 현재 시각을 문자열로 반환한다.
def get_current_time(timezone: str = "Asia/Seoul") -> str:
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"{timezone} 현재 시각: {now}"
    except pytz.UnknownTimeZoneError:
        return f"알 수 없는 타임존: {timezone}"

# 야후 파이낸스에서 종목의 기본 정보를 가져온다.
def get_yf_stock_info(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    return str(stock.info)

# 야후 파이낸스에서 종목의 가격 이력을 가져온다.
def get_yf_stock_history(ticker: str, period: str = "1mo") -> str:
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    return history.to_markdown()

# 야후 파이낸스에서 종목의 애널리스트 추천 정보를 가져온다.
def get_yf_stock_recommendations(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    recommendations = stock.recommendations
    return recommendations.to_markdown()

# OpenAI(OpenRouter) tool_calls 용 도구 스키마
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "현재 시각을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "타임존 (예: 'Asia/Seoul')",
                    }
                },
                "required": ["timezone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_info",
            "description": "야후 파이낸스에서 종목의 기본 정보를 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "종목 코드 (예: 'AAPL', '005930.KS')",
                    }
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_history",
            "description": "야후 파이낸스에서 종목의 가격 이력을 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "종목 코드 (예: 'AAPL', '005930.KS')",
                    },
                    "period": {
                        "type": "string",
                        "description": "조회 기간 (예: '1d', '5d', '1mo', '3mo', '1y')",
                    },
                },
                "required": ["ticker", "period"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_recommendations",
            "description": "야후 파이낸스에서 종목의 애널리스트 추천 정보를 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "종목 코드 (예: 'AAPL', '005930.KS')",
                    }
                },
                "required": ["ticker"],
            },
        },
    },
]
