
def old():
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

# def trim_move_objects(move, trimBoard):
#     global added
#     options = len(move.responses)
#     trimBoard.push(move.move)
#     if options == 0:
#         localBoard = trimBoard.copy()
#         responses = recur(localBoard, move, 0)
#         move.add_batch(responses)
#         added = added + 1
#         if added % 100 == 0:
#             print(f"Added {added} moves")
#     else:
#         move.remove_worst()
#         for resp in move.responses:
#             localBoard = trimBoard.copy()
#             trim_move_objects(resp, localBoard)


    # for move in list(board.legal_moves):
    #     board.push(move)
    #     move_object = MoveObject(move, not board.turn, calculate_points_color(board))
    #     print(move_object.points)
    #     responses = recur(board, move_object, move, 0)
    #     move_object.add_batch(responses)
    #     move_objects.append(move_object)
    #     board.pop()
    # print(len(lastMoves))