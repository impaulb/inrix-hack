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
    long1 = str(boundingBox['corner1']['coordinates'][0][0])
    lat1 = str(boundingBox['corner1']['coordinates'][0][1])
    long2 = str(boundingBox['corner2']['coordinates'][0][0])
    lat2 = str(boundingBox['corner2']['coordinates'][0][1])
    return lat1+'|'+long1+','+lat2+'|'+long2

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
        
        print("### TOTAL RISK: " + str(risk) + "\n")
        
        risks[route['id']] = risk
    
    return risks

def getTimeRisk(route):
    risk = 0
    
    travelTimeMinutes = route['travelTimeMinutes']
    abnormalMinutes = abs(route['abnormalityMinutes'])
    
    risk += min(travelTimeMinutes / 5, 50)
    risk += min(abnormalMinutes / 2, 50)
    
    print("TRAVEL TIME RISK: " + str(risk))

    return risk
    
def getSpeedRisk(route):
    risk = 0
    
    averageSpeed = route['averageSpeed']
    
    if(averageSpeed < 60 and averageSpeed > 25):
        risk += averageSpeed - 25
    elif(averageSpeed >= 60):
        risk += min(averageSpeed + 10, 100)
    
    print("SPEED RISK: " + str(risk))
    
    return risk

def getSlowdownRisk(route, token):
    headers = {'Authorization': 'Bearer ' + token}
    
    routeId = route['id']
    slowdownRequestString = BASE_URL + "v1/dangerousSlowdowns?box="+boundingBoxToString(route['boundingBox'])+'&format=json'
    
    slowdownResponseObj = json.loads(requests.get(slowdownRequestString, headers=headers).text)
    
    risk = 0
    
    for slowdown in slowdownResponseObj['result']['dangerousSlowdowns']:
        speedDelta = slowdown['speedDelta']
        risk += speedDelta - 20
    
    risk = risk / len(slowdownResponseObj['result']['dangerousSlowdowns'])
    
    if(risk > 100):
        return 100
    
    print("SLOWDOWN RISK: " + str(risk))
    
    return risk
    
