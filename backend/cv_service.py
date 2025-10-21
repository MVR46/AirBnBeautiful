"""Computer Vision Service: Amenity detection using YOLOv8 + OWL-ViT."""

import requests
import io
import numpy as np
from PIL import Image
from typing import List, Dict, Set
from ultralytics import YOLO
from transformers import pipeline
import torch

# Global models (lazy-loaded)
yolo_model = None
ovd_pipeline = None
top_amenities = []


# Top amenities from Madrid dataset (from notebook cell 4)
MADRID_TOP_AMENITIES = [
    "wifi router", "kitchen", "tv", "washer", "hot water", "heating",
    "air conditioning unit", "dryer", "hangers", "ironing board",
    "dishwasher", "oven", "coffee maker", "refrigerator", "microwave",
    "stove", "toaster", "elevator", "balcony", "pool", "gym equipment",
    "parking", "smoke alarm", "fire extinguisher", "first aid kit"
]


# Mapping from detected items to canonical amenity names
DETECTION_TO_AMENITY = {
    # COCO labels
    "couch": "Sofa",
    "bed": "Bed",
    "dining table": "Dining table",
    "tv": "TV",
    "laptop": "Workspace",
    "microwave": "Microwave",
    "oven": "Oven",
    "refrigerator": "Refrigerator",
    "sink": "Sink",
    "toilet": "Toilet",
    "potted plant": "Plants",
    "chair": "Seating",
    
    # OWL-ViT amenities
    "wifi router": "WiFi",
    "kitchen": "Kitchen",
    "washer": "Washer",
    "hot water": "Hot water",
    "heating": "Heating",
    "air conditioning unit": "Air conditioning",
    "dryer": "Dryer",
    "hangers": "Hangers",
    "ironing board": "Iron",
    "dishwasher": "Dishwasher",
    "coffee maker": "Coffee maker",
    "stove": "Stove",
    "toaster": "Toaster",
    "elevator": "Elevator",
    "balcony": "Balcony",
    "pool": "Pool",
    "gym equipment": "Gym",
    "parking": "Parking",
    "smoke alarm": "Smoke alarm",
    "fire extinguisher": "Fire extinguisher",
    "first aid kit": "First aid kit",
}


def init_cv_models():
    """Lazy-load CV models."""
    global yolo_model, ovd_pipeline, top_amenities
    
    if yolo_model is None:
        print("Loading YOLOv8 model...")
        yolo_model = YOLO("yolov8n.pt")
        print("YOLOv8 loaded")
    
    if ovd_pipeline is None:
        print("Loading OWL-ViT model for open-vocabulary detection...")
        device = 0 if torch.cuda.is_available() else -1
        ovd_pipeline = pipeline(
            "zero-shot-object-detection",
            model="google/owlvit-base-patch32",
            device=device
        )
        print(f"OWL-ViT loaded (device: {'GPU' if device == 0 else 'CPU'})")
    
    top_amenities = MADRID_TOP_AMENITIES


def load_image_from_url(url: str, max_size: int = 640) -> Image.Image:
    """Load and resize image from URL."""
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    
    img = Image.open(io.BytesIO(response.content)).convert("RGB")
    
    # Resize if too large
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    return img


def detect_with_yolo(image: Image.Image, conf_threshold: float = 0.35) -> Set[str]:
    """Detect objects using YOLOv8 (COCO labels)."""
    init_cv_models()
    
    results = yolo_model.predict(image, conf=conf_threshold, verbose=False)[0]
    
    detected = set()
    if hasattr(results, 'boxes') and len(results.boxes) > 0:
        names = results.names
        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            label = names.get(cls_id, str(cls_id))
            
            # Map to amenity name
            if label.lower() in DETECTION_TO_AMENITY:
                detected.add(DETECTION_TO_AMENITY[label.lower()])
    
    return detected


