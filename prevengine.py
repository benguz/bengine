import chess
import random
import chess.pgn
import math
from helpers import calculate_material, hangs, recapturable, calculate_points, calculate_points_color
import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import heapq


# next: add color logic
# not using original board diff yet?
# eval function should look 1 move ahead
# kill moves w/ opposite eval
# recapturable logic broken?
class MoveObject:
    def __init__(self, move, whiteMove, points, parent=None, depth=0):
        self.move = move
        self.whiteMove = whiteMove
        self.points = points
        self.responses = []
        self.parent = parent
        self.weights =[]
        self.depth = depth

    def change_points(self, points):
        self.points = points

    def add_weight(self, weight):
       self.weights.append(weight)

    def remove_worst(self):
        self.weights.clear()
        # get the three smallest weights
        if len(self.responses) > 3:
            self.responses = sorted(self.responses, key=lambda x: -1 * x.points)[:3]
        if len(self.responses) == 3:
            self.responses = sorted(self.responses, key=lambda x: -1 * x.points)[:2]
        # consider and double check a heapq method
        
    def max_weight(self):
       return max(self.weights) if self.weights else None
    
    def weighted_avg(self):
        if not self.weights:
            return None
        if len(self.weights) < 4:
            return min(self.weights)
        if len(self.weights) < 4:
            return (self.weights[0] * 2 + self.weights[1] + self.weights[2] * 0.5) / 3.5
        if len(self.weights) < 5:
            return (self.weights[0] * 3 + self.weights[1] * 2 + self.weights[2] + self.weights[3] * 0.5) / 6.5
        
        smallest_weights = heapq.nsmallest(5, self.weights)
        total_weight = sum((5 - i) * weight for i, weight in enumerate(smallest_weights))
        total_factors = sum(range(1, 6))
        return total_weight / total_factors
    
    def min_weight(self):
        return min(self.weights) if self.weights else None
    
    def avg_weight(self):
        if not self.weights:
            return None
        return sum(self.weights) / len(self.weights)

    def add_response(self, move, points):
        self.responses.append(MoveObject(move, points, parent=self))

    def add_object(self, obj):
        self.responses.append(obj)

    def add_batch(self, arr):
        self.responses.extend(arr)

def process_move(board, depth, vars, move):
    try:
        new_board = board.copy()
        new_board.push(move)
        move_object = MoveObject(move, not new_board.turn, calculate_points_color(new_board), depth=0)
        # print(move_object.move, move_object.points)
        responses = recur(new_board, move_object, 0, depth, vars)
        move_object.add_batch(responses)
        return move_object
    except Exception as e:
        print(f"Error w/ move: {e}")
        return None
    
def process_object(board, move_object, depth, vars):
    try:
        new_board = board.copy()
        new_board.push(move_object.move)
        # print(move_object.move, move_object.points)
        if len(move_object.responses) == 0:
            responses = recur(new_board, move_object, 0, depth, vars)
            move_object.add_batch(responses)
        else:
            for resp in move_object.responses:
                newer_board = new_board.copy()
                process_object(newer_board, resp, depth, vars)
        return move_object
    except Exception as e:
        print(f"Error w/ move: {e}")
        return None

