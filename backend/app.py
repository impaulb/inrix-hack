from flask import Flask

app = Flask(__name__)

appId = "xznhrx39ag"
appKey = "TSuX6rbGPR1JCLTgHWETX9TvEztAgzU04Bhy7fxT"
hashToken = "eHpuaHJ4MzlhZ3xUU3VYNnJiR1BSMUpDTFRnSFdFVFg5VHZFenRBZ3pVMDRCaHk3ZnhU"
expirationDate = "2021-11-28T18:46:48.65Z"

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"