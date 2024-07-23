import chess
import asyncio
import random
import chess.pgn
from stockfish import Stockfish
import signal

from helpers import choose_move, calculate_material, hangs, recapturable
from players import sensible_sam
from engine import engine
from prevengine import prevengine


piece_values = {
                'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
            }

async def run_chess_game():
    board = chess.Board()
    whiteMove = True
    moveNum = 1
    stockfish = Stockfish(path="/opt/homebrew/Cellar/stockfish/16.1/bin/stockfish", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 15, "Hash": 64})

    stockfish.set_elo_rating(1550)

    while not board.is_game_over():
        if whiteMove:
            # nextMove = await white_move(board)
            nextMove = await engine(board)
            print(f"{moveNum}. {nextMove}")
        else:
            stockfish.set_fen_position(board.fen())
            nextMove = board.san(chess.Move.from_uci(stockfish.get_best_move()))
            # nextMove = await white_move(board) # await black_move(board) # await get_user_move(board)
            moveNum += 1
            print(f"..{nextMove}")

        try:
            if board.parse_san(nextMove) in board.legal_moves:
                board.push_san(nextMove)
        except:
            print(f"Invalid move: {nextMove}")

        whiteMove = not whiteMove
        print(board)
    print("Game Over:", board.outcome())
    print_board(board)
    return board.outcome()

async def get_user_move(board):
    while True:
        user_input = input("Enter your move: ")
        try:
            move = board.parse_san(user_input)
            if move in board.legal_moves:
                return user_input
            else:
                print("Illegal move. Try again.")
        except:
            print("Invalid move format. Try again.")


def print_board(board):
    moves = []
    temp_board = board.copy()
    while temp_board.move_stack:
        move = temp_board.pop()
        moves.append(temp_board.san(move))
    
    moves.reverse()
    move_str = " ".join(f"{i//2 + 1}. {move}" if i % 2 == 0 else f"{move}" for i, move in enumerate(moves))
    print(move_str)

async def white_move(board):
    await asyncio.sleep(2)  # Simulate thinking time
    # move = choose_move(board)
    filteredMoves = []
    for move in list(board.legal_moves):
        board.push(move)
        w, b = calculate_material(board)
        mated = False
        losingMats = False
        for response in list(board.legal_moves):
            board.push(response)
            w2, b2 = calculate_material(board)
            if board.is_checkmate():
                mated = True
            if w2 > w:
                losingMats = True
            board.pop()
        if not mated and not losingMats:
            filteredMoves.append(move)
        board.pop()

    white, black = calculate_material(board)
    if len(filteredMoves) == 0:
        filteredMoves = list(board.legal_moves)
    for move in filteredMoves:
        temp = board.copy()
        temp.push(move)
        if temp.is_checkmate():
            return board.san(move)
        
    for move in filteredMoves:
        temp = board.copy()
        temp.push(move)
        if move.promotion is not None:
            return board.san(move)
        
    for move in filteredMoves:
        temp = board.copy()
        if white + black < 20 and temp.is_zeroing(move):
            hangs = False
            lost_piece_val = 0
            if board.piece_at(move.to_square) is not None:
                lost_piece = board.piece_at(move.to_square)
                lost_piece_val = piece_values[lost_piece.symbol()]
            temp.push(move)
            hangs = False
            last_move = move.to_square
            move_piece = move.drop.symbol()
            move_piece_val = piece_values[move_piece]
            for response in list(board.legal_moves):
                if board.is_capture(response):
                    capturing_piece = response.drop.symbol()
                    captured_square = response.to_square
                    if last_move == captured_square and move_piece_val > lost_piece_val:
                        hangs = True
                        break
            if not hangs:
                print("zeroing")
                return board.san(move)
            
    for move in filteredMoves:
        temp = board.copy()
        temp.push(move)
        if board.is_en_passant(move):
            return board.san(move)
        
    for move in filteredMoves:
        temp = board.copy()
        if temp.is_capture(move):
            captured_piece = temp.piece_at(move.to_square)
            capturing_piece = temp.piece_at(move.from_square)
            if piece_values[capturing_piece.symbol()] <= piece_values[captured_piece.symbol()] or white + black < 12:
                return board.san(move)
            else:
                continue

    for move in filteredMoves:
        temp = board.copy()
        temp.push(move)
        capture = temp.is_capture(move)
        if temp.is_check() and not capture:
            return board.san(move)
        
    for move in filteredMoves:
        temp = board.copy()
        if temp.is_castling(move):
            return board.san(move)
  
    move = random.choice(list(board.legal_moves))
    return board.san(move)

async def black_move(board):
    await asyncio.sleep(2)  # Simulate thinking time
    copy = board.copy()
    move = sensible_sam(copy)
    return board.san(move)

async def test_engine(board):
    return await engine(board)

async def run_multiple_games(num_games):
    results = {
        "white_wins": 0,
        "black_wins": 0,
        "draws": 0,
    }

    # Run games in parallel
    tasks = [run_chess_game() for _ in range(num_games)]
    outcomes = await asyncio.gather(*tasks)

    for outcome in outcomes:
        if outcome.winner is True:
            results["white_wins"] += 1
        elif outcome.winner is False:
            results["black_wins"] += 1
        else:
            results["draws"] += 1

    return results

def shutdown(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

if __name__ == "__main__":
    # rnbqkbnr/p2pppp1/1pp4p/8/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4 MATE IN ONE
    #6r1/pkN2p1r/3R3P/1N6/P3nP2/2P1p2R/1P2P3/4K3 w - - 1 39 MATED IN ONE
    # these are both white to move cases - I need to test black to move cases
    board = chess.Board(fen="rnbqkbnr/p2pppp1/1pp4p/8/2B1P3/5Q2/PPPP1PPP/RNB1K1NR")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown(loop))
    try:
        loop.run_until_complete(run_chess_game()) # run_chess_game() test_engine(board)
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()

#if __name__ == "__main__":
    # num_games = 30
    # results = asyncio.run(run_multiple_games(num_games))
    # print(f"Results after {num_games} games:")
    # print(f"White wins: {results['white_wins']}")
    # print(f"Black wins: {results['black_wins']}")
    # print(f"Draws: {results['draws']}")
    #asyncio.run(run_chess_game())

#  for move in list(board.legal_moves):
#         temp = board.copy()
#         temp.push(move)
#         if temp.is_checkmate():
#             return board.san(move)
#         if move.promotion is not None:
#             return board.san(move)
#         if board.is_en_passant(move):
#             return board.san(move)
#         if board.is_capture(move):
#             captured_piece = board.piece_at(move.to_square)
#             capturing_piece = board.piece_at(move.from_square)
#             piece_values = {
#                 'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
#                 'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
#             }
#             if piece_values[capturing_piece.symbol()] <= piece_values[captured_piece.symbol()] or white + black < 12:
#                 return board.san(move)
#             else:
#                 continue
#         if temp.is_check():
#             return board.san(move)
#         if board.is_castling(move):
#             return board.san(move)
#         if white + black < 12 and board.is_zeroing(move):
#             return board.san(move)
#     move = random.choice(list(board.legal_moves))
#     return board.san(move)