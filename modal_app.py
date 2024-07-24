from engine import engine
from bullet_engine import bullet_engine
from modal import Image
import modal 

chess_image = (
    Image.debian_slim(python_version="3.10")
    .pip_install("chess")
)

with chess_image.imports():
    import chess
    import chess.svg
    import chess.pgn
    import urllib.parse

app = modal.App(name="chess-bengine")

@app.function(image=chess_image, cpu=8.0, memory=2048, container_idle_timeout=120)
@modal.web_endpoint(method="POST", docs=True)
async def move(move: str, fen: str):
    print(move, fen)
    try:
        # fen = urllib.parse.unquote(fen)
        board = chess.Board(fen)
        move = board.parse_san(move)
        if move in board.legal_moves:
            board.push(move)
            nextMove = await engine(board)
            if board.parse_san(nextMove) in board.legal_moves:
                board.push_san(nextMove)
            else:
                return {'status': 'illegal', 'message': 'Illegal engine move'}
            # return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})
            return {'status': 'success', 'board_fen': board.fen()}
        else:
            return {'status': 'illegal', 'message': 'Illegal move'}
    except:
        return {'status': 'invalid', 'message': 'Invalid move format'}

@app.function(image=chess_image, cpu=8.0, memory=2048, container_idle_timeout=120)
@modal.web_endpoint(method="POST", docs=True)
async def bullet(move: str, fen: str):
    print(move, fen)
    try:
        # fen = urllib.parse.unquote(fen)
        board = chess.Board(fen)
        move = board.parse_san(move)
        if move in board.legal_moves:
            board.push(move)
            nextMove = await bullet_engine(board)
            if board.parse_san(nextMove) in board.legal_moves:
                board.push_san(nextMove)
            else:
                return {'status': 'illegal', 'message': 'Illegal engine move'}
            # return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})
            return {'status': 'success', 'board_fen': board.fen()}
        else:
            return {'status': 'illegal', 'message': 'Illegal move'}
    except:
        return {'status': 'invalid', 'message': 'Invalid move format'}

    # except ValueError as e:
    #     return web.json_response({'status': 'invalid', 'message': 'Invalid move format', 'error': str(e)})
    # except Exception as e:
    #     return web.json_response({'status': 'invalid', 'message': 'Invalid move format', 'error': str(e)})

# @app.function()
# @modal.web_endpoint(method="POST", docs=True)
# async def fen(fen: str):
#     try:
#         fen = urllib.parse.unquote(fen)
#         board = chess.Board(fen)
#         nextMove = await engine(board)
#         if board.parse_san(nextMove) in board.legal_moves:
#             board.push_san(nextMove)
#         else:
#             return {'status': 'illegal', 'message': 'Illegal engine move'}
#         # return jsonify({'status': 'success', 'board_svg': chess.svg.board(board)})
#         return {'status': 'success', 'board_fen': board.fen()}
#     except:
#         return {'status': 'invalid', 'message': 'Invalid move format'}

# app = web.Application()
# app.router.add_get('/', index)
# app.router.add_post('/move', move)
# app.router.add_post('/fen', fen)

# if __name__ == "__main__":
#     web.run_app(app)

#if __name__ == "__main__":
    # num_games = 30
    # results = asyncio.run(run_multiple_games(num_games))
    # print(f"Results after {num_games} games:")
    # print(f"White wins: {results['white_wins']}")
    # print(f"Black wins: {results['black_wins']}")
    # print(f"Draws: {results['draws']}")
    #asyncio.run(run_chess_game())
