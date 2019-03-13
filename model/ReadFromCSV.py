import pandas as pd

class Node(object):
    def __init__(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type

class Edge(object):
    def __init__(self, id, node1, node2, distance):
        self.id = id
        self.node1 = node1
        self.node2 = node2
        self.distance = distance

class Vessel(object):
    def __init__(self, id, width, length, speed, path):
        self.id = id
        self.width = width
        self.length = length
        self.speed = speed
        self.path = path

def getNodes(nodeFile):
    # Grab node list
    nodelist = pd.read_csv(nodeFile, sep=';')

    node_list = []
    for i, nlrow in nodelist.iterrows():
        # Make the node object
        id = nlrow['Id']
        x = nlrow['Latitude']
        y = nlrow['Longitude']
        type = nlrow['Type']
        node_list.append(Node(id, x, y, type))

    # Return nodelist
    return node_list

def getEdges(edgeFile):
    # Grab node list
    edgeslist = pd.read_csv(edgeFile, sep=';')

    edge_list = []
    for i, nlrow in edgeslist.iterrows():
        # Make the node object
        id = i
        node1 = nlrow['Node1']
        node2 = nlrow['Node2']
        distance = nlrow['Distance(m)']
        maxLength = nlrow['MaxLength(cm)']
        MaxDraught = nlrow['MaxDraught(cm)']
        MaxHeight = nlrow['MaxDraught(cm)']
        DefaultPassageDuration = nlrow['DefaultPassageDuration']
        AvgProcessingTime = nlrow['AvgProcessingTime']
        edge_list.append(Edge(id, node1, node2, distance))

    # Return nodelist
    return edge_list


def getVessels():
    # Grab vessel list
    vessellist = pd.read_csv('../files/vessels.csv', sep=';')

    vessel_list = []
    for i, nlrow in vessellist.iterrows():
        # Make the node object
        id = nlrow['id']
        width = nlrow['width']
        length = nlrow['length']
        speed = nlrow['speed']
        path = nlrow['path'].split(',')
        vessel_list.append(Vessel(id, width, length, speed, path))

    # Return nodelist
    return vessel_list