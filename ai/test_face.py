from face_detection import detect_face

image_path = "test.jpg"

result = detect_face(image_path)

if result:
    print("Face detected successfully!")
else:
    print("No face detected.")