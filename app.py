from flask import Flask, render_template, request, jsonify
import chess
import asyncio
import random
import chess.pgn
import chess.svg
from stockfish import Stockfish
import signal
import urllib.parse
from aiohttp import web

from engine import engine

async def index(request):
    board = chess.Board()
    board_svg = chess.svg.board(board)
    return web.FileResponse('templates/index.html')

async def move(request):
    data = await request.post()
    user_move = data['move']
    try:
        fen = urllib.parse.unquote(data['fen'])
        board = chess.Board(fen)
        move = board.parse_san(user_move)
        if move in board.legal_moves:
            board.push(move)
            nextMove = await engine(board)
            if board.parse_san(nextMove) in board.legal_moves:
                board.push_san(nextMove)
            else:
                return web.json_response({'status': 'illegal', 'message': 'Illegal engine move'})
            # return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})
            return web.json_response({'status': 'success', 'board_fen': board.fen()})
        else:
            return web.json_response({'status': 'illegal', 'message': 'Illegal move'})
    except:
        return web.json_response({'status': 'invalid', 'message': 'Invalid move format'})
    # except ValueError as e:
    #     return web.json_response({'status': 'invalid', 'message': 'Invalid move format', 'error': str(e)})
    # except Exception as e:
    #     return web.json_response({'status': 'invalid', 'message': 'Invalid move format', 'error': str(e)})

async def fen(request):
    data = await request.post()
    try:
        fen = urllib.parse.unquote(data['fen'])
        board = chess.Board(fen)
        nextMove = await engine(board)
        if board.parse_san(nextMove) in board.legal_moves:
            board.push_san(nextMove)
        else:
            return web.json_response({'status': 'illegal', 'message': 'Illegal engine move'})
        # return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})
        return web.json_response({'status': 'success', 'board_fen': board.fen()})
    except:
        return web.json_response({'status': 'invalid', 'message': 'Invalid move format'})

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/move', move)
app.router.add_post('/fen', fen)

app.router.add_static('/static/', path='static', name='static')

if __name__ == "__main__":
    web.run_app(app)

#if __name__ == "__main__":
    # num_games = 30
    # results = asyncio.run(run_multiple_games(num_games))
    # print(f"Results after {num_games} games:")
    # print(f"White wins: {results['white_wins']}")
    # print(f"Black wins: {results['black_wins']}")
    # print(f"Draws: {results['draws']}")
    #asyncio.run(run_chess_game())
