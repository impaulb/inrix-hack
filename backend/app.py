from flask import Flask, request
from dotenv import load_dotenv

import json
import requests
import os

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
    wp1 = request.args.get('wp1', default = '37.7958,-122.3938', type = str)
    wp2 = request.args.get('wp2', default = '37.7212,-122.4919', type = str)
    
    token = getToken()
    
    routes = getRoutes(token, wp1, wp2)
    
    return routes

def getToken():
    headers = {}
    
    tokenRequestString = BASE_URL + 'auth/v1/appToken?appId=' + APP_ID + '&hashToken=' + HASH_TOKEN
    tokenResponseObj = json.loads(requests.get(tokenRequestString, headers=headers).text)
    
    return tokenResponseObj['result']['token']

def getRoutes(token, wp1, wp2):
    headers = {'Authorization': 'Bearer ' + token}
    
    routeRequestString = BASE_URL + 'findRoute?wp_1=' + wp1 + '&wp_2=' + wp2 + '&format=json'
    routeResponseObj = json.loads(requests.get(routeRequestString, headers=headers).text)
    
    return routeResponseObj['result']
    
    