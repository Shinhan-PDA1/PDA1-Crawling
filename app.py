from flask import Flask, request, jsonify
import pandas as pd
import requests
import json
import FinanceDataReader as fdr
from datetime import datetime, timedelta
from flask_cors import CORS
import ssl

app = Flask(__name__)
CORS(app)

def scrape_financial_statements_data(code):
    URL = f"https://finance.naver.com/item/main.nhn?code={code}"
    req = requests.get(URL)

    df = pd.read_html(req.text)[3]
    df.set_index(df.columns[0],inplace=True)
    df.index.rename('주요재무정보', inplace=True)
    df.columns = df.columns.droplevel(2)
    df.fillna("-", inplace=True)

    
    annual_date = pd.DataFrame(df).xs('최근 연간 실적',axis=1)
    quater_date = pd.DataFrame(df).xs('최근 분기 실적',axis=1)

    annual_json_data = annual_date.to_json(force_ascii=False)
    quater_json_data = quater_date.to_json(force_ascii=False)

    a_data = json.loads(annual_json_data)
    q_data = json.loads(quater_json_data)
    total_json = {"최근 연간 실적": a_data, "최근 분기 실적": q_data}
    
    return total_json

def get_major_stock_data():
    # 45일 전 날짜 계산
    current_date = datetime.now();
    delta = timedelta(days=45)
    date_45_days_ago = current_date - delta
    date_formatted = date_45_days_ago.strftime('%Y-%m-%d')

    # KOSPI, KOSDAQ, KOSPI200 데이터 가져오기
    kospi = fdr.DataReader('KS11', date_formatted).round(3)
    kosdaq = fdr.DataReader('KQ11', date_formatted).round(3)
    kospi200 = fdr.DataReader('KS200', date_formatted).round(3)

    major_krxData = pd.concat([kospi['Close'], kosdaq['Close'], kospi200['Close']], axis=1)
    major_krxData.columns = ['kospi', 'kosdaq', 'kospi200']
    major_krxData['date'] = major_krxData.index.strftime('%Y-%m-%d')

    json_result = major_krxData.to_dict(orient="records")
    
    return json_result


@app.route('/api/v1/crawling', methods=['POST'])
def crawling():
    try:
        code = request.args.get('code')
        if code:
            result = scrape_financial_statements_data(code)
            return jsonify(result), 200
        else:
            return jsonify({"error": "종목 코드를 입력해주세요."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 800

@app.route('/api/v1/getmajorstock', methods=['POST'])
def get_stock_data():
    try:
        result = get_major_stock_data()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 800

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4000, debug=False)
