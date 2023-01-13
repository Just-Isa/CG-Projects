import numpy as np
from PIL import Image
import math as math
import Plane as pl
import Ray as strahl
import Camera as cam
import Triangle as dreieck
import Sphere as kugel
import Light as licht
import Material as material
import datetime
import multiprocessing
import sys

def normal(vector):
    return vector / np.linalg.norm(vector)

class CheckerboardMaterial(object):
    def __init__(self , a, b, c):
        self.baseColor = a
        self.otherColor = b
        self.checkSize = c

    def baseColorAt(self , p):
        p * (1.0 / self.checkSize)
        if (int(abs(p[0]) + 0.5) + int(abs(p[1]) + 0.5) + int(abs(p[2])+ 0.5)) %2:
            return self.otherColor
        return self.baseColor

def colorAt(level, ray, light, objectlist):
    hitPointData = intersect(level, ray, objectlist, 3)
    if hitPointData:
        return shade(level, hitPointData, light, objectlist)
    return np.array([0,0,0])

def computeDirectLight(object, ray, light, objectlist):
    if(isinstance(object.material, CheckerboardMaterial)):
        ambientPart = object.material.baseColorAt(ray.pointAtParameter(object.intersectionParameter(ray))) * 0.5
    else:
        ambientPart = object.material.ambient * 0.5
        
    schnittpunkt = ray.pointAtParameter(object.intersectionParameter(ray))
    lightRay = object.normalAt(light.origin - schnittpunkt)
    n = object.normalAt(schnittpunkt)

    diffusePart = light.color * 0.4 * lightRay.dot(n)
    invertedL = np.array([lightRay[0],-lightRay[2], lightRay[1]])  
    spekPart = light.color * 0.4 * invertedL.dot(-ray.direction) ** light.harte
    
    #Calculation of Norm-Vec from Vec of the Light to Intersection (shadow)
    normalVektorOriginSchnittpunkt = normal(light.origin - schnittpunkt)
    for object in objectlist:
        if object.intersectionParameter(strahl.Ray(schnittpunkt, normalVektorOriginSchnittpunkt)) and object.intersectionParameter(strahl.Ray(schnittpunkt, normalVektorOriginSchnittpunkt)) > 0.3:
            return (diffusePart + ambientPart + spekPart) * 0.4
    
    return diffusePart + ambientPart + spekPart

    # reflect viewing angle
def computeReflectedRay(object, ray):
    schnittpunkt = ray.pointAtParameter(object.intersectionParameter(ray))
    d = ray.direction 
    n = object.normalAt(schnittpunkt)
    dr =  d - (2 * n.dot(d) * n)
    return strahl.Ray(schnittpunkt, dr)
     
def shade( level , hitPointData, light, objectlist):
    directColor = computeDirectLight(hitPointData[0], hitPointData[1], light, objectlist)
    if(hitPointData[0].shallReflect == 1):
        reflectedRay = computeReflectedRay(hitPointData[0], hitPointData[1])
        reflectColor = colorAt(level+1, reflectedRay, light, objectlist) 
        return directColor + np.array([reflectColor[0]*0.4, reflectColor[1]*0.4, reflectColor[2]*0.4]) 
    return directColor
    
def intersect(level, ray, objectlist, rekursionsGrenze=1):
    if level == rekursionsGrenze:
        return None
    obj = iterateIntersect(ray, objectlist)
    if obj is None:
        return None
    return obj, ray

def iterateIntersect(ray, objectlist):
    obj = None 
    maxdist = float('inf')
    for object in objectlist:
        hitdist = object.intersectionParameter(ray)
        if hitdist and 0.0009 < hitdist < maxdist:
            maxdist = hitdist
            obj = object
    return obj

def loadSquirrel():
    file = open("squirrel_aligned_lowres.obj")
    squirrelPoints = []
    blueMaterial = material.Material(np.array([0,0,200]))
    faces = []
    for line in file:
        if "#" in line:
            continue
        if "v" in line:
            points = line.split()
            squirrelPoints.insert(len(squirrelPoints), [float(points[1]), float(points[2]), float(points[3])])
        if "f" in line:
            points = line.split()
            faces.insert(len(faces), [int(points[1]), int(points[2]), int(points[3])])

    for punkte in faces:
        pktone = int(punkte[0]-1)
        pkttwo = int(punkte[1]-1)
        pktthree = int(punkte[2]-1)
        squirrelList.insert(len(objectlist), 
            dreieck.Triangle(
                np.array([squirrelPoints[pktone][0], squirrelPoints[pktone][1], squirrelPoints[pktone][2]]), 
                np.array([squirrelPoints[pkttwo][0], squirrelPoints[pkttwo][1], squirrelPoints[pkttwo][2]]), 
                np.array([squirrelPoints[pktthree][0], squirrelPoints[pktthree][1], squirrelPoints[pktthree][2]]), 
                blueMaterial, 0))