lastMoves = deque()
async def prevengine(board):
    w, b = calculate_material(board)
    print(w, b)

    moveLen = len(list(board.legal_moves))
    depth = 4
    if (w + b) < 15 or b < 10 or moveLen < 4:
        depth = 6

    if (w + b) < 10 or b < 6 or moveLen < 3:
        depth = 8
    
    vars = 9# 9
    if (w + b) > 70:
       vars = 6# 5

    move_objects = []
    loop = asyncio.get_event_loop()

    # limit search to 10 moves + checks and captures?
    with ThreadPoolExecutor() as executor:
        tasks = [loop.run_in_executor(executor, process_move, board.copy(), depth, vars, move) for move in list(board.legal_moves)]
        move_objects = await asyncio.gather(*tasks)

    # for move in list(board.legal_moves):
    #     board.push(move)
    #     move_object = MoveObject(move, not board.turn, calculate_points_color(board))
    #     print(move_object.points)
    #     responses = recur(board, move_object, move, 0)
    #     move_object.add_batch(responses)
    #     move_objects.append(move_object)
    #     board.pop()
    # print(len(lastMoves))
    print("lm1", len(lastMoves))

    while len(lastMoves) > 0: # don't we want min move for black and max move for white?
        current_move = lastMoves.popleft()
        if (current_move.parent):
            options = len(current_move.parent.responses)
            current_move.parent.add_weight(-1 * current_move.points)  # invert the points
            # print(f"Current move: {current_move.move}, Parent move: {current_move.parent.move}, Weights: {current_move.parent.weights}")

            # lastMoves[0].parent.points = (lastMoves[0].parent.points * ((options-1)/options) - (1/options) * (lastMoves[0].points))
            if len(current_move.parent.weights) == options:
                #if lastMoves[0].whiteMove: 
                minWeight = None
                if (current_move.depth == depth):
                    minWeight = current_move.parent.weighted_avg()
                else:
                    minWeight = current_move.parent.min_weight()
                 # avg_weight()
                if minWeight > 100:
                    current_move.parent.points = minWeight - 10 # intended to favor closer checkmates
                elif minWeight < -100:
                    current_move.parent.points = minWeight + 10
                else:
                    current_move.parent.points = minWeight
                # print(f"Updated parent points: {current_move.parent.move} to {current_move.parent.points}, w: {len(current_move.parent.weights)} o:{options}")
                # else:
                #  lastMoves[0].parent.points = -1 * lastMoves[0].parent.max_weight()  # distant moves need a fuzzier calculation, proximal ones need this clearer one
                lastMoves.append(current_move.parent)

    max_points=-10000
    best = None
    choice = None
    # filter out none items in move_objects
    # pre_len = len(move_objects)
    move_objects = [move for move in move_objects if move is not None]
    # print(f"Filtered out {pre_len - len(move_objects)} None items")

    for choices in move_objects:
        # print(choices)
        # resp_string = f"{choices.move} {round(choices.points, 3)} --> "
        # best_response = min(choices.responses, key=lambda x: -1 * x.points, default=None)
        # if best_response:
        #     resp_string += f"{best_response.move} {round(best_response.points, 3)} "
        # while best_response and len(best_response.responses) > 0:
        #     best_response = min(best_response.responses, key=lambda x: -1 * x.points, default=None)
        #     resp_string += f"--> {best_response.move} {round(best_response.points, 3)}"
        # print(resp_string)
        if (choices.points > max_points):
            max_points = choices.points
            best = choices.move
            choice = choices

    print("best move", best, max_points)
    resp_string = f"{choice.move} {round(choice.points, 3)} --> "
    best_response = None
    if choice.responses:
        best_response = min(choice.responses, key=lambda x: -1 * x.points, default=None)
        if best_response:
            resp_string += f"{best_response.move} {round(best_response.points, 3)} "
    while best_response and len(best_response.responses) > 0:
       best_response = min(best_response.responses, key=lambda x: -1 * x.points, default=None)
       resp_string += f"--> {best_response.move} {round(best_response.points, 3)} "
    print(resp_string)

    # filter from move objects with the lowest points so there are at most 5 left
    move_objects = sorted(move_objects, key=lambda x: x.points, reverse=True)[:5]
    # check if choice is in move_objects
    if choice not in move_objects:
        print("choice not in move_objects")


    depth = 8

    sum = 0
    print("candidates:")
    for move in move_objects:
        print(move.move, move.points)
        sum += traverse_move_objects(move, board.copy(), 0, True, depth)
    print("sum", sum)
    print("lm", len(lastMoves))
    # with ThreadPoolExecutor() as executor:
    #     tasks = [loop.run_in_executor(executor, traverse_move_objects, move, board.copy(), 0, True, depth) for move in move_objects]
    #     promise = await asyncio.gather(*tasks)


    while len(lastMoves) > 0: # don't we want min move for black and max move for white?
        current_move = lastMoves.popleft()
        if (current_move.parent):
            options = len(current_move.parent.responses)
            current_move.parent.add_weight(-1 * current_move.points)  # invert the points
            if len(current_move.parent.weights) == options:
                minWeight = None
                if (current_move.depth == depth):
                    minWeight = current_move.parent.weighted_avg()
                else:
                    minWeight = current_move.parent.min_weight()

                # consider using a positional fuzz function here when deep
                if minWeight > 100:
                    current_move.parent.points = minWeight - 10 # intended to favor closer checkmates
                elif minWeight < -100:
                    current_move.parent.points = minWeight + 10
                else:
                    current_move.parent.points = minWeight
                lastMoves.append(current_move.parent)
    
    max_points=-10000
    best = None
    choice = None
    move_objects = [move for move in move_objects if move is not None]
    for choices in move_objects:
        if (choices.points > max_points):
            max_points = choices.points
            best = choices.move
            choice = choices

    print("best move", best, max_points)
    resp_string = f"{choice.move} {round(choice.points, 3)} --> "
    best_response = None
    if choice.responses:
        best_response = min(choice.responses, key=lambda x: -1 * x.points, default=None)
        if best_response:
            resp_string += f"{best_response.move} {round(best_response.points, 3)} "
    while best_response and len(best_response.responses) > 0:
       best_response = min(best_response.responses, key=lambda x: -1 * x.points, default=None)
       resp_string += f"--> {best_response.move} {round(best_response.points, 3)} "
    print(resp_string)

    return board.san(best)

    # with ThreadPoolExecutor() as executor:
    #     tasks = [loop.run_in_executor(executor, traverse_move_objects, move, board.copy(), 0, True) for move in move_objects]
    #     responses = await asyncio.gather(*tasks)


    return board.san(best)

    print(len(move_objects))
    # for move in move_objects:
    #     trimBoard = board.copy()
    #     trim_move_objects(move, trimBoard)
    print("clearedLm", len(lastMoves))
    with ThreadPoolExecutor() as executor:
        tasks = [loop.run_in_executor(executor, trim_move_objects, move, board.copy()) for move in move_objects]
        await asyncio.gather(*tasks)

    # with ThreadPoolExecutor() as executor:
    #     tasks = [loop.run_in_executor(executor, process_object, board.copy(), obj, depth, vars) for obj in move_objects]
    #     move_objects = await asyncio.gather(*tasks)
    
    print("lm", len(lastMoves))
    while len(lastMoves) > 0: # don't we want min move for black and max move for white?
        current_move = lastMoves.popleft()
        if (current_move.parent):
            options = len(current_move.parent.responses)
            current_move.parent.add_weight(-1 * current_move.points)  # invert the points
            if len(current_move.parent.weights) == options:
                minWeight = current_move.parent.min_weight()
                if minWeight > 100:
                    current_move.parent.points = minWeight - 10 # intended to favor closer checkmates
                elif minWeight < -100:
                    current_move.parent.points = minWeight + 10
                else:
                    current_move.parent.points = minWeight
                lastMoves.append(current_move.parent)
    
    max_points=-10000
    best = None
    choice = None
    move_objects = [move for move in move_objects if move is not None]
    for choices in move_objects:
        if (choices.points > max_points):
            max_points = choices.points
            best = choices.move
            choice = choices

    print("best move", best, max_points)

    return board.san(best)

