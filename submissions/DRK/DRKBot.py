from aiarena21.client.classes import Player, Map

import random

turnsFromCycle = 0
allNodes = None

def play_powerup(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    return ''


def play_turn(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    # Increment turns from cycle.
    global turnsFromCycle
    turnsFromCycle += 1
    if (turnsFromCycle > 20):
        turnsFromCycle = 1

    # Create a node for pathfind algorithm for each tile in map.

    allNodes = generate_nodes(game_map)
    playerX = me.location[0]
    playerY = me.location[1]
    playerNode = allNodes[playerX][playerY]

    enemyX = opponent.location[0]
    enemyY = opponent.location[1]
    enemyNode = allNodes[enemyX][enemyY]

    maxEfficiency = 0
    maxHeatmapSquare = None
    maxItemNode = None

    ### BASE.
    # Merge heatmap and item values into one.
    for i in range(len(heatmap)):
        for j in range(len(heatmap[0])):
            # Player distance.
            dist1 = get_manhattan_distance(playerNode,allNodes[i][j])
            # Opponent distance.
            dist2 = get_manhattan_distance(enemyNode,allNodes[i][j])
            heatmapEfficiency = 0
            itemEfficiency = 0
            if (dist1 < (20 - turnsFromCycle)):
                heatmapEfficiency = get_efficiency((20-turnsFromCycle),heatmap[i][j])

            itemEfficiency = get_efficiency_with_opponent(dist1,dist2,items[i][j])
            currentEfficiency = itemEfficiency + heatmapEfficiency
            
            if (currentEfficiency > maxEfficiency and dist1 < dist2):
                maxEfficiency = currentEfficiency
                maxItemNode = allNodes[i][j]


    # Move to most efficient heatmap square.
    #result = None
    result = pathfind_to_target(playerNode,maxItemNode,game_map.rows,game_map.cols,allNodes)

    if (result != None):
        nodeToMove = result[0]
        new_row = nodeToMove.X
        new_col = nodeToMove.Y
    else:
        new_row = playerX
        new_col = playerY
    
    return f'{new_row},{new_col}'


def play_auction(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):
    rows = game_map.rows
    cols = game_map.cols

    minimum_score = float('inf')

    for i in range(rows):
        for j in range(cols):
            s = get_score(i, j, game_map, items)
            if (s < minimum_score):
                minimum_score = s
            new_row = i
            new_col = j

    #print("min score", minimum_score)

    return round(minimum_score/15)


def play_transport(game_map: Map, me: Player, opponent: Player, items: list, new_items: list, heatmap, remaining_turns):

    rows = game_map.rows
    cols = game_map.cols

    #test
    new_row = 1
    new_col = cols-2

    if (not game_map.is_free(new_row,new_col)):
        new_row = 0
        new_col = cols-1
    elif (not game_map.is_free(new_row,new_col)):
        new_row = 0
        new_col = 0
    elif (not game_map.is_free(new_row,new_col)):
        new_row = rows-1
        new_col = cols-1
    elif (not game_map.is_free(new_row,new_col)):
        new_row = rows-1
        new_col = 0
            
    return f'{new_row},{new_col}'


# define manhattan distance
def get_manhattan_distance(node1,node2):
    return abs(node2.X-node1.X) + abs(node2.Y-node1.Y)

# Find best item.
def get_best_item(items,allNodes,playerNode,enemyNode):
    maxItemNode = None
    maxEfficiency = 0
    
    # Most efficient current item.
    for i in range(len(items)):
        for j in range(len(items[0])):
            if (items[i][j] > 0):
                # Player distance.
                dist1 = get_manhattan_distance(playerNode,allNodes[i][j])
                # Opponent distance.
                dist2 = get_manhattan_distance(enemyNode,allNodes[i][j])
                currentEfficiency = get_efficiency_with_opponent(dist1,dist2,items[i][j])
                #currentEfficiency = get_efficiency(dist1,items[i][j])
                if (currentEfficiency > maxEfficiency and dist1 < dist2):
                    maxEfficiency = currentEfficiency
                    maxItemNode = allNodes[i][j]

    return maxItemNode


# From player to food, obtain the route that hits the highest score along the way.
def pathfind_to_target(startNode,targetNode,rows,cols,allNodes):
    # calculate optimal score path from player to food
    if (targetNode == None):
        return None
    
    # closed list
    openNodes = []
    closedNodes = []

    # Starting node
    openNodes.append(startNode)

    breaker = 0
    # while we are not at our goal
    while (len(openNodes) > 0):
        breaker += 1
        if (breaker > 1000):
            return None
        
        currentNode = openNodes[0]
        del openNodes[0]

        # Make sure we don't expand nodes we've already checked
        closedNodes.append(currentNode);

        # Check if we found our food:
        #print("currentNodePos = ", (currentNode.X,currentNode.Y))
        #print("targetNodePos = ", (targetNode.X,targetNode.Y))
        if (currentNode == targetNode):     # targetNode is (x1,x2)
            # We found our goal
            return get_path(startNode,targetNode)

        # Check neighbours
        neighbours = []
        currentX = currentNode.X
        currentY = currentNode.Y
        xCoords = [-1,0,1,0]
        yCoords = [0,1,0,-1]
        for i in range(4):
            if (currentX + xCoords[i] < rows and currentY + yCoords[i] < cols
            and currentX + xCoords[i] >= 0 and currentY + yCoords[i] >= 0):
                neighbours.append(allNodes[currentX + xCoords[i]][currentY + yCoords[i]])

        # For each neighbour:
        for nextNode in neighbours:
            # Check if closed
            if (nextNode in closedNodes or (not nextNode.free)):
                continue
            else:
                # Calculate the distance.
                possible_g = currentNode.G + get_manhattan_distance(currentNode, nextNode)
                possible_g_isBetter = False
                
                if (nextNode not in openNodes):
                    openNodes.append(nextNode)
                    possible_g_isBetter = True

                elif (possible_g < nextNode.G):
                    possible_g_isBetter = True

                if (possible_g_isBetter):
                    nextNode.Parent = currentNode
                    nextNode.G = possible_g


    #print("Couldn't find path!")
    return None

# Get path to target.
def get_path(startNode,targetNode):
    pathLength = 0
    currentNode = targetNode

    
    path = []
    while (currentNode.Parent != None):
        path.append(currentNode)
        pathLength += 1
        currentNode = currentNode.Parent
        

    testPath = []
    for node in path:
        testPath.append((node.X,node.Y))

    # Empty path means we give our current location
    if (len(testPath) == 0):
        return (startNode,0)

        
    return (path[len(path)-1],pathLength)
                    

# Generate nodes for every tile in the map.
def generate_nodes(game_map:Map):
    allNodes = []
    
    for i in range(game_map.rows):
        allNodes.append([])
        for j in range(game_map.cols):
            newNode = Node(i,j,0,game_map.is_free(i,j))
            allNodes[i].append(newNode)

    return allNodes

# Get efficiency of item
def get_efficiency(distance,item):
    if (distance == 0):
        return item
    return item/distance

# Get efficiency of item versus opponent
def get_efficiency_with_opponent(distance1,distance2,item):
    val1 = 0
    val2 = 0
    if (distance1 == 0):
        distance1 = 1
    else:
        val1 = item/distance1
        
    if (distance2 == 0):
        distance2 = 1
    else:
        val2 = item/distance2

    return val1 + (val2/distance1)

class Node:
    def __init__(self, x=0, y=0, G=0, free=True):
        #
        self.X = x
        self.Y = y
        self.G = G
        self.free = free
        self.efficiency = 0
        self.Parent = None



def get_score(i_0, j_0, game_map:Map, items):
    rows = game_map.rows
    cols = game_map.cols
    score = 0

    for i in range(rows):
        for j in range(cols):
            dist = abs(i_0 - i) + abs(j_0 - j)
            score += items[i][j] / (dist+1)

    return score









