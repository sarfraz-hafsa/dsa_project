import pygame
import sys
import copy
import random
from collections import deque
import numpy as np
from constants import *
from datastructures import Stack,Queue
from ui import draw_game_screen,draw_menu_screen,draw_welcome_screen,handle_menu_click,update_timer,display_end_message







class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sudoku Game")

        self.adj_matrix = np.zeros((81, 81), dtype=int)

        self.state = "welcome"  # Possible states: welcome, menu, game
        self.difficulty = "Easy"
        self.base_grid = None
        self.grid = None
        self.fixed_cells = []
        self.selected_cell = None
        self.running = True
        self.undo_stack=Stack()

        # Hint queue
        self.hint_queue = Queue()

        # Mistake tracker
        self.mistakes = 0
        self.max_mistakes = 3

        # Score system
        self.score = 0

        # Game-specific buttons
        self.buttons = {
            "end game":pygame.Rect(400, 520, 100, 50),
            "auto":pygame.Rect(100, 520, 100, 50),
            "undo": pygame.Rect(50, 620, 100, 50),
            "erase": pygame.Rect(200, 620, 100, 50),
            "new_game": pygame.Rect(350, 620, 100, 50),
            "back": pygame.Rect(500, 620, 100, 50),
        }
        self.timer = 0
        self.clock = pygame.time.Clock()

        # Initialize graph
        self.build_graph_with_matrix()

    def build_graph_with_matrix(self):
        def cell_index(row, col):
            return row * 9 + col

        for row in range(9):
            for col in range(9):
                node = cell_index(row, col)

                # Add row connections
                for c in range(9):
                    if c != col:
                        neighbor = cell_index(row, c)
                        self.adj_matrix[node][neighbor] = 1

                # Add column connections
                for r in range(9):
                    if r != row:
                        neighbor = cell_index(r, col)
                        self.adj_matrix[node][neighbor] = 1

                # Add subgrid connections
                start_row, start_col = 3 * (row // 3), 3 * (col // 3)
                for r in range(start_row, start_row + 3):
                    for c in range(start_col, start_col + 3):
                        if (r, c) != (row, col):
                            neighbor = cell_index(r, c)
                            self.adj_matrix[node][neighbor] = 1

    def is_valid_move(self, row, col, value, grid):
        node = row * 9 + col
        for neighbor in range(81):
            if self.adj_matrix[node][neighbor] == 1:
                r, c = divmod(neighbor, 9)
                if grid[r][c] == value:
                    return False
        return True

    def generate_full_solution(self, grid):
        empty_cell = self.find_empty(grid)
        if not empty_cell:
            return True  # Solved
        row, col = empty_cell

        for num in range(1, 10):
            if self.is_valid_move(row, col, num, grid):
                grid[row][col] = num
                if self.generate_full_solution(grid):
                    return True
                grid[row][col] = 0

        return False

    def find_empty(self, grid):
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    return row, col
        return None

    def remove_numbers_from_grid(self, grid, difficulty):
        removed_count = {"Easy": 30, "Medium": 45, "Hard": 60}[difficulty]
        puzzle = copy.deepcopy(grid)

        while removed_count > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if puzzle[row][col] != 0:
                puzzle[row][col] = 0
                removed_count -= 1

        return puzzle

    def generate_puzzle(self, difficulty):
        grid = [[0] * 9 for _ in range(9)]
        self.generate_full_solution(grid)
        return self.remove_numbers_from_grid(grid, difficulty)

    def start_new_game(self):
        self.base_grid = self.generate_puzzle(self.difficulty)
        self.grid = copy.deepcopy(self.base_grid)
        self.fixed_cells = [
            (r, c) for r in range(9) for c in range(9) if self.base_grid[r][c] != 0
        ]
        self.selected_cell = None
        self.undo_stack.clear()
        self.mistakes = 0
        self.score = 0
        self.timer = 0
        self.generate_hints()

    def generate_hints(self):
        self.hint_queue.clear()
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    for value in range(1, 10):
                        if self.is_valid_move(row, col, value, self.grid):
                            self.hint_queue.enqueue((row, col, value))

    def provide_hint(self):
        if self.hint_queue:
            row, col, value = self.hint_queue.dequeue()
            self.undo_stack.push(copy.deepcopy(self.grid))
            self.grid[row][col] = value
        else:
            print("No hints available!")

    def handle_cell_selection(self, pos):
        """
        Handles cell selection based on mouse position.
        """
        x, y = pos
        if 50 <= x <= 500 and 50 <= y <= 500:
            col = (x - 50) // 50
            row = (y - 50) // 50
            if (row, col) not in self.fixed_cells:
                self.selected_cell = (row, col)
            else:
                self.selected_cell = None
    def handle_button_click(self, pos):
        """
        Handles button clicks for undo, erase, hint, and new game actions.
        """
        for key, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if key == "undo" and self.undo_stack:
                    self.grid = self.undo_stack.pop()
                elif key == "erase" and self.selected_cell:
                    row, col = self.selected_cell
                    if (row, col) not in self.fixed_cells:
                        self.undo_stack.push(copy.deepcopy(self.grid))
                        self.grid[row][col] = 0
                elif key == "hint":
                    self.provide_hint()
                elif key == "new_game":
                    self.start_new_game()
                elif key == "auto":
                    self.generate_full_solution(self.grid)  
                elif key == "end game":
                    display_end_message(self)      
                elif key == "back":
                    self.state= "menu"    
                

    def handle_key_input(self, event):
        """
        Handles number input for the selected cell.
        """
        if self.selected_cell and event.unicode.isdigit():
            value = int(event.unicode)
            if 1 <= value <= 9:
                row, col = self.selected_cell
                if self.is_valid_move(row, col, value, self.grid):  
                    self.undo_stack.push(copy.deepcopy(self.grid))
                    self.grid[row][col] = value
                    self.generate_hints()
                    self.score += 10
                else:
                    self.mistakes += 1
                    if self.mistakes >= self.max_mistakes:
                        print("Game Over!")
                        self.running = False


    def run(self):
        while self.running:
            if self.state == "welcome":
                draw_welcome_screen(self)
            elif self.state == "menu":
               draw_menu_screen(self)
            elif self.state == "game":
               draw_game_screen(self)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == "welcome" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.state = "menu"
                elif self.state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
                   handle_menu_click(self,event.pos)
                elif self.state == "game":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if 50 <= event.pos[0] <= 500 and 50 <= event.pos[1] <= 500:
                           self.handle_cell_selection(event.pos)
                        elif event.button == 1:
                           self.handle_button_click(event.pos)
                    elif event.type == pygame.KEYDOWN:
                        self.handle_key_input(event)
            update_timer(self)
            pygame.display.flip()
            self.clock.tick(60)
        display_end_message(self)



# if __name__ == "__main__":
#     game = SudokuGame()
#     game.run()