from solver.connect4 import Position


def negamax(p: Position) -> int:
    # full board without returning from winning condition (draw)
    if p.get_num_moves() == p.WIDTH * p.HEIGHT:
        return 0  # draw

    # winning move
    for i in range(p.WIDTH):
        if not p.is_col_full(i) and p.is_winning_move(i):
            return (p.WIDTH * p.HEIGHT + 1 - p.get_num_moves()) // 2

    # try all possible moves
    best_score = p.MIN_SCORE
    for i in range(p.WIDTH):
        if not p.is_col_full(i):
            p.play(i)
            score = - negamax(p)
            p.undo()
            if score > best_score:
                best_score = score

    return best_score