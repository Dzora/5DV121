#!/usr/bin/env python3
"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 
"""

MRDS_URL = 'localhost:50000'

import http.client, json, time
from math import sin,cos,pi,atan2,tan,sqrt,acos,degrees,asin

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}

class UnexpectedResponse(Exception): pass

class Point:
    """ Point class represents and manipulates x,y coords. """

    def __init__(self):
        """ Create a new point at the origin """
        self.x = 0
        self.y = 0
        
class Path:

    def __init__(self):
    # Load the path from a file and convert it into a list of coordinates
        self.loadPath('Path-around-table-and-back.json')
        self.vecPath = self.vectorizePath()
    
    def loadPath(self, file_name):
    
        with open(file_name) as path_file:
            data = json.load(path_file)
    
        self.path = data
    
    def vectorizePath(self):
        vecArray = [{'X': p['Pose']['Position']['X'], \
                     'Y': p['Pose']['Position']['Y'], \
                     'Z': p['Pose']['Position']['Z']}\
                     for p in self.path]
        return vecArray        

def postSpeed(angularSpeed,linearSpeed):
    """Sends a speed command to the MRDS server"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    params = json.dumps({'TargetAngularSpeed':angularSpeed,'TargetLinearSpeed':linearSpeed})
    mrds.request('POST','/lokarria/differentialdrive',params,HEADERS)
    response = mrds.getresponse()
    status = response.status
    #response.close()
    if status == 204:
        return response
    else:
        raise UnexpectedResponse(response)

def getLaser():
    """Requests the current laser scan from the MRDS server and parses it into a dict"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET','/lokarria/laser/echoes')
    response = mrds.getresponse()
    if (response.status == 200):
        laserData = response.read()
        response.close()
        return json.loads(laserData.decode())
    else:
        return response
    
def getLaserAngles():
    """Requests the current laser properties from the MRDS server and parses it into a dict"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET','/lokarria/laser/properties')
    response = mrds.getresponse()
    if (response.status == 200):
        laserData = response.read()
        response.close()
        properties = json.loads(laserData.decode())
        beamCount = int((properties['EndAngle']-properties['StartAngle'])/properties['AngleIncrement'])
        a = properties['StartAngle']#+properties['AngleIncrement']
        angles = []
        while a <= properties['EndAngle']:
            angles.append(a)
            a+=pi/180 #properties['AngleIncrement']
        #angles.append(properties['EndAngle']-properties['AngleIncrement']/2)
        return angles
    else:
        raise UnexpectedResponse(response)
    
def getPose():
    """Reads the current position and orientation from the MRDS"""
    mrds = http.client.HTTPConnection(MRDS_URL)
    mrds.request('GET','/lokarria/localization')
    response = mrds.getresponse()
    if (response.status == 200):
        poseData = response.read()
        response.close()
        return json.loads(poseData.decode())
    else:
        return UnexpectedResponse(response)

def heading(q):
    return rotate(q,{'X':1.0,'Y':0.0,"Z":0.0})

def rotate(q,v):
    return vector(qmult(qmult(q,quaternion(v)),conjugate(q)))

def quaternion(v):
    q=v.copy()
    q['W']=0.0;
    return q

def vector(q):
    v={}
    v["X"]=q["X"]
    v["Y"]=q["Y"]
    v["Z"]=q["Z"]
    return v

def conjugate(q):
    qc=q.copy()
    qc["X"]=-q["X"]
    qc["Y"]=-q["Y"]
    qc["Z"]=-q["Z"]
    return qc

def qmult(q1,q2):
    q={}
    q["W"]=q1["W"]*q2["W"]-q1["X"]*q2["X"]-q1["Y"]*q2["Y"]-q1["Z"]*q2["Z"]
    q["X"]=q1["W"]*q2["X"]+q1["X"]*q2["W"]+q1["Y"]*q2["Z"]-q1["Z"]*q2["Y"]
    q["Y"]=q1["W"]*q2["Y"]-q1["X"]*q2["Z"]+q1["Y"]*q2["W"]+q1["Z"]*q2["X"]
    q["Z"]=q1["W"]*q2["Z"]+q1["X"]*q2["Y"]-q1["Y"]*q2["X"]+q1["Z"]*q2["W"]
    return q
    
