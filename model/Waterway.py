from model import ReadFromCSV
import salabim as sim
import math
import networkx as nx
import random

# File vari
nodeFile = "../files/waterway_nodelist.csv"
edgeFile = "../files/waterway_edgelist.csv"

# Lock variables
left = -1
right = +1

def sidename(side):
    return "l" if side == left else "r"

def distance(comp1, comp2):
    return math.sqrt((comp1.x - comp2.x) ** 2 + (comp1.y - comp2.y) ** 2)

# Lock component
class Lock(sim.Component):
    def process(self):
        pass

# Intersection component
class Intersection(sim.Component):
    def process(self):
        pass

# Bridge component
class Bridge(sim.Component):
    def process(self):
        pass

# Narrowing component
class Narrowing(sim.Component):
    def process(self):
        pass

class Vessel(sim.Component):
    def setup(self, id, speed, path):
        self.path = path
        self.id = id
        self.speed = speed
        self.x = nodes[int(currentnode[int(self.id)])].x
        self.y = nodes[int(currentnode[int(self.id)])].y
        self.color = ('red', 'blue', 'green', 'purple', 'black', 'pink')[self.id%6]
        self.pic_vessel = sim.Animate(circle0=15, x0=self.x, y0=self.y,
                                      fillcolor0='', linecolor0=self.color, linewidth0=2)

    def process(self):
        print(currentnode[self.id])
        print(self.path)
        dist = 0
        stopcrit = True
        while stopcrit:
            if dist == 0:
                if(len(self.path)!=0):
                    node = nodes[self.path.pop()]
                    dist = distance(self,node)
                    x_speed = ((node.x - self.x) / dist) * self.speed
                    y_speed = ((node.y - self.y) / dist) * self.speed
                    amount = round(dist / self.speed)
                else:
                    stopcrit = False
            print(dist)

            print("amount "+str(amount))

            self.x = self.x + x_speed;
            self.y = self.y + y_speed;


            if(amount<2):
                dist = 0
                self.x = node.x
                self.y = node.y
                print("stop"+str(self.id) +" "+str(node.id))
                currentnode[self.id] = node.id
                if(stopcrit):
                    self.enter(wait[node.id])
            else :
                amount = amount -1

            self.pic_vessel.update(circle0=15, x0=self.x, y0=self.y,
                                   fillcolor0='', linecolor0=self.color, linewidth0=2)
            yield self.hold(1)

class Node(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type

        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200),linewidth0=2, linecolor0='black')
        sim.AnimateText(text=self.type+" "+str(self.id), font='narrow', textcolor='black', text_anchor='c', offsety=30, x=self.x,y=self.y)

    def process(self):
        while True:
            if len(wait[self.id])!=0:
                wait[self.id].pop()
            yield self.hold(5)






nodelist = ReadFromCSV.getNodes(nodeFile)   # Get list of nodes from the csv
edgelist = ReadFromCSV.getEdges(edgeFile)   # Get list of edges from the csv
vessels = ReadFromCSV.getVessels()  # Get vessels from the csv

G = nx.Graph()  # Generate graph

# Generate the environment
env = sim.Environment(trace=True)   # Print the stack trace

# Settings for the visualization
screen_x_min = 25
screen_x_max = 1000
screen_x_width = screen_x_max - screen_x_min
screen_y_min = 25
screen_y_max = 550
screen_y_width = screen_y_max - screen_y_min

# Visualize the background
sim.AnimateRectangle((screen_x_min, screen_y_min, screen_x_max, screen_y_max), fillcolor='90%gray')
sim.AnimateImage('../Pictures/layout.png', x=screen_x_min, y=screen_y_min)

# Dict to map a vessel's current node
currentnode = {}

# Queue for each node in the network
wait = {}

# Dict of nodes (used to request data later)
nodes = {}

# Make list of coordinates
nodes_x_coordinates = []    # Empty
nodes_y_coordinates = []
for node in nodelist:
    nodes_x_coordinates.append(node.x)
    nodes_y_coordinates.append(node.y)

node_x_min = min(nodes_x_coordinates)
node_x_max = max(nodes_x_coordinates)
node_y_min = min(nodes_y_coordinates)
node_y_max = max(nodes_y_coordinates)

# Coordinate distance
nodes_width = node_x_max - node_x_min
nodes_height = node_y_max - node_y_min

# Offset
xOffset = 10
yOffset = 10

# Get unit
x_coordinate_unit = (screen_x_width) / nodes_width
y_coordinate_unit = (screen_y_width) / nodes_height

# Iterate over the nodes and make a queue for each node
for node in nodelist:
    # Make a queue for each node
    wait[int(node.id)] = sim.Queue(name='Queue node ' + str(node.id))

    # Determine real x and y pos
    realX = (node.x - node_x_min) * x_coordinate_unit + screen_x_min
    realY = (node.y - node_y_min) * y_coordinate_unit + screen_y_min

    # Determine node type
    if node.type.upper()=='BRIDGE':
        node = Node(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    elif node.type.upper()=='LOCK':
        node = Node(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    elif node.type.upper()=='INTERSECTION':
        node = Node(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)

    elif node.type.upper() == 'DEFAULT':
        node = Node(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    else:
        print(str(node.type) + ' is an invalid type')
    # Put the nodes in the dict
    nodes[node.id] = node


for edge in edgelist:
    # Only if those edges have nodes in the corresponding file
    if edge.node1 in nodes and edge.node2 in nodes:
        node1 = nodes[edge.node1]
        node2 = nodes[edge.node2]
        # Add to the graph
        G.add_edge(edge.node1, edge.node2)
        # Animate the edges of the graph
        sim.AnimateLine(spec=(node1.x, node1.y, node2.x, node2.y), linewidth=2, linecolor='blue')



class VesselGenerator(sim.Component):
    def process(self):
        id = 0;
        while id < 10:
            # Set the current node of the vessel
            # currentnode[vessel.id] = vessel.path.pop(0)
            # Generate random starting and ending node
            vesselStartAndEnd = random.sample(nodelist, 2)
            print(str(vesselStartAndEnd[0].id) + " " + str(vesselStartAndEnd[1].id))
            # Generated path between vessels
            paths_between_generator = nx.all_simple_paths(G, source=vesselStartAndEnd[1].id,
                                                          target=vesselStartAndEnd[0].id)
            nodes_between_set = [node for path in paths_between_generator for node in path]

            # nodes_between_set = set()

            # for node in vessel.path:
            #    nodes_between_set.add(node)

            # Start node
            currentnode[id] = nodes_between_set.pop()
            print(currentnode[id])
            # Generate new vessel
            print(nodes_between_set)
            random_int = random.randint(0, 2)
            Vessel(name="Vessel " + str(id), id=id, speed=int(vessels[random_int].speed), path=nodes_between_set)
            id = id + 1
            yield self.hold(sim.Poisson(10).sample())


VesselGenerator()

env.animate(True)
env.speed(5)
env.modelname('Alsic Simulation')

x_start = screen_x_min
width = screen_x_max - x_start - 75

for x in range(len(wait)):
    wait[x+1].length.animate(x=x_start, y=screen_y_max+20, horizontal_scale=2, width=(width) / len(wait), title='# vessels at node ' + str(x + 1))
    x_start += (width) / len(wait) + 10

    pass
env.run(till=300)  # Set the duration of the simulation

for x in range(len(wait)):
    if x == 0:
        x = x + 1
    wait[x].print_histograms()
    pass
