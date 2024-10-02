import gradio as gr
import pandas as pd
from flask import Flask, request, jsonify
from datetime import datetime
import matplotlib
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import io
import base64
import cv2
import numpy as np

matplotlib.use('Agg')  # Use a non-GUI backend

# 初始化 Flask 應用
app = Flask(__name__)

# 初始化 DataFrames
attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])
reservation_df = pd.DataFrame(columns=["暱稱", "預約日期", "預約時間"])
leave_df = pd.DataFrame(columns=["暱稱", "請假日期", "請假原因"])

# 生成QR碼的函數
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# 解碼QR碼的函數
def decode_qr_code(image):
    decoded = decode(Image.fromarray(image))
    if decoded:
        return decoded[0].data.decode('utf-8')
    return None

# Flask 路由
@app.route('/sign_in', methods=['POST'])
def sign_in_api():
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

# ... (其他Flask路由保持不變) ...

# Gradio 函數
def sign_in(nickname, date, time):
    response = app.test_client().post('/sign_in', json={'nickname': nickname, 'date': date, 'time': time})
    data = response.get_json()
    if response.status_code == 200:
        return data['result'], pd.DataFrame(data['attendance'])
    else:
        return f"簽到失敗：{data.get('error', '未知錯誤')}", pd.DataFrame()

def generate_qr_for_sign_in(nickname):
    qr_data = f"SIGN_IN:{nickname}"
    qr_code = generate_qr_code(qr_data)
    return qr_code

def scan_qr_for_sign_in(image):
    if image is None:
        return "請先開啟攝像頭並掃描QR碼", pd.DataFrame()
    
    decoded_data = decode_qr_code(image)
    if decoded_data and decoded_data.startswith("SIGN_IN:"):
        nickname = decoded_data.split(":")[1]
        current_date, current_time = get_current_date_time()
        result, df = sign_in(nickname, current_date, current_time)
        return f"QR碼掃描成功！{result}", df
    return "無效的QR碼，請重新掃描", pd.DataFrame()

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
        with gr.Row():
            nickname_input = gr.Textbox(label="輸入暱稱")
            sign_in_date = gr.Textbox(label="簽到日期", value=current_date)
            sign_in_time = gr.Textbox(label="簽到時間", value=current_time)
        sign_in_button = gr.Button("簽到")
        sign_in_result = gr.Textbox(label="簽到結果")
        sign_in_records = gr.DataFrame(label="簽到記錄")
        sign_in_button.click(sign_in, inputs=[nickname_input, sign_in_date, sign_in_time], outputs=[sign_in_result, sign_in_records])
        
        gr.Markdown("## QR碼簽到")
        with gr.Row():
            qr_nickname_input = gr.Textbox(label="輸入暱稱生成QR碼")
            generate_qr_button = gr.Button("生成QR碼")
            qr_code_image = gr.Image(label="QR碼")
        generate_qr_button.click(generate_qr_for_sign_in, inputs=qr_nickname_input, outputs=qr_code_image)
        
        gr.Markdown("## 攝像頭QR碼掃描")
        camera_input = gr.Image(source="webcam", streaming=True, label="掃描QR碼")
        qr_scan_button = gr.Button("掃描並簽到")
        qr_sign_in_result = gr.Textbox(label="QR碼簽到結果")
        qr_sign_in_records = gr.DataFrame(label="QR碼簽到記錄")
        qr_scan_button.click(scan_qr_for_sign_in, inputs=camera_input, outputs=[qr_sign_in_result, qr_sign_in_records])
    
    # ... (其他Tab保持不變) ...

if __name__ == "__main__":
    demo.launch(share=True)