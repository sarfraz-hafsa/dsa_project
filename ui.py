import pygame
import sys
import copy
import random

import numpy as np
from constants import *
from datastructures import Stack,Queue
from PIL import Image
from itertools import cycle
import time

pygame.mixer.init()




def draw_grid(gameinstance):
        # Draw grid lines
        for row in range(10):
            line_width = 2 if row % 3 == 0 else 1
            pygame.draw.line(
                gameinstance.screen, BLACK, (50, 50 + row * 50), (500, 50 + row * 50), line_width
            )
            pygame.draw.line(
                gameinstance.screen, BLACK, (50 + row * 50, 50), (50 + row * 50, 500), line_width
            )

        # Fill in cells
        for row in range(9):
            for col in range(9):
                value = gameinstance.grid[row][col]
                if value != 0:
                    color = BLACK if (row, col) in gameinstance.fixed_cells else RED
                    text = FONT.render(str(value), True, color)
                    gameinstance.screen.blit(text, (65 + col * 50, 55 + row * 50))

        # Highlight selected cell
        if gameinstance.selected_cell:
            row, col = gameinstance.selected_cell
            pygame.draw.rect(
                gameinstance.screen, BLUE, (50 + col * 50, 50 + row * 50, 50, 50), 3
            )

def draw_top_bar(gameinstance):
        # Difficulty label
        difficulty_label = SMALL_FONT.render(f"Difficulty: {gameinstance.difficulty}", True, BLACK)
        gameinstance.screen.blit(difficulty_label, (50, 10))

        # Timer label
        minutes = gameinstance.timer // 60
        seconds = gameinstance.timer % 60
        timer_label = SMALL_FONT.render(f"Timer: {minutes:02}:{seconds:02}", True, BLACK)
        gameinstance.screen.blit(timer_label, (400, 10))

        # Mistake tracker
                # Mistake tracker
        mistake_label = SMALL_FONT.render(f"Mistakes: {gameinstance.mistakes}/{gameinstance.max_mistakes}", True, BLACK)
        gameinstance.screen.blit(mistake_label, (230, 10))
    




def load_gif_frames_with_durations(gif_path):
    """
    Loads GIF frames and their durations into a list of pygame Surfaces.
    """
    gif = Image.open(gif_path)
    frames = []
    durations = []

    try:
        while True:
            # Convert each frame to RGBA for pygame compatibility
            frame = gif.convert("RGBA")
            pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
            frames.append(pygame_frame)

            # Get frame duration in milliseconds
            duration = gif.info.get("duration", 100)  # Default to 100ms if duration not provided
            durations.append(duration)

            gif.seek(gif.tell() + 1)  # Move to the next frame
    except EOFError:
        pass  # End of GIF

    return frames, durations


def draw_welcome_screen(gameinstance):
    # Load GIF frames and durations
    gif_path = "E:\\Rana Shoaib\\Hafsa\\suduko-split\\Sudoku-Day_feature.gif"  # Replace with the path to your GIF
    if not hasattr(gameinstance, "gif_data"):
        frames, durations = load_gif_frames_with_durations(gif_path)
        gameinstance.gif_data = {
            "frames": frames,
            "durations": durations,
            "current_frame_index": 0,
            "last_update_time": time.time(),
        }

        music_path = "E:\\Rana Shoaib\\Hafsa\\suduko-split\\Sunset-Landscape(chosic.com).mp3"  # Replace with your music file path
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    gif_data = gameinstance.gif_data
    current_time = time.time()
    frame_index = gif_data["current_frame_index"]

    # Check if it's time to update the frame
    if current_time - gif_data["last_update_time"] > gif_data["durations"][frame_index] / 1000:
        gif_data["current_frame_index"] = (frame_index + 1) % len(gif_data["frames"])
        gif_data["last_update_time"] = current_time

    # Get the current frame
    current_frame = gif_data["frames"][gif_data["current_frame_index"]]

    # Scale the frame to fit the screen
    gif_surface = pygame.transform.scale(current_frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    gameinstance.screen.blit(gif_surface, (0, 0))

    # Add title and instructions
    title = BIG_FONT.render("Welcome to Sudoku", True, (0, 0, 0))  # Black text
    gameinstance.screen.blit(title, (60,60))
    instruction = SMALL_FONT.render("Press any key to continue", True, (128, 128, 128))  # Gray text
    gameinstance.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 650))





def draw_menu_screen(gameinstance):
        gameinstance.screen.fill(LIGHT)
        title = BIG_FONT.render("Sudoku,", True, BLACK)
        gameinstance.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        instruction = FONT.render("Try this numbers game,minus the math.", True, (0, 0, 0))  # Gray text
        gameinstance.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 200 ))


        buttons = {
            "Easy": pygame.Rect(200, 300, 200, 50),
            "Medium": pygame.Rect(200, 400, 200, 50),
            "Hard": pygame.Rect(200, 500, 200, 50),
        }

        for label, rect in buttons.items():
            pygame.draw.rect(gameinstance.screen, BLACK, rect)
            text = SMALL_FONT.render(label, True, GRAY)
            gameinstance.screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2, rect.y + 10))

        gameinstance.menu_buttons = buttons



def handle_menu_click(gameinstance, pos):
        for label, rect in gameinstance.menu_buttons.items():
            if rect.collidepoint(pos):
                gameinstance.difficulty = label
                gameinstance.start_new_game()
                gameinstance.state = "game"

def draw_game_screen(gameinstance):
        gameinstance.screen.fill(LIGHT)
        draw_grid(gameinstance)
        draw_top_bar(gameinstance)

        for key, rect in gameinstance.buttons.items():
            pygame.draw.rect(gameinstance.screen, BLACK, rect)
            label = SMALL_FONT.render(key.capitalize(), True, GRAY)
            gameinstance.screen.blit(label, (rect.x + (rect.width - label.get_width()) // 2, rect.y + 10))

def update_timer(gameinstance):
        """
        Updates the game timer.
        """
    
        gameinstance.timer += 1

def display_end_message(gameinstance):
        """
        Displays a message at the end of the game.
        """
        gameinstance.screen.fill(WHITE)
        if gameinstance.mistakes >= gameinstance.max_mistakes:
            message = "Game Over! Too many mistakes."
        else:
            message = f"Congratulations! Your score: {gameinstance.score}"

        label = FONT.render(message, True, RED)
        gameinstance.screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        # Wait for 3 seconds before quitting
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()
    

        pygame.quit()
        sys.exit()