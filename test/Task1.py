import json
import heapq


def Dataloader(filename):
    with open(filename) as f:
        return json.load(f)


INF = float("inf")

if __name__ == '__main__':
    # Coord = Dataloader('data/Coord.json')
    Cost = Dataloader('data/Cost.json')
    Dist = Dataloader('data/Dist.json')
    G = Dataloader('data/G.json')

    length = len(G) + 1
    source = 1
    goal = 50

    # For test
    # length = 10
    # source = 9
    # goal = 1

    priorityQueue = []

    # Shortest distance from source to the node
    d = [INF] * length
    # Parent of the node
    pi = [None] * length
    # visited
    visited = [False] * length

    # Initialize the source node
    d[source] = 0
    heapq.heappush(priorityQueue, (d[source], source))

    while priorityQueue:
        cur = heapq.heappop(priorityQueue)[1]
        if cur == goal:
            break
        visited[cur] = True
        for i in G[str(cur)]:
            if not visited[int(i)] and d[int(i)] > d[cur] + Dist[str(cur)+','+i]:
                if (d[int(i)], int(i)) in priorityQueue:
                    # Remove the node from PriorityQueue for updating
                    priorityQueue.remove((d[int(i)], int(i)))
                    heapq.heapify(priorityQueue)
                d[int(i)] = d[cur] + Dist[str(cur)+','+i]
                pi[int(i)] = cur
                # Update the distance of the node and add it back to PriorityQueue
                heapq.heappush(priorityQueue, (d[int(i)], int(i)))
    result = []
    distance = 0
    energyCost = 0
    result.append(goal)
    while pi[goal]:
        distance += Dist[str(goal)+','+str(pi[goal])]
        energyCost += Cost[str(goal)+','+str(pi[goal])]
        result.append(pi[goal])
        goal = pi[goal]

    print('Shortest path:')
    print(''.join(str(result[i]) +
          '->' for i in range(len(result)-1, -1, -1))[:-2])
    print('Shortest distance:')
    print(distance)
    print('Total energy cost:')
    print(energyCost)
