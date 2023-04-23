import math

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