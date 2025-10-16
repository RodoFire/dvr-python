#!/usr/bin/env python
#from distributed.http.worker.prometheus import routes

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

        # initialize the arrays
        self.routes = [None] * self.sim.NUM_NODES
        self.distanceTable = [[self.sim.INFINITY for _ in range(self.sim.NUM_NODES)] for _ in range(self.sim.NUM_NODES)]

        for i in range(self.sim.NUM_NODES):
            self.distanceTable[self.myID][i] = self.costs[i]

            # Set direct routes to neighbors (when the cost < INFINITY)
            if self.costs[i] < self.sim.INFINITY:
                self.routes[i] = i

        # Send initial distance vector to all neighbors
        for i in range(self.sim.NUM_NODES):
            if i != self.myID and self.costs[i] < self.sim.INFINITY:
                # Send update to this neighbor
                pkt = RouterPacket.RouterPacket(self.myID, i, self.costs)
                self.sendUpdate(pkt)

    # --------------------------------------------------
    def recvUpdate(self, pkt: RouterPacket.RouterPacket):
        # Update the distance table with received information + store the distance vector from the neighbor who sent this packet
        neighbor = pkt.sourceid
        
        # Update the row in distance table for this neighbor
        for i in range(self.sim.NUM_NODES):
            self.distanceTable[neighbor][i] = pkt.mincost[i]
        
        # Apply Bellman-Ford equation and for each destination, calculate if there's a better path
        updated = False
        for dest in range(self.sim.NUM_NODES):
            if dest == self.myID:
                continue
            
            # Find minimum cost to destination through all neighbors
            minCost = self.sim.INFINITY
            nextHop = None
            
            for via in range(self.sim.NUM_NODES):
                if via == self.myID:
                    continue
                # Cost to destination via this neighbor = cost to neighbor + neighbor's cost to destination
                cost = self.costs[via] + self.distanceTable[via][dest]
                if cost < minCost:
                    minCost = cost
                    nextHop = via
            
            # Update if we found a better route
            if minCost < self.costs[dest]:
                if self.costs[dest] != minCost or self.routes[dest] != nextHop:
                    self.costs[dest] = minCost
                    self.routes[dest] = nextHop
                    updated = True
        
        # If our distance vector changed, send updates to all neighbors
        if updated:
            for i in range(self.sim.NUM_NODES):
                # in the case the node is not our neighbor or is ourselves, we don't send a packet
                if i == self.myID or self.costs[i] == self.sim.INFINITY:
                    continue

                # Prepare packet to send
                if self.sim.POISONREVERSE:
                    # Apply poison reverse : if we route through neighbor i to reach destination, we must tell neighbor i that our distance to destination is infinity
                    mincost = deepcopy(self.costs)
                    for dest in range(self.sim.NUM_NODES):
                        if self.routes[dest] == i:
                            mincost[dest] = self.sim.INFINITY
                    pkt = RouterPacket.RouterPacket(self.myID, i, mincost)
                else:
                    pkt = RouterPacket.RouterPacket(self.myID, i, self.costs)
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

    def updateLinkCost(self, dest: int, newcost: int):

        pass
