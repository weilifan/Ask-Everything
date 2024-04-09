from flask import request, Flask
from transformers import AutoTokenizer, AutoModel
# import json
import os

app = Flask(__name__)


@app.route("/answer", methods=["POST"])
def send():
    global model, tokenizer

    param = request.json
    result = dict()
    if "sentence" in param:
        sentence = param["sentence"]

        response, _ = model.chat(tokenizer, sentence, history=[])

        result = {
            "ans": response
        }

    if "text" in param:
        text = param["text"]
        idx = tokenizer([text], return_tensors="pt")
        idx = idx["input_ids"].to(model.device)

        emb = model.transformer(idx, return_dict=False)[0]
        emb = emb.transpose(0, 1)
        emb = emb[:, -1]
        emb = emb.detach().cpu().numpy().tolist()
        result = {
            "emb": str(emb)
        }
    return result


if __name__ == "__main__":
    model_path = os.path.abspath("D:/Project/2309/2022CFF-Small-sample-data-classification-task/utils/chat_glm_model")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).cuda().half()

    model = model.eval()

    # app.run(host="0.0.0.0",port=8080)
    app.run(host="127.0.0.1")
