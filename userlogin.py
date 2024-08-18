from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
#from flask_cors import CORS


app = Flask(__name__)
#CORS(app)  # 這行允許所有來源的跨域請求

# 初始化DataFrames
attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])
reservation_df = pd.DataFrame(columns=["暱稱", "預約日期", "預約時間"])
leave_df = pd.DataFrame(columns=["暱稱", "請假日期", "請假原因"])

@app.route('/sign_in', methods=['POST'])
def sign_in():
    global attendance_df
    data = request.json
    nickname = data.get('nickname', '')
    if not nickname:
        return jsonify({'error': '暱稱不能为空'}), 400

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame({"暱稱": [nickname], "簽到時間": [current_time]})
    attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
    
    result_message = f"{nickname} 簽到成功！時間：{current_time}"
    records = attendance_df.to_dict(orient='records')
    
    return jsonify({
        'result': result_message,
        'attendance': records
    })

@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    global reservation_df
    data = request.json
    nickname = data.get('nickname', '')
    date = data.get('date', '')
    time = data.get('time', '')
    
    if not all([nickname, date, time]):
        return jsonify({'error': '所有欄位都必須填寫'}), 400

    new_reservation = pd.DataFrame({"暱稱": [nickname], "預約日期": [date], "預約時間": [time]})
    reservation_df = pd.concat([reservation_df, new_reservation], ignore_index=True)
    
    result_message = f"{nickname} 成功預約！日期：{date}，時間：{time}"
    records = reservation_df.to_dict(orient='records')
    
    return jsonify({
        'result': result_message,
        'reservations': records
    })

@app.route('/request_leave', methods=['POST'])
def request_leave():
    global leave_df
    data = request.json
    nickname = data.get('nickname', '')
    date = data.get('date', '')
    reason = data.get('reason', '')
    
    if not all([nickname, date, reason]):
        return jsonify({'error': '所有欄位都必須填寫'}), 400

    new_leave = pd.DataFrame({"暱稱": [nickname], "請假日期": [date], "請假原因": [reason]})
    leave_df = pd.concat([leave_df, new_leave], ignore_index=True)
    
    result_message = f"{nickname} 成功請假！日期：{date}，原因：{reason}"
    records = leave_df.to_dict(orient='records')
    
    return jsonify({
        'result': result_message,
        'leaves': records
    })

@app.route('/query_records', methods=['POST'])
def query_records():
    data = request.json
    nickname = data.get('nickname', '')
    if not nickname:
        return jsonify({'error': '暱稱不能为空'}), 400

    # 查詢該用戶的所有記錄
    attendance = attendance_df[attendance_df['暱稱'] == nickname].to_dict(orient='records')
    reservations = reservation_df[reservation_df['暱稱'] == nickname].to_dict(orient='records')
    leaves = leave_df[leave_df['暱稱'] == nickname].to_dict(orient='records')

    return jsonify({
        'attendance': attendance,
        'reservations': reservations,
        'leaves': leaves
    })


if __name__ == '__main__':
    app.run(debug=True) # share=True 生成共享連結