def detect_with_owlvit(image: Image.Image, amenity_labels: List[str],
                       score_threshold: float = 0.15,
                       max_per_label: int = 3) -> Set[str]:
    """Detect amenities using OWL-ViT open-vocabulary detection."""
    init_cv_models()
    
    # Run detection
    results = ovd_pipeline(image, candidate_labels=amenity_labels)
    
    # Organize by label
    detections_by_label = {}
    for det in results:
        label = det.get("label")
        score = float(det.get("score", 0.0))
        
        if score >= score_threshold:
            if label not in detections_by_label:
                detections_by_label[label] = []
            detections_by_label[label].append(score)
    
    # Keep only labels with confident detections
    detected = set()
    for label, scores in detections_by_label.items():
        # Take top scores for this label
        top_scores = sorted(scores, reverse=True)[:max_per_label]
        
        # If we have confident detections, add the amenity
        if top_scores and top_scores[0] >= score_threshold:
            # Map to canonical name
            canonical = DETECTION_TO_AMENITY.get(label.lower(), label.title())
            detected.add(canonical)
    
    return detected


def detect_amenities_from_image(image_url: str) -> List[str]:
    """
    Two-stage amenity detection:
    1. YOLOv8 for fast COCO object detection
    2. OWL-ViT for specific amenity detection
    """
    try:
        # Load image
        image = load_image_from_url(image_url)
        
        # Stage 1: COCO objects (fast, high confidence)
        yolo_detections = detect_with_yolo(image, conf_threshold=0.35)
        
        # Stage 2: Specific amenities with OWL-ViT
        owlvit_detections = detect_with_owlvit(
            image,
            amenity_labels=top_amenities,
            score_threshold=0.15,
            max_per_label=2
        )
        
        # Merge detections
        all_detections = yolo_detections | owlvit_detections
        
        # Remove duplicates and normalize
        normalized = set()
        for det in all_detections:
            # Normalize common variants
            det_lower = det.lower()
            
            if any(x in det_lower for x in ["wifi", "wi-fi", "internet"]):
                normalized.add("WiFi")
            elif any(x in det_lower for x in ["tv", "television"]):
                normalized.add("TV")
            elif any(x in det_lower for x in ["air conditioning", "ac", "air conditioner"]):
                normalized.add("Air conditioning")
            elif any(x in det_lower for x in ["washer", "washing machine"]):
                normalized.add("Washer")
            elif any(x in det_lower for x in ["dryer", "tumble dryer"]):
                normalized.add("Dryer")
            elif any(x in det_lower for x in ["kitchen"]):
                normalized.add("Kitchen")
            elif any(x in det_lower for x in ["dishwasher"]):
                normalized.add("Dishwasher")
            elif any(x in det_lower for x in ["microwave"]):
                normalized.add("Microwave")
            elif any(x in det_lower for x in ["oven"]):
                normalized.add("Oven")
            elif any(x in det_lower for x in ["refrigerator", "fridge"]):
                normalized.add("Refrigerator")
            elif any(x in det_lower for x in ["coffee maker", "espresso", "nespresso"]):
                normalized.add("Coffee maker")
            elif any(x in det_lower for x in ["pool", "swimming pool"]):
                normalized.add("Pool")
            elif any(x in det_lower for x in ["gym", "fitness", "exercise"]):
                normalized.add("Gym")
            elif any(x in det_lower for x in ["parking"]):
                normalized.add("Parking")
            elif any(x in det_lower for x in ["balcony"]):
                normalized.add("Balcony")
            elif any(x in det_lower for x in ["elevator", "lift"]):
                normalized.add("Elevator")
            elif any(x in det_lower for x in ["iron"]):
                normalized.add("Iron")
            elif any(x in det_lower for x in ["heating", "heater", "radiator"]):
                normalized.add("Heating")
            elif any(x in det_lower for x in ["smoke alarm", "smoke detector"]):
                normalized.add("Smoke alarm")
            elif any(x in det_lower for x in ["fire extinguisher"]):
                normalized.add("Fire extinguisher")
            else:
                normalized.add(det)
        
        return sorted(list(normalized))
    
    except Exception as e:
        print(f"Error detecting amenities: {e}")
        raise


def detect_amenities_from_photos(photo_urls: List[str]) -> List[str]:
    """Detect amenities from multiple photos and merge results."""
    all_amenities = set()
    
    for url in photo_urls:
        try:
            amenities = detect_amenities_from_image(url)
            all_amenities.update(amenities)
        except Exception as e:
            print(f"Failed to process {url}: {e}")
            continue
    
    return sorted(list(all_amenities))