def getHeading():
    """Returns the XY Orientation as a heading unit vector"""
    return heading(getPose()['Pose']['Orientation'])

def getBearingAngle(destPoint, currentPoint):
    deltaX = abs(destPoint.x) - abs(currentPoint.x)
    deltaY = abs(destPoint.y) - abs(currentPoint.y)
    
    theta = atan2(deltaX,deltaY)
    
    if theta < 0:
        theta = (2 * pi) + theta
        
    return theta

def calcLookAheadDistance(destPoint, currentPoint):
    
    #deltaX = abs(currentPoint.x) - abs(destPoint.x)
    #deltaY = abs(currentPoint.y) - abs(destPoint.y)
    
    deltaX = currentPoint.x - destPoint.x
    deltaY = currentPoint.y - destPoint.y    
    
    """if (currentPoint.x > 0 and destPoint.x > 0) or (currentPoint.x < 0 and destPoint.x < 0):
        deltaX = destPoint.x + currentPoint.x
        deltaY = destPoint.y - currentPoint.y
    elif (currentPoint.y > 0 and destPoint.y > 0) or (currentPoint.y < 0 and destPoint.y < 0):
        deltaX = destPoint.x - currentPoint.x
        deltaY = destPoint.y + currentPoint.y
    elif (currentPoint.x > 0  and destPoint.y < 0) or (currentPoint.x < 0 and destPoint.y > 0):
        deltaX = destPoint.x + currentPoint.x
        deltaY = destPoint.y + currentPoint.y        
    else:
        deltaX = destPoint.x - currentPoint.x
        deltaY = destPoint.y - currentPoint.y"""
        
    
    lookAheadDistance = sqrt((deltaX**2) + (deltaY**2))
        
    return lookAheadDistance
    

"""def calcSteeringAngle(destPoint, currentPoint):
    dict = {'steeringAngle': 0, 'hypotenuse': 0, 'fail': False}
    
    if currentPoint.x > 0 and destPoint.x > 0:
        deltaX = destPoint.x - currentPoint.x
        deltaY = destPoint.y - currentPoint.y
    elif currentPoint.x < 0 and destPoint.x < 0:
        deltaX = destPoint.x - currentPoint.x
        deltaY = destPoint.y - currentPoint.y
    else:
        deltaX = destPoint.x + currentPoint.x
        deltaY = destPoint.y + currentPoint.y
        
    hypotenuse = sqrt((deltaX**2) + (deltaY**2))
    dict['hypotenuse'] = hypotenuse
    if hypotenuse == 0 :
        dict['fail'] = True
        return dict
    else:
        print("Distance to target point: ", hypotenuse)
        angleInRadians = acos(deltaX / hypotenuse)
        print("Angle in radians: ", angleInRadians)
        dict['angle'] = angleInRadians
        return dict"""

def turnNorth():
    
    robotOrientation = getHeading()
    facingPoint = Point()
    facingPoint.x = robotOrientation['X']
    facingPoint.y = robotOrientation['Y']
    
    turnNorthDict = {'northAngle': 0, 'quadrant': 0}
    
    if facingPoint.x > 1 or facingPoint.y > 1:
        return turnNorthDict
    
    if facingPoint.y < 0 and facingPoint.x < 0:
        northAngle = asin(facingPoint.x / 1)
        
        turnNorthDict['northAngle'] = northAngle
        turnNorthDict['quadrant'] = 2
        
        return turnNorthDict
    elif facingPoint.y < 0 and facingPoint.x > 0:
        northAngle = asin(facingPoint.x / 1)
        
        turnNorthDict['northAngle'] = northAngle
        turnNorthDict['quadrant'] = 1
        
        return turnNorthDict
    elif facingPoint.y > 0 and facingPoint.x < 0:
        northAngle = acos(facingPoint.y / 1)
        
        turnNorthDict['northAngle'] = northAngle
        turnNorthDict['quadrant'] = 3        
        
        return turnNorthDict
    else:
        northAngle = acos(facingPoint.y / 1)
        
        turnNorthDict['northAngle'] = northAngle
        turnNorthDict['quadrant'] = 4
        
        return turnNorthDict            
                 
