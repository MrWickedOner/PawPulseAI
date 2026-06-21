import logging
import uuid
from datetime import datetime, date
from typing import List, Dict, Any

from ..db.base import query_db, escape_string
from pawpulse_ml.engine import PawPulseEngine

logger = logging.getLogger(__name__)

# Initialize the engine
# We might want to keep it as a singleton or initialize per request if needed
# But keeping it global for baseline caching as designed
engine = PawPulseEngine(enable_trends=True)

# Global status for analysis
analysis_status = {
    "last_run_at": None,
    "pets_analyzed": 0,
    "alerts_generated": 0
}

def calculate_age(birth_date_str: str) -> float:
    if not birth_date_str:
        return 5.0  # Default age if unknown
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = date.today()
        age_days = (today - birth_date).days
        return max(0.1, age_days / 365.25)
    except Exception:
        return 5.0

def get_pet_health_data_for_engine(pet_id: str, days: int = 14) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch health data from the database and format it for the ML engine.
    """
    # Fetch data from the last 'days' days
    rows = query_db(f"""
        SELECT timestamp, type, value 
        FROM health_data 
        WHERE pet_id = '{pet_id}' 
        AND timestamp >= date('now', '-{days} days')
        ORDER BY timestamp ASC
    """)
    
    if not rows:
        return {"fitbark_hourly": [], "fitbark_daily": []}

    # Hourly data: Group by timestamp
    data_by_hour = {}
    for row in rows:
        ts = row["timestamp"]
        if ts not in data_by_hour:
            data_by_hour[ts] = {"timestamp": ts}
        
        type_map = {
            "activity_score": "score",
            "activity_play_minutes": "min_play",
            "activity_moderate_minutes": "min_active",
            "rest_minutes": "min_rest",
            "distance_km": "distance_in_miles", # Map back to expected FitBark miles
            "calories": "calories"
        }
        
        pulse_type = row["type"]
        fb_type = type_map.get(pulse_type)
        if fb_type:
            val = row["value"]
            if fb_type == "distance_in_miles":
                val = val / 1.60934 # Convert back to miles
            data_by_hour[ts][fb_type] = val

    # Daily data: Aggregate by date
    data_by_day = {}
    for row in rows:
        ts_str = row["timestamp"]
        try:
            date_str = ts_str.split('T')[0] if 'T' in ts_str else ts_str.split(' ')[0]
        except Exception:
            continue
            
        if date_str not in data_by_day:
            data_by_day[date_str] = {"date": date_str}
        
        type_map = {
            "activity_score": "score",
            "activity_play_minutes": "min_play",
            "activity_moderate_minutes": "min_active",
            "rest_minutes": "min_rest",
            "distance_km": "distance_in_miles",
            "calories": "calories"
        }
        
        pulse_type = row["type"]
        fb_type = type_map.get(pulse_type)
        if fb_type:
            val = row["value"]
            if fb_type == "distance_in_miles":
                val = val / 1.60934
            
            if fb_type in data_by_day[date_str]:
                data_by_day[date_str][fb_type] += val
            else:
                data_by_day[date_str][fb_type] = val

    return {
        "fitbark_hourly": list(data_by_hour.values()),
        "fitbark_daily": list(data_by_day.values())
    }

async def run_anomaly_detection_for_pet(pet_id: str):
    """
    Run anomaly detection for a single pet and store alerts.
    """
    global analysis_status
    
    # 1. Get pet details
    pet_rows = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}'")
    if not pet_rows:
        logger.error(f"Pet {pet_id} not found for anomaly detection")
        return
    pet = pet_rows[0]

    # 2. Get owner tier
    user_rows = query_db(f"SELECT tier FROM users WHERE id = '{pet['owner_id']}'")
    tier = user_rows[0]["tier"] if user_rows else "basic"

    # 3. Get health data (last 14 days)
    health_data = get_pet_health_data_for_engine(pet_id, days=14)

    # 4. Run engine
    try:
        result = engine.check_pet(
            pet_id=pet_id,
            breed=pet.get("breed") or "Unknown",
            age_years=calculate_age(pet.get("birth_date")),
            weight_kg=pet.get("weight") or 20.0,
            fitbark_hourly=health_data.get("fitbark_hourly"),
            fitbark_daily=health_data.get("fitbark_daily"),
            tier=tier
        )

        analysis_status["pets_analyzed"] += 1
        analysis_status["last_run_at"] = datetime.now().isoformat()

        # 5. Process results and store alerts
        # The result from check_pet uses the formatter:
        # {
        #   "health_status": "attention_needed",
        #   "anomalies": { "anomalies": [ {...}, ... ] },
        #   ...
        # }
        
        if result.get("health_status") == "attention_needed":
            anomalies_data = result.get("anomalies", {})
            for anomaly in anomalies_data.get("anomalies", []):
                alert_type = escape_string(anomaly.get("type") or "behavioral_shift")
                description = escape_string(anomaly.get("narrative") or "Detected unusual activity pattern")
                severity = escape_string(anomaly.get("severity") or "medium")
                
                # Deduplication: 48 hours
                existing = query_db(f"""
                    SELECT id FROM anomaly_alerts 
                    WHERE pet_id = '{pet_id}' 
                    AND type = '{alert_type}' 
                    AND status = 'open'
                    AND created_at >= datetime('now', '-2 days')
                """)
                
                if not existing:
                    alert_id = str(uuid.uuid4())
                    query_db(f"""
                        INSERT INTO anomaly_alerts (id, pet_id, type, description, severity, status) 
                        VALUES ('{alert_id}', '{pet_id}', '{alert_type}', '{description}', '{severity}', 'open')
                    """)
                    analysis_status["alerts_generated"] += 1
                    logger.info(f"Created alert {alert_id} for pet {pet_id}: {alert_type}")

        return result

    except Exception as e:
        logger.exception(f"Error running anomaly detection for pet {pet_id}: {e}")
        return None

async def run_anomaly_detection_all_pets():
    """
    Run anomaly detection for all pets that have data.
    """
    # Get all pets that have a connected device
    pets_with_devices = query_db("SELECT DISTINCT pet_id FROM devices")
    for row in pets_with_devices:
        await run_anomaly_detection_for_pet(row["pet_id"])
