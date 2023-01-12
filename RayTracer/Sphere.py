from math import sqrt
import numpy as np
import Ray as strahl

def normal(vector):
    return vector / np.linalg.norm(vector)

class Sphere(object):
    def __init__(self, center, radius, material, shallReflect):
        self.center = center # point
        self.radius = radius # scalar
        self.material = material
        self.shallReflect = shallReflect

    def __repr__(self):
        return 'Sphere(%s,%s)' %(repr(self.center), self.radius)

    def intersectionParameter(self, ray):
        co = self.center - ray.origin
        v = co.dot(ray.direction)
        discriminant = v*v - (co.dot(co)) + self.radius * self.radius
        if discriminant < 0:
            return None
        else:
            return v - sqrt(discriminant)

    def normalAt(self, p):
        return normal(p - self.center)