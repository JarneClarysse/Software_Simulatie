from model import ReadFromCSV
import salabim as sim
import math
import networkx as nx
import random
import numpy as np

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
    def setup(self, id, x, y, type, maxLength):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.maxLength = maxLength
        sim.AnimateImage('../Pictures/lock.png', x=self.x - 15, y=self.y - 15, width=40)
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')
        sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x, y=self.y)
        self.currentlength = 0;
        print("test")
        self.neighbors = {}
        self.ingangen = {}
        self.nodecount = 0
        self.currentGate = 0;
        self.vessels = []


    def process(self):
        print("activated first")

        print("neighbours")

        while True:
            count = 0
            while count < self.nodecount:

                print("while loop")
                print("currentgate: "+str(self.currentGate))
                print("neighbors: "+str(self.neighbors[self.currentGate]))
                print("ingangen: "+str(len(self.ingangen[self.neighbors[self.currentGate]])))
                print("currentlength"+str(self.currentlength))
                if len(self.ingangen[self.neighbors[self.currentGate]]):
                    print("entered")
                    vessel = self.ingangen[self.neighbors[self.currentGate]].pop()
                    stop = True

                    #boten inladen vanuit deze ingang tot aan capaciteit voldaan is
                    while self.currentlength + vessel.length < self.maxLength+1 and stop:
                        if len(vessel.path)!=0:
                            self.vessels.append(vessel)
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                               fillcolor0='', linecolor0=vessel.color, linewidth0=2)
                            self.currentlength = self.currentlength + vessel.length
                        else:
                            vessel.leave(wait[self.id])
                            vessel.activate()
                        #ophalen nieuwe boot
                        if (len(self.ingangen[self.neighbors[self.currentGate]]) != 0):
                            vessel = self.ingangen[self.neighbors[self.currentGate]].pop()
                        else:
                            stop = False




                    if stop:
                        self.ingangen[self.neighbors[self.currentGate]].add_at_head(vessel)
                    #processen invaren schepen
                    yield self.hold(5)
                    #situatie bij nieuwe gate
                    count = 0
                else:
                    print("count1: "+str(count))
                    count = count + 1


                print("count2: "+ str(count))
                print("vessels length: "+ str(len(self.vessels)))
                self.currentGate = (self.currentGate + 1) % self.nodecount

                if len(self.vessels) != 0:
                    #vullen/ legen sluis en openen lock
                    yield self.hold(10)

                    tempvessels = []
                    uitvaart = False
                    for vessel in self.vessels:
                        if len(vessel.path) != 0:
                            print("vessel first on path" + str(vessel.path[(len(vessel.path)-1)]))
                            print(vessel.path)
                            print("node from gate" + str(self.neighbors[self.currentGate]))
                            print("opened gate: "+str(self.currentGate))
                            if vessel.path[(len(vessel.path)-1)] == self.neighbors[self.currentGate]:
                                print("releasing vessel: "+str(vessel.id))

                                self.currentlength = self.currentlength - vessel.length
                                vessel.leave(wait[self.id])
                                vessel.activate()
                                uitvaart = True
                            else:
                                tempvessels.append(vessel)
                        else:
                            self.currentlength = self.currentlength - vessel.length
                            vessel.leave(wait[self.id])
                            vessel.activate()
                    self.vessels = tempvessels
                    print("count3: " + str(count))
                    count = 0

                    if uitvaart:
                        #uitvaren schepen
                        yield self.hold(5)
                print("count4: "+ str(count))
            yield self.passivate()
            print("activated?")


# Intersection component
class Intersection(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        sim.AnimateImage('../Pictures/intersection_icon.png', x=self.x - 15, y=self.y - 15, width=30)
        sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x, y=self.y)
        self.vessels = []
        self.edgequeues = {}
        self.neighbours = {}
        self.count = {}

    def process(self):
        while True:
            if len(self.vessels) != 0:
                deadlockvessels = []
                uniqueEdgevessels = {}
                yield self.hold(1)
                for vessel in self.vessels:
                    rechterqueue = self.edgequeues[self.neighbours[currentnode[vessel.id]]]

                    if len(rechterqueue)!=0:

                        if self.count[vessel] == 5:
                            print (self.count[vessel])
                            if uniqueEdgevessels.get(currentnode[vessel.id])!=None:
                                deadlockvessels.append(vessel)
                                uniqueEdgevessels[currentnode[vessel.id]] = 1;
                        else:
                            self.count[vessel] += 1
                            vessel.activate()
                    else:
                        self.count[vessel] += 1
                        vessel.activate()
                if len(deadlockvessels)==4:
                    vessel = deadlockvessels[random.randint(0,len(deadlockvessels))]
                    vessel.activate()

            else:
                yield self.passivate()


