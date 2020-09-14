from kaggle_environments.envs.halite.helpers import *
from random import choice

## IMPORTANT ----> The board has (0, 0) as the BOTTOM LEFT corner, and (size - 1, size - 1) as the TOP RIGHT CORNER

def distance(fromPos, toPos, size):
    xVal = abs(fromPos[0] - toPos[0])
    if(xVal > (size//2)):
        if(fromPos[0] > toPos[0]):
            xVal = toPos[0] + (size - fromPos[0])
        else:
            xVal = fromPos[0] + (size - toPos[0])
    yVal = abs(fromPos[1]- toPos[1])
    if(yVal > (size//2)):
        if(fromPos[1] > toPos[1]):
            xVal = toPos[1] + (size - fromPos[1])
        else:
            xVal = fromPos[1] + (size - toPos[1])
    calVal = xVal + yVal
    return calVal

direction = ['north', 'east', 'south', 'west']

def positiveCheck(ship, view_size, size): # Scan for the direction with the most halite
# Use a distance of four most of the time for this
    positiveScore = [0, 0, 0, 0] # Divided into four quadrants - top left, top right, bottom right then bottom left

    startCoord = [ship.position[0] - (distance//2), ship.position[1] - (distance//2)] # Get the starting top left corner
    if(startCoord[0] < 0): # Wrap if it overflows from the playing field
        startCoord[0] = (size-1) - startCoord[0]
    if(startCoord[1] < 0):
        startCoord[1] = (size-1) - startCoord[1]
    for y in (view_size*2): # Loop through all rows
        for x in (view_size*2): # Loop through all cells in the row
            newCoord = [startCoord[0] + x, startCoord[1] + y] # Get the current cell coordinates
            coordSectors = []
            if(newCoord[0] >= ship.position[0]): # There is bias towards the cells in several different sectors - fix later?
                if(newCoord[1] >= ship.position[1]): # If the cell is top right of the ship
                    coordSectors.append(1)
                if(newCoord[1] <= ship.position[1]): # If the cell is bottom right of the ship
                    coordSectors.append(2)
            if(newCoord[0] <= ship.position[0]):
                if(newCoord[1] >= ship.position[1]): # If the cell is top left of the ship
                    coordSectors.append(0)
                if(newCoord[1] <= ship.position[1]): # If the cell is bottom left of the ship
                    coordSectors.append(3)

            if(newCoord[0] > (size-1)): # Modify the new coordinate to fit map wrapping
                newCoord[0] -= size - 1
            if(newCoord[1] > (size-1)):
                newCoord[1] -= size - 1

            cellScore = board.cells[newCoord].halite // distance(newCoord, ship.position, size) # How much that specific cell scores relative to the ship

            for i in coordSectors:
                positiveScore[i] += cellScore
    positiveScore /= 10
    return positiveScore


def negativeCheck(ship, me): # Scan for dangers and threats
# Return an array with the danger and interest values of the surrounding squares, in the order: [center, north, east, south, west]
    negativeScore = [0, 0, 0, 0, 0]

    if(ship.cell.shipyard != None): # If the spot the ship is on is a shipyard
        negativeScore[0] += -300 # Good incentive to leave, but it is possible to stay - just check later
    if(ship.cell.position in nextPositions):
        negativeScore[0] += -2000

    # Check surroundings for threats
    for i in range(0, 4): # Loop through all four directions
        currentCell = getattr(ship.cell, direction[i])
        if(currentCell.position in nextPositions): # If one of our ships is already going there
            negativeScore[i+1] += -2000 # DON'T GO (more than anything)
        if(currentCell.ship != None): # If there is a ship one block away
            # check that the obstacle ship isn't mine AND if the current ship would be destroyed if it crashed into it
            if(ship.halite >= currentCell.ship.halite and currentCell.ship.player != me):
                negativeScore[i+1] +=  -400
                negativeScore[0] += -400
        if(currentCell.shipyard != None and currentCell.shipyard.player != me): # If there is a shipyard there that's not ours
            negativeScore[i+1] += -1250 # DON'T GO (unless there's really no choice - it will be a noble sacrifice)
        for x in range(0, 4): # Loop through all the blocks surrounding the block one away...
            checkCell = getattr(currentCell, position[x])
            if(checkCell.position != ship.position): # ...except for the one the ship is currently on (we already checked it)
                if(checkCell.ship != None): # If there is a ship two blocks away
                    if(ship.halite >= checkCell.ship.halite and currentCell.ship.player != me):
                        negativeScore[i] += -200 # I'm coming up with these values as I go - refine later

    return negativeScore


nextPositions = []
shipRoles = {}

def agent(obs, config):

    board = Board(obs,config)
    me = board.current_player
    size = config.size

# Not sure whether to include below code - utilise it later?
#    # If there are no ships, use only shipyard to spawn a ship
#    if len(me.ships) == 0 and len(me.shipyards) == 1:
#        me.shipyards[0].next_action = ShipyardAction.SPAWN
#
#    # If there are no shipyards, convert first ship into shipyard, but only if they can make a ship afterwards
#    if len(me.shipyards) == 0 and len(me.ships) > 0 and player.halite >= 1000:
#        me.ships[0].next_action = ShipAction.CONVERT

    # Set actions for each shipyard
    for s in me.shipyards:
        if(s.next_action == None): # If the shipyard isn't doing something already
            # Move the ship with the most halite onto it
            highestShip = [,0]
            for i in range(4):
                currentCell = getattr(s.cell, direction[i])
                if(currentCell.ship != None):
                    if(currentCell.ship.halite > highestShip[1]):
                        highestShip[0] = currentCell.ship
                        highestShip[1] = currentCell.ship.halite
                        if(i >= 2): # Find which direction it would have to go to get on the shipyard
                            highestShip[2] = direction[i-2]
                        else:
                            highestShip[2] = direction[i+2]
            highestShip[0].next_action = getattr(ShipAction, highestShip[2])


    # Set actions for each ship
    for ship in me.ships:
        negativeScore = negativeCheck(ship, me) # Divided into the five possible moves - top, right, left, bottom, and centre

        if(shipRoles[ship.id] == 'Miner'):
            positiveScore = positiveCheck(ship, 3, size) # Divided into the four corners

            # If the current spot is worth mining and there is no risk around
            if(ship.next_action == None):
                if(ship.position.halite >= 200 and negativeScore[0] == 0 and ship.position not in nextPositions):
                    ship.next_action = None # Mine the Halite
                    nextPositions.append(ship.position)
                elif(ship.halite > 500): # Change this later so that it takes the current turn into account <---------------------------------- (!)
                    bestShipyard = [me.shipyards[0], distance(me.shipyards[0].position, ship.position, size]
                    for s in me.shipyards:
                        dis = distance(s.position, ship.position, size)
                        if(bestShipyard[1] < dis):
                            bestShipyard[0] = s
                            bestShipyard[1] = dis
                    possibleDir = [] # The possible directions in which it can move to reach the shipyard
                    # Staying put is always an option - represented by the 4
                    if(bestShipyard[0].position[0] > ship.position[0]): # Find best path to shipyard
                        possibleDir.append(0) # Go north
                    elif(bestShipyard[0].position[0] < ship.position[0]):
                        possibleDir.append(2) # Go south
                    if(bestShipyard[0].position[1] > ship.position[1]):
                        possibleDir.append(1) # Go east
                    elif(bestShipyard[0].position[1] < ship.position[1]):
                        possibleDir.append(3) # Go west
                    bestScore = [4, negativeScore[0]] # Start with no movement as an option
                    for d in possibleDir:
                        if(negativeScore[d+1] > bestScore[1]):
                            bestScore[0] = d
                            bestScore[1] = negativeScore[d]
                    if(bestScore[0] == 4):
                        ship.next_action = None
                        nextPositions.append(ship.position)
                    else:
                        ship.next_action = getattr(ShipAction, position[bestScore[0]])
                        nextPositions.append(getattr(ship.cell, position[bestScore[0]]).position)

                else: # If not, move away to a better spot
                    bestScore = [negativeScore[0], 4] # term 0 is the actual score, term 1 is the direction as the index value of the position[] array
                    for dir in range(5): # For each movement
                        if(dir != (len[positiveScore]-1)):
                            totalScore = (positiveScore[dir] + positiveScore[dir + 1]) + negativeScore[dir + 1]
                            if(totalScore > bestScore[0]):
                                bestScore[0] = totalScore
                                bestScore[1] = dir
                        else: # If it's the last possible term centre non inclusive (to wrap the array addition)
                            totalScore = (positiveScore[0] + positiveScore[dir]) + negativeScore[dir + 1]
                            if(totalScore > bestScore[0]):
                                bestScore[0] = totalScore
                                bestScore[1] = dir
                    if(dir != 4):
                        ship.next_action = getattr(ShipAction, bestScore[1])
                        nextPositions.append(getattr(ship.cell, bestScore[1]).position)
                    else:
                        ship.next_action = None
                        nextPositions.append(ship.position)

    return me.next_actions