leafs = 0
def traverse_move_objects(move, trimBoard, total=0, trim=False, max_depth=0):
    global leafs
    options = len(move.responses)
    trimBoard.push(move.move)
    if options == 0 and len(list(trimBoard.legal_moves)) > 0:
        responses = recur(trimBoard, move, move.depth, max_depth=max_depth)
        move.add_batch(responses)
        trimBoard.pop()
        return 1
    elif options == 0 and len(list(trimBoard.legal_moves)) == 0:
        trimBoard.pop()
        return 0
    else:
        if (trim):
            move.remove_worst()
            leafs += 1
            if (len(move.responses) == options and options > 3):
                print("failed to trim")
        for resp in move.responses:
            localBoard = trimBoard.copy()
            total += traverse_move_objects(resp, localBoard, 0, trim, max_depth)
    trimBoard.pop()
    return total

added = 0
def trim_move_objects(move, trimBoard):
    global added
    options = len(move.responses)
    trimBoard.push(move.move)
    if options == 0:
        localBoard = trimBoard.copy()
        responses = recur(localBoard, move, 0)
        move.add_batch(responses)
        added = added + 1
        if added % 100 == 0:
            print(f"Added {added} moves")
    else:
        move.remove_worst()
        for resp in move.responses:
            localBoard = trimBoard.copy()
            trim_move_objects(resp, localBoard)

# we should consider not adding duplicates to lastMoves
def recur(board, parent, depth, max_depth=4, max_variations=9):
  responseObjects = []
  variations = 0
  if (depth < max_depth):
    for move in list(board.legal_moves):
      check = board.gives_check(move)
      capture = board.is_capture(move)
      if (variations < max_variations or check or move.promotion is not None or capture):
        board.push(move)
        response_object = MoveObject(move, not board.turn, calculate_points_color(board), parent=parent, depth=depth + 1)
        response_object.add_batch(recur(board, response_object, depth + 1, max_depth, max_variations)) 
        if len(response_object.responses) == 0 and depth + 1 < max_depth:
            # print(f"No responses for {move}, {response_object.points}")
            lastMoves.append(response_object)
        board.pop()
        responseObjects.append(response_object)
        variations += 1
  else:
    lastMoves.append(parent)
  return responseObjects 

