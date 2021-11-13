import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request

app = Flask(__name__)

appId = os.getenv("appID")
appKey = os.getenv("appKey")
hashToken = os.getenv("hashToken")
expirationDate = os.getenv("expeirationDate")

# Get risk for a route using start and end point
@app.route('/risk', methods=['GET'])
def risk():
    wp_1 = request.args.get('wp_1', default = 'ERR', type = str)
    return wp_1
