1. 在带有显卡的电脑上部署ChatGLM2-6b
    - 在带有显卡的电脑上运行`model_api.py`，将`model_api.py`中的`model_path = os.path.abspath`设置为存放ChatGLM2-6b模型的文件地址
    - 如果是本机，使用本地环网`app.run(host="127.0.0.1")`；如果是要部署到服务器上，使用`app.run(host="0.0.0.0",port=8080)`，使运行后出现的连接不仅仅是内网可以用
2. 将运行`model_api.py`后出现的连接填入`search.py` 的`model_url = "XXXX/answer"`
3. 运行`search.py`，点击运行后出现的链接

![img](https://github.com/weilifan/Ask-Everything/blob/master/demo.gif)
