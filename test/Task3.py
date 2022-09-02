import json
import math
from test.Task2 import PriorityQ
import time


def Dataloader(filename):
    with open(filename) as f:
        return json.load(f)


def h1(target):
    coord = Dataloader('data/Coord.json')

    destination = coord.get(str(target))
    size = len(coord)
    h = {}
    for i in range(1, target):
        node = coord.get(str(i))
        distance = math.sqrt((node[0]-destination[0])
                             ** 2 + (node[1]-destination[1])**2)
        h[i] = distance
    h[target] = 0.00
    for i in range(target+1, size+1):
        node = coord.get(str(i))
        distance = math.sqrt((node[0]-destination[0])
                             ** 2 + (node[1]-destination[1])**2)
        h[i] = distance

    return h


def h2(src, goal):

    # load data and initialization
    Dist = Dataloader('data/Dist.json')
    G = Dataloader('data/G.json')
    cost = Dataloader('data/Cost.json')
    Coord = Dataloader('data/Coord.json')
    budget = 287932

    start = time.time()
    ###
    # first, UCS algorithm from target node to all nodes(within budget) on the energy cost
    # obtain the upper bound of distance.
    ###

    # initialization
    c = {}
    d_c = {}
    pi_c = {}
    visited_c = set()
    pq = PriorityQ()

    pi_c[goal] = None
    c[goal] = 0
    d_c[goal] = 0
    pq.push(c[goal], goal)
    dist_max = float("inf")

    while not pq.isEmpty():
        cur = pq.pop()
        visited_c.add(cur)
        if cur == src:
            dist_max = d_c[cur]

        for adj_node in G[cur]:  # for each node adjacent to the current node
            # expand only when the node is not visited,
            # the new cost is lower and is within the budget.
            new_cost = c[cur] + cost[cur+','+adj_node]
            new_dist = d_c[cur] + Dist[cur+','+adj_node]
            if adj_node not in visited_c and new_cost <= budget:
                if adj_node not in c:
                    c[adj_node] = new_cost
                    d_c[adj_node] = new_dist
                    pi_c[adj_node] = cur
                    pq.push(c[adj_node], adj_node)
                elif new_cost < c[adj_node]:
                    c[adj_node] = new_cost
                    d_c[adj_node] = new_dist
                    pi_c[adj_node] = cur
                    # Update the distance of the node and add it back to PriorityQueue
                    pq.decreaseKey(c[adj_node], adj_node)
    end = time.time()
    print('time spent by the first initialization search: '+str(end-start))

    start = time.time()
    ###
    # second UCS algorithm from target node to all nodes to find the minimum distance.
    ###

    # initialization
    d_d = {}
    pi_d = {}
    visited_d = set()  # this will be the final search space
    pq = PriorityQ()

    d_d[goal] = 0
    pi_d[goal] = None
    pq.push(d_d[goal], goal)

    while not pq.isEmpty():
        cur = pq.pop()
        visited_d.add(cur)

        for adj_node in G[cur]:
            # join the pq only when the node is not visited, but visited in the first search,
            # the new distance is lower than the previous distance and is lower than the upper bound
            new_dist = d_d[cur]+Dist[cur+','+adj_node]
            if adj_node not in visited_d and adj_node in visited_c and new_dist <= dist_max:
                if adj_node not in d_d:
                    d_d[adj_node] = new_dist
                    pi_d[adj_node] = cur
                    pq.push(d_d[adj_node], adj_node)
                elif new_dist < d_d[adj_node]:
                    d_d[adj_node] = new_dist
                    pi_d[adj_node] = cur
                    pq.decreaseKey(d_d[adj_node], adj_node)

    end = time.time()
    print('time spent by the second initialization search:'+str(end-start))

    start = time.time()
    ###
    # main A* search
    ###

    # initialization
    weights = {}  # weights store all the distance and energy states of each node
    pq = PriorityQ()
    dist = math.sqrt((Coord[src][0] - Coord[goal][0]) **
                     2 + (Coord[src][1] - Coord[goal][1])**2)
    pq.push(0+dist, (None, 0+dist, 0, 0, src))
    # evaluation function, (previous-node-state, evaluation function, distance, energy-cost, node)
    # the tuple needs to carry distance for heuristic calculation
    weights[src] = set()
    weights[src].add((0, 0))  # (evaluation function,energy-cost)

    while not pq.isEmpty():
        curstate = pq.pop()  # curstate: current state
        cur = curstate[4]
        if cur == goal:
            distance = curstate[2]  # actually curstate[1]=curstate[2]
            cost = curstate[3]
            path = [goal]
            while curstate[0]:
                path.insert(0, curstate[0][4])
                curstate = curstate[0]
            end = time.time()
            print('time spent by the main search:' + str(end - start))
            return path, distance, cost

        for adj_node in G[cur]:
            to_add = True
            new_dist = curstate[2] + Dist[cur+','+adj_node]  # distance
            new_cost = curstate[3]+cost[cur+','+adj_node]  # energy cost
            f = new_dist + math.sqrt((Coord[adj_node][0] - Coord[goal][0]) **
                     2 + (Coord[adj_node][1] - Coord[goal][1])**2)  # evaluation function = distance + heuristic
            if adj_node in visited_d and new_cost <= budget and new_cost+c[adj_node] <= budget and new_dist+d_d[adj_node] <= dist_max:
                if adj_node in weights:
                    for weight in weights[adj_node]:
                        if f > weight[0] and new_cost > weight[1]:
                            # if v has been visited in the current path, its current distance
                            # and energy cost must both be higher than the existing values.That's why
                            # this condition is enough
                            to_add = False
                            break
                    if to_add:
                        pq.push(f, (curstate, f, new_dist, new_cost, adj_node))
                        weights[adj_node].add((f, new_cost))
                else:
                    pq.push(f, (curstate, f, new_dist, new_cost, adj_node))
                    weights[adj_node] = set()
                    weights[adj_node].add((f, new_cost))
    return None

