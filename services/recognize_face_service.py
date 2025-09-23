import cv2
import pickle
import csv
import os
from datetime import datetime
from services.services import mark_attendance
from threading import Thread



running = False
thread = None
def recognize_and_mark_attendance(app):
    ''' Recognize faces and mark attendance '''
    global running
      # Load model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(r"D:\projects\ml_model\trainer.yml")

    # Load mapping
    with open(r"D:\projects\ml_model\label_mapping.pkl", "rb") as f:
        label_mapping = pickle.load(f)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {"error": "❌ Could not open camera"}

    
    attendance_file = "attendance.csv"
    if not os.path.exists(attendance_file):
        with open(attendance_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Date", "Time"])
            
    marked = set()


    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            id_, confidence = recognizer.predict(face)

            if confidence < 50:
                # Get stored label like "9124_John"
                user_label = label_mapping[id_]
                user_id, user_name = user_label.split("_", 1)

                display_text = f"{user_name} (ID: {user_id})"

                if user_id not in marked:
                    with app.app_context():
                        mark_attendance(student_id=user_id, status="Present")
                    now = datetime.now()
                    with open(attendance_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([user_id, user_name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])
                    marked.add(user_id)
            else:
                display_text = "Unknown"

            cv2.putText(frame, display_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)

        cv2.imshow("Attendance System", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def start_recognition(app):
    """Start the background thread if not already running"""
    global running
    if not running:
        running = True
        thread = Thread(target=recognize_and_mark_attendance(app))
        thread.daemon = True
        thread.start()
        return {"status": "Recognition started"}
    else:
        return {"status": "Recognition already running"}
    

def stop_recognition():
    """Stop the background recognition loop"""
    global running
    if running:
        running = False
        return {"status": "Recognition stopped"}
    else:
        return {"status": "Recognition is not running"}