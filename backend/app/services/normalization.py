def normalize_data(device_type: str, raw_data: list):
    normalized = []
    if device_type == "fitbark":
        for item in raw_data:
            # FitBark activity series hourly data has: timestamp, score, min_play, min_active, min_rest, etc.
            # But the instructons mention:
            # min_play -> activity_play_minutes
            # min_active -> activity_moderate_minutes
            # min_rest -> rest_minutes
            # distance_in_miles -> distance_km
            # calories -> calories
            # score -> activity_score
            # goal_progress -> goal_progress_pct
            
            timestamp = item.get("timestamp") or item.get("date")
            
            # Map according to unified schema instructions
            mappings = {
                "score": "activity_score",
                "min_play": "activity_play_minutes",
                "min_active": "activity_moderate_minutes",
                "min_rest": "rest_minutes",
                "distance_in_miles": "distance_km",
                "calories": "calories",
                "goal_progress": "goal_progress_pct"
            }
            
            for fb_key, pulse_key in mappings.items():
                if fb_key in item and item[fb_key] is not None:
                    value = float(item[fb_key])
                    # Conversion for distance
                    if pulse_key == "distance_km":
                        value = value * 1.60934
                    
                    unit = "minutes"
                    if "score" in pulse_key: unit = "points"
                    if "km" in pulse_key: unit = "km"
                    if "calories" in pulse_key: unit = "kcal"
                    if "pct" in pulse_key: unit = "percent"
                    
                    normalized.append({
                        "type": pulse_key,
                        "value": value,
                        "unit": unit,
                        "timestamp": timestamp
                    })
                
    return normalized
