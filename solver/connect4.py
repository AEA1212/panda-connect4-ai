import matplotlib.pyplot as plt


class Position:
    WIDTH = 7
    HEIGHT = 6

    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3
    MIN_SCORE = - MAX_SCORE

    def __init__(self):
        # board[col][row]: 0 empty, 1 first player, 2 second player (row 0 = bottom)
        self.board = [[0 for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
        self.cols_height = [0] * self.WIDTH
        self.num_moves = 0
        self.history = []  # (col, row) of each move, in play order

    def is_col_full(self, col: int) -> bool:
        return self.cols_height[col] >= self.HEIGHT

    def get_num_moves(self) -> int:
        return self.num_moves

    def play(self, col: int) -> None:
        if not self.is_col_full(col):
            self.board[col][self.cols_height[col]] = 1 + self.num_moves % 2
            self.history.append((col, self.cols_height[col]))
            self.cols_height[col] += 1
            self.num_moves += 1
        else:
            raise ValueError(f"Invalid move, col {col} is full.")

    def undo(self) -> None:
        if len(self.history) and self.get_num_moves() > 0:
            col, row = self.history.pop()
            self.board[col][row] = 0
            self.cols_height[col] -= 1
            self.num_moves -= 1
        else:
            raise ValueError(f"Invalid undo, num_moves <= 0 or history is empty.")

    def is_winning_move(self, col: int) -> bool:
        player = 1 + self.num_moves % 2
        row = self.cols_height[col]

        # vertical
        if row >= 3 and all(self.board[col][row - k] == player for k in (1, 2, 3)):
            return True

        # horizontal (dy=0) and the two diagonals (dy=-1, dy=1)
        for dy in (-1, 0, 1):
            nb = 0  # aligned stones of the current player around dy
            for dx in (-1, 1):  # continue counting for different dx directions, reset only for dy
                x, y = col + dx, row + dx * dy
                while 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT and self.board[x][y] == player:
                    x += dx
                    y += dx * dy
                    nb += 1
            if nb >= 3:
                return True
        return False

    def sequence_encode(self, seq: str) -> int:
        for i, ch in enumerate(seq):
            col = ord(ch) - ord("1")

            if col < 0 or col >= self.WIDTH:
                raise ValueError(f"Out of range (i = {i}), col {col} is invalid.")
            elif self.is_col_full(col):
                raise ValueError(f"col full (i = {i}),col {col} is already full.")
            elif self.is_winning_move(col):
                raise ValueError(f"Winning move (i = {i}), This move is the winning move -> no score.")

            self.play(col)
        return len(seq)

    def __str__(self) -> str:
        symbols = {0: ".", 1: "X", 2: "O"}
        rows = []
        for y in reversed(range(self.HEIGHT)):
            row_y = [chr(ord("A") + y)] + [symbols[self.board[x][y]] for x in range(self.WIDTH)]
            row_y_str = " ".join(row_y)
            rows.append(row_y_str)

        index_row = " ".join([" "] + [str(x + 1) for x in range(self.WIDTH)])
        rows.append(index_row)
        board_str = "\n".join(rows)
        return board_str

    def show(self) -> None:
        colors = {0: "white", 1: "red", 2: "gold"}
        plt.gca().set_facecolor("blue")
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                plt.scatter(x, y, s=1800, c=colors[self.board[x][y]])
        for i, (x, y) in enumerate(self.history):
            plt.text(x, y, i + 1, ha="center", va="center")
        plt.xlim(-0.6, self.WIDTH - 0.4)
        plt.ylim(-0.6, self.HEIGHT - 0.4)
        plt.gca().set_aspect("equal")
        plt.xticks(range(self.WIDTH), [str(x + 1) for x in range(self.WIDTH)])
        plt.yticks(range(self.HEIGHT), [chr(ord("A") + y) for y in range(self.HEIGHT)])
        plt.tight_layout()
        plt.show()


# pos = Position()
# pos.sequence_encode("112211221122556655665566")
# pos.show()
