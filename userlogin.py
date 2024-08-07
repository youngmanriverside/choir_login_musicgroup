from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# 初始化一个空的DataFrame来存储签到记录
attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])

@app.route('/sign_in', methods=['POST'])
def sign_in():
    global attendance_df
    data = request.json
    nickname = data.get('nickname', '')
    if not nickname:
        return jsonify({'error': '暱稱不能为空'}), 400

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame({"暱稱": [nickname], "簽到時間": [current_time]})
    global attendance_df
    attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
    
    result_message = f"{nickname} 簽到成功！時間：{current_time}"
    
    # Convert the DataFrame to a list of dictionaries for JSON serialization
    records = attendance_df.to_dict(orient='records')
    
    return jsonify({
        'result': result_message,
        'attendance': records
    })

if __name__ == '__main__':
    app.run(debug=True)
