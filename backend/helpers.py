import json

def boundingBoxToString( boundingBox ):
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

    routeRequestString = BASE_URL + 'findRoute?wp_1=' + wp1 + '&wp_2=' + wp2 + '&format=json'
    routeResponseObj = json.loads(requests.get(routeRequestString, headers=headers).text)

    return routeResponseObj['result']

