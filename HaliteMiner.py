from kaggle_environments.envs.halite.helpers import *
from random import choice

def optimumScan(pos, obj, dis, bear): # Get the pos, requested object, distance wanted, and bearing at which to scan
    width = (distance*2)-1
    iterNum = width*width
    bestScore = 0
    bestDis = dis + 1 # A value that instantly loses to any other value
    for i in range(iterNum):
        position = ((xOrigin + (i%width)) * 21) + (yOrigin + (i//width))
        if(cell[position]. )
    optimumScan()

def distance(fromPos, toPos):
    calVal = abs(fromPos[0] - toPos[0]) + abs(fromPos[1] - toPos[1])
    return calVal

def movementCheck(ship): # Return an array with the danger and interest values of the surrounding squares, in the order: [center, north, east, south, west]
    positionScore = [0, 0, 0, 0, 0]
    if(ship.cell.shipyard != null): # If the spot the ship is on is a shipyard
        positionScore[0] = -100 # Heavy incentive to leave, but it is possible to stay - just check later
    if(ship.cell.north.ship != null): # If there is a ship out north
        postionScore[2]


nextPos = []

def agent(obs,config):

    board = Board(obs,config)
    me = board.current_player

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
        options = movementCheck(ship)

        if ship.next_action == None:
            position = optimumScan(ship.position, cell.halite, 3)

    return me.next_actions
