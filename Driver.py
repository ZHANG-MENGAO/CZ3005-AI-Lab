from pyswip import Prolog
import random
import copy
import sys

AGENT_PATH = 'Group0-Agent.pl'


class WumpusWorld:
    default_percept = ['off'] * 6
    random_position = [4, 4],  # default position
    random_direction = "north"  # default direction

    def __init__(self,
                 world_map=[['#', '#', '#', '#', '#', '#'],
                            ['#', ' ', ' ', 'W', ' ', '#'],
                            ['#', 'O', ' ', ' ', 'O', '#'],
                            ['#', ' ', 'A', ' ', ' ', '#'],
                            ['#', '$', ' ', ' ', ' ', '#'],
                            ['#', ' ', ' ', 'O', ' ', '#'],
                            ['#', '#', '#', '#', '#', '#'],
                            ],
                 origin=[3, 2],  # absolute position
                 init_direction="north",  # absolute direction
                 ):
        self.world_map = copy.deepcopy(world_map)
        self.origin = origin
        self.init_direction = init_direction
        self.generate_random()

    def rel_to_abs(self, rel):
        if self.init_direction == 'north':
            abs = [rel[0] + self.origin[0], rel[1] + self.origin[1]]
        elif self.init_direction == 'west':
            abs = [-rel[1] + self.origin[0], rel[0] + self.origin[1]]
        elif self.init_direction == 'east':
            abs = [rel[1] + self.origin[0], -rel[0] + self.origin[1]]
        else:
            abs = [-rel[0] + self.origin[0], -rel[1] + self.origin[1]]
        return abs

    def abs_to_rel(self, abs):  # never used, math helper for rel_to_abs
        if self.init_direction == 'north':
            rel = [abs[0] - self.origin[0], abs[1] - self.origin[1]]
        elif self.init_direction == 'west':
            rel = [abs[1] - self.origin[1], -(abs[0] - self.origin[0])]
        elif self.init_direction == 'east':
            rel = [-(abs[1] - self.origin[1]), abs[0] - self.origin[0]]
        else:
            rel = [-(abs[0] - self.origin[0]), -(abs[1] - self.origin[1])]
        return rel

    @staticmethod
    def print_map(map):
        for i in range(len(map)):
            for j in range(3):
                for k in range(len(map[0])):
                    for m in range(3):
                        print(map[i][k][3 * j + m], end="")
                    print(" ", end="")
                print()
            print()

    def print_absolute_map(self, percept):
        print("Absolute map:\n")
        agent_cur = next(prolog.query("current(X,Y,D)."))
        agent_cur_rel = [agent_cur['X'], agent_cur['Y']]
        agent_cur_abs = self.rel_to_abs(agent_cur_rel)
        dir_rel = agent_cur['D']
        dir_abs = self.calc_direction(
            dir_rel, self.direction_diff(self.init_direction))
        visited = list(prolog.query("visited(X,Y)."))
        map = []
        for j in range(len(self.world_map[0]) - 1, -1, -1):  # 6
            row = []
            for i in range(len(self.world_map)):  # 7
                cell = ['error'] * 9
                cur_abs = [i, j]
                # Wall
                if self.world_map[i][j] == '#':
                    cell = ['#']*9
                    row.append(cell)
                    continue
                # Symbol1 -- start:init_percept; portal:next_percept
                if cur_abs == agent_cur_abs and percept[0] == 'on':
                    cell[0] = '%'
                else:
                    cell[0] = '.'
                # Symbol2
                if self.wumpus_around(cur_abs):
                    cell[1] = '='
                else:
                    cell[1] = '.'
                # Symbol3
                if self.portal_around(cur_abs):
                    cell[2] = 'T'
                else:
                    cell[2] = '.'
                # Symbol4
                if cur_abs == agent_cur_abs or self.in_portal(cur_abs) or self.in_wumpus(cur_abs) or self.has_coin(cur_abs):
                    cell[3] = '-'
                else:
                    cell[3] = ' '
                # Symbol5
                if self.in_portal(cur_abs):
                    cell[4] = 'O'
                elif self.in_wumpus(cur_abs):
                    cell[4] = 'W'
                elif cur_abs == agent_cur_abs:
                    if dir_abs == "north":
                        cell[4] = '∧'
                    elif dir_abs == "west":
                        cell[4] = '<'
                    elif dir_abs == "east":
                        cell[4] = '>'
                    else:
                        cell[4] = '∨'
                elif cur_abs in self.safe_positions():
                    if cur_abs not in [self.rel_to_abs([dic['X'], dic['Y']]) for dic in visited]:
                        cell[4] = 's'
                    else:
                        cell[4] = 'S'
                else:
                    cell[4] = '?'
                # Symbol6
                cell[5] = cell[3]
                # Symbol7
                if self.has_coin(cur_abs):
                    cell[6] = '*'
                else:
                    cell[6] = '.'
                # Symbol8
                if cur_abs == agent_cur_abs and percept[4] == 'on':
                    cell[7] = 'B'
                else:
                    cell[7] = '.'
                # Symbol9
                if cur_abs == agent_cur_abs and percept[5] == 'on':
                    cell[8] = '@'
                else:
                    cell[8] = '.'
                row.append(cell)
            map.append(row)
        WumpusWorld.print_map(map)

    def print_relative_map(self, percept):
        if percept == []:
            print("Game over! No relative map")
            return
        agent_cur = next(prolog.query("current(X,Y,D)."))
        agent_cur_rel = [agent_cur['X'], agent_cur['Y']]
        dir_rel = agent_cur['D']

        visited = list(prolog.query("visited(X,Y)."))
        row_max = max(abs(dic['X']) for dic in visited) + 1
        col_max = max(abs(dic['Y']) for dic in visited) + 1

        map = []
        for n in range(col_max, -col_max - 1, -1):
            row = []
            for m in range(-row_max, row_max + 1):
                cell = ['error'] * 9
                cur_rel = [m, n]

                # Wall
                if next(prolog.query(f"wall({m},{n})."), None) == {}:
                    cell = ['#']*9
                    row.append(cell)
                    continue
                # Symbol1
                if cur_rel == agent_cur_rel and percept[0] == 'on':
                    cell[0] = '%'
                else:
                    cell[0] = '.'
                # Symbol2
                if next(prolog.query(f"stench({m},{n})."), None) == {}:
                    cell[1] = '='
                else:
                    cell[1] = '.'
                # Symbol3
                if next(prolog.query(f"tingle({m},{n})."), None) == {}:
                    cell[2] = 'T'
                else:
                    cell[2] = '.'
                # Symbol4
                if cur_rel == agent_cur_rel or next(prolog.query(f"confundus({m},{n})."), None) == {} or next(prolog.query(f"wumpus({m},{n})."), None) == {} or next(prolog.query(f"glitter({m},{n})."), None) == {}:
                    cell[3] = '-'
                else:
                    cell[3] = ' '
                # Symbol5
                if next(prolog.query(f"confundus({m},{n})."), None) == {} and next(prolog.query(f"wumpus({m},{n})."), None) == {}:
                    cell[4] = 'U'
                elif next(prolog.query(f"confundus({m},{n})."), None) == {}:
                    cell[4] = 'O'
                elif next(prolog.query(f"wumpus({m},{n})."), None) == {}:
                    cell[4] = 'W'
                elif cur_rel == agent_cur_rel:
                    if dir_rel == "rnorth":
                        cell[4] = '∧'
                    elif dir_rel == "rwest":
                        cell[4] = '<'
                    elif dir_rel == "reast":
                        cell[4] = '>'
                    else:
                        cell[4] = '∨'
                elif next(prolog.query(f"safe({m},{n})."), None) == {}:
                    if cur_rel not in [[dic['X'], dic['Y']] for dic in visited]:
                        cell[4] = 's'
                    else:
                        cell[4] = 'S'
                else:
                    cell[4] = '?'
                # Symbol6
                cell[5] = cell[3]
                # Symbol7
                if next(prolog.query(f"glitter({m},{n})."), None) == {}:
                    cell[6] = '*'
                else:
                    cell[6] = '.'
                # Symbol8
                if cur_rel == agent_cur_rel and percept[4] == 'on':
                    cell[7] = 'B'
                else:
                    cell[7] = '.'
                # Symbol9
                if cur_rel == agent_cur_rel and percept[5] == 'on':
                    cell[8] = '@'
                else:
                    cell[8] = '.'
                row.append(cell)
            map.append(row)
        WumpusWorld.print_map(map)

    # find all safe posiitons in the world
    def safe_positions(self):
        safe_positions = []
        for i in range(1, len(self.world_map)-1):
            for j in range(1, len(self.world_map[0])-1):
                if not self.is_wall([i, j]) and not self.in_portal([i, j]) and not self.in_wumpus([i, j]):
                    safe_positions.append([i, j])
        # print(safe_positions)
        return safe_positions

    # generate random safe positions
    def generate_random(self):
        self.random_position = random.choice(self.safe_positions())
        self.random_direction = random.choice(
            ['north', 'south', 'east', 'west'])

    # methods to manipulate percepts
    def confounded(self, list):  # set indicator when at the start of the game and after the Agent stepped into a cell with a Confundus Portal
        temp = list[:]
        temp[0] = 'on'
        return temp

    def stench(self, list):  # set indicatot when the Wumpus is around
        temp = list[:]
        temp[1] = 'on'
        return temp

    def tingle(self, list):  # set indicatot when a Confundus Portal is around
        temp = list[:]
        temp[2] = 'on'
        return temp

    def glitter(self, list):  # set indicatot when at a cell with a coin in
        temp = list[:]
        temp[3] = 'on'
        return temp

    def bump(self, list):  # set indicatot when walk into the wall
        temp = list[:]
        temp[4] = 'on'
        return temp

    def scream(self, list):  # set indicatot when successfully kills the Wumpus
        temp = list[:]
        temp[5] = 'on'
        return temp

    def is_wall(self, position):
        return self.world_map[position[0]][position[1]] == '#'

    def move_forward(self, cur_position, cur_direction):
        if cur_direction == "east":
            cur_position[0] += 1
        elif cur_direction == "west":
            cur_position[0] -= 1
        elif cur_direction == "north":
            cur_position[1] += 1
        else:
            cur_position[1] -= 1
        return cur_position, cur_direction

    def move_backward(self, cur_position, cur_direction):
        if cur_direction == "east":
            cur_position[0] -= 1
        elif cur_direction == "west":
            cur_position[0] += 1
        elif cur_direction == "north":
            cur_position[1] -= 1
        else:
            cur_position[1] += 1
        return cur_position, cur_direction

    def turn_left(self, cur_position, cur_direction):
        if cur_direction == "east":
            next_direction = "north"
        elif cur_direction == "north":
            next_direction = "west"
        elif cur_direction == "west":
            next_direction = "south"
        else:
            next_direction = "east"
        return cur_position, next_direction

    def turn_right(self, cur_position, cur_direction):
        if cur_direction == "east":
            next_direction = "south"
        elif cur_direction == "north":
            next_direction = "east"
        elif cur_direction == "west":
            next_direction = "north"
        else:
            next_direction = "west"
        return cur_position, next_direction

    # calculate the next position after taking the action at the current position in the current direction
    def move(self, action, cur_position, cur_direction):
        if action == "moveforward":
            return self.move_forward(cur_position, cur_direction)
        elif action == "turnleft":
            return self.turn_left(cur_position, cur_direction)
        elif action == "turnright":
            return self.turn_right(cur_position, cur_direction)
        else:
            return cur_position, cur_direction

    def wumpus_around(self, cur_position):  # check if there is a wumpus around
        if cur_position[0] < 0 or cur_position[1] < 0 or cur_position[0] >= len(self.world_map) or cur_position[1] >= len(self.world_map[0]):
            return False
        else:
            if cur_position[0] == 0:
                return self.world_map[cur_position[0]+1][cur_position[1]] == 'W'
            if cur_position[1] == 0:
                return self.world_map[cur_position[0]][cur_position[1]+1] == 'W'
            if cur_position[0] == len(self.world_map)-1:
                return self.world_map[cur_position[0]-1][cur_position[1]] == 'W'
            if cur_position[1] == len(self.world_map[0])-1:
                return self.world_map[cur_position[0]][cur_position[1]-1] == 'W'
            return self.world_map[cur_position[0]+1][cur_position[1]] == 'W' or self.world_map[cur_position[0]-1][cur_position[1]] == 'W' or self.world_map[cur_position[0]][cur_position[1]+1] == 'W' or self.world_map[cur_position[0]][cur_position[1]-1] == 'W'

    def portal_around(self, cur_position):  # check if there is a portal around
        if cur_position[0] < 0 or cur_position[1] < 0 or cur_position[0] >= len(self.world_map) or cur_position[1] >= len(self.world_map[0]):
            return False
        else:
            if cur_position[0] == 0:
                return self.world_map[cur_position[0]+1][cur_position[1]] == 'O'
            if cur_position[1] == 0:
                return self.world_map[cur_position[0]][cur_position[1]+1] == 'O'
            if cur_position[0] == len(self.world_map)-1:
                return self.world_map[cur_position[0]-1][cur_position[1]] == 'O'
            if cur_position[1] == len(self.world_map[0])-1:
                return self.world_map[cur_position[0]][cur_position[1]-1] == 'O'
            return self.world_map[cur_position[0]+1][cur_position[1]] == 'O' or self.world_map[cur_position[0]-1][cur_position[1]] == 'O' or self.world_map[cur_position[0]][cur_position[1]+1] == 'O' or self.world_map[cur_position[0]][cur_position[1]-1] == 'O'

    def has_coin(self, cur_position):  # check if the current position has a coin
        return self.world_map[cur_position[0]][cur_position[1]] == '$'

    def in_portal(self, cur_position):  # check if in the Confundus Portal
        return self.world_map[cur_position[0]][cur_position[1]] == 'O'

    def in_wumpus(self, cur_position):  # check if encounter the Wumpus
        return self.world_map[cur_position[0]][cur_position[1]] == 'W'

    def in_both(self, cur_position):
        return self.in_portal(cur_position) and self.in_wumpus(cur_position)

    def pickup_coin(self, cur_position):  # pick up the coin
        self.world_map[cur_position[0]][cur_position[1]] = ' '

    # check whether can kill Wumpus at the current position and in the current direction
    def kill_wumpus(self, cur_position, cur_direction):
        if cur_direction == "north":
            for i in range(cur_position[1], len(self.world_map[0])):
                if self.world_map[cur_position[0]][i] == 'W':
                    self.world_map[cur_position[0]][i] = ' '
                    return True
            return False
        elif cur_direction == "south":
            for i in range(cur_position[1]+1):
                if self.world_map[cur_position[0]][i] == 'W':
                    self.world_map[cur_position[0]][i] = ' '
                    return True
            return False
        elif cur_direction == "west":
            for i in range(cur_position[0]+1):
                if self.world_map[i][cur_position[1]] == 'W':
                    self.world_map[i][cur_position[1]] = ' '
                    return True
            return False
        else:
            for i in range(cur_position[0], len(self.world_map)):
                if self.world_map[i][cur_position[1]] == 'W':
                    self.world_map[i][cur_position[1]] = ' '
                    return True
            return False

    # take in an action and return one list of percepts accordingly
    def generate_percepts(self, action, cur_position, cur_direction):
        percept = self.default_percept[:]
        cur_position, cur_direction = self.move(
            action, cur_position, cur_direction)

        # step into Confundus Portal -> reborn at a random position with a random direction
        if self.in_portal(cur_position):
            print("Fall into Confundus Portal! Game Reset!\n")
            percept = self.confounded(percept)
            cur_position, cur_direction = self.random_position, self.random_direction
            self.origin = self.random_position
            self.init_direction = self.random_direction
            self.generate_random()
            init_percept = self.cur_percept(
                self.confounded(self.default_percept), cur_position)
            next(prolog.query("reposition(" + str(init_percept) + ")."))

        # walk into Wumpus -> end-game; start again from origin
        if self.in_wumpus(cur_position):
            print("Encounter Wumpus! Game Ends!\n")
            return [], cur_position, cur_direction

        if self.is_wall(cur_position):
            cur_position, cur_direction = self.move_backward(
                cur_position, cur_direction)
            percept = self.bump(percept)

        if action == 'shoot' and self.kill_wumpus(cur_position, cur_direction):
            percept = self.scream(percept)

        if self.has_coin(cur_position) and action == 'pickup':
            self.pickup_coin(cur_position)

        percept = self.cur_percept(percept, cur_position)

        # print('cur_direction: ', cur_direction)
        # print('cur_position: ', cur_position)
        # print()

        return percept, cur_position, cur_direction

    # generate the percepts for stench, tingle, and coins at the current position and in the current direction
    def cur_percept(self, percept, cur_position):

        if self.wumpus_around(cur_position):
            percept = self.stench(percept)

        if self.portal_around(cur_position):
            percept = self.tingle(percept)

        if self.has_coin(cur_position):
            percept = self.glitter(percept)

        return percept

    # calculate the initial difference between the absolute north and the absolute direction of the Agent
    def direction_diff(self, agent_absolute_direction):
        if agent_absolute_direction == "north":
            return 0
        elif agent_absolute_direction == "west":
            return 270
        elif agent_absolute_direction == "south":
            return 180
        else:
            return 90

    # convert the relative direction from the Agent into the absolute direction
    def calc_direction(self, relative_direction, direction_diff):
        if relative_direction == "rnorth":
            if direction_diff == 0:
                return "north"
            elif direction_diff == 90:
                return "east"
            elif direction_diff == 180:
                return "south"
            else:
                return "west"
        elif relative_direction == "reast":
            if direction_diff == 0:
                return "east"
            elif direction_diff == 90:
                return "south"
            elif direction_diff == 180:
                return "west"
            else:
                return "north"
        elif relative_direction == "rsouth":
            if direction_diff == 0:
                return "south"
            elif direction_diff == 90:
                return "west"
            elif direction_diff == 180:
                return "north"
            else:
                return "east"
        else:
            if direction_diff == 0:
                return "west"
            elif direction_diff == 90:
                return "north"
            elif direction_diff == 180:
                return "east"
            else:
                return "south"


