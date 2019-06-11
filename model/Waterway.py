from model import ReadFromCSV
import tkinter as tk
from tkinter import simpledialog
import salabim as sim
import math
import networkx as nx
import random
import ctypes
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


import numpy as np
name = "test"
# File vari
if name == "test":
    nodeFile = "../files/waterway_nodelist_modified.csv"
    edgeFile = "../files/waterway_edgelist_modified.csv"
elif name == "scen1":
    nodeFile = "../files/scenario_nodes.csv"
    edgeFile = "../files/edges_scenario_1.csv"
elif name == "scen2":
    nodeFile = "../files/scenario_nodes2.csv"
    edgeFile = "../files/edges_scenario_2.csv"
elif name == "scen3":
    nodeFile = "../files/scenario_nodes3.csv"
    edgeFile = "../files/edges_scenario_3.csv"
# Lock variables
left = -1
right = +1
opentijd = 5
sluittijd = 5
sink_raise_tijd = 10

scen2afslag283 = 3
scen2afslag673 = 5

CEMT_turn_tijd = 5
def sidename(side):
    return "l" if side == left else "r"


def distance(comp1, comp2):
    return math.sqrt((comp1.x - comp2.x) ** 2 + (comp1.y - comp2.y) ** 2)

# verkeerslicht
class Light(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x =x
        self.y = y
        self.type = type
        self.stop = False
        self.cycle = 5
        self.green = False
        self.red = False
        sim.AnimateImage('../Pictures/verkeerslicht.png', x=self.x - 12, y=self.y - 15, width=40)
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')
        sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x, y=self.y)
        self.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=self.x - 15, y=self.y - 45, width=30)
        self.showing = False
        self.button = sim.AnimateButton(x=self.x-50, y= self.y-30,fillcolor=(100,100,100),text="menu", width = 30,action=self.show_buttons)

    def show_buttons(self):
        if self.showing:
            self.red_button.remove()
            self.green_button.remove()
            self.cycle_button.remove()
            self.showing = False
        else:
            print("showing buttons")
            self.red_button = self.button = sim.AnimateButton(x=self.x+100, y= self.y-30,fillcolor=(255,0,0),text="red", width = 30,action=self.always_red)
            self.green_button = self.button = sim.AnimateButton(x=self.x+100, y= self.y-60,fillcolor=(0,255,0),text = "green",width = 30,action=self.always_green)
            self.cycle_button = self.button = sim.AnimateButton(x=self.x+100, y= self.y-90,fillcolor=(128,128,128),text= "cycle", width = 30,action=self.adjust_cycle)
            self.showing = True
    def always_red(self):
        if self.red:
            self.red = False
        else:
            if self.green:
                self.green = False
            self.red = True
            self.stop = True
            self.lightsource.remove()
            self.lightsource = sim.AnimateImage('../Pictures/red-light.png', x=self.x - 15, y=self.y - 45, width=30)

    def always_green(self):
        if self.green:
            self.green = False
        else:
            if self.red:
                self.red = False
            self.green = True
            self.stop = False
            self.lightsource.remove()
            self.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=self.x - 15, y=self.y - 45, width=30)

    def adjust_cycle(self):
        answer = simpledialog.askstring("Cycle", "Enter new cycle")
        if answer is not None:
            self.cycle = int(answer)

    def toggle(self):
        if (self.stop):
            self.stop = False
            self.count = self.cycle
            self.lightsource.remove()
            self.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=self.x - 15, y=self.y - 45, width=30)
        else:
            self.stop = True
            self.count = self.cycle
            self.lightsource.remove()
            self.lightsource = sim.AnimateImage('../Pictures/red-light.png', x=self.x - 15, y=self.y - 45, width=30)
        #sim.AnimateText(text="did action", font='narrow', textcolor='black', text_anchor='c',
        #                offsety=30, x=self.x+30, y=self.y+30)
    def process(self):
        self.count = self.cycle
        while True:
            if not self.green and not self.red:
                if len(wait[self.id]) != 0:
                    vessel = wait[self.id].pop()
                    wait[self.id].add_at_head(vessel)
                    if self.stop:
                        yield self.hold(self.count)
                        wait[self.id].pop()
                        vessel.activate()
                        self.stop = False
                        self.lightsource.remove()
                        self.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=self.x - 15, y=self.y - 45,
                                                            width=30)
                        self.count = self.cycle
                    else:
                        wait[self.id].pop()
                        vessel.activate()



                else:
                    if self.count > 0:
                        self.count= self.count -1
                        yield self.hold(1)
                    else:
                        if(self.stop):
                            self.stop = False
                            self.lightsource.remove()
                            self.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=self.x - 15, y=self.y - 45, width=30)
                        else:
                            self.lightsource.remove()
                            self.stop = True
                            self.lightsource = sim.AnimateImage('../Pictures/red-light.png', x=self.x - 15, y=self.y - 45, width=30)

                        self.count = self.cycle
            elif self.green:
                if len(wait[self.id]) != 0:
                    vessel = wait[self.id].pop()
                    vessel.activate()
                yield self.hold(1)
            else:
                yield self.hold(1)

