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

    def swap(self,i,j):
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
        if(min!=i):
            self.swap(min, i)
            self.sinkDown(min)

    def push(self, w, v):
        self.Q.append((w, v))
        self.positions[v] = len(self.Q)-1
        self.bubbleUp(len(self.Q)-1)

    def decreaseKey(self, decreased_w, v):
        position = self.positions[v]
        self.Q[position] = (decreased_w,v)
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