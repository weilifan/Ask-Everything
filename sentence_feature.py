import os
import shutil

# import docx
from pypdf import PdfReader
import torch
from transformers import AutoTokenizer, AutoModel
import faiss
import gradio as gr


def get_data(root_path):
    all_content = []
    files = os.listdir(root_path)

    for file in files:
        path = os.path.join(root_path, file)
        if path.endswith(".docx"):
            doc = docx.Document(path)
            paragraphs = doc.paragraphs
            content = [i.text for i in paragraphs]

            texts = ""
            for text in content:
                if len(texts) <= 1:
                    continue
                if len(texts) > 150:
                    all_content.append(texts)
                    texts = ""
                texts += text
        elif path.endswith(".pdf"):
            with open(path, "rb") as f:
                pdf_reader = PdfReader(f)

                pages_info = pdf_reader.pages

                for page_info in pages_info:
                    content = page_info.extract_text()
                    texts = ""
                    for text in content:
                        if len(texts) <= 1:
                            texts += text
                        if len(texts) > 150:
                            all_content.append(texts)
                            texts = ""
        elif path.endswith(".txt"):
            with open(path, "rb") as f:
                content = f.read()
                all_content.append(content)

    return all_content


class DFaiss:
    def __init__(self):
        self.index = faiss.IndexFlatL2(4096)
        self.text_str_list = []


    def search(self, emb):

        D, I = self.index.search(emb, 3)

        if D[0][0] > distance:
            content = ""
        else:
            content = self.text_str_list[I[0][0]]
        return content

class Dprompt:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)

        self.myfaiss = DFaiss()

        self.load_data("datas")

    def answer(self, text):
        emb = self.get_sentence_emb(text, is_numpy=True)
        prompt = self.myfaiss.search(emb)
        if prompt:
            prompt_content = f"请根据内容回答问题，内容是：{prompt}, 问题是：{text}"
        else:
            prompt_content = text

        response, history = self.model.chat(self.tokenizer, prompt_content, history=[])

        return response

    def load_data(self, root_path):
        all_content = get_data(root_path)
        for content in all_content:
            self.myfaiss.text_str_list.append(content)
            emb = self.get_sentence_emb(content, is_numpy=True)
            self.myfaiss.index.add(emb)

    def get_sentence_emb(self, text, is_numpy=False):
        idx = self.tokenizer([text], return_tensors="pt")
        idx = idx["input_ids"].to(device)

        self.model.to(idx.device)
        emb = self.model.transformer(idx, return_dict=False)[0]
        emb = emb.transpose(0, 1)
        emb = emb[:, -1]

        if is_numpy:
            emb = emb.detach().cpu()
        return emb


def load_file(files):
    global prompt_model

    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.mkdir("temp")

    for file in files:
        n = os.path.basename(file.orig_name)
        p = os.path.join("temp", n)
        shutil.move(file.name, p)

    prompt_model.myfaiss.index.reset()
    prompt_model.load_data("temp")

    return [[None, "文件加载成功😎"]]


if __name__ == "__main__":
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    distance = 35000
    model_path = os.path.abspath("D:/Project/2309/2022CFF-Small-sample-data-classification-task/utils/chat_glm_model")

    prompt_model = Dprompt()

    with gr.Blocks() as Robot:
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    [[None, "this is😎机器人"], [None, "😎😭"]],
                    height=600
                )
                query = gr.Textbox(placeholder="输入问题，回车提问😎")
            with gr.Column(scale=1):
                file = gr.File(file_count="multiple")
                button = gr.Button("加载文件")
                button.click(load_file, inputs=file, outputs=chatbot)

    Robot.launch(server_name="127.0.0.1", server_port=9999, share=False)



    while True:
        text = input("输入:")
        ans = prompt_model.answer(text)
        print(ans)

