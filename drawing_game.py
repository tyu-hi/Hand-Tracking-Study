import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from random import choice

# Run program with python drawing_game.py
"""
## How to Play ##
User your index finger to draw. Logs (i.e correct answers) will show up in terminal.
To draw, press on the camera screen, then press:
'd': Start or stop drawing using hand tracking.
'n': Switch to the next player's turn.
'e': Erase drawing.
'q': Quit the game.
Popup Window: Use the text box to input your guesses, and hit "Submit Guess" to see if it's correct.
"""

# Initialize MediaPipe and OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Open a video capture window
cap = cv2.VideoCapture(0)

# Set canvas resolution (720p)
canvas_width, canvas_height = 1280, 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, canvas_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, canvas_height)

# Initialize a blank image for the drawing canvas
canvas = np.zeros((canvas_height, canvas_width, 3), dtype="uint8")
drawing = False
erasing = False  # Track whether the player is in erase mode
prev_x, prev_y = None, None

# Game-related variables
players = ['Player1', 'Player2', 'Player3']
scores = {player: 0 for player in players}  # Dictionary to track scores for each player
current_drawer = 0  # Index of the player who is drawing
word_list = ['cat', 'house', 'car', 'tree', 'dog']  # List of possible words
correct_word = choice(word_list)  # Choose a random word for the drawer

# Function to log messages in the Tkinter text widget
def log_message(message):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, message + '\n')
    log_area.see(tk.END)  # Scroll to the end
    log_area.config(state=tk.DISABLED)

# Function to draw on the canvas
def draw_line(canvas, start, end, color=(255, 255, 255), thickness=5):
    cv2.line(canvas, start, end, color, thickness)

# Function to update scores
def update_scores():
    score_text = "\n".join([f"{player}: {scores[player]} points" for player in players])
    score_label.config(text=score_text)

# Function to change turns
def next_turn():
    global current_drawer, correct_word, canvas
    current_drawer = (current_drawer + 1) % len(players)
    log_message(f"{players[current_drawer]}'s turn to draw!")
    correct_word = choice(word_list)  # Assign a new word to the next drawer
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype="uint8")  # Clear the canvas for the next player
    update_scores()  # Update scores on the Tkinter window

# Tkinter window for guessing and displaying logs
root = tk.Tk()
root.title("Drawing Game")

# Drop-down menu to select guessing player
selected_guesser = tk.StringVar(root)
selected_guesser.set(players[0])  # Default to first player

# Create a label and drop-down for selecting the guessing player
guess_label = tk.Label(root, text="Select Guessing Player:")
guess_label.pack()

guesser_menu = tk.OptionMenu(root, selected_guesser, *players)
guesser_menu.pack()

# Input box for the guess
guess_input_label = tk.Label(root, text="Enter your guess:")
guess_input_label.pack()

guess_entry = tk.Entry(root)
guess_entry.pack()

# Score display label
score_label = tk.Label(root, text="", font=("Arial", 14))
score_label.pack()
update_scores()  # Initialize score display

# Log area to display all game events and logs
log_area = tk.Text(root, height=10, state=tk.DISABLED)
log_area.pack()

def check_guess():
    # Get the current guess and the guessing player
    guess = guess_entry.get().strip().lower()
    guesser = selected_guesser.get()

    # Only allow guessers to guess the word, not the drawer
    if guesser != players[current_drawer]:
        if guess == correct_word.lower():
            log_message(f"{guesser} guessed correctly!")
            scores[guesser] += 1  # Increment the score for the guessing player
            next_turn()  # Move to the next turn after a correct guess
        else:
            log_message("Wrong guess, try again!")
    else:
        log_message(f"{guesser} is the drawer and can't guess!")

# Guess button
guess_button = tk.Button(root, text="Submit Guess", command=check_guess)
guess_button.pack()

def game_loop():
    global prev_x, prev_y, drawing, erasing

    success, frame = cap.read()
    if not success:
        return

    # Flip the frame to avoid mirrored movement
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Only the current drawer can draw
    if results.multi_hand_landmarks and players[current_drawer] == players[current_drawer]:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip = hand_landmarks.landmark[8]

            # Map the index finger tip to screen coordinates
            height, width, _ = frame.shape
            x = int(index_finger_tip.x * width)
            y = int(index_finger_tip.y * height)

            # Start drawing or erasing when the index finger is down
            if drawing:
                if prev_x is not None and prev_y is not None:
                    color = (0, 0, 0) if erasing else (255, 255, 255)  # Use black for erasing, white for drawing
                    draw_line(canvas, (prev_x, prev_y), (x, y), color=color, thickness=15 if erasing else 5)
                prev_x, prev_y = x, y

    else:
        prev_x, prev_y = None, None

    # Overlay the drawing canvas on the video feed
    combined = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    # Display the current word on the screen for the drawing player only
    if players[current_drawer] == players[current_drawer]:
        cv2.putText(combined, f"Word: {correct_word}", (10, canvas_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Show the result
    cv2.imshow('Drawing Game', combined)

    # Key press events: 'd' to start drawing, 'e' to erase, 'q' to quit
    key = cv2.waitKey(1)
    if key == ord('d'):
        drawing = not drawing  # Toggle drawing on/off
    elif key == ord('e'):
        erasing = not erasing  # Toggle erasing on/off
    elif key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        root.quit()

    # Run the tkinter guessing window in the background
    root.update_idletasks()
    root.update()

    # Call the game loop again
    root.after(10, game_loop)

# Start the game loop
game_loop()

# Tkinter main loop
root.mainloop()