#!/usr/bin/env python3
"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 
"""

MRDS_URL = 'localhost:50000'

import http.client, json, time
from math import sin,cos,pi,atan2,tan,sqrt,acos,degrees

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

def calcSteeringAngle(destPoint, currentPoint):
    print("---------------------------")
    dict = {'steeringAngle': 0, 'hypotenuse': 0, 'fail': False}
    deltaX = destPoint.x - currentPoint.x
    deltaY = destPoint.y - currentPoint.y
    hypotenuse = sqrt((deltaX**2) + (deltaY**2))
    dict['hypotenuse'] = hypotenuse
    if hypotenuse == 0 :
        dict['fail'] = True
        return dict
    else:
        print("Distance to target point: ", hypotenuse)
        angleInRadians = acos(deltaY / hypotenuse)
        print("Angle in radians: ", angleInRadians)
        dict['angle'] = angleInRadians
        return dict
    
    
def calcFacingAngle(facingPoint):
    x = facingPoint.x
    facingAngle = acos(x / 1)
    return facingAngle

def calcAdjustAngle(facingAngle, steeringAngle):
    diffAngle = (pi/2) - facingAngle
    adjustAngle = diffAngle + steeringAngle
    return adjustAngle

if __name__ == '__main__':
    print('Sending commands to MRDS server', MRDS_URL)
    try:
        path = Path()
        destPoint = Point()
        currentPoint = Point()
        facingPoint = Point()
        defaultSpeed = 0.5
        
        listLength = len(path.vecPath)
        
        for i in range(0, listLength-10, 10):
            heading = getHeading()
            pose = getPose()
            currentPoint.x = pose['Pose']['Position']['X']
            currentPoint.y = pose['Pose']['Position']['Y']
            
            destPoint.x = path.vecPath[i+10]["X"]
            destPoint.y = path.vecPath[i+10]["Y"]
            
            dict = calcSteeringAngle(destPoint,currentPoint)
            facingPoint.x = heading['X']
            facingPoint.y = heading['Y']
            
            
            facingAngle = calcFacingAngle(facingPoint)
            adjustAngle = calcAdjustAngle(facingAngle, dict['steeringAngle'])
            
            
            if dict['fail'] == False:
                timeToRun = dict['hypotenuse']  / defaultSpeed
                postSpeed(adjustAngle,defaultSpeed)
                time.sleep(int(round(timeToRun)))
            
        
    except UnexpectedResponse as ex:
        print('Unexpected response from server when sending speed commands:', ex)
