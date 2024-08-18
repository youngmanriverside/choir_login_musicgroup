import gradio as gr
import pandas as pd
from flask import Flask, request, jsonify
from datetime import datetime
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend



# 初始化 Flask 應用
app = Flask(__name__)


# 初始化 DataFrames
attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])
reservation_df = pd.DataFrame(columns=["暱稱", "預約日期", "預約時間"])
leave_df = pd.DataFrame(columns=["暱稱", "請假日期", "請假原因"])

# Flask 路由
@app.route('/sign_in', methods=['POST'])
def sign_in_api():
    global attendance_df
    data = request.json
    nickname = data.get('nickname', '')
    date = data.get('date', '')
    time = data.get('time', '')
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
def make_reservation_api():
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
def request_leave_api():
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
def query_records_api():
    data = request.json
    nickname = data.get('nickname', '')
    if not nickname:
        return jsonify({'error': '暱稱不能为空'}), 400

    attendance = attendance_df[attendance_df['暱稱'] == nickname].to_dict(orient='records')
    reservations = reservation_df[reservation_df['暱稱'] == nickname].to_dict(orient='records')
    leaves = leave_df[leave_df['暱稱'] == nickname].to_dict(orient='records')

    return jsonify({
        'attendance': attendance,
        'reservations': reservations,
        'leaves': leaves
    })

# Gradio 函數
def sign_in(nickname, date, time):
    response = app.test_client().post('/sign_in', json={'nickname': nickname, 'date': date, 'time': time})
    data = response.get_json()
    if response.status_code == 200:
        return data['result'], pd.DataFrame(data['attendance'])
    else:
        return f"簽到失敗：{data.get('error', '未知錯誤')}", pd.DataFrame()

def make_reservation(nickname, date, time):
    response = app.test_client().post('/make_reservation', json={'nickname': nickname, 'date': date, 'time': time})
    data = response.get_json()
    if response.status_code == 200:
        return data['result'], pd.DataFrame(data['reservations'])
    else:
        return f"預約失敗：{data.get('error', '未知錯誤')}", pd.DataFrame()

def request_leave(nickname, date, reason):
    response = app.test_client().post('/request_leave', json={'nickname': nickname, 'date': date, 'reason': reason})
    data = response.get_json()
    if response.status_code == 200:
        return data['result'], pd.DataFrame(data['leaves'])
    else:
        return f"請假失敗：{data.get('error', '未知錯誤')}", pd.DataFrame()

def query_records(nickname):
    response = app.test_client().post('/query_records', json={'nickname': nickname})
    data = response.get_json()
    if response.status_code == 200:
        attendance = pd.DataFrame(data['attendance'])
        reservations = pd.DataFrame(data['reservations'])
        leaves = pd.DataFrame(data['leaves'])
        result = f"{nickname} 的記錄查詢成功"
        return result, attendance, reservations, leaves
    else:
        error_message = f"查詢失敗：{data.get('error', '未知錯誤')}"
        return error_message, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def get_current_date_time():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    return current_date, current_time

# Gradio 界面
with gr.Blocks(title="合唱團系統") as demo:
    gr.Markdown("# 合唱團系統")
    
    current_date, current_time = get_current_date_time()


    with gr.Tab("簽到"):
        nickname_input = gr.Textbox(label="輸入暱稱")
        sign_in_date = gr.Textbox(label="簽到日期", value=current_date)
        sign_in_time = gr.Textbox(label="簽到時間", value=current_time)
        sign_in_button = gr.Button("簽到")
        sign_in_result = gr.Textbox(label="簽到結果")
        sign_in_records = gr.DataFrame(label="簽到記錄")
        sign_in_button.click(sign_in, inputs=nickname_input, outputs=[sign_in_result, sign_in_records])
    
    with gr.Tab("預約"):
        with gr.Row():
            reserve_nickname = gr.Textbox(label="暱稱")
            reserve_date = gr.Textbox(label="預約日期" , value=current_date)
            reserve_time = gr.Textbox(label="預約時間", value=current_time)
        reserve_button = gr.Button("預約")
        reserve_result = gr.Textbox(label="預約結果")
        reserve_records = gr.DataFrame(label="預約記錄")
        reserve_button.click(make_reservation, inputs=[reserve_nickname, reserve_date, reserve_time], outputs=[reserve_result, reserve_records])
    
    with gr.Tab("請假"):
        with gr.Row():
            leave_nickname = gr.Textbox(label="暱稱")
            leave_date = gr.Textbox(label="請假日期", value=current_date)
            leave_reason = gr.Textbox(label="請假原因")
        leave_button = gr.Button("請假")
        leave_result = gr.Textbox(label="請假結果")
        leave_records = gr.DataFrame(label="請假記錄")
        leave_button.click(request_leave, inputs=[leave_nickname, leave_date, leave_reason], outputs=[leave_result, leave_records])
    
    with gr.Tab("查詢記錄"):
        query_nickname = gr.Textbox(label="輸入暱稱查詢記錄")
        query_button = gr.Button("查詢")
        query_result = gr.Textbox(label="查詢結果")
        query_attendance = gr.DataFrame(label="簽到記錄")
        query_reservations = gr.DataFrame(label="預約記錄")
        query_leaves = gr.DataFrame(label="請假記錄")
        query_button.click(query_records, inputs=query_nickname, outputs=[query_result, query_attendance, query_reservations, query_leaves])

if __name__ == "__main__":
    demo.launch(share=True)