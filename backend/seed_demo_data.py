import uuid
import random
from datetime import datetime, timedelta
import logging
import asyncio

# Assuming we are running from the pawpulse-backend directory
from app.db.base import query_db, escape_string
from app.services.anomaly import run_anomaly_detection_for_pet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_demo")

async def seed_demo():
    # 1. Create a demo user
    user_id = str(uuid.uuid4())
    email = f"demo_{uuid.uuid4().hex[:8]}@example.com"
    # Password 'password123' hashed (mock for simplicity, or just use raw if DB allows)
    # Actually users table might have password_hash. 
    # Let's just use a simple insert.
    query_db(f"INSERT INTO users (id, email, password_hash, tier) VALUES ('{user_id}', '{email}', 'mock_hash', 'premium')")
    logger.info(f"Created demo user {email} ({user_id})")

    # 2. Create a demo pet
    pet_id = str(uuid.uuid4())
    pet_name = "DemoDog"
    breed = "Golden Retriever"
    query_db(f"INSERT INTO pets (id, owner_id, name, species, breed, birth_date, weight) VALUES ('{pet_id}', '{user_id}', '{pet_name}', 'dog', '{breed}', '2021-01-01', 30.0)")
    logger.info(f"Created demo pet {pet_name} ({pet_id})")

    # 3. Generate 17 days of data
    # 14 days normal, 3 days anomaly
    end_date = datetime.now()
    start_date = end_date - timedelta(days=17)
    
    current_time = start_date.replace(minute=0, second=0, microsecond=0)
    
    data_points = []
    
    mappings_list = []
    
    while current_time < end_date:
        is_anomaly_day = (end_date - current_time).days < 3
        hour = current_time.hour
        is_night = hour < 7 or hour > 21
        
        # Base values
        score = 0
        min_play = 0
        min_active = 0
        min_rest = 0
        
        if not is_anomaly_day:
            # Normal patterns
            if is_night:
                min_rest = random.randint(50, 60)
                min_active = random.randint(0, 5)
                min_play = 0
                score = random.randint(10, 50)
            else:
                min_rest = random.randint(10, 30)
                min_active = random.randint(15, 30)
                min_play = random.randint(5, 20)
                score = random.randint(200, 500)
        else:
            # Anomaly patterns (reduced activity, nighttime restlessness)
            if is_night:
                # Restlessness: higher active/play, lower rest
                min_rest = random.randint(20, 40)
                min_active = random.randint(10, 20)
                min_play = random.randint(0, 5)
                score = random.randint(100, 200)
            else:
                # Reduced activity during day
                min_rest = random.randint(40, 55)
                min_active = random.randint(0, 10)
                min_play = 0
                score = random.randint(50, 150)
        
        # Format timestamp for SQLite
        ts_str = current_time.isoformat()
        
        # Add to batch
        mappings = {
            "activity_score": score,
            "activity_play_minutes": min_play,
            "activity_moderate_minutes": min_active,
            "rest_minutes": min_rest
        }
        
        for p_type, val in mappings.items():
            mappings_list.append((str(uuid.uuid4()), pet_id, p_type, val, 'minutes', ts_str))
        
        current_time += timedelta(hours=1)

    # Insert in batches of 50 to avoid command line length limits
    batch_size = 50
    for i in range(0, len(mappings_list), batch_size):
        batch = mappings_list[i:i+batch_size]
        values_str = ", ".join([f"('{m[0]}', '{m[1]}', '{m[2]}', {m[3]}, '{m[4]}', '{m[5]}')" for m in batch])
        query_db(f"INSERT INTO health_data (id, pet_id, type, value, unit, timestamp) VALUES {values_str}")
        logger.info(f"Inserted batch {i//batch_size + 1}/{(len(mappings_list)-1)//batch_size + 1}")

    logger.info(f"Inserted 17 days of hourly data for {pet_name}")

    # 4. Trigger analysis
    logger.info("Triggering analysis pipeline...")
    result = await run_anomaly_detection_for_pet(pet_id)
    
    if result:
        logger.info(f"Analysis result: {result.get('health_status')}")
        anomalies = result.get("anomalies", {}).get("anomalies", [])
        logger.info(f"Detected {len(anomalies)} anomalies")
        for a in anomalies:
            logger.info(f" - {a.get('type')}: {a.get('narrative')}")
    else:
        logger.error("Analysis failed")

if __name__ == "__main__":
    asyncio.run(seed_demo())