def print_input_percept(percept):
    if percept == []:
        print("Game over! No percept")
        return
    percept_name = ["Confounded", "Stench",
                    "Tingle", "Glitter", "Bump", "Scream"]
    result = []
    for j in range(len(percept_name)):
        if percept[j] == "on":
            result.append(percept_name[j])
        else:
            result.append(percept_name[j][0])
    print_result = "-".join(result)
    print(print_result)
    print()

# Test1: test for Correctness 1,2,3
# Correctness1: Correctness of Agent’s localisation and mapping abilities
# Correctness2: Correctness of Agent’s sensory inference
# Correctness3: Correctness of Agent’s memory management in response to stepping though a Confundus Portal


def Test_1():  # Agent will fall into a Confundus portal

    prolog.consult(AGENT_PATH)

    print()
    print("------- Test 1 -------")
    print('''Test for:
        Correctness1: Correctness of Agent’s localisation and mapping abilities
        Correctness2: Correctness of Agent’s sensory inference
        Correctness3: Correctness of Agent’s memory management in response to stepping though a Confundus Portal
        ''')

    # initial information (absolute)
    # use the default Wumpus world
    # to use customized Wumpus world
    # WumpusWorld(world_map,origin,init_direction,random_position,random_direction)
    world_1 = WumpusWorld(origin=[5, 1], init_direction='south')
    cur_position, cur_direction = world_1.origin[:], world_1.init_direction

    init_percept_1 = world_1.cur_percept(
        world_1.confounded(world_1.default_percept), cur_position)

    next(prolog.query("reposition(" + str(init_percept_1) + ")."))

    # print absolute map
    world_1.print_absolute_map(init_percept_1)

    action_1 = ["moveforward", "turnright", "turnleft", "turnright", "moveforward", "pickup", "moveforward", "turnright", "moveforward",
                "moveforward", "turnleft", "moveforward", "shoot", "turnright", "moveforward", "moveforward", "turnleft", "moveforward"]
    print("Action sequence:")
    print(",".join(action_1))
    print()

    # print initial relative map
    print("Initial Relative map (Test 1.0):")
    world_1.print_relative_map(init_percept_1)

    # lead the Agent into a Confundus Portal
    for i in range(len(action_1)):

        # percepts = [Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,Scream_i]
        percept_1, cur_position, cur_direction = world_1.generate_percepts(
            action_1[i], cur_position, cur_direction)

        next(prolog.query(
            "move(" + action_1[i] + "," + str(percept_1) + ")."), None)

        # check hasarrow status
        if action_1[i] == "shoot":
            if next(prolog.query("hasarrow()."), None) == {}:
                raise Exception(
                    'Wrong! The Agent still has an arrow after shooting!')

        if(percept_1 != []):
            # print current action
            print(action_1[i])

            # print input percept
            print_input_percept(percept_1)

            # print relative map
            print(f"Relative map (Test 1.{i + 1}):")
            world_1.print_relative_map(percept_1)

