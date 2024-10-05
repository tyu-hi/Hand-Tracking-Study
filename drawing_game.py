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

# initialize MediaPipe and OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# open a video capture window
cap = cv2.VideoCapture(0)

# set canvas resolution (720p)
canvas_width, canvas_height = 1280, 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, canvas_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, canvas_height)

# initialize a blank image for the drawing canvas
canvas = np.zeros((canvas_height, canvas_width, 3), dtype="uint8")
drawing = False
erasing = False  # track whether the player is in erase mode
prev_x, prev_y = None, None

# game-related variables
players = ['Player1', 'Player2', 'Player3']
scores = {player: 0 for player in players}  # dictionary to track scores for each player
current_drawer = 0  # index of the player who is drawing
word_list = ['cat', 'house', 'car', 'tree', 'dog']  # list of possible words, adjustable
correct_word = choice(word_list)  # choose a random word for the drawer

# function to log messages in the Tkinter text widget
def log_message(message):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, message + '\n')
    log_area.see(tk.END)  # Scroll to the end
    log_area.config(state=tk.DISABLED)

# function to draw on the canvas
def draw_line(canvas, start, end, color=(255, 255, 255), thickness=5):
    cv2.line(canvas, start, end, color, thickness)

# function to update scores
def update_scores():
    score_text = "\n".join([f"{player}: {scores[player]} points" for player in players])
    score_label.config(text=score_text)

# function to change turns
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

# drop-down menu to select guessing player
selected_guesser = tk.StringVar(root)
selected_guesser.set(players[0])  # default to first player

# create a label and drop-down for selecting the guessing player
guess_label = tk.Label(root, text="Select Guessing Player:")
guess_label.pack()

guesser_menu = tk.OptionMenu(root, selected_guesser, *players)
guesser_menu.pack()

# input box for the guess
guess_input_label = tk.Label(root, text="Enter your guess:")
guess_input_label.pack()

guess_entry = tk.Entry(root)
guess_entry.pack()

# score display label
score_label = tk.Label(root, text="", font=("Arial", 14))
score_label.pack()
update_scores()  # initialize score display

# log area to display all game events and logs
log_area = tk.Text(root, height=10, state=tk.DISABLED)
log_area.pack()

def check_guess():
    #gGet the current guess and the guessing player
    guess = guess_entry.get().strip().lower()
    guesser = selected_guesser.get()

    # only allow guessers to guess the word, not the drawer
    if guesser != players[current_drawer]:
        if guess == correct_word.lower():
            log_message(f"{guesser} guessed correctly!")
            scores[guesser] += 1  # increment the score for the guessing player
            next_turn()  # move to the next turn after a correct guess
        else:
            log_message("Wrong guess, try again!")
    else:
        log_message(f"{guesser} is the drawer and can't guess!")

# guess button
guess_button = tk.Button(root, text="Submit Guess", command=check_guess)
guess_button.pack()

def game_loop():
    global prev_x, prev_y, drawing, erasing

    success, frame = cap.read()
    if not success:
        return

    # flip the frame to avoid mirrored movement
    frame = cv2.flip(frame, 1)

    # convert the frame to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # only the current drawer can draw
    if results.multi_hand_landmarks and players[current_drawer] == players[current_drawer]:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip = hand_landmarks.landmark[8]

            # map the index finger tip to screen coordinates
            height, width, _ = frame.shape
            x = int(index_finger_tip.x * width)
            y = int(index_finger_tip.y * height)

            # start drawing or erasing when the index finger is down
            if drawing:
                if prev_x is not None and prev_y is not None:
                    color = (0, 0, 0) if erasing else (255, 255, 255)  # Use black for erasing, white for drawing
                    draw_line(canvas, (prev_x, prev_y), (x, y), color=color, thickness=15 if erasing else 5)
                prev_x, prev_y = x, y

    else:
        prev_x, prev_y = None, None

    # overlay the drawing canvas on the video feed
    combined = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    # display the current word on the screen for the drawing player only
    if players[current_drawer] == players[current_drawer]:
        cv2.putText(combined, f"Word: {correct_word}", (10, canvas_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # show the result
    cv2.imshow('Drawing Game', combined)

    # key press events
    key = cv2.waitKey(1)
    if key == ord('d'):
        drawing = not drawing  # Toggle drawing on/off
    elif key == ord('e'):
        erasing = not erasing  # Toggle erasing on/off
    elif key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        root.quit()

    # run the tkinter guessing window in the background
    root.update_idletasks()
    root.update()

    # call the game loop again
    root.after(10, game_loop)

# start the game loop
game_loop()

# Tkinter main loop
root.mainloop()