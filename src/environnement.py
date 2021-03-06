import random
import enum
import numpy as np

class CP(enum.Enum):
    """ Cardinal Points """
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class Environnement(object):
    """
    Environment class
    """
    def __init__(self,N,M,na,nb,nAgent) -> None:
        self.grid = [[ "0" for j in range(M)] for i in range(N)]
        self.na  = na
        self.nb  = nb
        self.nAgent  = nAgent
        self.N = N 
        self.M = M
        self.agentsPosition = dict()

    def dropObjects(self) -> None:
        """
        Drops the A , the B
        """
        naDroped = 0
        while(naDroped != self.na):
            x = random.randint(0,self.N-1)
            y = random.randint(0,self.M-1)
            if self.grid[x][y] == "0":
                self.grid[x][y] = "A"
                naDroped +=1
        nbDropped = 0
        while(nbDropped != self.nb):
            x = random.randint(0,self.N-1)
            y = random.randint(0,self.M-1)
            if self.grid[x][y] == "0":
                self.grid[x][y] = "B"
                nbDropped +=1

    def dropAgents(self,ids:list) -> None:
        """
        Places agents in the environment only on the available 0 boxes
        """
        naDroped = 0
        while(naDroped != self.nAgent):
            x = random.randint(0,self.N-1)
            y = random.randint(0,self.M-1)
            if self.grid[x][y] == "0":
                self.grid[x][y] = "R"
                self.agentsPosition[ids[naDroped]] = {"x":x,"y":y}
                naDroped +=1
        # return agentPosition

    def getNeighborhood(self,id:str, range:int) -> list:
        """
        Return the neighborhood of the agent
        Args:
            id (str): agent id
            range (int): agent view distance
        """
        ap = self.agentsPosition[id] #Position de l'agent
        nbh = []
        for oriantation in [(0,-1),(1,0),(0,1),(-1,0)]:
            boundx = ap["x"] + (oriantation[0] * range)
            boundy = ap["y"] + (oriantation[1] * range)
            if (boundx < self.N and boundx >= 0 and 
                boundy < self.M and boundy >= 0 and
                self.grid[boundx][boundy] != "R"and 
                len(self.grid[boundx][boundy]) != 2):
                if boundx == ap["x"]:
                    if boundy < ap["y"]:
                        nbh.append(self.grid[ap["x"]][boundy:ap["y"]])
                    else:
                        nbh.append(self.grid[ap["x"]][ap["y"]+oriantation[1]:boundy+oriantation[1]])
                else:
                    if boundx < ap["x"]:
                        nbh.append([ line[ap["y"]] for line in self.grid[boundx:ap["x"]] ])
                    else:
                        nbh.append([ line[ap["y"]] for line in self.grid[ap["x"] + oriantation[0]:boundx + oriantation[0]] ])
            else:
                nbh.append([])
        underAgent = "0"
        if len(self.grid[ap["x"]][ap["y"]]) == 2:
            underAgent = self.grid[ap["x"]][ap["y"]][0]
        return nbh, underAgent

    def newPosition(self, id:str, orentation:CP, range:int) -> None:
        """
        Set the new position of the agent
        Args:
            id (str): agent id
            orentation (CP): agent orienation (cardinal point)
            range (int): range of a step
        """
        orientations = [(0,-1),(1,0),(0,1),(-1,0)]
        ap = self.agentsPosition[id] #Position de l'agent
        newx = ap["x"] + (orientations[orentation.value][0] * range)
        newy = ap["y"] + (orientations[orentation.value][1] * range)
        # clean the previous position
        if len(self.grid[ap["x"]][ap["y"]]) == 2:
            self.grid[ap["x"]][ap["y"]] = self.grid[ap["x"]][ap["y"]][0]
        else:
            self.grid[ap["x"]][ap["y"]] = "0"
            
        # Set the new position
        self.agentsPosition[id] = {"x":newx, "y":newy}
        if self.grid[newx][newy] != "0":
            self.grid[newx][newy] += "R"
        else:
            self.grid[newx][newy] = "R"
            
    def setBlock(self, id:str, block:str) -> None:
        """
        Set the block under the agent
        Args:
            id (str): agent id
            block (str): the new value of the block
        """
        ap = self.agentsPosition[id] #Position de l'agent
        if block == "0":
            # take block AR or BR
            self.grid[ap["x"]][ap["y"]] = "R"
        else:
            # drop block
            self.grid[ap["x"]][ap["y"]] = block+"R"
    
    def evaluateEnv(self) -> object:
        """
        Calculate the rate of neighbor of the same type per object
        Returns:
            object: the Q1 and the mean
        """
        tab = np.array([])
        for x in range(self.N):
            for y in range(self.M):
                if self.grid[x][y][0] != 'A' and self.grid[x][y][0] != 'B':
                    continue
                counter = 0
                same = 0
                for i in range(-1,2):
                    for j in range(-1,2):
                        xn = x + i
                        yn = y + j
                        if (not(i == 0 and j == 0) 
                            and xn < self.N and xn >= 0
                            and yn < self.M and yn >= 0):
                            counter += 1
                            if self.grid[x][y][0] == self.grid[xn][yn][0]:
                                same += 1
                tab = np.append(tab,float(same) / float(counter)) 
        return np.quantile(tab,0.25), np.mean(tab)
    
    def __str__(self) -> str:
        result = ""
        for line in self.grid:
            for value in line:
                if value == "0":
                    result += "⬜"
                elif value == "A":
                    result += "🅰 "
                elif value == "B":
                    result += "🅱 "
                elif len(value) == 2:
                    result += "🛂"
                else:
                    result += "🤖"
            result += "\n"
        return result