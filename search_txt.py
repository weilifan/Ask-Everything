import os
from pypdf import PdfReader
import faiss
import requests
import torch
import shutil
# import docx


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
                        if len(texts) <= 150:
                            texts += text
                        if len(texts) > 150:
                            all_content.append(texts)
                            texts = ""
                    all_content.append(texts)
        elif path.endswith(".txt"):
            with open(path, "rb") as f:
                content = f.read()
                all_content.append(content)

    print(all_content)
    return all_content


class DFaiss:
    def __init__(self):
        self.index = faiss.IndexFlatL2(4096)
        self.text_str_list = []

    def search(self, emb):
        distance = 80000

        D, I = self.index.search(emb, 3)
        print(D)
        print(I)

        if D[0][0] > distance:
            content = ""
        else:
            content = self.text_str_list[I[0][0]]
        return content


class Dprompt:
    def __init__(self):

        self.myfaiss = DFaiss()

        # self.load_data("datas")

    def answer(self, text):
        emb = self.get_sentence_emb(text, is_numpy=True)
        prompt = self.myfaiss.search(emb)
        if prompt:
            prompt_content = f"请根据内容回答问题，内容是：{prompt}, 问题是：{text}"
        else:
            prompt_content = text

        # response, history = self.model.chat(self.tokenizer, prompt_content, history=[])

        chatglm_url = "http://127.0.0.1:5000/answer"
        param = {
            "sentence": prompt_content
        }

        res = requests.post(chatglm_url, json=param)
        res = res.json()
        response = res["ans"]

        return response

    def load_data(self, root_path):
        all_content = get_data(root_path)
        for content in all_content:
            self.myfaiss.text_str_list.append(content)
            emb = self.get_sentence_emb(content, is_numpy=True)
            self.myfaiss.index.add(emb)

    def get_sentence_emb(self, text, is_numpy=False):
        # idx = self.tokenizer([text], return_tensors="pt")
        # idx = idx["input_ids"].to(device)
        #
        # self.model.to(idx.device)
        # emb = self.model.transformer(idx, return_dict=False)[0]
        chatglm_url = "http://127.0.0.1:5000/answer"
        param = {
            "text": text
        }

        res = requests.post(chatglm_url, json=param)
        res = res.json()
        emb = res["emb"]
        # print("hhhhh", emb)
        emb = torch.tensor(eval(emb), dtype=torch.float16)

        # emb = emb.transpose(0, 1)
        # emb = emb[:, -1]
        #
        # if is_numpy:
        #     emb = emb.detach().cpu()
        return emb


class Search:
    def __init__(self):
        self.prompt_model = Dprompt()

    def load_file(self, files):

        if os.path.exists("temp"):
            shutil.rmtree("temp")
        os.mkdir("temp")

        for file in files:
            n = os.path.basename(file.orig_name)
            p = os.path.join("temp", n)
            shutil.move(file.name, p)

        self.prompt_model.myfaiss.index.reset()
        self.prompt_model.load_data("temp")

        return [[None, "文件加载成功😎"]]


    # def ans_stream(query, his):
    #     global prompt_model
    #
    #     result = his + [[query, ""]]
    #
    #     emb = prompt_model.get_sentence_emb(query, is_numpy=True)
    #     prompt = prompt_model.myfaiss.search(emb)
    #     if prompt:
    #         prompt_content = f"请根据内容回答问题，内容是：{prompt}，问题的是：{query}"
    #     else:
    #         prompt_content = query
    #     for res, his in prompt_model.model.stream_chat(prompt_model.tokenizer, prompt_content, history=[]):
    #         result[-1] = [query, res + "😎"]
    #         yield result


    def ans(self, query, his):
        res = self.prompt_model.answer(query)

        return his + [[query, res]]


if __name__ == "__main__":
    prompt_model = Dprompt()