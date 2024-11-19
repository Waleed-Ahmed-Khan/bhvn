import streamlit as st 
import cv2
import face_recognition
import numpy as np
import os

obama_image = face_recognition.load_image_file(os.path.join("data", "obama.jpg"))
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file(os.path.join("data","biden.jpg"))
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden"
]



st.title("Webcam Live Feed")
run = st.checkbox('Run')
FRAME_WINDOW = st.image([], width = 900)
camera = cv2.VideoCapture(0)

while run:
    _, frame = camera.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        

        face_names.append(name)

        #process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        print("Got innn")
        # top *= 4
        # right *= 4
        # bottom *= 4
        # left *= 4
        # Draw a box around the face
        img = cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        img = cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        img = cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


        #print(img)
        #st.image(img)
        FRAME_WINDOW.image(img)

    #FRAME_WINDOW.image(img)
else:
    st.write('Stopped')