# Bridge component
class Bridge(sim.Component):

    def setup(self, id, x, y, type, height):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        sim.AnimateImage('../Pictures/bridge_icon.png', x=self.x - 15, y=self.y - 15, width=30)
        sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x, y=self.y)
        self.closed = True
        self.height = height

    def process(self):
        count = 0
        while True:
            if len(wait[self.id]) != 0:
                vessel = wait[self.id].pop()
                wait[self.id].add_at_head(vessel)
                if vessel.height > self.height:
                    if self.closed:
                        yield self.hold(5)
                        wait[self.id].pop()
                        vessel.activate()
                        self.closed = False
                    else:
                        wait[self.id].pop()
                        vessel.activate()
                    count = 10
                else:
                    wait[self.id].pop()
                    vessel.activate()

            else:
                if count > 0:
                    count= count -1
                    yield self.hold(1)
                else:
                    self.closed = True
                    yield self.passivate()


# Narrowing component
class Narrowing(sim.Component):
    def process(self):
        pass


class Vessel(sim.Component):
    def setup(self, id, speed, path, length,height):
        self.path = path
        self.id = id
        self.speed = speed
        self.x = nodes[int(currentnode[int(self.id)])].x
        self.y = nodes[int(currentnode[int(self.id)])].y
        self.color = ('red', 'blue', 'green', 'purple', 'black', 'pink')[self.id%6]
        self.pic_vessel = sim.Animate(circle0=15, x0=self.x, y0=self.y,
                                      fillcolor0='', linecolor0=self.color, linewidth0=2)
        self.length = length
        self.height = height

    #def hold(self, time):
    #   yield self.hold(time)

    def process(self):
        print("vessel created with:" + str(self.id))
        print(self.path)
        start = True
        while start:
            if(len(self.path)!=0):
                node = nodes[self.path.pop()]
                dist = distance(self, node)
                x_speed = ((node.x - self.x) / dist) * self.speed
                y_speed = ((node.y - self.y) / dist) * self.speed
                amount = round(dist / self.speed)
                if amount > 5:
                    treshold = amount - 6
                    count = 1
                else:
                    treshold = 0
                    count = 6 - amount
                for x in range(0, amount-1):
                    self.x = self.x + x_speed;
                    self.y = self.y + y_speed;

                    self.pic_vessel.update(circle0=15, x0=self.x, y0=self.y,
                                           fillcolor0='', linecolor0=self.color, linewidth0=2)
                    if node.type.upper() == "INTERSECTION" and x >=treshold:

                        if(x == treshold):
                            print("we did it guys")
                            node.vessels.append(self)
                            self.enter(node.edgequeues[currentnode[self.id]])
                            node.count[self] = count
                            if node.ispassive():
                                node.activate()
                        print("wollah")
                        yield self.passivate()
                    else:
                        yield self.hold(1)

                self.x = node.x
                self.y = node.y

                self.enter(wait[node.id])

                # nieuw stuff
                if (node.type.upper() == "LOCK"):
                    print("its a lock")
                    self.enter(node.ingangen[currentnode[self.id]])
                elif node.type.upper() == "INTERSECTION":
                    if (amount == 1):
                        node.vessels.append(self)
                        self.enter(node.edgequeues[currentnode[self.id]])
                        node.count[self] = count
                        if node.ispassive():
                            node.activate()
                        yield self.passivate()

                    oldnode = currentnode[self.id]
                    self.pic_vessel.update(circle0=15, x0=self.x, y0=self.y,
                                           fillcolor0='', linecolor0=self.color, linewidth0=2)
                else:
                    self.pic_vessel.update(circle0=15, x0=self.x, y0=self.y,
                                           fillcolor0='', linecolor0=self.color, linewidth0=2)
                # einde nieuw stuff

                if node.ispassive():
                    node.activate()

                yield self.passivate()

                if(node.type.upper() =="INTERSECTION"):
                    print("jeweetzelf+"+str(self.id))
                    print("oldnode: "+str(oldnode))
                    node.vessels.remove(self)
                    self.leave(node.edgequeues[oldnode])
                    print(len(node.edgequeues[oldnode]))
                    node.count.pop(self)
                    self.leave(wait[node.id])

                currentnode[self.id] = node.id

            else:
                self.pic_vessel.update(visible=False)
                start = False


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
                yield self.hold(5)
                vessel = wait[self.id].pop()
                vessel.activate()
            else:
                yield self.passivate()


