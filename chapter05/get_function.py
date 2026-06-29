from datetime import datetime
import pytz
import yfinance as yf

def get_current_time(timezone : str = "Asia/Seoul"):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    now_timezone = f'{now} {timezone}'
    print(now_timezone)
    return now_timezone

def get_yf_stock_info(ticker : str):
    stock = yf.Ticker(ticker)
    info = stock.info
    print(info)
    return str(info)

def get_yf_stock_history(ticker : str, period : str):
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    history_md = history.to_markdown()
    print(history_md)
    return history_md

def get_yf_stock_recommendations(ticker : str):
    stock = yf.Ticker(ticker)
    recommendations = stock.recommendations
    recommendations_md = recommendations.to_markdown()
    print(recommendations_md)
    return recommendations_md

# 도구 정의
tools = [
    {
        "type": "function", # 도구의 타입을 function으로 지정
        "function": { # 도구의 상세 정보
            "name": "get_current_time", # 도구 이름
            "description": "해당 타임존의 날짜와 시간을 반환합니다.", # 도구 설명
            "parameters": { # 도구의 파라미터 정의
                "type": "object", # 파라미터 타입을 object로 지정
                "properties": { # 파라미터의 상세 정보
                    "timezone": { # 파라미터 이름
                        "type": "string", # 파라미터 타입을 string으로 지정
                        # 파라미터 설명
                        "description": "현재 날짜와 시간을 반환할 타임존. 사용자가 지역을 명시한 경우에만 채우세요. (예 : Asia/Seoul)"
                    }
                },
                "required": ["timezone"], # 필수 파라미터 지정
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_info",
            "description": "해당 종목의 Yahoo Finance 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Yahoo Finance에서 조회할 주식 종목을 입력하세요. (예 : AAPL)",
                    },
                },
                "required": ["ticker"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_history",
            "description": "해당 종목의 Yahoo Finance 주가 이력을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Yahoo Finance에서 조회할 주식 종목을 입력하세요. (예 : AAPL)",
                    },
                    "period": {
                        "type": "string",
                        "description": "조회할 기간을 입력하세요. (예 : 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                    },
                },
                "required": ["ticker", "period"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_yf_stock_recommendations",
            "description": "해당 종목의 Yahoo Finance 추천 정보를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Yahoo Finance에서 조회할 주식 종목을 입력하세요. (예 : AAPL)",
                    },
                },
                "required": ["ticker"],
            }
        }
    }
]

if __name__ == "__main__": # 이 파일이 직접 실행될 때만 아래 코드가 실행되도록 함
    get_yf_stock_history("AAPL", "5d") # Apple 주식 최근 5일간의 주가 이력 가져오기
    print('----')
    get_yf_stock_recommendations("AAPL") # Apple 주식 추천 정보 가져오기
    info = get_yf_stock_info("AAPL") # Apple 주식 정보 가져오기
    get_current_time('Asia/Seoul') # 서울 시간 가져오기