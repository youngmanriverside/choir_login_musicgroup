import gradio as gr
import pandas as pd
import matplotlib

from datetime import datetime
from userlogin import sign_in


matplotlib.use('Agg')  # Use a non-GUI backend

# 初始化一个空的DataFrame来存储签到记录
attendance_df = pd.DataFrame(columns=["暱稱", "簽到時間"])

def sign_in(nickname):
    global attendance_df
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame({"暱稱": [nickname], "簽到時間": [current_time]})
    attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
    return f"{nickname} 簽到成功！時間：{current_time}", attendance_df

# 创建Gradio界面
gradio = gr.Interface(
    fn=sign_in,
    inputs=gr.Textbox(label="輸入暱稱"),
    outputs=[
        gr.Textbox(label="簽到結果"),
        gr.Dataframe(label="簽到記錄")
    ],
    title="合唱團簽到系統",
    description="請輸入暱稱進行簽到"
)

# 启动应用
if __name__ == "__main__":
    gradio.launch(inline=False)


