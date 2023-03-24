from Classes.GameObject import *
import random

def GenerateFakeData() -> list[GameObject]:
    fake_data = list[GameObject]()

    num_of_frisbee = 100

    for i in range(num_of_frisbee):
        obj = GameObject()
        obj.id = i
        obj.position = Vec(random.randrange(-490,490), random.randrange(-490,490), 0)
        obj.type = ObjectType.FRISBEE
        fake_data.append(obj)

    for i in range(2):
        obj = GameObject()
        obj.id = i+num_of_frisbee
        obj.velocity = Vec(random.uniform(-2,2), random.uniform(-2,2), 0)
        obj.position = Vec(random.randrange(-490,490), random.randrange(-490,490), 0)
        obj.type = ObjectType.ENEMY_ROBOT
        fake_data.append(obj)
    
    obj = GameObject()
    obj.id = num_of_frisbee + 2
    obj.position = Vec(random.randrange(-50,50), random.randrange(-50,50), 0)
    obj.velocity = Vec(random.uniform(-2,2), random.uniform(-2,2), 0)
    obj.type = ObjectType.FRIENDLY_ROBOT
    fake_data.append(obj)

    return fake_data
