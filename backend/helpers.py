import json
import os
import requests

from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')
HASH_TOKEN = os.getenv('HASH_TOKEN')
EXPIRATION_DATE = os.getenv('EXPIRATION_DATE')
BASE_URL = os.getenv('BASE_URL')

def boundingBoxToString(boundingBox):
    lat1 = str(boundingBox['corner1']['coordinates'][0][0])
    long1 = str(boundingBox['corner1']['coordinates'][0][1])
    lat2 = str(boundingBox['corner2']['coordinates'][0][0])
    long2 = str(boundingBox['corner2']['coordinates'][0][1])
    return lat1+'|'+long1+'|'+lat2+'|'+long2

def getToken():
    headers = {}

    tokenRequestString = BASE_URL + 'auth/v1/appToken?appId=' + APP_ID + '&hashToken=' + HASH_TOKEN
    tokenResponseObj = json.loads(requests.get(tokenRequestString, headers=headers).text)

    return tokenResponseObj['result']['token']

def getRoutes(token, wp1, wp2):
    headers = {'Authorization': 'Bearer ' + token}

    routeRequestString = BASE_URL + 'findRoute?wp_1=' + wp1 + '&wp_2=' + wp2 + '&format=json&maxAlternates=2&routeOutputFields=ALL'
    routeResponseObj = json.loads(requests.get(routeRequestString, headers=headers).text)

    return routeResponseObj['result']['trip']['routes']

def formatRoutesForFrontEnd(routes, risks):
    response = {'routes': []}
    
    for route in routes:
        center1 = (route['boundingBox']['corner1']['coordinates'][0][0] + route['boundingBox']['corner2']['coordinates'][0][0]) / 2
        center2 = (route['boundingBox']['corner1']['coordinates'][0][1] + route['boundingBox']['corner2']['coordinates'][0][1]) / 2
        
        boundingBox = {'center': [center1, center2], 'radius': max(abs(route['boundingBox']['corner1']['coordinates'][0][0]-center1), abs(route['boundingBox']['corner1']['coordinates'][0][1]-center2)) * 111111}
        
        response['routes'].append({'id': route['id'], 'risk': risks[route['id']], 'boundingBox': boundingBox, 'points': route['points']['coordinates']})
    
    return response

def getRisk(routes, token):
    risks = {}
    
    for route in routes:
        risk = 0
        risk += 0.25 * getTimeRisk(route)
        risk += 0.25 * getSpeedRisk(route)
        risk += 0.25 * getSlowdownRisk(route, token)
        
        print("RISK : " + str(risk) + "\n")
        
        risks[route['id']] = risk
    
    return risks

def getTimeRisk(route):
    risk = 0
    
    travelTimeMinutes = route['travelTimeMinutes']
    abnormalMinutes = abs(route['abnormalityMinutes'])
    
    if(travelTimeMinutes >= 10 and travelTimeMinutes < 30):
        risk += 10
    elif(travelTimeMinutes >= 30 and travelTimeMinutes < 50):
        risk += 20
    elif(travelTimeMinutes >= 50 and travelTimeMinutes < 70):
        risk += 30
    elif(travelTimeMinutes >= 70):
        risk += 50
        
    if(abnormalMinutes >= 5 and abnormalMinutes < 10):
        risk += 10
    elif(abnormalMinutes >= 15 and abnormalMinutes < 20):
        risk += 20
    elif(abnormalMinutes >= 20 and abnormalMinutes < 25):
        risk += 30
    elif(abnormalMinutes >= 25 and abnormalMinutes < 30):
        risk += 40
    elif(abnormalMinutes >= 30):
        risk += 50
    
    print("TRAVEL TIME: " + str(travelTimeMinutes))
    print("ABNORMAL MINUTES: " + str(abnormalMinutes))
    
    return risk
    
def getSpeedRisk(route):
    risk = 0
    
    averageSpeed = route['averageSpeed']
    
    if(averageSpeed >= 25 and averageSpeed < 30):
        risk += 10
    elif(averageSpeed >= 30 and averageSpeed < 35):
        risk += 20
    elif(averageSpeed >= 40 and averageSpeed < 45):
        risk += 30
    elif(averageSpeed >= 45 and averageSpeed < 50):
        risk += 40
    elif(averageSpeed >= 50 and averageSpeed < 55):
        risk += 50
    elif(averageSpeed >= 55 and averageSpeed < 60):
        risk += 60
    elif(averageSpeed >= 60 and averageSpeed < 65):
        risk += 70
    elif(averageSpeed >= 65 and averageSpeed < 70):
        risk += 80
    elif(averageSpeed >= 70 and averageSpeed < 75):
        risk += 90
    elif(averageSpeed >= 75):
        risk += 100
        
    print("SPEED: " + str(averageSpeed))
    
    return risk

def getSlowdownRisk(route, token):
    headers = {'Authorization': 'Bearer ' + token}
    
    routeId = route['id']
    slowdownRequestString = BASE_URL + "v1/dangerousSlowdowns?box="+boundingBoxToString(route['boundingBox'])
    
    slowdownResponseObj = json.loads(requests.get(slowdownRequestString, headers=headers).text)
    
    return '1'
    