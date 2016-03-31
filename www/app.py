from flask import Flask, request, abort
from readability.readability import Document
import requests
import html2text

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/get', methods=['GET'])
def get():
    url = request.args.get('url') #使用request获取GET参数
    r = requests.get(url)
    r.encoding = 'utf-8'
    readable_article = Document(r.text).summary()
#    markdownify_article = html2text.html2text(readable_article)
    return html2text.html2text(readable_article)

if __name__ == "__main__":
    app.run()