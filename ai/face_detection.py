import os
import cv2


def analyze_face(image_path):
    """
    Detect a face in an image and estimate basic face proportions.

    Note:
    Haar Cascade detects faces, but its bounding box cannot
    reliably determine a person's actual face shape.
    The face-shape result below is only a rough estimate.
    """

    try:
        if not os.path.exists(image_path):
            return {
                "detected": False,
                "message": "Image file not found."
            }

        image = cv2.imread(image_path)

        if image is None:
            return {
                "detected": False,
                "message": "Unable to read the image."
            }

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.equalizeHist(gray)

        cascade_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        face_cascade = cv2.CascadeClassifier(
            cascade_path
        )

        if face_cascade.empty():
            return {
                "detected": False,
                "message": "Face detection model could not load."
            }

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        if len(faces) == 0:
            return {
                "detected": False,
                "message": (
                    "No face detected. "
                    "Please upload a clear, front-facing photo."
                )
            }

        # Choose the largest detected face.
        x, y, width, height = max(
            faces,
            key=lambda face: face[2] * face[3]
        )

        # Rough estimate based on face bounding-box proportions.
        ratio = width / height

        if ratio >= 0.85:
            face_shape = "Round"
        elif ratio <= 0.65:
            face_shape = "Long"
        else:
            face_shape = "Oval"

        return {
            "detected": True,
            "face_shape": face_shape,
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "message": "Face detected successfully."
        }

    except Exception as error:
        print("Face detection error:", error)

        return {
            "detected": False,
            "message": (
                "An error occurred during face detection."
            )
        }


def detect_face(image_path):
    result = analyze_face(image_path)
    return result.get("detected", False)