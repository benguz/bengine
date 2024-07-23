import chess
import asyncio
import random
import chess.pgn

from helpers import choose_move, calculate_material, hangs, recapturable, calculate_points

piece_values = {
                'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
            }
class moveObject:
    def __init__(self, move, points, parent=None):
        self.move = move
        self.points = points
        self.responses = []
        self.parent = parent

    def add_response(self, move, points):
        self.responses.append(moveObject(move, points, self))


def evaluator_edward(board):
    diff = calculate_points(board)
    moves = []
    for move in list(board.legal_moves):
        board.push(move)
        moveObject = moveObject(move, calculate_points(board))

        if board.is_checkmate():
            board.pop()
            return move
        if calculate_points(board) > diff:
            for response in list(board.legal_moves):
                board.push(response)
                moveObject.add_response(response, calculate_points(board))
                board.pop()

        board.pop()

def sensible_sam(board):
    white, black = calculate_material(board)
    copy = board.copy() # refactor to use the copy
    for move in list(copy.legal_moves):
        copy.push(move)
        if copy.is_checkmate():
            copy.pop()
            print("checkmate")
            return board.san(move)
        copy.pop()
    
    for move in list(copy.legal_moves):
        if move.promotion is not None:
            print("promotion")
            return board.san(move)

    for move in list(copy.legal_moves):
        if white + black < 12 and board.is_zeroing(move):
            if not hangs(copy, move):
                print("zeroing")
                return board.san(move)
        
    for move in list(copy.legal_moves):
        if copy.is_en_passant(move):
            print("en passant")
            return board.san(move)
    
    for move in list(copy.legal_moves):
        if copy.is_capture(move):
            print("capture")
            captured_piece = copy.piece_at(move.to_square)
            capturing_piece = copy.piece_at(move.from_square)
            
            if piece_values[capturing_piece.symbol()] <= piece_values[captured_piece.symbol()] or white + black < 12:
                print("recapturable")
                copy.push(move)
                recap = True
                for response in list(copy.legal_moves):
                    if copy.is_capture(response):
                        recap = False
                copy.pop()
                if not recap:
                    print("move", move)
                    return board.san(move)
                else:
                    print("not recapturable")
                    continue
            else:
                print("not recapturable")
                continue

    for move in list(copy.legal_moves):
        if copy.is_check():
            copy.push(move)
            recap = recapturable(copy)
            copy.pop()
            if not recap:
                print("check")
                return board.san(move)
            else:
                print("not check") 
                continue
        
    for move in list(copy.legal_moves):
        if copy.is_castling(move):
            print("castling")
            return board.san(move)

    move = random.choice(list(copy.legal_moves))
    return board.san(move)