import math
import numpy as np

cos, sin, tan, radians, degrees, arccos, arcsin, arctan, arctan2 = np.cos, np.sin, np.tan, np.radians, np.degrees, np.arccos, np.arcsin, np.arctan2
PI = 3.14159
METERS_TO_INCHES = 39.3700787
EPSILON = 1e-7

class Vec(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def dot(v1, v2):
        return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

    @staticmethod
    def cross(v1, v2):
        x = v1.y * v2.z - v1.z * v2.y
        y = v1.x * v2.x - v1.x * v2.z
        z = v1.z * v2.y - v1.y * v2.x
        return Vec(x, y, z)

    @staticmethod
    def normalize(v):
        return v * (1 / v.norm())
    
    def angle_between(self, v2):
        norm_v1 = self.norm()
        norm_v2 = v2.norm()

        if norm_v1 == 0 or norm_v2 == 0:
            # Return a default value or raise a custom exception when one of the vectors is a zero vector.
            # Example: return None, or raise ValueError("One of the vectors is a zero vector")
            # Return 180 for weights
            return 180

        dot_product = Vec.dot(self, v2)
        cos_theta = dot_product / (norm_v1 * norm_v2)
        angle = math.degrees(math.acos(min(max(cos_theta, -1.0), 1.0)))  # Clamp the value between -1 and 1 to avoid domain errors
        return angle

    def norm(self):
        return math.sqrt(Vec.dot(self, self))

    def __add__(self, v):
        return Vec(self.x + v.x, self.y + v.y, self.z + v.z)

    def __neg__(self):
        return Vec(-self.x, -self.y, -self.z)

    def __sub__(self, v):
        return self + (-v)

    def __mul__(self, v):
        if isinstance(v, Vec):
            return Vec(self.x * v.x, self.y * v.y, self.z * v.z)
        else:
            return Vec(self.x * v, self.y * v, self.z * v)

    def __rmul__(self, v):
        return self.__mul__(v)

    def __div__(self, v):
        if isinstance(v, Vec):
            return Vec(self.x / v.x, self.y / v.y, self.z / v.z)
        else:
            return Vec(self.x / v, self.y / v, self.z / v)

    def __str__(self):
        return '[ %.4f, %.4f, %.4f ]' % (self.x, self.y, self.z)

    def toVector2( self ):
        return Vector2(x=self.x, y=self.y)
    
class Vector2:
    '''x and y components OR the length and angle from X-Axis Counter Clockwise in Degrees'''
    def __init__(self,x=0, y=0, r=0, theta=0):
      if x!=0 or y!=0:
        self.x = x
        self.y = y
        self.r = ((self.x**2 + self.y**2)**0.5)
        self.theta = degrees(arctan2(self.y,self.x))
      else:
        self.r = r
        self.theta = theta
        self.x = self.r * cos(radians(theta))
        self.y = self.r * sin(radians(theta))
        
    def dot(self, b):
      return (self.x*b.x) + (self.y*b.y)
    def unit(self) -> 'Vector2':
      return Vector2(x=self.x/self.r, y=self.y/self.r) 
    def scale(self, scalar: float) -> 'Vector2':
      return Vector2(x=self.x*scalar, y=self.y*scalar)   
    def angle_from_dot(a, b):
      return degrees(arccos((a.dot(b)) / (a.r * b.r) ))
    def __str__(self):
      return "i:{}, j:{}, r:{}, theta:{}".format(self.x, self.y, self.r, self.theta)
    def __repr__(self):
      return "i:{}, j:{}, r:{}, theta:{}".format(self.x, self.y, self.r, self.theta)
    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        if idx == 1:
            return self.y
        else:
            return None
    def __add__(self, other) -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)
    def __sub__(self, other) -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)
    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)