class LightLock(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.stop = False
        sim.AnimateImage('../Pictures/verkeerslicht.png', x=self.x - 12, y=self.y - 15, width=40)
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')
        sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x, y=self.y)
        self.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=self.x - 15, y=self.y - 45, width=30)

    def process(self):
        while True:
            #print("here we go again "+str(self.id))
            if self.stop:
                #print("i stopped")
                yield self.hold(1)
                #print("free after stop")
            else:
                #print("i did not")
                #print(len(wait[self.id]))
                for ves in wait[self.id]:
                    # yield self.hold(5)
                    ves = wait[self.id].pop()
                    print("for: "+str(len(wait[self.id])))
                    ves.activate()
                #print("activated the nodes")
                yield self.hold(1)
            #print("free")

# Lock component
class Lock(sim.Component):
    def setup(self, id, x, y, type, maxLength):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.maxLength = maxLength
        sim.AnimateImage('../Pictures/lock.png', x=self.x - 10, y=self.y - 10, width=20)
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')
        #sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
        #                offsety=30, x=self.x, y=self.y)
        self.currentlength = 0
        print("test")
        #de neighbors zijn alle aanliggende nodes van de sluis
        #deze hebben een verschillend id. Er zijn n aantal neighbours
        #om een volgorde te bepalen van deze buren wordt aan iedere node
        #een getal van 0 tot n-1 gegeven deze komt overeen met
        #het id nummer van de buur
        self.neighbors = {}
        self.ingangen = {}
        self.nodecount = 0

        #gate die we bekijken
        self.currentGate = 0
        self.openGate = -1
        self.waterlevel = 1
        self.vessels = []
        self.lights = []

        self.info = sim.AnimateText(text="default" , font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x+50, y=self.y-50)

    def open_sluis(self):
        self.openGate = self.currentGate
        self.info.remove()
        self.info = sim.AnimateText(text="opening gate "+ str(self.currentGate), font='narrow', textcolor='black', text_anchor='c',
                        offsety=30, x=self.x+50, y=self.y-50)
        self.hold(opentijd)

    def sluit_sluis(self, gate=-1):
        self.openGate = -1
        if gate == -1:
            gate = self.currentGate

        self.info.remove()
        self.info = sim.AnimateText(text="closing gate " + str(gate), font='narrow', textcolor='black',
                                    text_anchor='c',
                                    offsety=30, x=self.x+50, y=self.y-50)
        self.hold(sluittijd)

    def raise_lower_sluis(self):
        self.info.remove()
        self.info = sim.AnimateText(text="adjust water to " + str(self.currentGate), font='narrow', textcolor='black',
                                    text_anchor='c',
                                    offsety=30, x=self.x+50, y=self.y-50)
        self.waterlevel = self.currentGate
        self.hold(sink_raise_tijd)


    def process(self):

        while True:
            count = 0
            while count < self.nodecount:
                #overlopen boten aan ingang van de huidige gate

                if len(self.ingangen[self.neighbors[self.currentGate]]):
                    #voor stoplichten horend bij de sluis

                    if len(self.lights) != 0:
                        for l in self.lights:
                            l.stop = True
                            l.lightsource.remove()
                            l.lightsource = sim.AnimateImage('../Pictures/red-light.png', x=l.x - 15,
                                                                y=l.y - 45, width=30)

                    vessel = self.ingangen[self.neighbors[self.currentGate]].pop()
                    stop = True

                    added = False
                    #boten inladen vanuit deze ingang tot aan capaciteit voldaan is
                    while self.currentlength + vessel.length < self.maxLength+1 and stop:
                        if len(vessel.path)!=0:
                            self.vessels.append(vessel)
                            added=True
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

                    # indien sluis deur nog open is kunnen boten verder
                    # doorvaren zonder vertraging. Anders zijn een aantal vertragingen nodig
                    if added:
                        if (self.openGate != self.currentGate):
                            # indien een gate open staat sluit deze gate,
                            # verlaag/verhoog waterniveau
                            # open juiste sluisdeur

                            if (self.openGate != -1):
                                yield self.sluit_sluis(self.openGate)
                                yield self.raise_lower_sluis()
                                yield self.open_sluis()

                            # indien geen sluis open staat controleer het waterniveau
                            # indien nit gelijk met niveau huidige gate dan water aanpassen

                            elif self.waterlevel != self.currentGate:
                                yield self.raise_lower_sluis()
                                yield self.open_sluis()
                            # indien alle sluisdeuren dicht en waterniveau al juist
                            # enkel nog sluisdeur opendoen

                            else:
                                yield self.open_sluis()

                    for ves in self.vessels:

                        ves.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)
                    #sluiten gate
                    yield self.sluit_sluis()
                    #situatie bij nieuwe gate
                    count = 0
                else:
                    count = count + 1

                self.currentGate = (self.currentGate + 1) % self.nodecount

                #kijken of boten uit de nieuwe gate moeten varen zo ja laat uitvaren
                if len(self.vessels) != 0:
                    #vullen/ legen sluis en openen lock


                    tempvessels = []
                    varendevessels = []
                    #uitvaart = False
                    for vessel in self.vessels:
                        if len(vessel.path) != 0:

                            if vessel.path[(len(vessel.path)-1)] == self.neighbors[self.currentGate]:

                                self.currentlength = self.currentlength - vessel.length
                                varendevessels.append(vessel)

                            else:
                                tempvessels.append(vessel)
                        else:
                            self.currentlength = self.currentlength - vessel.length
                            vessel.leave(wait[self.id])
                            vessel.activate()
                    self.vessels = tempvessels
                    count = 0

                    if len(varendevessels)!=0:
                        yield self.raise_lower_sluis()
                        yield self.open_sluis()
                        for vessel in varendevessels:
                            vessel.leave(wait[self.id])
                            vessel.activate()
                        #uitvaren schepen
                        waiting = len(wait[self.id])
                        for ing in self.ingangen:
                            waiting += len(self.ingangen[ing])
                        if(waiting==0):
                            if len(self.lights) != 0:
                                for l in self.lights:
                                    l.stop = False
                                    l.lightsource.remove()
                                    l.lightsource = sim.AnimateImage('../Pictures/green-light.png', x=l.x - 15,
                                                                        y=l.y - 45, width=30)
            yield self.passivate()


