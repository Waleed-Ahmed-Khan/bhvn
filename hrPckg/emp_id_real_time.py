import streamlit as st 
import cv2
import face_recognition
import adminPckg.userManagement as userManagement
import numpy as np
import os
from pathlib import Path
import pickle
import time

current_dir = Path("hrPckg").resolve()
def get_out_img_path(username):
    time_stamp_img = time.strftime(f"{username}_%Y%m%d_at_%H%M%S_.jpg")
    images = os.path.join(current_dir, "images")
    os.makedirs(images, exist_ok=True)
    IMG_OUT = os.path.join(images, time_stamp_img)
    return IMG_OUT

def render_realtime(username):
    IMG_OUT = get_out_img_path(username)
    files = os.listdir(current_dir)
    if "known_face_encodings.pkl" not in files:
        known_face_encodings = []
        known_face_ids = []

        for img in os.listdir(Path("static","worker_images").resolve()):
            known_face_ids.append(img.split(".")[0])
            img = os.path.join("static","worker_images", img)
            loaded_img = face_recognition.load_image_file(img)
            encodings = face_recognition.face_encodings(loaded_img)[0]
            known_face_encodings.append(encodings)
        with open(os.path.join(current_dir, 'known_face_encodings.pkl'), 'wb') as f:
            pickle.dump(known_face_encodings, f)
        with open(os.path.join(current_dir, 'known_face_ids.pkl'), 'wb') as f:
            pickle.dump(known_face_ids, f)
    else:
        if "known_face_encodings" not in st.session_state or "known_face_ids" not in st.session_state:
            with open(os.path.join(current_dir, 'known_face_encodings.pkl'), "rb") as f:
                st.session_state["known_face_encodings"] = pickle.load(f)
            with open(os.path.join(current_dir, 'known_face_ids.pkl'), "rb") as f:
                st.session_state["known_face_ids"] = pickle.load(f)
            known_face_encodings = st.session_state["known_face_encodings"]
            known_face_ids = st.session_state["known_face_ids"]
        else:
            known_face_encodings = st.session_state["known_face_encodings"]
            known_face_ids = st.session_state["known_face_ids"]



    # obama_image = face_recognition.load_image_file("data/obama.jpg")
    # obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

    # # Load a second sample picture and learn how to recognize it.
    # biden_image = face_recognition.load_image_file("data/biden.jpg")
    # biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

    # # Create arrays of known face encodings and their names
    # known_face_encodings = [
    #     obama_face_encoding,
    #     biden_face_encoding
    # ]
    # known_face_names = [
    #     "Barack Obama",
    #     "Joe Biden"
    # ]

    col1, col2 = st.columns(2)

    FRAME_WINDOW = col2.image([])
    #camera = cv2.VideoCapture(0)
    try:
        img_file_buffer = col1.camera_input("Take a picture")
    
        if img_file_buffer is not None:
            # To read image file buffer with OpenCV:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        #frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(cv2_img)
        face_encodings = face_recognition.face_encodings(cv2_img, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_ids[best_match_index]

            face_names.append(name)

            #process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            # top *= 4
            # right *= 4
            # bottom *= 4
            # left *= 4
            # Draw a box around the face
            img = cv2.rectangle(cv2_img, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            img = cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            img = cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(IMG_OUT, img)
            FRAME_WINDOW.image(img)
            
            userManagement.app_logger(username, "HR Face Recognition")

        #FRAME_WINDOW.image(img)
    except Exception as e:
        #raise e
        pass