# Test2: test for Correctness 5
# Correctness5: Correctness of the Agent’s end-game reset in a manner similar to that of Confundus Portal reset


def Test_2():  # Agent will walk into the Wumpus at the end

    prolog.consult(AGENT_PATH)

    print()
    print("------- Test 2 -------")
    print('''Test for:
        Correctness5: Correctness of the Agent’s end-game reset in a manner similar to that of Confundus Portal reset
        ''')

    # initial information (absolute)
    # use the default Wumpus world
    # to use customized Wumpus world
    # WumpusWorld(world_map,origin,init_direction,random_position,random_direction)
    world_2 = WumpusWorld()
    cur_position, cur_direction = world_2.origin[:], world_2.init_direction

    init_percept_2 = world_2.cur_percept(
        world_2.confounded(world_2.default_percept), cur_position)

    next(prolog.query("reposition(" + str(init_percept_2) + ")."))

    # print absolute map
    world_2.print_absolute_map(init_percept_2)

    # len(action_2) = 6
    action_2_1 = ["turnleft", "moveforward", "moveforward",
                  "moveforward", "turnright", "moveforward"]
    print("Action sequence 1:")
    print(",".join(action_2_1))
    print()

    # print initial relative map
    print("Initial Relative map (Test 2_1.0):")
    world_2.print_relative_map(init_percept_2)

    for i in range(len(action_2_1)):
        # percepts = [Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,Scream_i]
        percept_2_1, cur_position, cur_direction = world_2.generate_percepts(
            action_2_1[i], cur_position, cur_direction)

        next(prolog.query(
            "move(" + action_2_1[i] + "," + str(percept_2_1) + ")."), None)

        if(percept_2_1 != []):
            # print current action
            print(action_2_1[i])

            # print input percept
            print_input_percept(percept_2_1)

            # print relative map
            print(f"Relative map (Test 2_1.{i + 1}):")
            world_2.print_relative_map(percept_2_1)

    # game restart after walk into the wumpus
    print("Game restart!")
    next(prolog.query("reborn()."))
    next(prolog.query("reposition(" + str(init_percept_2) + ")."))

    cur_position, cur_direction = world_2.origin[:], world_2.init_direction

    action_2_2 = ["turnright", "moveforward", "moveforward",
                  "moveforward"]
    print("Action sequence 2:")
    print(",".join(action_2_2))
    print()

    print("Initial Relative map (Test 2_2.0):")
    world_2.print_relative_map(init_percept_2)

    for i in range(len(action_2_2)):
        # percepts = [Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,Scream_i]
        percept_2_2, cur_position, cur_direction = world_2.generate_percepts(
            action_2_2[i], cur_position, cur_direction)

        next(prolog.query(
            "move(" + action_2_2[i] + "," + str(percept_2_2) + ")."), None)

        if(percept_2_2 != []):
            # print current action
            print(action_2_2[i])

            # print input percept
            print_input_percept(percept_2_2)

            # print relative map
            print(f"Relative map (Test 2_2.{i + 1}):")
            world_2.print_relative_map(percept_2_2)


