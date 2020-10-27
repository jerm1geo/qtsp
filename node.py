import math

class Node:
    def __init__(self, id, person, location, lat, lon):
        self.id = id
        self.person = person
        self.location = location
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return "%s %s %s %f %f" % \
            (self.id, self.person, self.location, self.lat, self.lon)

    def compute_distance(self, to_node):
        lat1 = math.radians(self.lat)
        lon1 = math.radians(self.lon)
        lat2 = math.radians(to_node.lat)
        lon2 = math.radians(to_node.lon)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        ans = math.pow(math.sin(dlat / 2), 2) + \
            math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon / 2), 2)
        ans = 2 * math.asin(math.sqrt(ans))

        # Radius of Earth: 6371km or 3956mi
        radius = 3956
        return ans * radius
