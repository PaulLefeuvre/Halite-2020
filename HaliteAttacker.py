# Imports helper functions
from kaggle_environments.envs.halite.helpers import *

def distance(fromPos, toPos):
    calVal = abs(fromPos[0] - toPos[0]) + abs(fromPos[1] - toPos[1])
    return calVal

def bestDirection(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST

def agent(obs,config):

    size = config.size
    board = Board(obs,config)
    me = board.current_player

    # Set actions for each ship
    for ship in me.ships:
        # If there are no shipyards, convert first ship into shipyard, but only if they can make a ship afterwards
        if ship.halite > 500:
            bestDistance = 0
            bestPosition = [0,0]
            for shipyard in me.shipyards:
                currentDistance = distance(ship.position, shipyard.position)
                if currentDistance >= bestDistance:
                    bestDistance = currentDistance
                    bestPosition = shipyard.position
            if distance(bestPosition, ship.position) > 6:
                ship.next_action = ShipAction.CONVERT
            else:
                ship.next_action = bestDirection(ship.position, bestPosition, size)

        else:
            bestScore = 0
            bestDistance = 43
            bestPosition = [0, 0]
            for totalShip in board.ships: # Scan through all enemy ships
                # If colliding with it would actually be advantegeous
                if board.ships[totalShip].player != me and board.ships[totalShip].halite > ship.halite:
                    currentDistance = distance(board.ships[totalShip].position, ship.position)
                    currentScore = board.ships[totalShip].halite // currentDistance
                    # If it's more worth it than other ships
                    if(currentScore >= bestScore and currentDistance <= bestDistance):
                        bestDistance = currentDistance
                        bestScore = currentScore
                        bestPosition = board.ships[totalShip].position
            if bestScore == 0:
                bestDistance = 0
                bestPosition = [0,0]
                for shipyard in me.shipyards:
                    currentDistance = distance(ship.position, shipyard.position)
                    if currentDistance >= bestDistance:
                        bestDistance = currentDistance
                        bestPosition = shipyard.position
                if distance(bestPosition, ship.position) > 6 and me.halite >= 1000 * len(me.shipyards):
                    ship.next_action = ShipAction.CONVERT
                else:
                    ship.next_action = bestDirection(ship.position, bestPosition, size)
            else:
                ship.next_action = bestDirection(ship.position, bestPosition, size)

    # Set actions for each shipyard
    for shipyard in me.shipyards:
        if ((len(me.ships) * 500) + 500) <= me.halite:
            shipyard.next_action = ShipyardAction.SPAWN
        else:
            shipyard.next_action = None

    # If there are no ships, use only shipyard to spawn a ship
    if len(me.ships) == 0 and len(me.shipyards) > 0:
        me.shipyards[0].next_action = ShipyardAction.SPAWN

    # If there are no shipyards, use only ship to create a shipyard
    if len(me.shipyards) < 1 and me.halite >= 1000:
        me.ships[0].next_action = ShipAction.CONVERT

    return me.next_actions