"""def calcTurningAngle(destPoint, currentPoint, steeringAngle, turnNorthDict):
    if destPoint.y < currentPoint.y:
        if destPoint.x > currentPoint.X:
        print("Curret Y is SMALLER")
        turningAngle = northAngle - (pi/2) + steeringAngle
        return turningAngle
    else:
        print("Curret Y is BIGGER")
        turningAngle = northAngle - ((pi/2) - steeringAngle)
        return turningAngle"""
    
def lookAheadFunction(path, currentPoint, angle):
    destPoint = Point()
    destPoint.x = path.vecPath[0]["X"]
    destPoint.y = path.vecPath[0]["Y"]
    
       
    
    lookAheadDistance = calcLookAheadDistance(destPoint, currentPoint)
    
    print("lookAheadDistance: ", lookAheadDistance)
    threashHold = abs(2/angle)
    print("threashHold: ", threashHold)
    
    if lookAheadDistance > threashHold:
        steeringAngle = getBearingAngle(destPoint, currentPoint)
        steeringAngle = steeringAngle - (pi/2)
        turnNorthDict = turnNorth()

        if(turnNorthDict['quadrant'] != 0):
            turnNorthDict['northAngle'] = turnNorthDict['northAngle'] - (pi/2)
        
        if(turnNorthDict['quadrant'] == 1 or turnNorthDict['quadrant'] == 2):
            turnNorthDict['northAngle'] = abs(turnNorthDict['northAngle'])
            print("CONV = " , degrees(turnNorthDict['northAngle']))
            
                
        
        print("steeringAngle: " , degrees(steeringAngle))
        print("NorthAngle in quadrant: ", degrees(turnNorthDict['northAngle']),turnNorthDict['quadrant'])
        
             
        turningAngle = turnNorthDict['northAngle']  - steeringAngle
        
       
            
        
        print("TurningAngle: ", degrees(turningAngle))
        
        smartPostSpeed(turningAngle)
        #postSpeed(turningAngle,0.5)
        #print("Destpoint X: ", destPoint.x)
        #print("Destpoint Y: ", destPoint.y)         
    
        #path.vecPath.pop(0)
        #Do STuff
        return turningAngle
    else:
        print("Pop")
        path.vecPath.pop(0)
        return 1
    
    
    
def smartPostSpeed(turningAngle):
    #If turning angle is big don't go fast
    postSpeed(turningAngle, abs(1 / turningAngle))
    
    

if __name__ == '__main__':
    print('Sending commands to MRDS server', MRDS_URL)
    try:
        path = Path()
        currentPoint = Point()
        defaultSpeed = 0.2
        angle = 1;
        
        while True:
            
            print("---------------------------")
            pose = getPose()
            currentPoint.x = pose['Pose']['Position']['X']
            currentPoint.y = pose['Pose']['Position']['Y']
            
            #print("CurrentPOS X: ", currentPoint.x)
            #print("CurrentPOS Y: ", currentPoint.y)
            
            angle = lookAheadFunction(path, currentPoint, angle)
            
            if(len(path.vecPath) == 0):
                print("DONE")
                break
            
            time.sleep(0.01)
            
            
            
            
            
            
            """dict = calcSteeringAngle(destPoint,currentPoint)
            
            facingPoint.x = robotOrientation['X']
            facingPoint.y = robotOrientation['Y']                
           
            turnNorthDict = turnNorth(facingPoint)
            turningAngle = calcTurningAngle(destPoint, currentPoint, dict['steeringAngle'], turnNorthDict)
            print("Turning angle: ", turningAngle)
            print("Turning angle in degrees: " , degrees(turningAngle))
                  
            
            if dict['fail'] == False:
                timeToRun = dict['hypotenuse']  / defaultSpeed
                postSpeed(turningAngle,defaultSpeed)
                #time.sleep(int(round(timeToRun)))
                time.sleep(2)
                lookAheadDict = lookAheadFunction(path, lookAheadDict , dict['hypotenuse'])"""
            
        
    except UnexpectedResponse as ex:
        print('Unexpected response from server when sending speed commands:', ex)
