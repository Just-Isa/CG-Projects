
import numpy as np
import Ray as strahl

class Camera(object):
    def __init__(self, eye, centerpoint, up, pixelWidth, pixelHeight, width, height):
        self.eye = eye
        self.centerpoint = centerpoint
        self.up = up
        self.pixelWidth = pixelWidth
        self.pixelHeight = pixelHeight
        self.width = width
        self.height = height

        self.f = normal(centerpoint-eye)
        self.s = normal(np.cross(self.f, self.up))
        self.u = np.cross(self.s, self.f)
        
    def calcRay(self, x, y):
        xcomp = self.s * (x*self.pixelWidth - self.width/2)
        ycomp = self.u * (y*self.pixelHeight - self.height/2)
        return strahl.Ray(self.eye, self.f + xcomp + ycomp)
    
    def __repr__(self):
        return "eye: %s, center: %s, up: %s, f: %s, s: %s, u: %u" % (self.eye, self.centerpoint, self.up, self.f, self.s, self.u)

        
def normal(vector):
    return vector / np.linalg.norm(vector)