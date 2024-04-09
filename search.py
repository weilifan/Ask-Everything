import search_txt
import search_web
import gradio as gr

if __name__ == "__main__":
    model_url = "http://127.0.0.1:5000/answer"
    search_t = search_txt.Search(url=model_url)
    search_w = search_web.Search(url=model_url)

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
            # with gr.Row():
            #     with gr.Column():
            #         button1 = gr.Button(value="生成回答")
            #     with gr.Column():
            #         button2 = gr.Button(value="清空历史")
            #     button1.click(search_t.ans, inputs=[query, chatbot], outputs=chatbot, show_progress=True)

        with gr.Tab("联网搜索"):
            chioce = gr.Radio(choices=["本地模型", "知乎回答", "百度百科"], label="功能选择", value="知乎回答")
            chatbot = gr.Chatbot([[None, "this is😎机器人"]], show_label=False).style(height=450)

            query = gr.Textbox(show_label=False, placeholder="输入问题，回车提问😎").style(container=False)

            # with gr.Row():
            #     with gr.Column():
            #         button3 = gr.Button(value="生成回答")
            #     with gr.Column():
            #         button4 = gr.Button(value="清空历史")
            # button3.click(search_web.ans, inputs=[chatbot, query, chioce], outputs=[chatbot])
            query.submit(search_w.ans, inputs=[chatbot, query, chioce], outputs=[chatbot])

    Robot.queue(concurrency_count=3).launch(server_name="127.0.0.1", server_port=9999, share=False)