# Intersection component
class Intersection(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        #sim.AnimateImage('../Pictures/intersection_icon.png', x=self.x - 15, y=self.y - 15, width=30)
        #sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
        #                offsety=30, x=self.x, y=self.y)

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
                            if not (currentnode[vessel.id] in uniqueEdgevessels):
                                print("entered deadvessels")
                                deadlockvessels.append(vessel)
                                uniqueEdgevessels[currentnode[vessel.id]] = 1;
                                print(str(uniqueEdgevessels[currentnode[vessel.id]])+" jap ")
                        else:
                            self.count[vessel] += 1
                            vessel.activate()
                    else:
                        self.count[vessel] += 1
                        vessel.activate()
                if len(deadlockvessels)==len(self.neighbours):
                    print(len(deadlockvessels))
                    vessel = deadlockvessels[random.randint(0,len(deadlockvessels))-1]
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
        sim.AnimateImage('../Pictures/bridge_icon.png', x=self.x - 10, y=self.y - 10, width=20)
        #sim.AnimateText(text=self.type + " " + str(self.id), font='narrow', textcolor='black', text_anchor='c',
        #                offsety=30, x=self.x, y=self.y)

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
                        waiting_boats = []
                        waiting_boats.append(vessel)
                        for x in range(0,5):
                            for vessel2 in wait[self.id]:
                                if vessel2.height < self.height:
                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                elif not waiting_boats.__contains__(vessel2):
                                    waiting_boats.append(vessel2)
                            yield self.hold(1)

                        for ves in waiting_boats:
                            print("removing boat: "+ str(ves.id))
                            wait[self.id].remove(ves)
                            vessel.activate()
                        self.closed = False
                    else:
                        wait[self.id].pop()
                        vessel.activate()
                    count = 10
                else:
                    wait[self.id].pop()
                    vessel.activate()
                    if not self.closed:
                        if count > 0:
                            count = count - 1
                        else:
                            self.closed = True

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

class Knoop1(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')

    def process(self):
        while True:
            if len(wait[self.id]) != 0:
                yield self.hold(5)
                vessel = wait[self.id].pop()
                vessel.activate()
            else:
                yield self.passivate()

class Knoop2(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')
        self.Q0 = sim.Queue()
        self.Q1 = sim.Queue()
        self.Q2 = sim.Queue()
    def process(self):
        while True:
            if len(wait[self.id]) != 0:

                if len(self.Q1)!=0:
                    print("inside Q1")
                    vessel = self.Q1.pop()
                    abort = False
                    while vessel.path[(len(vessel.path)-1)] == 3 and not abort:
                        print("next location is 3")
                        wait[self.id].remove(vessel)
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                              fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        vessel.activate()
                        if len(self.Q1) != 0:
                            vessel = self.Q1.pop()
                        else:
                            abort = True

                    if vessel.path[(len(vessel.path) - 1)] != 3:
                        self.Q1.add_at_head(vessel)




                if len(self.Q0)!=0:
                    vessel = self.Q0.pop()

                    abort=False
                    while vessel.path[(len(vessel.path)-1)] == 67 and not abort:
                        wait[self.id].remove(vessel)
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        vessel.activate()
                        if len(self.Q0)!=0:
                            vessel = self.Q0.pop()
                        else:
                            abort = True
                    if vessel.path[(len(vessel.path) - 1)] != 67:
                        self.Q0.add_at_head(vessel)

                if len(self.Q1) != 0:
                    print("inside Q1 again")
                    vessel = self.Q1.pop()
                    if vessel.path[(len(vessel.path)-1)] == 283:
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        yield self.hold(scen2afslag283)
                        wait[self.id].remove(vessel)
                        vessel.activate()
                elif len(self.Q2) != 0:
                    vessel = self.Q2.pop()
                    vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                    yield self.hold(scen2afslag673)
                    wait[self.id].remove(vessel)
                    vessel.activate()
                elif len(self.Q0)!=0:
                    vessel = self.Q0.pop()
                    if vessel.path[(len(vessel.path)-1)] == 283:
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        yield self.hold(scen2afslag283)
                        wait[self.id].remove(vessel)
                        vessel.activate()


            else:
                yield self.passivate()

class Knoop3(sim.Component):
    def setup(self, id, x, y, type):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        sim.Animate(circle0=2, x0=self.x, y0=self.y, fillcolor0=('black', 200), linewidth0=2, linecolor0='black')
        self.Q0 = sim.Queue()
        self.Q1 = sim.Queue()
        self.Q2 = sim.Queue()

    def process(self):
        while True:
            while len(wait[self.id])!=0:
                CEMT = False
                if len(self.Q1) !=0:
                    vessel = self.Q1.pop()
                    if vessel.CEMT == 5:
                        if vessel.path[(len(vessel.path)-1)] == 285:
                            CEMT = True
                            abort = False
                            while len(self.Q0)!=0 and not abort:
                                vessel2 = self.Q0.pop()
                                if vessel2.CEMT <3:
                                    vessel2.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                else:
                                    abort = True
                                    self.Q0.add_at_head(vessel2)
                            abort = False
                            while len(self.Q2)!=0 and not abort:
                                vessel2 = self.Q2.pop()
                                if vessel2.CEMT <3:
                                    vessel2.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                else:
                                    abort = True
                                    self.Q2.add_at_head(vessel2)
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                     fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                            yield self.hold(CEMT_turn_tijd)
                            wait[self.id].remove(vessel)
                            vessel.activate()
                        else:
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                     fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                            wait[self.id].remove(vessel)
                            vessel.activate()

                    else:
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        wait[self.id].remove(vessel)
                        vessel.activate()
                if len(self.Q2) !=0 and not CEMT:
                    vessel = self.Q2.pop()
                    if vessel.CEMT == 5:
                        if vessel.path[(len(vessel.path)-1)] == 285:
                            CEMT = True
                            abort = False
                            while len(self.Q0)!=0 and not abort:
                                vessel2 = self.Q0.pop()
                                if vessel2.CEMT <3:
                                    vessel2.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                else:
                                    abort = True
                                    self.Q0.add_at_head(vessel2)
                            abort = False
                            while len(self.Q1)!=0 and not abort:
                                vessel2 = self.Q1.pop()
                                if vessel2.CEMT <3:
                                    vessel2.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                else:
                                    abort = True
                                    self.Q1.add_at_head(vessel2)
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                     fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                            yield self.hold(CEMT_turn_tijd)
                            wait[self.id].remove(vessel)
                            vessel.activate()
                        else:
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                     fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                            wait[self.id].remove(vessel)
                            vessel.activate()

                    else:
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        wait[self.id].remove(vessel)
                        vessel.activate()


                if len(self.Q0) !=0 and not CEMT:
                    vessel = self.Q0.pop()
                    if vessel.CEMT == 5:
                        if vessel.path[(len(vessel.path)-1)] == 285:
                            CEMT = True
                            abort = False
                            while len(self.Q2)!=0 and not abort:
                                vessel2 = self.Q2.pop()
                                if vessel2.CEMT <3:
                                    vessel2.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                else:
                                    abort = True
                                    self.Q2.add_at_head(vessel2)
                            abort = False
                            while len(self.Q1)!=0 and not abort:
                                vessel2 = self.Q1.pop()
                                if vessel2.CEMT <3:
                                    vessel2.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                             fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                                    wait[self.id].remove(vessel2)
                                    vessel2.activate()
                                else:
                                    abort = True
                                    self.Q1.add_at_head(vessel2)
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                     fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                            yield self.hold(CEMT_turn_tijd)
                            wait[self.id].remove(vessel)
                            vessel.activate()
                        else:
                            vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                     fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                            wait[self.id].remove(vessel)
                            vessel.activate()

                    else:
                        vessel.pic_vessel.update(circle0=15, x0=self.x, y0=vessel.y,
                                                 fillcolor0='', linecolor0=vessel.color, linewidth0=2)

                        wait[self.id].remove(vessel)
                        vessel.activate()

            yield self.passivate()

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

        self.CEMT = 5
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
                if(dist != 0 ):
                    x_speed = ((node.x - self.x) / dist) * self.speed
                    y_speed = ((node.y - self.y) / dist) * self.speed
                else:

                    x_speed = 0
                    y_speed = 0

                #amount is aantal sec voor de volgende node bereikt is
                amount = round(dist / self.speed)
                if amount > 5:
                    treshold = amount - 6
                    count = 1 #VAARWATER
                else:
                    treshold = 0
                    count = 6 - amount
                #print("vessel is stuck")
                #treshold is het aantal sec dat de boot nog mag varen voor alleer in de 5 sec queue geplaatst wordt.
                for x in range(0, amount-1):
                    #print("here we go")
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
                elif node.type.upper() == "SCEN1KNOT" and len(wait[node.id])>1:
                    print("waiting outside")
                elif node.type.upper() == "SCEN2KNOT":
                    print(currentnode[self.id])
                    if currentnode[self.id]== 3:
                        self.enter(node.Q0)
                    elif currentnode[self.id]==67:
                        print("entered Q1")
                        self.enter(node.Q1)
                    elif currentnode[self.id] == 283:
                        self.enter(node.Q2)
                elif node.type.upper() == "SCEN3KNOT":
                    if currentnode[self.id]== 71:
                        self.enter(node.Q0)
                    elif currentnode[self.id]==4:
                        print("entered Q1")
                        self.enter(node.Q1)
                    elif currentnode[self.id] == 285:
                        self.enter(node.Q2)
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
        #sim.AnimateText(text=self.type+" "+str(self.id), font='narrow', textcolor='black', text_anchor='c', offsety=30, x=self.x,y=self.y)

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
screen_x_min = 50
screen_x_max = 900
screen_x_width = screen_x_max - screen_x_min
screen_y_min = 50
screen_y_max = 600
screen_y_width = screen_y_max - screen_y_min

# Visualize the background
sim.AnimateRectangle((0,0, screen_x_max, screen_y_max), fillcolor='90%gray')
if name == "test":
    sim.AnimateImage('../Pictures/layout.png', x=0, y=27, width=940)
elif name == "scen1":
    sim.AnimateImage('../Files/scenario1.png', x=0, y=27, width=940)
elif name == "scen2":
    sim.AnimateImage('../Files/scenario2.png', x=0, y=27, width=940)
elif name == "scen3":
    sim.AnimateImage('../Files/scenario3.png', x=0, y=27, width=940)


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
lightLocks = []
# Iterate over the nodes and make a queue for each node



for node in nodelist:
    # Make a queue for each node
    wait[int(node.id)] = sim.Queue(name='Queue node ' + str(node.id))

    # Determine real x and y pos
    realX = (node.x - node_x_min) * x_coordinate_unit + screen_x_min
    realY = ((node.y-node_y_min ) * y_coordinate_unit + screen_y_min)

    # Determine node type
    if node.type.upper()=='BRIDGE':
        node = Bridge(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type, height = 650)
    elif node.type.upper()=='LOCK':
        node = Lock(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type, maxLength=15);
        locknodes.append(node)
    elif node.type.upper()=='INTERSECTION':
        node = Intersection(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
        intersectnodes.append(node)
    elif node.type.upper() == 'DEFAULT':
        node = Node(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    elif node.type.upper() == 'LIGHT':
        node = Light(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    elif node.type.upper() == 'LIGHTLOCK':
        node = LightLock(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
        lightLocks.append(node)
    elif node.type.upper() == "SCEN1KNOT":
        node = Knoop1(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    elif node.type.upper() == "SCEN2KNOT":
        node = Knoop2(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)
    elif node.type.upper() == "SCEN3KNOT":
        node = Knoop3(name="Node " + str(node.id), id=node.id, x=realX, y=realY, type=node.type)

    else:
        print(str(node.type) + ' is an invalid type')
    # Put the nodes in the dict
    nodes[node.id] = node


nodes[3].lights = lightLocks
for edge in edgelist:
    # Only if those edges have nodes in the corresponding file
    if edge.node1 in nodes and edge.node2 in nodes:
        node1 = nodes[edge.node1]
        node2 = nodes[edge.node2]
        # Add to the graph
        G.add_edge(edge.node1, edge.node2)
        # Animate the edges of the graph
        sim.AnimateLine(spec=(node2.x, node2.y, node1.x, node1.y), linewidth=2, linecolor='blue')

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
        while True:
            # Set the current node of the vessel
            # currentnode[vessel.id] = vessel.path.pop(0)
            # Generate random starting and ending node
            customized_nodelist = []
            for no in nodelist:
                if no.type.upper() != 'LIGHTLOCK' and no.type.upper() != "LOCK" and no.type.upper() != "SCEN3KNOT" and no.type.upper() != "SCEN2KNOT" and no.type.upper() != "SCEN1KNOT":
                    customized_nodelist.append(no)

            vesselStartAndEnd = random.sample(customized_nodelist, 2)
            print(str(vesselStartAndEnd[0].id) + " tester " + str(vesselStartAndEnd[1].id))
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
            random_int = random.randint(0, 59)
            random_height = random.randint(200,1100)
            Vessel(name="Vessel " + str(id), id=id, speed=int(vessels[random_int].speed), path=nodes_between_set,length=5, height=int(random_height))
            id = id + 1
            yield self.hold(sim.Poisson(10).sample())


print("start")
VesselGenerator()
print("vessels generated")
env.an_synced_buttons()
env.an_unsynced_buttons()
env.animate(True)
env.speed(5)
env.modelname('Alsic Simulation')
env.height(screensize[1])
env.width(screensize[0])
x_start = screen_x_min
width = screen_x_max

for node in G.nodes():
    print(node)

stuff = nx.check_planarity(G, False)
print(stuff[1].check_structure())
'''
for x in range(len(wait)):
    wait[x+1].length.animate(x=x_start, y=screen_y_max+20, horizontal_scale=2, width=(width) / len(wait), title='# vessels at node ' + str(x + 1))
    x_start += (width) / len(wait) + 10'''
print("starting env")
env.run(till=400)  # Set the duration of the simulation

for x in range(len(wait)):
    if x == 0:
        x = x + 1
    wait[x].print_histograms()
    pass
