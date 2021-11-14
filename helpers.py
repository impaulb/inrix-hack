import json
import os
import requests
import math

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

        incidents = getIncidentsRisk(route, token)  * 1
        time = getTimeRisk(route)                   * 1
        speed = getSpeedRisk(route)                 * 0.25
        slowdown = getSlowdownRisk(route, token)    * 0.5
        weather = getWeatherRisk(route)             * 0.25
        road = getRoadRisk(route)                   * 1

        risk = math.ceil(incidents + time + speed + slowdown + weather)
        print("INCIDENT RISK: " + str(incidents))
        print("TIME RISK: " + str(time))
        print("SPEED RISK: " + str(speed))
        print("SLOWDOWN RISK: " + str(slowdown))
        print("WEATHER RISK: " + str(weather))
        print("ROAD RISK: " + str(road))
        print("### TOTAL RISK: " + str(risk) + "\n")

        risks[route['id']] = {'total': risk, 'road': road, 'incidents': incidents, 'time': time, 'speed': speed, 'slowdown': slowdown, 'weather': weather}

    return risks

def getRoadRisk(route):
    risk = 0
    roads = route['summary']['roads']
    
    for road in roads:
        roadType = road['roadClass']
        
        # Highway
        if(roadType == 1):
            risk += 10
        
        # Major Artery
        if(roadType == 2):
            risk += 5
            
        # Major Road
        if(roadType == 3):
            risk += 3
        
        # All other types (neighborhood)
        if(roadType > 3):
            risk +=1
    
    if(risk > 100):
        return 100
    
    return risk

def getIncidentsRisk(route, token):
    risk = 0
    incidents = getIncidents(route, token)

    for incident in incidents:
        risk += 10 * int(incident['severity'])

    return risk

def getIncidents(route, token):
    incidentIds = ''

    if 'incidents' in route.keys():
        for incident in route['incidents']:
            incidentIds += str(incident)+','
        incidentIds = incidentIds[:-1]
    else:
        return {}

    headers = {'Authorization': 'Bearer ' + token}

    incidentRequestString = BASE_URL + 'v1/incidents?ids=' + incidentIds + '&format=json'
    incidents = json.loads(requests.get(incidentRequestString, headers=headers).text)

    return incidents['result']['incidents']

def getTimeRisk(route):
    risk = 0

    travelTimeMinutes = route['travelTimeMinutes']
    abnormalMinutes = abs(route['abnormalityMinutes'])

    risk += min(travelTimeMinutes / 5, 50)
    risk += min(abnormalMinutes / 2, 50)

    return risk

def getSpeedRisk(route):
    risk = 0

    averageSpeed = route['averageSpeed']

    risk += min(averageSpeed + 10, 100)

    return risk

def getSlowdownRisk(route, token):
    headers = {'Authorization': 'Bearer ' + token}

    routeId = route['id']
    slowdownRequestString = BASE_URL + "v1/dangerousSlowdowns?box="+boundingBoxToString(route['boundingBox'])+'&format=json'

    slowdownResponseObj = json.loads(requests.get(slowdownRequestString, headers=headers).text)

    risk = 0

    if('result' not in slowdownResponseObj.keys()):
        return risk

    if(len(slowdownResponseObj['result']['dangerousSlowdowns']) == 0):
        return risk

    for slowdown in slowdownResponseObj['result']['dangerousSlowdowns']:
        speedDelta = slowdown['speedDelta']
        risk += speedDelta - 20

    risk = risk / len(slowdownResponseObj['result']['dangerousSlowdowns'])

    if(risk > 100):
        return 100

    return risk

def getWeatherRisk(route):
    weatherRequestString = 'http://api.weatherapi.com/v1/current.json?key=6f47484c009940f1915234049211311&q=San Francisco&aqi=no'
    weatherResponseObj = json.loads(requests.get(weatherRequestString).text)['current']

    risk = 0

    if(not weatherResponseObj['is_day']):
        risk += 25

    risk += weatherResponseObj['gust_mph']

    risk += math.ceil((weatherResponseObj['condition']['code'] - 1000) / 3)

    return risk
