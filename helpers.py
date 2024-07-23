import chess
import random
import chess.pgn

piece_values = {
                'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
            }
def hangs(board, move):
    board.push(move)
    last_move = move.to_square
    move_piece = move.drop.symbol()
    for response in list(board.legal_moves):
        if board.is_capture(response):
            captured_piece = response.drop.symbol()
            captured_square = response.to_square
            if last_move == captured_square and piece_values[move_piece] < piece_values[captured_piece]:
                return True
            return False
    board.pop()
    return False

def recapturable(board):
    for response in list(board.legal_moves):
        if board.is_capture(response):
            print("true")
            return True
    print("false")
    return False

def calculate_material(variant: chess.Board):
    fen = variant.fen()
    player = fen.split(' ')[1]

    
    # Define piece values
    piece_values = {
                    'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
                }
    
    # Initialize counters for White and Black material
    white_material = 0
    black_material = 0
    
    # Extract the board layout from the FEN string
    board_layout = fen.split(' ')[0]
    
    # Iterate through the board layout to calculate material
    for char in board_layout:
        if char.isdigit() or char == '/':
            continue
        elif char.isupper():
            white_material += piece_values.get(char, 0)
        elif char.islower():
            black_material += piece_values.get(char, 0)


    return white_material, black_material

def calculate_points(variant: chess.Board, white=True):
    fen = variant.fen()
    player = fen.split(' ')[1]
    if variant.outcome() is not None:
        if variant.is_checkmate() and player == 'b':
            return 1000
        if variant.is_checkmate() and player == 'w':
            return 1000
        else:
            return 0
    
    # Define piece values
    piece_values = {
                'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
            }
    
    # Initialize counters for White and Black material
    white_material = 0
    black_material = 0
    
    # Extract the board layout from the FEN string
    board_layout = fen.split(' ')[0]
    
    # Iterate through the board layout to calculate material
    for char in board_layout:
        if char.isdigit() or char == '/':
            continue
        elif char.isupper():
            white_material += piece_values.get(char, 0)
        elif char.islower():
            black_material += piece_values.get(char, 0)

    ranks = board_layout.split('/')
    # white_material -= 0.3 * (ranks[0].count('N') + ranks[0].count('B'))
    # black_material -= 0.3 * (ranks[7].count('n') + ranks[7].count('b'))
    if black_material < 25:
        white_material -= 0.2 * ranks[0].count('Q')
    if white_material < 25:
        black_material -= 0.2 * ranks[7].count('q') 
    if black_material > 15:
        white_material -= 0.2 * (1 - ranks[0].count('K'))
    if white_material > 15:
        black_material -= 0.2 * (1 - ranks[7].count('k'))
    


    # meh pawn pushing logic
    whitePawn = fen.count('P')
    blackPawn = fen.count('p')
    if white_material < 15:
        white_material += 0.01 * (ranks[5].count('P')) + 0.02 * (ranks[4].count('P')) + 0.03 * (ranks[3].count('P')) + 0.04 * (ranks[2].count('P')) + 0.05 * (ranks[1].count('P'))
    if black_material < 15:
        black_material += 0.01 * (ranks[1].count('p')) + 0.02 * (ranks[2].count('p')) + 0.03 * (ranks[3].count('p')) + 0.04 * (ranks[4].count('p')) + 0.05 * (ranks[5].count('p'))
    

    checked = variant.is_check()
    if checked:
        if player == 'w':
            black_material += 0.1
        elif player == 'b':
            white_material += 0.1

    # if (ranks[4][5] == 'N' and white_material > 25):
    #     white_material += 0.2

  
    
    return white_material - black_material

