import numpy as np
import Ray as ray

class Triangle(object):
    def __init__(self, a, b, c, material, shallReflect):
        self.a=a # point
        self.b=b # point
        self.c=c # point
        self.u = self.b - self.a # direction vector
        self.v = self.c - self.a # direction vector
        self.material = material
        self.shallReflect = shallReflect

    def __repr__(self):
        return 'Triangle(%s,%s,%s)' %(repr(self.a), repr(self.b),repr(self.c))

    def intersectionParameter(self, ray):
        w = ray.origin - self.a
        dv = np.cross(ray.direction, self.v)
        dvu = dv.dot(self.u)
        if dvu == 0.0:
            return None
        wu = np.cross(w, self.u)
        r = dv.dot(w) / dvu
        s = wu.dot(ray.direction) / dvu
        if 0<=r and r<=1 and 0<=s and s<=1 and r+s<=1:
            return wu.dot(self.v) / dvu
        else :
            return None

    def normalAt(self, p):
        return normal(np.cross(self.u, self.v))
    

def normal(vector):
    return vector / np.linalg.norm(vector)