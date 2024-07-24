import chess
import random
import chess.pgn
import math
from helpers import calculate_material, hangs, recapturable, calculate_points, calculate_points_color
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque
import heapq
import concurrent.futures

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

    def diff(self):
        if len(self.weights) < 2:
            return None
        smallest_weights = heapq.nsmallest(2, self.weights)
        return abs(smallest_weights[1] - smallest_weights[0])

    def remove_worst(self):
        self.weights.clear()
        # get the three smallest weights
        if (self.depth > 4):
            if len(self.responses) > 5:
                self.responses = sorted(self.responses, key=lambda x: -1 * x.points)[:5]
            elif len(self.responses) == 5:
                self.responses = sorted(self.responses, key=lambda x: -1 * x.points)[:4]
        else:
            if len(self.responses) > 3:
                self.responses = sorted(self.responses, key=lambda x: -1 * x.points)[:3]
            elif len(self.responses) == 3:
                self.responses = sorted(self.responses, key=lambda x: -1 * x.points)[:2]

        
        # consider and double check a heapq method
        
    def max_weight(self):
       return max(self.weights) if self.weights else None
    
    def weighted_avg(self):  # need a better fuzz function - if there are many positive moves, only consider them
        if not self.weights:
            return None
        if len(self.weights) < 2:
            return self.weights[0]
        if len(self.weights) < 4:
            smallest_weights = heapq.nsmallest(2, self.weights)
            return (smallest_weights[0] * 2 + smallest_weights[1]) / 3
        if len(self.weights) < 5:
            smallest_weights = heapq.nsmallest(3, self.weights)
            return (smallest_weights[0] * 3 + smallest_weights[1] * 2 + smallest_weights[2]) / 6
        
        smallest_weights = heapq.nsmallest(5, self.weights)
         # if three of the smallest weights have the same sign, only consider them
        if smallest_weights[0] > 0 and smallest_weights[1] > 0 and smallest_weights[2] > 0:
            return (smallest_weights[0] * 3 + smallest_weights[1] * 2 + smallest_weights[2] + smallest_weights[3] * 0.5) / 6.5
        if smallest_weights[0] < 0 and smallest_weights[1] < 0 and smallest_weights[2] < 0:
            return (smallest_weights[0] * 3 + smallest_weights[1] * 2 + smallest_weights[2] + smallest_weights[3] * 0.5) / 6.5
        
        total_weight = sum((5 - i) * weight for i, weight in enumerate(smallest_weights))
        total_factors = sum(range(1, 6))
        return total_weight / total_factors
    
    def naive_avg(self):
        if not self.weights:
            return None

        smallest_weights = heapq.nsmallest(5, self.weights)

        return sum(self.weights) / len(self.weights)
    
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
async def bullet_engine(board):
    w, b = calculate_material(board)
    print(w, b)
    diffInit = calculate_points_color(board)
    print(diffInit)
    thread_executor = ThreadPoolExecutor()

    # moveLen = len(list(board.legal_moves))
    depth = 4
    # if (w + b) < 15 or b < 10 or moveLen < 2:
    #     depth = 6

    # if (w + b) < 10 or b < 6:
    #     depth = 8
    
    vars = 9# 9
    if (w + b) > 70:
       vars = 6# 5

    move_objects = []
    loop = asyncio.get_event_loop()

    # limit search to 10 moves + checks and captures?
    # with ProcessPoolExecutor() as executor:  # Changed to ProcessPoolExecutor
    tasks = [loop.run_in_executor(thread_executor, process_move, board.copy(), depth, vars, move) for move in list(board.legal_moves)]
    move_objects = await asyncio.gather(*tasks)
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
        # resp_string = f"{choices.move} {round(choices.points, 3)} --> "
        # best_response = None
        # diff = choices.diff()
        # if choices.responses:
        #     best_response = min(choices.responses, key=lambda x: -1 * x.points, default=None)
        #     if best_response:
        #         resp_string += f"{best_response.move} {round(best_response.points, 3)} "
        #         diff = best_response.parent.diff()

        # while best_response and len(best_response.responses) > 0:
        #     best_response = min(best_response.responses, key=lambda x: -1 * x.points, default=None)
        #     resp_string += f"--> {best_response.move} {round(best_response.points, 3)} "
        #     diff = best_response.parent.diff()
        # print(resp_string, diff)
        if (choices.points > max_points):
            max_points = choices.points
            best = choices.move
            choice = choices

    print("best move", best, max_points)

    return board.san(best)


leafs = 0
def traverse_move_objects(move, trimBoard, total=0, max_depth=0): # penultimate_move=None, best_response=None
    global leafs
    options = len(move.responses)
    trimBoard.push(move.move)
    if options == 0 and len(list(trimBoard.legal_moves)) > 0: # shouldn't be reached
        responses = recur(trimBoard, move, move.depth, max_depth=max_depth, max_variations=9)
        move.add_batch(responses)
        trimBoard.pop()
        return 1
    elif options == 0 and len(list(trimBoard.legal_moves)) == 0:
        lastMoves.append(move)
        trimBoard.pop()
        return 0
    else:
        move.remove_worst()
        leafs += 1
            # if penultimate_move and move == penultimate_move:
            #     print("in")
            #     if (best_response not in move.responses):
            #         print(f"out move: {move.move}, points: {move.points}, depth: {move.depth}")
            # if (move.depth == 3):
            #     print(f"move: {move.move}, points: {move.points}, depth: {move.depth} respLen: {len(move.responses)} pretrim: {pretrimLen} parents: {move.parent.parent.parent.move} {move.parent.parent.move} {move.parent.move} ")
            #     for resp in move.responses:
            #         print(resp.move, resp.points, resp.depth)
        for resp in move.responses:
            localBoard = trimBoard.copy()
            total += traverse_move_objects(resp, localBoard, 0, max_depth)
    trimBoard.pop()
    return total

added = 0

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
        response_object = MoveObject(move, not board.turn, calculate_points_color(board, depth + 1, max_depth), parent=parent, depth=depth + 1)
        response_object.add_batch(recur(board, response_object, depth + 1, max_depth, max_variations)) 
        if len(response_object.responses) == 0 and depth + 1 < max_depth: # what does this and do?
            lastMoves.append(response_object)
        board.pop()
        responseObjects.append(response_object)
        variations += 1
  else:
    lastMoves.append(parent)
  return responseObjects 

def update_moves():
    while len(lastMoves) > 0: # don't we want min move for black and max move for white?
        current_move = lastMoves.popleft()
        if (current_move.parent):
            options = len(current_move.parent.responses)
            current_move.parent.add_weight(-1 * current_move.points)  # invert the points
            if len(current_move.parent.weights) == options:
                minWeight = None
                # if (current_move.depth == depth):
                #     minWeight = current_move.parent.weighted_avg()
                # else:
                #     minWeight = current_move.parent.min_weight()
                minWeight = current_move.parent.min_weight()
                # consider using a positional fuzz function here when deep
                if minWeight > 100:
                    current_move.parent.points = minWeight - 10 # intended to favor closer checkmates
                elif minWeight < -100:
                    current_move.parent.points = minWeight + 10
                else:
                    current_move.parent.points = minWeight
                lastMoves.append(current_move.parent)