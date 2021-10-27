import numpy as np
import Ray as ray

def normal(vector):
    return vector / np.linalg.norm(vector)

class Plane(object):
    def __init__(self, point, normalVec, material, shallReflect):
        self.point = point # point
        self.normalVec = normal(normalVec) # vector
        self.material = material
        self.shallReflect = shallReflect

    def __repr__(self):
        return 'Plane(%s,%s)' %(repr(self.point), repr(self.normalVec))
    
    def intersectionParameter(self , ray):
        op = ray.origin - self.point
        a = op.dot(self.normalVec)
        b = ray.direction.dot(self.normalVec)
        if b < 0:
            return -a/b
        else :
            return None

    def normalAt(self, p):
        return self.normalVec