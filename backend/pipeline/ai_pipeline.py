"""
AI Pipeline for Video Scene Search
-----------------------------------
Pipeline chạy nền sau khi video được upload:
1. Download video từ Supabase Storage public URL
2. Detect scenes bằng PySceneDetect
3. Extract frame đại diện tại midpoint mỗi scene
4. Upload frame lên Supabase Storage (bucket: scene-frames)
5. Encode frame bằng CLIP (sentence-transformers clip-ViT-B-32) → vector 512-dim
6. Upsert vector vào Supabase pgvector qua vecs Python client
7. Update video status → "ready"
"""
import os
import io
import uuid
import logging
import tempfile
from pathlib import Path
from typing import Optional

import cv2
import httpx
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
import vecs
from supabase import Client

logger = logging.getLogger(__name__)

# CLIP model — loaded once when module is first imported (lazy initialization)
_clip_model: Optional[SentenceTransformer] = None


def get_clip_model() -> SentenceTransformer:
    """Lazy-load CLIP model (downloads ~340MB on first call)."""
    global _clip_model
    if _clip_model is None:
        logger.info("Loading CLIP model clip-ViT-B-32...")
        _clip_model = SentenceTransformer("clip-ViT-B-32")
        logger.info("CLIP model loaded.")
    return _clip_model


def detect_scenes(video_path: str) -> list[float]:
    """
    Detect scene changes và trả về list midpoint timestamps (seconds).
    Mỗi scene sẽ có một frame đại diện tại midpoint của scene đó.
    """
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=27.0))
    scene_manager.detect_scenes(video, show_progress=False)
    scene_list = scene_manager.get_scene_list()

    # Nếu không detect được scene nào, lấy frame tại 0s, 25%, 50%, 75%
    if not scene_list:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        cap.release()
        duration = total_frames / fps
        return [duration * p for p in [0.0, 0.25, 0.5, 0.75] if duration * p < duration]

    # Lấy midpoint của mỗi scene
    midpoints = []
    for start_time, end_time in scene_list:
        start_sec = start_time.get_seconds()
        end_sec = end_time.get_seconds()
        midpoints.append((start_sec + end_sec) / 2.0)

    return midpoints