# Test3: test for Correctness 4
# Correctness4: Correctness of Agent’s exploration capabilities


def Test_3():

    prolog.consult(AGENT_PATH)

    print()
    print("------- Test 3 -------")
    print('''Test for:
        Correctness4: Correctness of Agent’s exploration capabilities
        ''')

    # initial information (absolute)
    # use the default Wumpus world
    # to use customized Wumpus world
    # WumpusWorld(world_map,origin,init_direction,random_position,random_direction)
    world_3 = WumpusWorld(init_direction='west')

    init_percept_3 = world_3.cur_percept(
        world_3.confounded(world_3.default_percept), world_3.origin[:])

    next(prolog.query("reposition(" + str(init_percept_3) + ")."), None)

    # print absolute map
    world_3.print_absolute_map(init_percept_3)

    # print initial relative map
    print("Initial Relative map (Test 3.0):")
    world_3.print_relative_map(init_percept_3)

    # in case the Agent is stucked:
    # max explore loop is 60
    count = 0

    while count < 42:
        explore = next(prolog.query("explore(L)."))["L"]

        init_direction_diff = world_3.direction_diff(world_3.init_direction)

        cur_position, cur_direction = [list(prolog.query("current(X,Y,D)."))[0]["X"], list(prolog.query(
            "current(X,Y,D)."))[0]["Y"]], world_3.calc_direction(list(prolog.query("current(X,Y,D)."))[0]["D"], init_direction_diff)
        cur_position = world_3.rel_to_abs(cur_position)

        if not explore:
            if cur_position[0] == world_3.origin[0] and cur_position[1] == world_3.origin[1]:
                print("Agent finished the Game!")
            break

        print(f"Action sequence {count + 1}:")
        print(",".join(explore))
        print()

        for i in range(len(explore)):

            percept_3, cur_position, cur_direction = world_3.generate_percepts(
                explore[i], cur_position, cur_direction)

            next(prolog.query(
                "move(" + explore[i] + "," + str(percept_3) + ")."))

            if(percept_3 != []):
                # print current action
                print(explore[i])

                # print input percept
                print_input_percept(percept_3)

                # print relative map
                print(f"Relative map (Test 3_{count + 1}.{i + 1}):")
                world_3.print_relative_map(percept_3)

        # update the counter
        count += 1

    if count == 60:
        print("Agent is stucked! Test Failed!")


if __name__ == "__main__":
    sys.stdout = open('Group0-testPrintout-Self-Self.txt', 'w')
    print("There are 3 test cases in total.")
    prolog = Prolog()
    Test_1()
    Test_2()
    Test_3()
    sys.stdout.close()
