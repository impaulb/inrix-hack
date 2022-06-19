from flask import Flask, request
from dotenv import load_dotenv

import json
import requests
import os
from helpers import *

load_dotenv()

app = Flask(__name__)

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')
HASH_TOKEN = os.getenv('HASH_TOKEN')
EXPIRATION_DATE = os.getenv('EXPIRATION_DATE')
BASE_URL = os.getenv('BASE_URL')

# Get risk for a route using start and end point
@app.route('/risk', methods=['GET'])
def risk():
    wp1 = request.args.get('wp1', default = '37.857,-122.4951334', type = str)
    wp2 = request.args.get('wp2', default = '37.730904,-122.401962', type = str)

    print(wp1,wp2)

    token = getToken()

    apiRoutes = getRoutes(token, wp1, wp2)

    risks = getRisk(apiRoutes, token)

    return formatRoutesForFrontEnd(apiRoutes, risks)
