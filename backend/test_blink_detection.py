#!/usr/bin/env python3
"""
Test script for blink detection with USB camera
Run this to verify face detection and blink detection are working
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BlinkTest")

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# Camera setup
cap = cv2.VideoCapture('/dev/video0')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Blink detector parameters
eye_aspect_ratio_threshold = 0.25
ear_history = []
last_blink_time = 0
is_blinking = False
blink_start_time = None
calibration_frames = 0
max_ear = 0.5
min_ear = 0.2

log.info("Starting blink detection test...")
log.info("Instructions:")
log.info("1. Make sure your face is clearly visible in the camera")
log.info("2. Ensure adequate lighting")
log.info("3. Blink several times")
log.info("4. Press 'q' to quit\n")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        log.warning("Failed to read frame")
        continue
    
    frame_count += 1
    
    # Flip for selfie view
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_mesh.process(rgb)
    
    # Display frame count and status
    status_text = f"Frames: {frame_count}"
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0]
        
        # Extract eye landmarks (left eye)
        left_eye_indices = [33, 163, 133, 144, 145, 153, 154, 155]
        left_eye = []
        for idx in left_eye_indices:
            lm = landmarks.landmark[idx]
            left_eye.append([lm.x, lm.y, lm.z])
        
        # Extract eye landmarks (right eye)
        right_eye_indices = [362, 398, 263, 373, 374, 380, 381, 382]
        right_eye = []
        for idx in right_eye_indices:
            lm = landmarks.landmark[idx]
            right_eye.append([lm.x, lm.y, lm.z])
        
        # Calculate EAR
        def calc_ear(eye):
            if len(eye) < 6:
                return 0.5
            eye_array = np.array(eye)
            vertical1 = np.linalg.norm(eye_array[1] - eye_array[5])
            vertical2 = np.linalg.norm(eye_array[2] - eye_array[4])
            horizontal = np.linalg.norm(eye_array[0] - eye_array[3])
            if horizontal == 0:
                return 0.5
            return (vertical1 + vertical2) / (2.0 * horizontal)
        
        left_ear = calc_ear(left_eye)
        right_ear = calc_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        ear_history.append(avg_ear)
        if len(ear_history) > 100:
            ear_history.pop(0)
        
        # Calibration
        if calibration_frames < 50:
            calibration_frames += 1
            max_ear = max(max_ear, avg_ear)
            min_ear = min(min_ear, avg_ear)
            threshold = min_ear + (max_ear - min_ear) * 0.4
            
            if calibration_frames == 50:
                log.info(f"✓ Calibration complete: EAR range [{min_ear:.3f}, {max_ear:.3f}], threshold: {threshold:.3f}")
        else:
            # Use calibrated threshold
            threshold = min_ear + (max_ear - min_ear) * 0.4
            
            # Blink detection
            current_time = time.time()
            if avg_ear < threshold:
                if not is_blinking:
                    is_blinking = True
                    blink_start_time = current_time
            else:
                if is_blinking:
                    blink_duration = current_time - blink_start_time
                    is_blinking = False
                    if blink_duration >= 0.05:  # Ignore very brief detections
                        log.info(f"✓ BLINK detected! Duration: {blink_duration:.3f}s")
                    last_blink_time = current_time
        
        # Display info
        cv2.putText(frame, f"Face detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"EAR: {avg_ear:.3f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        if calibration_frames < 50:
            cv2.putText(frame, f"Calibrating... {calibration_frames}/50", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        # Draw face landmarks
        for point in landmarks.landmark[::3]:  # Draw every 3rd point to avoid clutter
            x = int(point.x * w)
            y = int(point.y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
    
    else:
        cv2.putText(frame, "No face detected", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "Position yourself in front of camera", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Show frame
    cv2.imshow('Blink Detection Test', frame)
    
    # Check for quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

log.info("Test completed")
cap.release()
cv2.destroyAllWindows()
