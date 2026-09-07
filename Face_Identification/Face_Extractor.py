import cv2
from deepface import DeepFace

MODEL_NAME = "ArcFace"
DETECTOR = "mtcnn"

def Detect_Encode_Face(image_path: str):
    """
    Detects a face, crops the image to that face region, then extracts
    and returns the embedding. Output is identical to before so downstream
    code is unaffected.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot open '{image_path}'")

    results = DeepFace.represent(
        img_path=img,
        model_name=MODEL_NAME,
        detector_backend=DETECTOR,
        enforce_detection=True,
        align=True
    )

    face = results[0]
    #crop
    region = face["facial_area"]          # {"x", "y", "w", "h"}
    x, y, w, h = region["x"], region["y"], region["w"], region["h"]
    face_crop = img[y : y + h, x : x + w]
    # enforce_detection=False because the crop is already face-only
    crop_results = DeepFace.represent(
        img_path=face_crop,
        model_name=MODEL_NAME,
        detector_backend=DETECTOR,
        enforce_detection=False,
        align=True
    )

    embedding = crop_results[0]["embedding"]
    return embedding