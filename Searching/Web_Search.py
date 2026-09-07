import io
import os
import requests
import numpy as np
from PIL import Image
import serpapi
from Searching.Cosine import MATCH_THRESHOLD, cosine_distance
from Searching.Image_Byte import _get_image_bytes
from Blockchain.Backend.util.util import hash256
from Searching.API_tk import token

SERPAPI_API_KEY = token

def search_google_lens(image_bytes, api_key):
    upload_res = requests.post(
        "https://serpapi.com/image",
        files={"image": ("input.jpg", image_bytes, "image/jpeg")},
        data={"api_key": api_key},
        timeout=30
    ).json()

    image_id = upload_res.get("image_id")
    if not image_id:
        raise ValueError(f"SerpApi upload failed: {upload_res}")

    client = serpapi.Client(api_key=api_key)
    
    # Removed "type": "visual_matches" so we get the full JSON including the knowledge graph
    results = client.search({
        "engine": "google_lens",
        "image_id": image_id,
        "hl": "en"
    })
    
    visual_matches = results.get("visual_matches", [])
    knowledge_graph = results.get("knowledge_graph", [])
    
    # Extract the single recognized name from the Knowledge Graph
    entity_name = "Unknown"
    if knowledge_graph and len(knowledge_graph) > 0:
        entity_name = knowledge_graph[0].get("title", "Unknown")
        
    return visual_matches, entity_name


def find_faces_on_web(ref_vector, incoming_image, api_key=SERPAPI_API_KEY, threshold=MATCH_THRESHOLD):
    img_bytes = _get_image_bytes(incoming_image)
    
    # Unpack both the visual matches and the recognized entity name
    visual_matches, top_entity = search_google_lens(img_bytes, api_key)

    results_list = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for idx, match in enumerate(visual_matches):
        img_url = match.get("thumbnail")
        if not img_url:
            continue

        try:
            resp = requests.get(img_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue

            candidate_bytes = resp.content
            candidate_img = Image.open(io.BytesIO(candidate_bytes)).convert("RGB")
            candidate_arr = np.array(candidate_img)

            from deepface import DeepFace
            embedding_objs = DeepFace.represent(
                img_path=candidate_arr,
                model_name="ArcFace",
                detector_backend="mtcnn",
                enforce_detection=False,  
                align=True
            )
            candidate_vector = embedding_objs[0]["embedding"]
            distance = cosine_distance(ref_vector, candidate_vector)

            if distance >= threshold:
                raw_title = match.get("title", "No Title")
                if top_entity != "Unknown":
                    extracted_name = top_entity
                else:
                    possible_name = raw_title.replace('|', '-').split('-')[0].strip()
                    if len(possible_name.split()) > 3:
                        extracted_name = "Identity Not Explicitly Named"
                    else:
                        extracted_name = possible_name

                results_list.append({
                    "match_id": idx,
                    "identified_name": extracted_name,
                    "title": raw_title,
                    "page_url": match.get("link", ""),
                    "image_url": img_url,
                    "image_fingerprint": hash256(candidate_bytes).hex(),
                    "cosine_distance": round(float(distance), 4)
                })
        except Exception:
            continue

    results_list.sort(key=lambda x: x["cosine_distance"])
    
    return results_list, top_entity