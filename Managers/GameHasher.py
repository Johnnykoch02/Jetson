from Classes.GameObject import *

ROBOT_SPEED = 100.0

# Weights from 0-100 with -1 being infinite priority
hash_weights = {
    ObjectType.FRISBEE: {
        "time_weights": {
            # Auton
            0: 100,
            15000: 100,
            # Start of match
            15001: 100,
            # Last 15 seconds
            105000 - 15000: 80,
            # Last 5 seconds
            105000 - 5000: 10,
            # End game
            105000: 0
        }
    }
}

class Hasher:
    def __init__(self) -> None:
        self.robot_velocity = Vec(1,0,0)
        pass

    def GetGenericHash( self, weight_type: ObjectType, weight, delta ) -> float:
        weights = hash_weights[weight_type]
        final = 0
        last = None
        for value in weights[weight]:
            if value >= delta:
                percentage = ((value - delta) + last) / value
                diff = weights[weight][last] - weights[weight][value]    
                final = weights[weight][value] + (diff * percentage)
                break
            else:
                last = value
        return final
    
    def GetTimeHash( self, deltatime ) -> float:
        return self.GetGenericHash(ObjectType.FRISBEE, "time_weights", deltatime ) / 100
    
    def GetDistanceHash( self, frisbee: GameObject, robots: list[GameObject]):
        score = 1

        for robot in robots:
            distance_to_frisbee = (frisbee.position - robot.position).norm()
            our_distance_to_frisbee = frisbee.position.norm()

            direction_to_frisbee = Vec.normalize(frisbee.position - robot.position)
            robot_direction = Vec.normalize(robot.velocity)

            angle_between_robot_and_frisbee = direction_to_frisbee.angle_between(robot_direction)

            if angle_between_robot_and_frisbee <= 30 or distance_to_frisbee <= 100:  # Check if the angle is within the desired range
                time_for_robot_to_reach_frisbee = distance_to_frisbee / robot.velocity.norm()
                time_for_us_to_reach_frisbee = our_distance_to_frisbee / ROBOT_SPEED

                if time_for_us_to_reach_frisbee > time_for_robot_to_reach_frisbee or distance_to_frisbee <= 100:
                    if distance_to_frisbee > 300:
                        drop_factor = 1
                    elif distance_to_frisbee <= 50:
                        drop_factor = 0
                    else:
                        drop_factor = (distance_to_frisbee - 50) / (300 - 50)

                    if score > drop_factor:
                        score = drop_factor

        return score
        
    def HashFrisbee( self, frisbee, deltatime, extra) -> float:
        # Distance/Direction hash
        our_position = Vec(0, 0, 0)
        our_distance_to_frisbee = abs((frisbee.position - our_position).norm())
        our_direction = Vec.normalize(self.robot_velocity)

        direction_to_frisbee = Vec.normalize(frisbee.position)
        angle_between_us_and_frisbee = direction_to_frisbee.angle_between(our_direction)

        local_distance = 0
        # Check if the frisbee is within the 180-degree cone in front of our robot
        if angle_between_us_and_frisbee <= 90 or our_distance_to_frisbee <= 50:
            if our_distance_to_frisbee <= 50:
                local_distance = 1
            # Calculate the score based on the distance to the frisbee within the range of 50 to 300 units
            elif our_distance_to_frisbee <= 300:
                local_distance = 1 - (((our_distance_to_frisbee + 200) / 300) - 1)
                

        distance_scores = []
        for bot in extra["bots"]:
            direction_to_frisbee = frisbee.position - bot.position
            distance_to_frisbee = direction_to_frisbee.norm()

            angle = direction_to_frisbee.angle_between(bot.velocity)
            if (angle < 45 and distance_to_frisbee < 300) or distance_to_frisbee < 100:
                if distance_to_frisbee < 100:
                    distance_score = 0
                elif angle < 45 and distance_to_frisbee < 200 and bot.velocity.norm() > 100:
                    distance_score = 0.1
                else:
                    distance_score = distance_to_frisbee / 300
            else:
                distance_score = 1

            distance_scores.append(distance_score)

        distance_score = min(distance_scores)

        # Frisbee cluster hash
        frisbee_cluster_score = 0
        for other_frisbee in extra["frisbees"]:
            if other_frisbee.id == frisbee.id:
                continue
            dist = (frisbee.position - other_frisbee.position).norm()
            if dist <= 75:
                frisbee_cluster_score += 1

        frisbee_cluster_score = min(frisbee_cluster_score, 5) / 5
        time_weight = self.GetTimeHash(deltatime)

        if local_distance > 0.25:
            local_distance = max(local_distance, abs(local_distance - frisbee_cluster_score) / 2)

        return distance_score * time_weight * local_distance
    
    def HashGameObject( self, object: GameObject, deltatime: float, extra: list[GameObject] ) -> float:
        if object.type == ObjectType.FRISBEE:
            return self.HashFrisbee( object, deltatime, extra )
        
    def rotate_velocity(self, rotation_speed, delta_time):
        # Calculate the rotation angle based on rotation speed and delta time (in degrees)
        rotation_angle_deg = rotation_speed * delta_time

        # Convert the rotation angle to radians
        rotation_angle_rad = math.radians(rotation_angle_deg)

        # Calculate the new x and y components of the velocity vector
        new_x = self.robot_velocity.x * math.cos(rotation_angle_rad) - self.robot_velocity.y * math.sin(rotation_angle_rad)
        new_y = self.robot_velocity.x * math.sin(rotation_angle_rad) + self.robot_velocity.y * math.cos(rotation_angle_rad)

        # Update the velocity vector with the new components
        self.robot_velocity = Vec(new_x, new_y, self.robot_velocity.z)