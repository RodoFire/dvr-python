#!/usr/bin/env python
from distributed.http.worker.prometheus import routes

import GuiTextArea, RouterPacket, F
from copy import deepcopy


class RouterNode():
    myID = None
    myGUI = None
    sim = None
    costs = None

    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    # --------------------------------------------------
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")

        self.costs = deepcopy(costs)

    # --------------------------------------------------
    def recvUpdate(self, pkt):
        pass

    # --------------------------------------------------
    def sendUpdate(self, pkt):
        self.sim.toLayer2(pkt)

    # --------------------------------------------------
    def printDistanceTable(self):
        self.myGUI.println("Current table for " + str(self.myID) +
                           "  at time " + str(self.sim.getClocktime()))

        self.myGUI.println("")
        self.printDistanceVectorNRoutes()

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
        for i in range(len(self.costs)):
            value = self.costs[i]
            if value == 999:
                line += "     -"
            else:
                line += "     " + str(i)

        return line

    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):
        pass
