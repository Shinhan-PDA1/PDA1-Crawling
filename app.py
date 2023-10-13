from flask import Flask, request, jsonify
import pandas as pd
import requests
import json

app = Flask(__name__)

def scrape_finance_data(code):
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

@app.route('/api/v1/crawling', methods=['POST'])
def crawling():
    try:
        code = request.args.get('code')
        if code:
            result = scrape_finance_data(code)
            return jsonify(result), 200
        else:
            return jsonify({"error": "종목 코드를 입력해주세요."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 800

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
