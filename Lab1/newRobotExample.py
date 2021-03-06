#!/usr/bin/env python3

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
        #self.loadPath('Path-around-table-and-back.json')
        #self.loadPath('Path-around-table.json')
        #self.loadPath('Path-from-bed.json')
        #self.loadPath('Path-to-bed.json')
        self.loadPath('exam2018.json')
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
    deltaX = destPoint.x - currentPoint.x
    deltaY = destPoint.y - currentPoint.y         
     
    
    theta = atan2(deltaY,deltaX)
    
    if theta < 0:
        print("BEARING CONV")
        theta = (2 * pi) + theta
        print("CURR: " , currentPoint.x, currentPoint.y)
        print("DEST: " , destPoint.x, destPoint.y)
        
    return theta

def getOrientationAngle():
    orientation = getHeading()
    
    theta = atan2(orientation['Y'],orientation['X'])
    
    if theta < 0:
        print("ORIENTATION CONV")
        theta = (2 * pi) + theta

        
    return theta

def calcLookAheadDistance(destPoint, currentPoint):
    
    deltaX = destPoint.x - currentPoint.x
    deltaY = destPoint.y - currentPoint.y   
    
    lookAheadDistance = sqrt((deltaX**2) + (deltaY**2))
        
    return lookAheadDistance

def newSmartPostSpeed(turningAngle):
    #If turning angle is big don't go fast
    turnDiff = (turningAngle / (pi/2))
    #print("TurnDiff :", turnDiff)
    #1.4
    konst = 2
    angSpeed = konst * turnDiff
    linSpeed = (konst/3) * (1-abs(turnDiff))
    postSpeed(angSpeed, linSpeed)  

def lookAheadFunction(path, currentPoint):
    destPoint = Point()
    destPoint.x = path.vecPath[0]["X"]
    destPoint.y = path.vecPath[0]["Y"]
    
    lookAheadDistance = calcLookAheadDistance(destPoint, currentPoint)
    
    print("lookAheadDistance: ", lookAheadDistance)
    #1.1
    if lookAheadDistance > 1.0:
        steeringAngle = getBearingAngle(destPoint, currentPoint)
        orientationAngle = getOrientationAngle()
       
        print("steeringAngle: " , degrees(steeringAngle))
        print("orientationAngle: " , degrees(orientationAngle))
        
        
        turningAngle = steeringAngle - orientationAngle 
        print("TurningAngle: ", degrees(turningAngle))
 
        if(pi < abs(turningAngle)):
            print("PI")
            turningAngle = (2*pi) - abs(turningAngle)
            turningAngle = -turningAngle
            print("TurningAngle: ", degrees(turningAngle))
        
        #smartPostSpeed(turningAngle)
        newSmartPostSpeed(turningAngle)
        #postSpeed(turningAngle,0.5)
    else:
        print("Pop")
        path.vecPath.pop(0)
    

if __name__ == '__main__':
    print('Sending commands to MRDS server', MRDS_URL)
    try:
        path = Path()
        currentPoint = Point()
        while True:
            print("---------------------------")
            pose = getPose()
            currentPoint.x = pose['Pose']['Position']['X']
            currentPoint.y = pose['Pose']['Position']['Y']
            
            lookAheadFunction(path, currentPoint)
            
            if(len(path.vecPath) == 0):
                print("DONE")
                postSpeed(0,0)
                break
            #0.005
            time.sleep(0.01 )

    except UnexpectedResponse as ex:
        print('Unexpected response from server when sending speed commands:', ex)
