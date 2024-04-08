import os
import search_txt
import search_web
import gradio as gr
# import shutil
#
# import numpy as np
# # import docx
# from pypdf import PdfReader
# import torch
# from transformers import AutoTokenizer, AutoModel
# import faiss
# import gradio as gr
# import requests




if __name__ == "__main__":
    # device = "cuda:0" if torch.cuda.is_available() else "cpu"
    distance = 80000
    model_path = os.path.abspath("D:/Project/2309/2022CFF-Small-sample-data-classification-task/utils/chat_glm_model")

    search_t = search_txt.Search()

    with gr.Blocks() as Robot:
        with gr.Tab("文档问答"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        [[None, "this is😎机器人"]],
                        height=600
                    )
                    query = gr.Textbox(placeholder="输入问题，回车提问😎", show_label=False, container=False)
                with gr.Column(scale=1):
                    file = gr.File(file_count="multiple")
                    button = gr.Button("加载文件")
                button.click(search_t.load_file, inputs=file, outputs=chatbot, show_progress=True)
                query.submit(search_t.ans, inputs=[query, chatbot], outputs=chatbot, show_progress=True)

        with gr.Tab("联网搜索"):
            chioce = gr.Radio(choices=["本地模型", "知乎回答", "百度知道", "CSDN"], label="功能选择", value="知乎回答")
            chatbot = gr.Chatbot([[None, "this is😎机器人"]], show_label=False).style(height=450)

            query = gr.Textbox(show_label=False, placeholder="请输入:").style(container=False)

            with gr.Row():
                with gr.Column():
                    button1 = gr.Button(value="生成回答")
                with gr.Column():
                    button2 = gr.Button(value="清空历史")
            button1.click(search_web.ans, inputs=[chatbot, query, chioce], outputs=[chatbot])
            query.submit(search_web.ans, inputs=[chatbot, query, chioce], outputs=[chatbot])

    # with gr.Blocks() as Robot:
    #     choice = gr.Radio(choices=["本地文档", "知乎回答", "百度知道", "CSDN"], label="功能选择", value="本地文档")
    #
    #     # local_doc_row = create_local_doc_layout()
    #     # search_row = create_search_layout()
    #
    #     # local_doc_row.visible = True
    #     # search_row.visible = False
    #
    #     choice.change(fn=show_component, inputs=[choice], outputs=[])

        # with gr.Row():
        #     with gr.Column(scale=3):
        #         chatbot = gr.Chatbot(
        #             [[None, "this is😎机器人"]],
        #             height=600
        #         )
        #         query = gr.Textbox(placeholder="输入问题，回车提问😎", show_label=False, container=False)
        #     with gr.Column(scale=1):
        #         file = gr.File(file_count="multiple")
        #         button = gr.Button("加载文件")
        #     button.click(load_file, inputs=file, outputs=chatbot, show_progress=True)
        #     query.submit(ans_stream, inputs=[query, chatbot], outputs=chatbot, show_progress=True)

    Robot.queue(concurrency_count=3).launch(server_name="127.0.0.1", server_port=9999, share=False)
