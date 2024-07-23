from flask import Flask, render_template, request, jsonify
import chess
import asyncio
import random
import chess.pgn
import chess.svg
from stockfish import Stockfish
import signal

from helpers import choose_move, calculate_material, hangs, recapturable
from players import sensible_sam
from engine import engine
from prevengine import prevengine

app = Flask(__name__)
board = chess.Board()

@app.route('/')
async def index():
    board_svg = chess.svg.board(board)
    return render_template('index.html', board_svg=board_svg)

@app.route('/move', methods=['POST'])
async def move():
    user_move = request.form['move']
    try:
        move = board.parse_san(user_move)
        if move in board.legal_moves:
            board.push(move)
            nextMove = await engine(board)
            if board.parse_san(nextMove) in board.legal_moves:
                board.push_san(nextMove)
            else:
                return jsonify({'status': 'illegal', 'message': 'Illegal engine move'})
            # return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})
            return jsonify({'status': 'success', 'board_fen': board.fen()})
        else:
            return jsonify({'status': 'illegal', 'message': 'Illegal move'})
    except:
        return jsonify({'status': 'invalid', 'message': 'Invalid move format'})

@app.route('/new_game', methods=['POST'])
async def new_game():
    global board
    board = chess.Board()
    return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})

if __name__ == "__main__":
    app.run(debug=True)

#if __name__ == "__main__":
    # num_games = 30
    # results = asyncio.run(run_multiple_games(num_games))
    # print(f"Results after {num_games} games:")
    # print(f"White wins: {results['white_wins']}")
    # print(f"Black wins: {results['black_wins']}")
    # print(f"Draws: {results['draws']}")
    #asyncio.run(run_chess_game())