nodelist = ReadFromCSV.getNodes(nodeFile)   # Get list of nodes from the csv
edgelist = ReadFromCSV.getEdges(edgeFile)   # Get list of edges from the csv
vessels = ReadFromCSV.getVessels()  # Get vessels from the csv

G = nx.Graph()  # Generate graph

# Generate the environment
env = sim.Environment(trace=False)   # Print the stack trace

# Settings for the visualization
screen_x_min = 25
screen_x_max = 1000
screen_x_width = screen_x_max - screen_x_min
screen_y_min = 25
screen_y_max = 550
screen_y_width = screen_y_max - screen_y_min

# Visualize the background
sim.AnimateRectangle((screen_x_min, screen_y_min, screen_x_max, screen_y_max), fillcolor='90%gray')
sim.AnimateImage('../Pictures/layout2.png', x=screen_x_min, y=screen_y_min)

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

locknodes = []
intersectnodes = []
# Iterate over the nodes and make a queue for each node
for node in nodelist:
    # Make a queue for each node
    wait[int(node.id)] = sim.Queue(name='Queue node ' + str(node.id))

    # Determine real x and y pos
    realX = (node.x - node_x_min) * x_coordinate_unit + screen_x_min
    realY = (node.y - node_y_min) * y_coordinate_unit + screen_y_min

    # Determine node type
    if node.type.upper()=='BRIDGE':
        node = Bridge(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type,height = 50)
    elif node.type.upper()=='LOCK':
        node = Lock(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type, maxLength=15);
        locknodes.append(node)
    elif node.type.upper()=='INTERSECTION':
        node = Intersection(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
        intersectnodes.append(node)
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

for node in locknodes:
    count = 0
    for neighbour in G.neighbors(node.id):
        node.ingangen[neighbour] = sim.Queue()
        node.neighbors[count] = neighbour
        count = count + 1
    node.nodecount = count
    node.currentGate = count % count

for node in intersectnodes:
    first = True
    for neighbour in G.neighbors(node.id):
        if first:
            first = False
            firstneighbour = neighbour
        else:
            node.neighbours[neighbour]=previousneighbour
        node.edgequeues[neighbour] = sim.Queue()
        previousneighbour = neighbour

    node.neighbours[firstneighbour]=previousneighbour


class VesselGenerator(sim.Component):
    def process(self):
        id = 0;
        while id < 20:
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
            Vessel(name="Vessel " + str(id), id=id, speed=int(vessels[random_int].speed), path=nodes_between_set,length=5, height=60)
            id = id + 1
            yield self.hold(sim.Poisson(10).sample())


print("start")
VesselGenerator()
print("vessels generated")
env.animate(True)
env.speed(5)
env.modelname('Alsic Simulation')

x_start = screen_x_min
width = screen_x_max - x_start - 75

for node in G.nodes():
    print(node)

stuff = nx.check_planarity(G, False)
print(stuff[1].check_structure())
for x in range(len(wait)):
    wait[x+1].length.animate(x=x_start, y=screen_y_max+20, horizontal_scale=2, width=(width) / len(wait), title='# vessels at node ' + str(x + 1))
    x_start += (width) / len(wait) + 10
print("starting env")
env.run(till=400)  # Set the duration of the simulation

for x in range(len(wait)):
    if x == 0:
        x = x + 1
    wait[x].print_histograms()
    pass