def calculate_points_color(variant: chess.Board, depth=0, max_depth=4):
    # fen shows the move of the next player
    fen = variant.fen()
    player = fen.split(' ')[1] == 'w'
    if variant.outcome() is not None:
        if variant.is_checkmate(): #  and not player
            return 1000
        # if variant.is_checkmate() and player:
        #     return -1000
        else:
            return 0
        
    if max_depth - depth > 1:
        return 0
    
    # Define piece values
    piece_values = {
                'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
                'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
            }
    
    # Initialize counters for White and Black material
    white_material = 0
    black_material = 0
    
    # Extract the board layout from the FEN string
    board_layout = fen.split(' ')[0]
    
    # Iterate through the board layout to calculate material
    for char in board_layout:
        if char.isdigit() or char == '/':
            continue
        elif char.isupper():
            white_material += piece_values.get(char, 0)
        elif char.islower():
            black_material += piece_values.get(char, 0)
    ranks = board_layout.split('/')
    white_material -= 0.1 * (ranks[7].count('N') + ranks[7].count('B'))
    black_material -= 0.1 * (ranks[0].count('n') + ranks[0].count('b'))
    if black_material < 25:
        white_material -= 0.15 * ranks[7].count('Q')        
    if white_material < 25:
        black_material -= 0.15 * ranks[0].count('q') 

    # print("white", white_material, ranks[0])

    if black_material > 15:
        white_material -= 0.2 * (1 - ranks[7].count('K'))
    if white_material > 15:
        black_material -= 0.2 * (1 - ranks[0].count('k'))
    
    # meh pawn pushing logic
    # whitePawn = fen.count('P')
    # blackPawn = fen.count('p')
    if white_material < 15 or black_material < 15:
        white_material += 0.01 * (ranks[5].count('P')) + 0.02 * (ranks[4].count('P')) + 0.03 * (ranks[3].count('P')) + 0.04 * (ranks[2].count('P')) + 0.05 * (ranks[1].count('P'))
        black_material += 0.01 * (ranks[1].count('p')) + 0.02 * (ranks[2].count('p')) + 0.03 * (ranks[3].count('p')) + 0.04 * (ranks[4].count('p')) + 0.05 * (ranks[5].count('p'))
    
    # reward pieces on the opponent's side of the board after move 10

    # maybe some castling logic, too
    lastchar = ranks[7][-1] if len(ranks[7]) > 0 else None
    secondlastchar = ranks[7][-2] if len(ranks[7]) > 1 else None

    blackLastChar = ranks[0][-1] if len(ranks[7]) > 0 else None
    blackSecondLastChar = ranks[0][-1] if len(ranks[7]) > 0 else None

    # kinda mid logic, needs queenside castling
    if variant.has_castling_rights(chess.WHITE) or (not variant.has_castling_rights(chess.WHITE) and (secondlastchar == 'K') and white_material > 15 and lastchar != 'R'):
        white_material += 0.1
    if variant.has_castling_rights(chess.BLACK) or (not variant.has_castling_rights(chess.BLACK) and (blackSecondLastChar == 'k') and black_material > 15 and blackLastChar != 'r'):
        black_material += 0.1

    # knight on the rim
    N = variant.pieces(chess.KNIGHT, chess.WHITE)
    while len(N) > 0:
        nSquare = N.pop()
        if chess.square_file(nSquare) == 0 or chess.square_file(nSquare) == 7:
            white_material -= 0.05
    N = variant.pieces(chess.KNIGHT, chess.BLACK)
    while len(N) > 0:
        nSquare = N.pop()
        if chess.square_file(nSquare) == 0 or chess.square_file(nSquare) == 7:
            black_material -= 0.05

    # bishop visibility - this is an OK start
    B = variant.pieces(chess.BISHOP, chess.WHITE)
    while len(B) > 0:
        bSquare = B.pop()
        white_material += 0.005 * len(variant.attacks(bSquare))
    
    B = variant.pieces(chess.BISHOP, chess.BLACK)
    while len(B) > 0:
        bSquare = B.pop()
        black_material += 0.005 * len(variant.attacks(bSquare))

    checked = variant.is_check()
    if checked:
        if player:
            black_material += 0.1
        elif not player:
            white_material += 0.1

    # this type of feature might be more generalizeable if we look for the largest hanging piece of both colors
    # if (depth == max_depth):
    #     for move in list(variant.legal_moves):
    #         if variant.is_capture(move):
    #             move.from_square

    stop = False
    piece_types = [
        (chess.QUEEN, 6),
        (chess.ROOK, 3.5),
        (chess.KNIGHT, 2),
        (chess.BISHOP, 2)
    ]
    # for piece_type, material_value in piece_types:
    #     pieces = variant.pieces(piece_type, player)

    # we also don't want to hang checks?

    if (depth == max_depth):
        if not player:
            stop = False
            Q = variant.pieces(chess.QUEEN, chess.WHITE)
            if len(Q) > 0:
                qSquare = Q.pop()
                attackers = variant.attackers(chess.BLACK, qSquare)
                defenders = variant.attackers(chess.WHITE, qSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if (variant.is_legal(chess.Move(attack_square, qSquare)) and variant.piece_type_at(attack_square) is not chess.QUEEN):
                        white_material -= 6
                        stop = True
                    else:
                        if len(defenders) == 0:
                            white_material -= 6
                            stop = True

            R = variant.pieces(chess.ROOK, chess.WHITE)
            while len(R) > 0 and not stop:
                rSquare = R.pop()
                attackers = variant.attackers(chess.BLACK, rSquare)
                defenders = variant.attackers(chess.WHITE, rSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if ((variant.piece_type_at(attack_square) is chess.PAWN or variant.piece_type_at(attack_square) is chess.KNIGHT or variant.piece_type_at(attack_square) is chess.BISHOP) and variant.is_legal(chess.Move(attack_square, rSquare))):
                        white_material -= 3.5
                        stop = True
                    else:
                        if len(defenders) == 0:
                            white_material -= 3.5
                            stop = True

            N = variant.pieces(chess.KNIGHT, chess.WHITE)
            while len(N) > 0 and not stop:
                nSquare = N.pop()
                attackers = variant.attackers(chess.BLACK, nSquare)
                defenders = variant.attackers(chess.WHITE, nSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if (variant.piece_type_at(attack_square) is chess.PAWN and variant.is_legal(chess.Move(attack_square, nSquare))):
                        white_material -= 2
                        stop = True
                    else:
                        if len(defenders) == 0:
                            white_material -= 2
                            stop = True

            B = variant.pieces(chess.BISHOP, chess.WHITE)
            while len(B) > 0 and not stop:
                bSquare = B.pop()
                attackers = variant.attackers(chess.BLACK, bSquare)
                defenders = variant.attackers(chess.WHITE, bSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if (variant.piece_type_at(attack_square) is chess.PAWN and variant.is_legal(chess.Move(attack_square, bSquare))):
                        white_material -= 2
                        stop = True
                    else:
                        if len(defenders) == 0:
                            white_material -= 2
                            stop = True

        if player:
            stop = False
            Q = variant.pieces(chess.QUEEN, chess.BLACK)
            if len(Q) > 0:
                qSquare = Q.pop()
                attackers = variant.attackers(chess.WHITE, qSquare)
                defenders = variant.attackers(chess.BLACK, qSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if (variant.is_legal(chess.Move(attack_square, qSquare)) and variant.piece_type_at(attack_square) is not chess.QUEEN):
                        black_material -= 6
                        stop = True
                    else:
                        if len(defenders) == 0:
                            black_material -= 6
                            stop = True

            R = variant.pieces(chess.ROOK, chess.BLACK)
            while len(R) > 0 and not stop:
                rSquare = R.pop()
                attackers = variant.attackers(chess.WHITE, rSquare)
                defenders = variant.attackers(chess.BLACK, rSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if ((variant.piece_type_at(attack_square) is chess.PAWN or variant.piece_type_at(attack_square) is chess.KNIGHT or variant.piece_type_at(attack_square) is chess.BISHOP) and variant.is_legal(chess.Move(attack_square, rSquare))):
                        black_material -= 3.5
                        stop = True
                    else:
                        if len(defenders) == 0:
                            black_material -= 3.5
                            stop = True

            N = variant.pieces(chess.KNIGHT, chess.BLACK)
            while len(N) > 0 and not stop:
                nSquare = N.pop()
                attackers = variant.attackers(chess.WHITE, nSquare)
                defenders = variant.attackers(chess.BLACK, nSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if (variant.piece_type_at(attack_square) is chess.PAWN and variant.is_legal(chess.Move(attack_square, nSquare))):
                        black_material -= 2
                        stop = True
                    else:
                        if len(defenders) == 0:
                            black_material -= 2
                            stop = True
            B = variant.pieces(chess.BISHOP, chess.BLACK)
            while len(B) > 0 and not stop:
                bSquare = B.pop()
                attackers = variant.attackers(chess.WHITE, bSquare)
                defenders = variant.attackers(chess.BLACK, bSquare)
                while len(attackers) > 0 and not stop:
                    attack_square = attackers.pop()
                    if (variant.piece_type_at(attack_square) is chess.PAWN and variant.is_legal(chess.Move(attack_square, bSquare))):
                        black_material -= 2
                        stop = True
                    else:
                        if len(defenders) == 0:
                            black_material -= 2
                            stop = True

    # if (ranks[4][5] == 'N' and white_material > 25):
    #     white_material += 0.2
    
    return (white_material - black_material) * (1 if not player else -1)

def play_all_moves(game_node, board):
    MAX_VARIATIONS = 9
    VAR_COUNT = 0
    # for move in list(board.legal_moves):
    #     check = board.gives_check(move)
    #     capture = board.is_capture(move)
    #     if (VAR_COUNT > MAX_VARIATIONS and not check and move.promotion is not None and not capture):
    #         continue
    #     else:
    #         board.push(move)
    #         material = calculate_points(board)
    #         if not game.has_variation(move):
    #             game.add_variation(move, comment=str(material))
    #         board.pop()
    #         VAR_COUNT += 1
        
    # if (VAR_COUNT == 0):
    #     return game
    # return game
    if not game_node.variations:
        for move in list(board.legal_moves):
            check = board.gives_check(move)
            capture = board.is_capture(move)
            if (VAR_COUNT > MAX_VARIATIONS and not check and move.promotion is None and not capture):
                continue
            else:
                branchBoard = board.copy()
                branchBoard.push(move)
                material = calculate_points(branchBoard)
                game_node.add_variation(move, comment=str(material))
                VAR_COUNT += 1
    else:
        # Traverse existing variations
        for variation in game_node.variations:
            branchBoard = board.copy()
            branchBoard.push(variation.move)
            play_all_moves(variation, branchBoard)

    return game_node

# rewards:
# pieces over midline
# rooks on 7th
# knight on f5
# giving a check
# developed pieces

# look at the best move for black a step back, then find the best move for white on the next step

# fastest win against random move
def evaluate_variations(node, player, highest_eval, best_variation, best_parent):
    for variation in node.variations:
        eval_comment = variation.comment
        try:
            eval_value = float(eval_comment)
        except ValueError:
            continue

        if (player == 'w' and eval_value > highest_eval) or (player == 'b' and eval_value < highest_eval):
            highest_eval = eval_value
            best_variation = variation
            best_parent = node

        sub_eval, sub_variation, sub_parent = evaluate_variations(variation, player, highest_eval, best_variation, best_parent)
        
        if (player == 'w' and sub_eval > highest_eval) or (player == 'b' and sub_eval < highest_eval):
            highest_eval = sub_eval
            best_variation = sub_variation
            best_parent = sub_parent
    
    return highest_eval, best_variation, best_parent


def choose_move(board):
    game = chess.pgn.Game()
    game.setup(board)
    player = board.turn
    current_node = game.add_variation(chess.Move.null())
    current_node.board().set_fen(board.fen())
    
    # Generate variations from the current position
    play_all_moves(current_node, board)

    MOVE_DEPTH = 4
    current_depth = 0
    # while current_depth < MOVE_DEPTH:
    # game = play_all_moves(game, board)
        # if len(new_boards) < 5000 and current_depth == MOVE_DEPTH - 1:
        #     MOVE_DEPTH += 1

        # print("Depth level", current_depth+1, "with", len(new_boards), "new boards")
        # current_depth += 1

    print("game", current_node)

    highest_eval = float('-inf') if player == 'w' else float('inf')
    best_variation = None
    best_parent = None
    highest_eval, best_variation, best_parent = evaluate_variations(current_node, player, highest_eval, best_variation, best_parent)

    if best_variation and best_parent:
        best_parent.variations.remove(best_variation)
        best_parent.add_main_variation(best_variation.move, comment=best_variation.comment)
        print("best variation", best_variation)
        return best_variation.move
    
    return None

    max_variant = float('-inf') if player == 'w' else float('inf')
    best_board = all_boards[0][0]
    better_white = []
    better_black = []
    for board, material in all_boards:
        diff = material
        if diff > 0:
            better_white.append(board)
        elif diff < 0:
            better_black.append(board)
        if max_variant < diff:
            print("changing")
            max_variant = diff
            best_board = board
    print("best board", best_board)
    original_turn = board.fullmove_number

    for variant in better_white:
        while (variant.fullmove_number > original_turn):
            variant.pop()

    # weight = current_depth * weighted avg of diffs
    
    # better_moves = [board.copy() for _ in range(len(better_white))]
    # for i in range(0, len(better_white)):
    #     better_moves[i].push(better_white[i][0].pop())
    
    # backprop = []
    # for i in range(0, 1):
    #     new_boards = []
    #     for line in better_moves:
    #         new_boards.extend(play_all_moves(line))
    #     better_moves = new_boards  
    #     backprop.extend(new_boards)  
    #     print("Depth level", i+1, "with", len(new_boards), "new boards")

    # best_retort = 0
    # best_board = backprop[0]
    # for variant in backprop:
    #     diff = variant[1]
    #     if best_retort < diff:
    #         best_retort = diff
    #         best_board = variant
        
    while (best_board.fullmove_number > original_turn):
        best_board.pop()
    # best_moves = list(best_board.legal_moves)
    
    return best_board.pop()
