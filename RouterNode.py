#!/usr/bin/env python
# from distributed.http.worker.prometheus import routes

import GuiTextArea, RouterPacket, F
from copy import deepcopy

import RouterSimulator


class RouterNode():
    # we define the variable types for better readability
    myID: int = None
    myGUI: GuiTextArea.GuiTextArea = None
    sim: RouterSimulator.RouterSimulator = None
    costs: list[int] = None

    # set to keep track of direct neighbors
    neighbours: set[int] = None
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
        self.neighbours = set()

        self.routes = [None] * self.sim.NUM_NODES
        self.distanceTable = [[self.sim.INFINITY for _ in range(self.sim.NUM_NODES)] for _ in range(self.sim.NUM_NODES)]

        for i in range(self.sim.NUM_NODES):
            self.distanceTable[self.myID][i] = self.costs[i]

            if self.costs[i] < self.sim.INFINITY:
                self.routes[i] = i

                if self.myID != i:
                    self.neighbours.add(i)

        for i in range(self.sim.NUM_NODES):
            if i != self.myID and self.costs[i] < self.sim.INFINITY:
                pkt = RouterPacket.RouterPacket(self.myID, i, self.costs)
                self.sendUpdate(pkt)

    # --------------------------------------------------
    def recvUpdate(self, pkt: RouterPacket.RouterPacket):
        neighbor = pkt.sourceid
        self.distanceTable[neighbor] = pkt.mincost

        updated = False
        for dest in range(self.sim.NUM_NODES):
            if dest == self.myID:
                continue

            minCost = self.sim.connectcosts[self.myID][dest]
            nextHop = dest

            for nbr in self.neighbours:
                cost = self.sim.connectcosts[self.myID][nbr] + self.distanceTable[nbr][dest]
                if cost < minCost:
                    minCost = cost
                    nextHop = nbr

            if self.costs[dest] != minCost or self.routes[dest] != nextHop:
                self.costs[dest] = minCost
                self.routes[dest] = nextHop
                updated = True

        if updated:
            for neighbor in self.neighbours:
                mincost_to_send = deepcopy(self.costs)
                if self.sim.POISONREVERSE:
                    for d in range(self.sim.NUM_NODES):
                        if self.routes[d] == neighbor:
                            mincost_to_send[d] = self.sim.INFINITY

                pkt = RouterPacket.RouterPacket(self.myID, neighbor, mincost_to_send)
                self.sendUpdate(pkt)

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
            # we do not print its node cost since that its not our neighbor.
            neighbour = i in self.neighbours
            if not neighbour:
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

    def updateLinkCost(self, dest: int, newcost: int):

        self.myGUI.println("Router " + str(self.myID) + " is updating link cost to neighbour " + str(dest) + " to a cost of " + str(newcost))
        print("updating")
        self.sim.connectcosts[self.myID][dest] = newcost

        updated = False
        for d in range(self.sim.NUM_NODES):
            if d == self.myID:
                continue

            minCost = self.sim.connectcosts[self.myID][d]
            nextHop = d

            for nbr in self.neighbours:
                cost = self.sim.connectcosts[self.myID][nbr] + self.distanceTable[nbr][d]
                if cost < minCost:
                    minCost = cost
                    nextHop = nbr

            if self.costs[d] != minCost or self.routes[d] != nextHop:
                self.costs[d] = minCost
                self.routes[d] = nextHop
                updated = True

        if updated:
            for neighbor in self.neighbours:
                mincost_to_send = deepcopy(self.costs)
                if self.sim.POISONREVERSE:
                    for destination in range(self.sim.NUM_NODES):
                        if self.routes[destination] == neighbor:
                            mincost_to_send[destination] = self.sim.INFINITY

                pkt = RouterPacket.RouterPacket(self.myID, neighbor, mincost_to_send)
                self.sendUpdate(pkt)
