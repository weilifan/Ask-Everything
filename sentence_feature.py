import os
# import docx
from pypdf import PdfReader
import torch
from transformers import AutoTokenizer, AutoModel
import faiss


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
                    text = page_info.extract_text()
                    all_content.append(text)
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
        idx = idx["input_idx"].to(device)

        emb = self.model.transformer(idx, return_dict=False)[0]
        emb = emb.transpose(0, 1)
        emb = emb[:, -1]

        if is_numpy:
            emb = emb.detach().cpu()
        return emb


if __name__ == "__main__":
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    distance = 35000
    model_path = os.path.abspath("E:/2022CFF-Small-sample-data-classification-task/utils/chat_glm_model")

    prompt_model = Dprompt()

    while True:
        text = input("输入:")
        ans = prompt_model.answer(text)
        print(ans)

