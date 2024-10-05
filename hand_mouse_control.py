import cv2
import mediapipe as mp # using mediapipe library for handtracking
import pyautogui
import math
import threading # introduce multithraeding to run hand tracking and clicking recongition asyncrhously

# Run program with python hand_mouse_control.py
# "landmarks" go from 0-10, starting from wrist and moving to each joing from thumb first pinky finger
# index_finger is landmark[8]
# To simulate clicking, track distance between landmarks

"""
## How to Use ##
The cursor follows the hand's index finger. 
To left-click, pinch the index finger and thumb togther.
To right-click, pinch the index finger and middle finger togther.
"""
# initialize MediaPipe hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, 
    model_complexity=0,  # Use less complex hand tracking model for faster performance
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# get screen size
screen_width, screen_height = pyautogui.size()

# initialize previous position variables for smoother movement
prev_x, prev_y = screen_width // 2, screen_height // 2  # start from the center of the screen
smoothing_factor = 0.3  # adjust this for more or less smoothing
                        # a higher value (like 0.3) will make the mouse move more quickly, while a lower value (like 0.1) will make it move more slowly but smoothly.

# start video capture
cap = cv2.VideoCapture(0)
# function to calculate the Euclidean distance between two points
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# function for linear interpolation between two points
def lerp(start, end, smoothing_factor):
    return start + smoothing_factor * (end - start)


# multithreading
def process_frame():
    global img_rgb, result
    while True:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

# Run the hand tracking in a separate thread
threading.Thread(target=process_frame, daemon=True).start()

while True:
    success, img = cap.read()
    if not success:
        break
    
    # reduce image size for faster processing
    # img = cv2.resize(img, (640, 480))  # adjust the size according to needs
    
    # convert image color to RGB as required by MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    
    # if hand landmarks are detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # get the coordinates of the index fingertip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]
            middle_finger_tip = hand_landmarks.landmark[12]
            
            # map the hand coordinates to screen coordinates
            screen_x = screen_width - int(screen_width * index_finger_tip.x)  # invert X-axis
            screen_y = int(screen_height * index_finger_tip.y)

            # map the hand coordinates to screen coordinates
            target_x = screen_width - int(screen_width * index_finger_tip.x)  # invert X-axis
            target_y = int(screen_height * index_finger_tip.y)  
            
            # smooth the movement with linear interpolation
            smooth_x = int(lerp(prev_x, target_x, smoothing_factor))
            smooth_y = int(lerp(prev_y, target_y, smoothing_factor))

            # move the mouse cursor to the smoothed position
            pyautogui.moveTo(smooth_x, smooth_y)

            # Update previous position
            prev_x, prev_y = smooth_x, smooth_y

            # calculate distances between thumb and index, and thumb and middle finger
            thumb_index_distance = calculate_distance(
                thumb_tip.x, thumb_tip.y,
                index_finger_tip.x, index_finger_tip.y
            )

            thumb_middle_distance = calculate_distance(
                thumb_tip.x, thumb_tip.y,
                middle_finger_tip.x, middle_finger_tip.y
            )

            # simulate left-click if thumb is close to index fingertip
            if thumb_index_distance < 0.08: # adjust to change speed of click response
                pyautogui.click()

            # simulate right-click if thumb is close to middle fingertip
            if thumb_middle_distance < 0.08:
                pyautogui.rightClick()
            
            # draw hand landmarks for visualization
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # display the camera feed with landmarks
    cv2.imshow('Hand Tracking', img)
    
    # break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release resources
cap.release()
cv2.destroyAllWindows()