def extract_frame(video_path: str, timestamp_sec: float) -> Optional[Image.Image]:
    """Extract một frame tại timestamp (seconds) và trả về PIL.Image (RGB)."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_number = int(timestamp_sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    # OpenCV dùng BGR, PIL cần RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)


def encode_text(text: str) -> np.ndarray:
    """Encode một câu query text thành vector 512-dim bằng CLIP."""
    model = get_clip_model()
    embedding = model.encode(text)
    return embedding.astype(np.float32)


def encode_image(image: Image.Image) -> np.ndarray:
    """Encode một PIL Image thành vector 512-dim bằng CLIP."""
    model = get_clip_model()
    embedding = model.encode(image)
    return embedding.astype(np.float32)


def run_pipeline(
    video_id: str,
    video_url: str,
    title: str,
    supabase_client: Client,
    supabase_db_url: str,
    frames_bucket: str = "scene-frames",
) -> None:
    """
    Pipeline chính chạy sau khi video được upload.
    Gọi trong FastAPI BackgroundTasks.
    """
    logger.info(f"[Pipeline] Bắt đầu xử lý video_id={video_id}")

    # Tạo thư mục tạm để lưu video
    with tempfile.TemporaryDirectory() as tmp_dir:
        video_path = os.path.join(tmp_dir, f"{video_id}.mp4")

        # --- Bước 1: Download video từ Supabase Storage public URL ---
        logger.info(f"[Pipeline] Đang download video từ {video_url}")
        try:
            with httpx.Client(timeout=300.0, follow_redirects=True) as client:
                response = client.get(video_url)
                response.raise_for_status()
                with open(video_path, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            logger.error(f"[Pipeline] Download thất bại: {e}")
            _update_video_status(supabase_client, video_id, "error")
            return

        # --- Bước 2: Detect scenes ---
        logger.info("[Pipeline] Đang detect scenes...")
        try:
            timestamps = detect_scenes(video_path)
        except Exception as e:
            logger.error(f"[Pipeline] Scene detection thất bại: {e}")
            _update_video_status(supabase_client, video_id, "error")
            return
        logger.info(f"[Pipeline] Detect được {len(timestamps)} scenes/frames")

        # --- Bước 3: Kết nối vecs (tự tạo schema và collection nếu chưa có) ---
        try:
            vx = vecs.create_client(supabase_db_url)
            # CLIP ViT-B/32 → 512-dim vectors
            collection = vx.get_or_create_collection(name="video_frames", dimension=512)
        except Exception as e:
            logger.error(f"[Pipeline] Kết nối vecs thất bại: {e}")
            _update_video_status(supabase_client, video_id, "error")
            return

        records = []

        for timestamp_sec in timestamps:
            # --- Bước 4: Extract frame ---
            frame_image = extract_frame(video_path, timestamp_sec)
            if frame_image is None:
                logger.warning(f"[Pipeline] Không thể extract frame tại {timestamp_sec:.1f}s")
                continue

            # --- Bước 5: Upload frame lên Supabase Storage ---
            frame_id = str(uuid.uuid4())
            frame_path = f"{video_id}/{frame_id}.jpg"
            try:
                # Convert PIL Image → JPEG bytes
                buffer = io.BytesIO()
                frame_image.save(buffer, format="JPEG", quality=85)
                frame_bytes = buffer.getvalue()

                supabase_client.storage.from_(frames_bucket).upload(
                    path=frame_path,
                    file=frame_bytes,
                    file_options={"content-type": "image/jpeg"},
                )
                frame_url = supabase_client.storage.from_(frames_bucket).get_public_url(frame_path)
            except Exception as e:
                logger.error(f"[Pipeline] Upload frame thất bại tại {timestamp_sec:.1f}s: {e}")
                continue

            # --- Bước 6: Encode frame bằng CLIP ---
            try:
                embedding = encode_image(frame_image)
            except Exception as e:
                logger.error(f"[Pipeline] Encode CLIP thất bại tại {timestamp_sec:.1f}s: {e}")
                continue

            # Tạo record cho vecs upsert
            records.append((
                frame_id,           # vector identifier (unique)
                embedding,          # vector 512-dim
                {                   # metadata
                    "video_id": video_id,
                    "title": title,
                    "timestamp_seconds": timestamp_sec,
                    "frame_url": frame_url,
                    "video_url": video_url,
                }
            ))
            logger.info(f"[Pipeline] Frame {timestamp_sec:.1f}s → encoded OK")

        # --- Bước 7: Upsert vectors vào vecs collection ---
        if records:
            try:
                collection.upsert(records=records)
                # Tạo index để tăng tốc độ similarity search
                try:
                    collection.create_index()
                except Exception:
                    pass  # Index có thể đã tồn tại
                logger.info(f"[Pipeline] Upserted {len(records)} vectors vào vecs collection")
            except Exception as e:
                logger.error(f"[Pipeline] Upsert vecs thất bại: {e}")
                _update_video_status(supabase_client, video_id, "error")
                return

        vx.disconnect()

    # --- Bước 8: Update video status → "ready" ---
    _update_video_status(supabase_client, video_id, "ready")
    logger.info(f"[Pipeline] Video {video_id} đã xử lý xong → status='ready'")


def _update_video_status(supabase_client: Client, video_id: str, status: str) -> None:
    """Helper: cập nhật cột status trong bảng videos."""
    try:
        supabase_client.table("videos").update({"status": status}).eq("video_id", video_id).execute()
    except Exception as e:
        logger.error(f"[Pipeline] Update status thất bại: {e}")
