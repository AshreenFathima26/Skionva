import cv2
import numpy as np

def preprocess_image(image_path):
    """
    Real-time safe preprocessing:
    - Detect face
    - Crop face region
    - Resize to model input
    """

    # Load image using OpenCV
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Image not loaded properly")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load Haar Cascade (face detector)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    # If face detected → crop first face
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face_img = img[y:y+h, x:x+w]
    else:
        # Fallback: use center crop
        h, w, _ = img.shape
        cx, cy = w // 2, h // 2
        size = min(w, h) // 2
        face_img = img[
            cy-size:cy+size,
            cx-size:cx+size
        ]

    # Resize for model
    face_img = cv2.resize(face_img, (224, 224))

    # Normalize
    face_img = face_img.astype("float32") / 255.0

    # Expand batch dimension
    face_img = np.expand_dims(face_img, axis=0)

    return face_img