def computePixels(wRes, hRes, camera, BACKGROUND_COLOR, objectlist, image, licht, part, anzahlProzesse, return_dict):
    colorPoints = []
    if part == 0:
        vonBreite, breite = 0, int(wRes/anzahlProzesse)
    elif part == 1:
        vonBreite, breite = int(wRes/anzahlProzesse), int(wRes/anzahlProzesse)*2
    elif part == 2:
        vonBreite, breite = int(wRes/anzahlProzesse)*2, int(wRes/anzahlProzesse)*3
    elif part == 3:
        vonBreite, breite = int(wRes/anzahlProzesse)*3, int(wRes/anzahlProzesse)*4
    elif part == 4:
        vonBreite, breite = int(wRes/anzahlProzesse)*4, int(wRes/anzahlProzesse)*5
    elif part == 5:
        vonBreite, breite = int(wRes/anzahlProzesse)*5, int(wRes/anzahlProzesse)*6
    elif part == 6:
        vonBreite, breite = int(wRes/anzahlProzesse)*6, int(wRes/anzahlProzesse)*7
    elif part == 7:
        vonBreite, breite = int(wRes/anzahlProzesse)*7, int(wRes/anzahlProzesse)*8
    elif part == 8:
        vonBreite, breite = int(wRes/anzahlProzesse)*8, int(wRes/anzahlProzesse)*9
    
    if(part+1 == anzahlProzesse):
        breite = wRes
    hoehe = hRes

    for x in range(vonBreite, breite):
        for y in range(0, hoehe):
            ray = camera.calcRay(x,y)
            maxdist = float('inf')
            color = BACKGROUND_COLOR
            for object in objectlist:
                hitdist = object.intersectionParameter(ray) 
                if hitdist:
                    if hitdist < maxdist:
                        maxdist = hitdist
                        #eig. 1
                        color = colorAt(1, ray, licht, objectlist)
            colorPoints.insert(len(return_dict), (x,y, (int(color[0]), int(color[1]), int(color[2]))))
    return_dict[part] = colorPoints
    
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("How to run : python .\RayTracer.py width height [-mp]/[-squirrel] processCount")
        print("-mp processCount for multiprocessing, -squirrel for squirrel ")
        print("Example command for multiprocessing: python .\RayTracer.py 400 400 -mp 8 ")
        print("Example command for Squirrel: python .\RayTracer.py 20 20 -squirrel 4 ")
        print("MAX processCount = 8, MIN processCount = 1")
        sys.exit(-1)
    licht = licht.Light(np.array([1,3,2]), 1, np.array([200, 200, 200]))
    redMaterial = material.Material(np.array([200,0,0]))
    greenMaterial = material.Material(np.array([0,200,0]))
    blueMaterial = material.Material(np.array([0,0,200]))
    yellowMat = material.Material(np.array([100,100,0]))
    xdMaterial = material.Material(np.array([211,211,211]))
    checkerMaterial = CheckerboardMaterial(np.array([0,0,0]), np.array([255,255,255]), 1)

    objectlist = []
    squirrelList = []
    
    #Objects for RayTracing test
    objectlist = [
        kugel.Sphere(np.array([0, 1, 10]), 1, redMaterial, 1), 
        kugel.Sphere(np.array([-1.2, -1, 10]), 1, greenMaterial, 1), 
        kugel.Sphere(np.array([1.2, -1, 10]), 1, blueMaterial, 1),
        pl.Plane(np.array([0, -2.3, 4.5]), np.array([0, 550, -0.1]), checkerMaterial, 0),
        dreieck.Triangle(np.array([0, 2, 20]), np.array([2.5,-2, 20]), np.array([-2.5, -2, 20]), yellowMat, 0)
        ]
    
    BACKGROUND_COLOR = (0,0,0)

    wRes, hRes = int(sys.argv[1]), int(sys.argv[2])

    a = np.deg2rad(45)/2 
    height = 2 * math.tan(a) 
    aspectRatio = wRes / hRes 
    width = aspectRatio * height 
    pixelWidth = width / (wRes)
    pixelHeight = height / (hRes) 
    image = Image.new("RGB", (wRes, hRes)) 

    camera = None 

    #Time-Tracking
    startZeit = datetime.datetime.now()    
    processes = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    if sys.argv[3] == '-mp':
        processes = []
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        camera = cam.Camera(np.array([0, 0, 0 ]),np.array([0, 0, 50]),np.array([0,-1,0]), pixelWidth, pixelHeight, width, height) 
        #Multiprocessing
        prozessmenge = int(sys.argv[4])
        if prozessmenge > 0 and prozessmenge <= 8:
            for i in range(prozessmenge):
                t = multiprocessing.Process(target=computePixels, args=(wRes, hRes, camera, BACKGROUND_COLOR, objectlist, image, licht, i, prozessmenge, return_dict,))
                processes.append(t)
                t.start()
            for i in range(prozessmenge):
                processes[i].join()

            for elements in return_dict.values():
                for values in elements:
                    image.putpixel((values[0], values[1]), values[2])

            image.save("./images/raytracedShapesMultiProcessing"+ str(wRes) + "x"+ str(hRes) +".png", 'PNG')
            image.show("raytracedShapes"+ str(wRes) + "x"+ str(hRes) +".png")
        else:
            print("MAXIMALE PROZESSMENGE = 8, MINIMALE PROZESSMENGE = 1")
    elif sys.argv[3] == '-squirrel':
        processes = []
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        camera = cam.Camera(np.array([2, 0, -6 ]),np.array([0, 2, 0]),np.array([0,-1,0]), pixelWidth, pixelHeight, width, height)
        loadSquirrel()
        prozessmenge = int(sys.argv[4]);
        if prozessmenge > 0 and prozessmenge <= 8:
            for i in range(prozessmenge):
                t = multiprocessing.Process(target=computePixels, args=(wRes, hRes, camera, BACKGROUND_COLOR, squirrelList, image, licht, i, prozessmenge, return_dict,))
                processes.append(t)
                t.start()
            for i in range(prozessmenge):
                processes[i].join()
            for elements in return_dict.values():
                for values in elements:
                    image.putpixel((values[0], values[1]), values[2])
            print(f"hat {datetime.datetime.now() - startZeit} gedauert")
            image.save("./images/squirrel"+ str(wRes) + "x"+ str(hRes) +".png", 'PNG')
            image.show("squirrel"+ str(wRes) + "x"+ str(hRes) +".png")
        else:
            print("MAXIMALE PROZESSMENGE = 8, MINIMALE PROZESSMENGE = 1")
    print(f"hat {datetime.datetime.now() - startZeit} gedauert. ")