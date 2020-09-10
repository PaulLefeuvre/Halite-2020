from kaggle_environments.envs.halite.helpers import *
from random import choice

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

def movementCheck(ship, me): # Return an array with the danger and interest values of the surrounding squares, in the order: [center, north, east, south, west]
    positionScore = [0, 0, 0, 0, 0]

    if(ship.cell.shipyard != None): # If the spot the ship is on is a shipyard
        positionScore[0] += -100 # Good incentive to leave, but it is possible to stay - just check later

    # Check surroundings for threats
    for i in range(0, 4): # Loop through all four directions
        currentCell = getattr(ship.cell, direction[i])
        if(currentCell.ship != None): # If there is a ship one block away
            # check that the obstacle ship isn't mine AND if the current ship would be destroyed if it crashed into it
            if(ship.halite >= currentCell.ship.halite and currentCell.ship.player != me):
                positionScore[i+1] +=  -200
                positionScore[0] += -200
        if(currentCell.shipyard != None): # If there is a shipyard one block away
            positionScore[i+1] += -1000 # Heavy incentive not to go - ship will always be destroyed there
        for x in range(0, 4): # Loop through all the blocks surrounding the block one away...
            checkCell = getattr(currentCell, position[x])
            if(checkCell.position != ship.position): # ...except for the one the ship is currently on (we already checked it)
                if(checkCell.ship != None): # If there is a ship two blocks away
                    if(ship.halite >= checkCell.ship.halite and currentCell.ship.player != me):
                        positionScore[i] += -150 # I'm coming up with these values as I go - refine later

    return positionScore


nextPos = []

shipRoles = {}

def agent(obs, config):

    board = Board(obs,config)
    me = board.current_player
    size = config.size

#    # If there are no ships, use only shipyard to spawn a ship
#    if len(me.ships) == 0 and len(me.shipyards) == 1:
#        me.shipyards[0].next_action = ShipyardAction.SPAWN
#
#    # If there are no shipyards, convert first ship into shipyard, but only if they can make a ship afterwards
#    if len(me.shipyards) == 0 and len(me.ships) > 0 and player.halite >= 1000:
#        me.ships[0].next_action = ShipAction.CONVERT

    # Set actions for each shipyard
    for shipyard in me.shipyards:
        shipyard.next_action = None

    # Set actions for each ship
    for ship in me.ships:

        options = movementCheck(ship, me)
        if(shipRoles[ship.id] == 'Miner'):
            # If the current spot is worth mining and there is no risk around
            if(ship.position.halite >= 200 && options[0] == 0):
                ship.next_action = ShipAction.None # Mine the Halite
            else: # If not, move away to a better spot
                lowestScore = options[0]
                lowestOptions = []
                for i in range(0, 5): # Find all the highest scoring options from the options[] array - there may be several
                    if(options[i] == lowestScore):
                        lowestOptions.append(i)
                    elif(options[i] > lowestScore):
                        lowestScore = options[i]
                        lowestOptions = []
                        lowestOptions.append(i)
                if(len(lowestOptions) == 1):
                    if(lowestOptions[0] == 0):
                        ship.next_action = ShipAction.None
                    elif(lowestOptions[0] == 1):
                        ship.next_action = ShipAction.north
                    elif(lowestOptions[0] == 2):
                        ship.next_action = ShipAction.east
                    elif(lowestOptions[0] == 3):
                        ship.next_action = ShipAction.south
                    else:
                        ship.next_action = ShipAction.west

        if ship.next_action == None:
            position = optimumScan(ship.position, cell.halite, 3)

    return me.next_actions
