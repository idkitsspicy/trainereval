import cv2
import os


face_cascade = cv2.CascadeClassifier(

    cv2.data.haarcascades +
    'haarcascade_frontalface_default.xml'
)


def analyze_video(video_path):

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        return {

            "status": "ERROR",

            "message": "Could not open video."
        }

    off_center_count = 0

    total_frames = 0

    no_face_frames = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        h, w, _ = frame.shape

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(

            gray,

            scaleFactor=1.1,

            minNeighbors=5,

            minSize=(100, 100)
        )

        total_frames += 1

        center_x = w // 2

        if len(faces) == 0:

            no_face_frames += 1

            continue

        for (x, y, fw, fh) in faces:

            face_center_x = x + fw // 2

            diff = face_center_x - center_x

            if diff < -100:

                off_center_count += 1

            elif diff > 100:

                off_center_count += 1

    cap.release()

    # -----------------------------------
    # METRICS
    # -----------------------------------

    off_center_ratio = (

        off_center_count /

        max(total_frames, 1)
    ) * 100

    no_face_ratio = (

        no_face_frames /

        max(total_frames, 1)
    ) * 100

    suspicion_score = (

        off_center_ratio * 0.7

        +

        no_face_ratio * 0.3
    )

    # -----------------------------------
    # RISK LEVEL
    # -----------------------------------



    if no_face_ratio > 85:

        risk = "INVALID"

        message = (
            "No consistent face detected. "
            "Uploaded video may not be "
            "a valid teaching demo."
        )

    elif suspicion_score < 20:

        risk = "LOW"

        message = (
            "Behavior appears stable."
        )

    elif suspicion_score < 50:

        risk = "MEDIUM"

        message = (
            "Moderate behavioral deviation detected."
        )

    else:

        risk = "HIGH"

        message = (
            "Frequent off-center behavior detected."
        )

    return {

        "status": "SUCCESS",

        "total_frames": total_frames,

        "off_center_ratio":
            round(off_center_ratio, 2),

        "no_face_ratio":
            round(no_face_ratio, 2),

        "suspicion_score":
            round(suspicion_score, 2),

        "risk": risk,

        "message": message
    }