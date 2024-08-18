import gradio as gr
import pandas as pd
import matplotlib
import requests
from datetime import datetime
from userlogin import sign_in,make_reservation,request_leave


matplotlib.use('Agg')  # Use a non-GUI backend

# 初始化DataFrames
attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])
reservation_df = pd.DataFrame(columns=["暱稱", "預約日期", "預約時間"])
leave_df = pd.DataFrame(columns=["暱稱", "請假日期", "請假原因"])


# 設置後端服務器的URL
SERVER_URL = "http://localhost:5000"

def sign_in(nickname):
    try:
        response = requests.post(f'{SERVER_URL}/sign_in', json={'nickname': nickname})
        if response.status_code == 200:
            data = response.json()
            return data['result'], pd.DataFrame(data['attendance'])
        else:
            return f"簽到失敗：{response.json().get('error', '未知錯誤')}", pd.DataFrame()
    except requests.exceptions.ConnectionError:
        return "無法連接到服務器。請確保後端服務正在運行。", pd.DataFrame()

def make_reservation(nickname, date, time):
    try:
        response = requests.post(f'{SERVER_URL}/make_reservation', json={'nickname': nickname, 'date': date, 'time': time})
        if response.status_code == 200:
            data = response.json()
            return data['result'], pd.DataFrame(data['reservations'])
        else:
            return f"預約失敗：{response.json().get('error', '未知錯誤')}", pd.DataFrame()
    except requests.exceptions.ConnectionError:
        return "無法連接到服務器。請確保後端服務正在運行。", pd.DataFrame()

def request_leave(nickname, date, reason):
    try:
        response = requests.post(f'{SERVER_URL}/request_leave', json={'nickname': nickname, 'date': date, 'reason': reason})
        if response.status_code == 200:
            data = response.json()
            return data['result'], pd.DataFrame(data['leaves'])
        else:
            return f"請假失敗：{response.json().get('error', '未知錯誤')}", pd.DataFrame()
    except requests.exceptions.ConnectionError:
        return "無法連接到服務器。請確保後端服務正在運行。", pd.DataFrame()

def query_records(nickname):
    try:
        response = requests.post(f'{SERVER_URL}/query_records', json={'nickname': nickname})
        if response.status_code == 200:
            data = response.json()
            attendance = pd.DataFrame(data['attendance'])
            reservations = pd.DataFrame(data['reservations'])
            leaves = pd.DataFrame(data['leaves'])
            result = f"{nickname} 的記錄查詢成功"
            return result, attendance, reservations, leaves
        else:
            error_message = f"查詢失敗：{response.json().get('error', '未知錯誤')}"
            return error_message, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except requests.exceptions.ConnectionError:
        return "無法連接到服務器。請確保後端服務正在運行。", pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


with gr.Blocks(title="合唱團系統") as demo:
    gr.Markdown("# 合唱團系統")
    
    with gr.Tab("簽到"):
        nickname_input = gr.Textbox(label="輸入暱稱")
        sign_in_button = gr.Button("簽到")
        sign_in_result = gr.Textbox(label="簽到結果")
        sign_in_records = gr.DataFrame(label="簽到記錄")
        sign_in_button.click(sign_in, inputs=nickname_input, outputs=[sign_in_result, sign_in_records])
    
    with gr.Tab("預約"):
        with gr.Row():
            reserve_nickname = gr.Textbox(label="暱稱")
            reserve_date = gr.Textbox(label="預約日期 (YYYY-MM-DD)")
            reserve_time = gr.Textbox(label="預約時間 (HH:MM)")
        reserve_button = gr.Button("預約")
        reserve_result = gr.Textbox(label="預約結果")
        reserve_records = gr.DataFrame(label="預約記錄")
        reserve_button.click(make_reservation, inputs=[reserve_nickname, reserve_date, reserve_time], outputs=[reserve_result, reserve_records])
    
    with gr.Tab("請假"):
        with gr.Row():
            leave_nickname = gr.Textbox(label="暱稱")
            leave_date = gr.Textbox(label="請假日期 (YYYY-MM-DD)")
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
    demo.launch(share=True)  # share=True 生成共享連結



# matplotlib.use('Agg')  # Use a non-GUI backend

# # 初始化一个空的DataFrame来存储签到记录
# attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])

# def sign_in(nickname):
#     global attendance_df
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     new_record = pd.DataFrame({"暱稱": [nickname], "簽到時間": [current_time]})
#     attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
#     return f"{nickname} 簽到成功！時間：{current_time}", attendance_df

# # 创建Gradio界面
# gradio = gr.Interface(
#     fn=sign_in,
#     inputs=gr.Textbox(label="輸入暱稱"),
#     outputs=[
#         gr.Textbox(label="簽到結果"),
#         gr.Dataframe(label="簽到記錄")
#     ],
#     title="合唱團簽到系統",
#     description="請輸入暱稱進行簽到"
# )

# # 启动应用
# if __name__ == "__main__":
#     gradio.launch(inline=False)


