# Hand-Tracking-Games

## Project Overview
This project implements hand tracking to control mouse movement and a multiplayer drawing game where players take turns drawing with their hands using OpenCV and MediaPipe. The project allows for real-time detection of hand movements to control a virtual drawing canvas, as well as a guessing game where other players can guess the drawing in real time.

## Features
- Hand Tracking for Mouse Control: Move the mouse cursor by tracking the index finger using a webcam.
- Drawing Mode: Players can use hand gestures to draw on a canvas in real-time, simulating drawing with the mouse.
- Multiplayer Drawing Game: Players take turns drawing while others guess the drawing using a Tkinter-based interface.
- Interactive UI: A Tkinter GUI allows players to manage turns, submit guesses, and view dynamic logs and score updates.

## Technology Stack
- OpenCV: For real-time video capture and frame processing.
- MediaPipe: For hand tracking and gesture detection.
- Tkinter: For the GUI, managing player interactions, guesses, logs, and scorekeeping.

## Prerequisites
Before running the project, ensure you have the following dependencies installed:
1. Python 3.7 or higher
2. Install the required Python libraries:
```
pip install opencv-python mediapipe
```

## How to Run
1. Clone the Repository or download the project files.
2. Open a terminal in the project directory.
3. Run the Python script:
```
python _fileName_.py
```
## Game Modes
1. Hand Tracking for Mouse Control:
   - Use hand gestures (index finger movements) to move the mouse cursor.
   - This feature can be expanded to control external devices or interact with virtual environments.
2. Drawing Game:
   - One player draws while others guess the word.
   - The drawer uses hand movements to draw on a virtual canvas, and guessers submit guesses via a Tkinter input box.
   - Points are awarded for correct guesses, and player scores are dynamically updated on the screen.

## How to Play Drawing Game
- Select the Guessing Player: Use the drop-down menu to select which player is submitting the guess.
- Submit Guess: Enter the guess in the input box and click Submit Guess.
- Switch Turns: When a guess is correct, the game automatically switches to the next player, and the scores are updated.
- Track Scores: The current scores for each player are displayed on the Tkinter window and update dynamically.
### Game Controls
- 'd' Key: Start or stop drawing mode (for the current drawing player).
- 'e' Key: Toggle erasing mode.
- 'n' Key: Pass the turn to the next player after a correct guess.
- 'q' Key: Quit the game.
Demo

## Possible Future Improvements
- Augmented Reality Integration: Expand the project to integrate AR features such as projecting the canvas into a 3D space or using AR glasses.
