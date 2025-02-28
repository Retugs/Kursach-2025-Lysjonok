import sys
import random
from PySide6.QtWidgets import (QApplication, QWidget,QGridLayout, QLabel)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent


class W1djet(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.start_game()

    def init_ui(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.setLayout(self.grid)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.cells = []
        self.board = [[0] * 4 for _ in range(4)]

        # Создаем ячейки для отображения
        for i in range(4):
            row = []
            for j in range(4):
                label = QLabel()
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setMinimumSize(QSize(80, 80))
                self.update_cell_style(label, 0)
                self.grid.addWidget(label, i, j)
                row.append(label)
            self.cells.append(row)

    def start_game(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.add_new_tile()
        self.add_new_tile()
        self.update_ui()

    def update_cell_style(self, label, value):
        colors = {
            0: ("#cdc1b4", ""),
            2: ("#eee4da", "2"),
            4: ("#ede0c8", "4"),
            8: ("#f2b179", "8"),
            16: ("#f59563", "16"),
            32: ("#f67c5f", "32"),
            64: ("#f65e3b", "64"),
            128: ("#edcf72", "128"),
            256: ("#edcc61", "256"),
            512: ("#edc850", "512"),
            1024: ("#edc53f", "1024"),
            2048: ("#edc22e", "2048")
        }
        color, text = colors.get(value, ("#3c3a32", str(value)))
        label.setText(text)
        label.setStyleSheet(f"""
            font-size: {24 if value < 1000 else 18}px; 
            font-weight: bold; 
            background-color: {color}; 
            border-radius: 5px;
            color: {'#776e65' if value < 8 else '#f9f6f2'};
        """)

    def add_new_tile(self):
        empty_cells = [(i, j)
                       for i in range(4)
                       for j in range(4)
                       if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
            self.update_ui()

    def update_ui(self):
        for i in range(4):
            for j in range(4):
                self.update_cell_style(self.cells[i][j], self.board[i][j])

    def compress(self, row):
        new_row = [num for num in row if num != 0]
        new_row += [0] * (4 - len(new_row))
        return new_row

    def merge(self, row):
        score = 0
        for j in range(3):
            if row[j] == row[j + 1] and row[j] != 0:
                row[j] *= 2
                score += row[j]
                row[j + 1] = 0
        return row, score

    def move_row_left(self, row):
        compressed = self.compress(row)
        merged, score = self.merge(compressed)
        compressed = self.compress(merged)
        return compressed, score

    def move_left(self):
        new_board = []
        total_score = 0
        moved = False
        for row in self.board:
            new_row, score = self.move_row_left(row)
            new_board.append(new_row)
            total_score += score
            if row != new_row:  # Проверяем, изменилась ли строка
                moved = True
        if moved:
            self.board = new_board  # Обновляем доску
        return moved, total_score

    def move_right(self):
        new_board = []
        total_score = 0
        moved = False
        for row in self.board:
            reversed_row = list(reversed(row))
            new_row, score = self.move_row_left(reversed_row)
            new_row = list(reversed(new_row))
            new_board.append(new_row)
            total_score += score
            if row != new_row:  # Проверяем, изменилась ли строка
                moved = True
        if moved:
            self.board = new_board  # Обновляем доску
        return moved, total_score

    def move_up(self):
        total_score = 0
        moved = False
        transposed = list(zip(*self.board))
        new_transposed = []
        for row in transposed:
            new_row, score = self.move_row_left(list(row))
            new_transposed.append(new_row)
            total_score += score
        if transposed != new_transposed:
            moved = True
        self.board = list(zip(*new_transposed))
        self.board = [list(row) for row in self.board]
        return moved, total_score

    def move_down(self):
        total_score = 0
        moved = False
        transposed = list(zip(*self.board))
        reversed_transposed = [list(reversed(row)) for row in transposed]
        new_transposed = []
        for row in reversed_transposed:
            new_row, score = self.move_row_left(row)
            new_transposed.append(list(reversed(new_row)))
            total_score += score
        if reversed_transposed != new_transposed:
            moved = True
        self.board = list(zip(*new_transposed))
        self.board = [list(row) for row in self.board]
        return moved, total_score

    def is_game_over(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return False
                if i < 3 and self.board[i][j] == self.board[i + 1][j]:
                    return False
                if j < 3 and self.board[i][j] == self.board[i][j + 1]:
                    return False
        return True

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        moved = False
        score = 0

        if key == Qt.Key.Key_Left:
            moved, score = self.move_left()
        elif key == Qt.Key.Key_Right:
            moved, score = self.move_right()
        elif key == Qt.Key.Key_Up:
            moved, score = self.move_up()
        elif key == Qt.Key.Key_Down:
            moved, score = self.move_down()
        else:
            super().keyPressEvent(event)

        if moved:
            self.add_new_tile()
            if self.is_game_over():
                print("Game Over!")
            self.update_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = W1djet()
    game.setWindowTitle("2048")
    game.resize(400, 400)
    game.show()
    sys.exit(app.exec())