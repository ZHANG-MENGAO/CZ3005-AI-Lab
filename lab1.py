import json
import math


def Dataloader(filename):
    with open(filename) as f:
        return json.load(f)

# minHeap based on array--starting from 1
class PriorityQ():
    def __init__(self):
        self.Q = []
        self.positions = {}

    def parent(self, i):
        return (i-1)//2

    def leftChild(self, i):
        return 2*i+1

    def rightChild(self, i):
        return 2*i+2

    def swap(self, i, j):
        self.Q[i], self.Q[j] = self.Q[j], self.Q[i]
        self.positions[self.Q[i][1]] = i
        self.positions[self.Q[j][1]] = j

    def bubbleUp(self, i):
        while(i != 0 and self.Q[i][0] < self.Q[self.parent(i)][0]):
            self.swap(self.parent(i), i)
            i = self.parent(i)

    def sinkDown(self, i):
        min = i
        l = self.leftChild(i)
        r = self.rightChild(i)
        if(l < len(self.Q) and self.Q[l][0] < self.Q[min][0]):
            min = l
        if(r < len(self.Q) and self.Q[r][0] < self.Q[min][0]):
            min = r
        if(min != i):
            self.swap(min, i)
            self.sinkDown(min)

    def push(self, w, v):
        self.Q.append((w, v))
        self.positions[v] = len(self.Q)-1
        self.bubbleUp(len(self.Q)-1)

    def decreaseKey(self, decreased_w, v):
        position = self.positions[v]
        self.Q[position] = (decreased_w, v)
        self.bubbleUp(position)

    def pop(self):
        min_v = self.Q[0][1]
        last_position = len(self.Q)-1
        self.swap(0, last_position)
        self.positions.pop(min_v)
        self.Q.pop(last_position)
        self.sinkDown(0)
        return min_v

    def isEmpty(self):
        return len(self.Q) == 0


def UCS(src, goal):
    pi = {}
    d = {}
    visited = set()
    pq = PriorityQ()

    pi[src] = None
    d[src] = 0
    cost = 0
    pq.push(d[src], src)

    while not pq.isEmpty():
        cur = pq.pop()

        if cur == goal:
            path = [goal]
            while pi[cur]:
                path.insert(0, pi[cur])
                cost += Cost[pi[cur]+','+cur]
                cur = pi[cur]
            #alternatively, cost = sum([Cost[path[i]+','+path[i+1]] for i in range(1, len(path))])
            distance = d[goal]
            return path, distance, cost

        visited.add(cur)
        for v in G[cur]:
            if v not in visited:
                if v not in d:
                    pi[v] = cur
                    d[v] = d[cur] + Dist[cur+','+v]
                    pq.push(d[v], v)
                elif d[v] > d[cur] + Dist[cur+','+v]:
                    pi[v] = cur
                    d[v] = d[cur] + Dist[cur+','+v]
                    pq.decreaseKey(d[v], v)
    return None


def constrainedUCS(src, goal):
    weights = {}  # weights store all the distance and energy states of each node
    pq = PriorityQ()
    pq.push(0, (None, 0, 0, src))
    # distance, (previous-node-state, distance, energy-cost, node)
    weights[src] = set()
    weights[src].add((0, 0))  #(distance, energy-cost)

    while not pq.isEmpty():
        curstate = pq.pop()  # curstate: current state
        cur = curstate[3]
        if cur == goal:
            distance = curstate[1]
            cost = curstate[2]
            path = [goal]
            while curstate[0]:
                path.insert(0, curstate[0][3])
                curstate = curstate[0]
            return path, distance, cost

        for v in G[cur]:
            to_add = True
            if curstate[2]+Cost[cur+','+v] <= energyConstraint:
                d = curstate[1]+Dist[cur+','+v]  #distance
                e = curstate[2]+Cost[cur+','+v]  #energy cost
                if v in weights:
                    for weight in weights[v]:
                        if d >= weight[0] and e >= weight[1]:
                        # if v has been visited in the current path, its current distance
                        # and energy cost must both be higher than the existing values.That's why
                        # this condition is enough
                            to_add = False
                            break
                    if to_add:
                        pq.push(d, (curstate, d, e, v))
                        weights[v].add((d, e))
                else:
                    pq.push(d, (curstate, d, e, v))
                    weights[v] = set()
                    weights[v].add((d, e))
    return None


def calculateDistance(v1, v2):
    dist = math.sqrt((Coord[v2][0] - Coord[v1][0]) **
                     2 + (Coord[v2][1] - Coord[v1][1])**2)
    return dist


def Astar(src, goal):
    weights = {}  # weights store all the distanc and energy states of each node
    pq = PriorityQ()
    pq.push(0+calculateDistance(src,goal), (None, 0+calculateDistance(src,goal), 0, 0, src))
    # evaluation function, (previous-node-state, evaluation function, distance, energy-cost, node)
    #the tupple needs to carry distance for heuristic calculation
    weights[src] = set()
    weights[src].add((0, 0)) #(evaluation function,energy-cost)

    while not pq.isEmpty():
        curstate = pq.pop()  # curstate: current state
        cur = curstate[4]    
        if cur == goal:
            distance = curstate[2] #actually curstate[1]=curstate[2]
            cost = curstate[3]
            path = [goal]
            while curstate[0]:
                path.insert(0, curstate[0][4])
                curstate = curstate[0]
            return path, distance, cost

        for v in G[cur]:
            to_add = True
            if curstate[3]+Cost[cur+','+v] <= energyConstraint:
                d = curstate[2]+Dist[cur+','+v]  #distance
                f = d + calculateDistance(v,goal) #evaluaion function = distance + heuristic
                e = curstate[3]+Cost[cur+','+v]  #energy cost
                if v in weights:
                    for weight in weights[v]:
                        if f >= weight[0] and e >= weight[1]:
                        # if v has been visited in the current path, its current distance
                        # and energy cost must both be higher than the existing values.That's why
                        # this condition is enough
                            to_add = False
                            break
                    if to_add:
                        pq.push(f, (curstate, f, d, e, v))
                        weights[v].add((f, e))
                else:
                    pq.push(f, (curstate, f, d, e, v))
                    weights[v] = set()
                    weights[v].add((f, e))
    return None


def printResult(path, distance, cost):
    print('Shortest path:')
    print(' -> '.join(path))
    print('Shortest distance:')
    print(distance)
    print('Total energy cost:')
    print(cost)
    print()


if __name__ == '__main__':
    Coord = Dataloader('data/Coord.json')
    Cost = Dataloader('data/Cost.json')
    Dist = Dataloader('data/Dist.json')
    G = Dataloader('data/G.json')
    energyConstraint = 287932
    src = '1'
    goal = '50'

    print("Task1")
    path1, distance1, cost1 = UCS(src, goal)
    printResult(path1, distance1, cost1)

    path2, distance2, cost2 = constrainedUCS(src, goal)
    print("Task2")
    printResult(path2, distance2, cost2)

    path3, distance3, cost3 = Astar(src, goal)
    print("Task3")
    printResult(path3, distance3, cost3)
    