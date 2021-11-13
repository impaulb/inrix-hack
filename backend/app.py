import requests
import json

from flask import Flask, request

app = Flask(__name__)

appId = "xznhrx39ag"
appKey = "TSuX6rbGPR1JCLTgHWETX9TvEztAgzU04Bhy7fxT"
hashToken = "eHpuaHJ4MzlhZ3xUU3VYNnJiR1BSMUpDTFRnSFdFVFg5VHZFenRBZ3pVMDRCaHk3ZnhU"
expirationDate = "2021-11-28T18:46:48.65Z"

# Get risk for a route using start and end point
@app.route('/risk', methods=['GET'])
def risk():
    wp_1 = request.args.get('wp_1', default = 'ERR', type = str)
    return wp_1