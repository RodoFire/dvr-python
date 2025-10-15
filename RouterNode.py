#!/usr/bin/env python
from distributed.http.worker.prometheus import routes

import GuiTextArea, RouterPacket, F
from copy import deepcopy

import RouterSimulator


class RouterNode():
    # we define the variable types for better readability
    myID: int = None
    myGUI: GuiTextArea.GuiTextArea = None
    sim: RouterSimulator.RouterSimulator = None
    costs: list[int] = None

    routes: list[int] = None
    distanceTable: list[list[int]] = None

    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    # --------------------------------------------------
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        self.costs = deepcopy(costs)

        self.routes = [None] * self.sim.NUM_NODES
        self.distanceTable = [[self.sim.INFINITY for _ in range(self.sim.NUM_NODES)] for _ in range(self.sim.NUM_NODES)]

        for i in range(self.sim.NUM_NODES):
            self.distanceTable[self.myID][i] = self.costs[i]

            if self.costs[i] == 999:
                continue

            self.routes[i] = i

    # --------------------------------------------------
    def recvUpdate(self, pkt: RouterPacket.RouterPacket):

        pass

    # --------------------------------------------------
    def sendUpdate(self, pkt: RouterPacket.RouterPacket):
        self.sim.toLayer2(pkt)

    # --------------------------------------------------
    def printDistanceTable(self):
        self.myGUI.println("Current table for " + str(self.myID) +
                           "  at time " + str(self.sim.getClocktime()))

        self.myGUI.println("")
        self.printDistanceVector()
        self.myGUI.println("")
        self.printDistanceVectorNRoutes()
        self.myGUI.println("")
        self.myGUI.println("")

    def printTopTable(self):
        table = "     dts  |     0     1"
        spacer = "----------+------------"
        if (len(self.costs) >= 3):
            table += "     2"
            spacer += "-------"
        if (len(self.costs) >= 4):
            table += "     3"
            spacer += "-------"
        if (len(self.costs) >= 5):
            table += "     4"
            spacer += "-------"

        self.myGUI.println(table)
        self.myGUI.println(spacer)

    def printDistanceVector(self):
        self.myGUI.println("distancetable")
        self.printTopTable()
        for i in range(len(self.distanceTable)):
            hop = self.routes[i]
            if hop is None:
                continue
            self.myGUI.println("  nbr  " + str(i) + "  |" + self.printNodeCost(i))

    def printNodeCost(self, actualNode: int):
        line = ""
        for i in range(len(self.distanceTable)):
            value = self.distanceTable[actualNode][i]
            if value > 99:
                line += "   " + str(value)
            elif value > 9:
                line += "    " + str(value)
            else:
                line += "     " + str(value)
        return line

    def printDistanceVectorNRoutes(self):
        self.myGUI.println("Our distance vector and routes:")
        self.printTopTable()
        self.myGUI.println("  cost    |" + self.getCost())
        self.myGUI.println("  route   |" + self.getRoute())

    def getCost(self):
        line = ""
        for i in range(len(self.costs)):
            value = self.costs[i]
            if value > 99:
                line += "   " + str(value)
            elif value > 9:
                line += "    " + str(value)
            else:
                line += "     " + str(value)

        return line

    def getRoute(self):
        line = ""
        for i in range(len(self.routes)):
            value = self.routes[i]
            if value is None:
                line += "     -"
            else:
                line += "     " + str(value)

        return line

    # --------------------------------------------------

    def updateLinkCost(self, dest, newcost):
        pass
