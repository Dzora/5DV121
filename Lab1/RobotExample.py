#!/usr/bin/env python3
"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 
"""

START_THRESHOLD = 0.1
PASS_THRESHOLD = 1.5
GOAL_THRESHOLD = 1
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
        #self.loadPath('Path-around-table.json')
        #self.loadPath('Path-from-bed.json')
        #self.loadPath('Path-to-bed.json')
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
    #deltaX = destPoint.x - currentPoint.x
    #deltaY = destPoint.y - currentPoint.y         
     
    
    theta = atan2(deltaX,deltaY)
    
    if theta < 0:
        print("THETA: ", theta)
        theta = (2 * pi) + theta
        print("CURR: " , currentPoint.x, currentPoint.y)
        print("DEST: " , destPoint.x, destPoint.y)
        
    return theta

def calcLookAheadDistance(destPoint, currentPoint):
    
    deltaX = currentPoint.x - destPoint.x
    deltaY = currentPoint.y - destPoint.y   
    
    lookAheadDistance = sqrt((deltaX**2) + (deltaY**2))
        
    return lookAheadDistance
    
def turnWest():
    robotOrientation = getHeading()
    facingPoint = Point()
    facingPoint.x = robotOrientation['X']
    facingPoint.y = robotOrientation['Y']
    
    turnWestDict = {'westAngle': 0, 'quadrant': 0}
    
    if abs(facingPoint.x) > 1 or abs(facingPoint.y) > 1:
        turnWestDict['quadrant'] = 5
        return turnWestDict
    
    if facingPoint.x == 1 and facingPoint.y == 1:
        turnWestDict['quadrant'] = 6
        return turnWestDict    
    
    if facingPoint.y < 0 and facingPoint.x < 0:
        westAngle = acos(abs(facingPoint.y) / 1) + pi
       
        turnWestDict['westAngle'] = westAngle
        turnWestDict['quadrant'] = 3
        
        return turnWestDict
    elif facingPoint.y < 0 and facingPoint.x > 0:
        westAngle = acos(facingPoint.x / 1) + (pi/2)
        
        turnWestDict['westAngle'] = westAngle
        turnWestDict['quadrant'] = 2
        
        return turnWestDict
    elif facingPoint.y > 0 and facingPoint.x < 0:
        westAngle = acos(abs(facingPoint.x) / 1) + ((3*pi)/2)
        
        turnWestDict['westAngle'] = westAngle
        turnWestDict['quadrant'] = 4      
        
        return turnWestDict
    else:
        westAngle = acos(facingPoint.y / 1)
        
        turnWestDict['westAngle'] = westAngle
        turnWestDict['quadrant'] = 1
        
        return turnWestDict
    
def calcDynamicThreshHold(angle):
    prevAngle = abs(angle)
    if(prevAngle < 30):
        threashHold = 2
    elif(prevAngle > 90):
        threashHold = 1.3
    else:
        threashHold = 1.8
        
    #print("threashHold: ", threashHold)    
    return threashHold
    
def lookAheadFunction(path, currentPoint, angle):
    destPoint = Point()
    destPoint.x = path.vecPath[0]["X"]
    destPoint.y = path.vecPath[0]["Y"]
    
       
    
    lookAheadDistance = calcLookAheadDistance(destPoint, currentPoint)
    
    print("lookAheadDistance: ", lookAheadDistance)
    
    threashHold = calcDynamicThreshHold(angle)
    
    if lookAheadDistance > 1:
        steeringAngle = getBearingAngle(destPoint, currentPoint)
        turnWestDict = turnWest()
        westAngle = turnWestDict['westAngle']
       
        print("steeringAngle: " , degrees(steeringAngle))
        print("WestAngle in quadrant: ", degrees(westAngle),turnWestDict['quadrant'])
        
        if(steeringAngle < westAngle):
            turningAngle = westAngle - steeringAngle
        else:
            turningAngle = steeringAngle - westAngle
            if(turnWestDict['quadrant'] != 3 or turnWestDict['quadrant'] != 4):
                turningAngle = -turningAngle
        
        
        if(pi < abs(turningAngle)):
            turningAngle = (2*pi) - abs(turningAngle)
            turningAngle = -turningAngle
               
        
        
        
        print("TurningAngle: ", degrees(turningAngle))
        #print("TurningAngle: ", turningAngle)
        
        #smartPostSpeed(turningAngle)
        newSmartPostSpeed(turningAngle)
        #postSpeed(turningAngle,0.7)
        turningAngleInDegrees = degrees(turningAngle)
        return turningAngleInDegrees
    else:
        print("Pop")
        path.vecPath.pop(0)
        return 10
    
def smartPostSpeed(turningAngle):
    #If turning angle is big don't go fast
    turnRadius = degrees(turningAngle)
    #print("TurnRadius :", turnRadius)
    dynamicSpeed = 30/ abs(turnRadius)
    #print("dynamicSpeed : ", dynamicSpeed)
    postSpeed(turningAngle, dynamicSpeed)
    
    
def newSmartPostSpeed(turningAngle):
    #If turning angle is big don't go fast
    turnDiff = (turningAngle / (pi/2))
    #print("TurnDiff :", turnDiff)
    konst = 5
    angSpeed = konst * turnDiff
    linSpeed = (konst/3) * (1-abs(turnDiff))
    postSpeed(angSpeed, linSpeed)  

if __name__ == '__main__':
    print('Sending commands to MRDS server', MRDS_URL)
    try:
        path = Path()
        currentPoint = Point()
        defaultSpeed = 0.2
        angle = 10;
        while True:
            print("---------------------------")
            pose = getPose()
            currentPoint.x = pose['Pose']['Position']['X']
            currentPoint.y = pose['Pose']['Position']['Y']
            
            angle = lookAheadFunction(path, currentPoint, angle)
            
            if(len(path.vecPath) == 0):
                print("DONE")
                postSpeed(0,0)
                break
            
            time.sleep(0.01 )

    except UnexpectedResponse as ex:
        print('Unexpected response from server when sending speed commands:', ex)
