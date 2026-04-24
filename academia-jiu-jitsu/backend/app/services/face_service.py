"""
Face recognition service using DeepFace.
Encodes faces from images and matches them against stored encodings.
"""
import io
import json
import uuid
import os
import numpy as np
from typing import Optional
from PIL import Image

MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.4"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def _load_image_from_bytes(data: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return np.array(img)


def encode_face_from_bytes(image_bytes: bytes) -> Optional[list[float]]:
    """Extract face encoding from image bytes. Returns None if no face found."""
    try:
        from deepface import DeepFace
        img_array = _load_image_from_bytes(image_bytes)

        result = DeepFace.represent(
            img_path=img_array,
            model_name="Facenet",
            enforce_detection=True,
            detector_backend="opencv",
        )
        if result:
            return result[0]["embedding"]
        return None
    except Exception:
        return None


def detect_and_crop_faces(image_bytes: bytes) -> list[tuple[np.ndarray, dict]]:
    """
    Detect all faces in image. Returns list of (cropped_face_array, region_dict).
    region_dict has keys: x, y, w, h
    """
    try:
        from deepface import DeepFace
        import cv2

        img_array = _load_image_from_bytes(image_bytes)

        faces = DeepFace.extract_faces(
            img_path=img_array,
            detector_backend="opencv",
            enforce_detection=False,
            align=True,
        )
        results = []
        for face_obj in faces:
            if face_obj.get("confidence", 0) < 0.85:
                continue
            face_arr = (face_obj["face"] * 255).astype(np.uint8)
            region = face_obj.get("facial_area", {})
            results.append((face_arr, region))
        return results
    except Exception:
        return []


def get_face_encoding(face_array: np.ndarray) -> Optional[list[float]]:
    """Get encoding from an already-cropped face array."""
    try:
        from deepface import DeepFace
        result = DeepFace.represent(
            img_path=face_array,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="skip",
        )
        if result:
            return result[0]["embedding"]
        return None
    except Exception:
        return None


def cosine_distance(a: list[float], b: list[float]) -> float:
    va = np.array(a)
    vb = np.array(b)
    return 1 - np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-10)


def match_face(
    face_encoding: list[float],
    students_encodings: list[tuple[int, list[float]]],  # [(student_id, encoding), ...]
) -> Optional[tuple[int, float]]:
    """
    Compare a face encoding against stored encodings.
    Returns (student_id, confidence_score) or None if no match.
    confidence_score is 0-1, higher is better.
    """
    best_id = None
    best_dist = float("inf")

    for student_id, encoding in students_encodings:
        dist = cosine_distance(face_encoding, encoding)
        if dist < best_dist:
            best_dist = dist
            best_id = student_id

    if best_id is not None and best_dist < MATCH_THRESHOLD:
        confidence = round(1 - best_dist, 4)
        return best_id, confidence
    return None


def save_face_crop(face_array: np.ndarray, session_id: int) -> str:
    """Save a face crop image to disk and return the path."""
    import cv2
    faces_dir = os.path.join(UPLOAD_DIR, "faces")
    os.makedirs(faces_dir, exist_ok=True)
    filename = f"session_{session_id}_{uuid.uuid4()}.jpg"
    path = os.path.join(faces_dir, filename)
    rgb = cv2.cvtColor(face_array, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, rgb)
    return path
