from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    tier: str = "free"
    created_at: datetime

    class Config:
        from_attributes = True

# Pet schemas
class PetBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[str] = None
    weight: Optional[float] = None

class PetCreate(PetBase):
    pass

class Pet(PetBase):
    id: str
    owner_id: str
    created_at: datetime

# Device schemas
class DeviceBase(BaseModel):
    type: str # fitbark, whistle, tractive
    external_id: str

class DeviceCreate(DeviceBase):
    pet_id: str
    access_token: str
    refresh_token: Optional[str] = None

class Device(DeviceBase):
    id: str
    pet_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    token_type: Optional[str] = None
    created_at: datetime

# Health Data schemas
class HealthDataBase(BaseModel):
    type: str # activity, sleep, vitals, gait
    value: float
    unit: str
    timestamp: datetime

class HealthDataCreate(HealthDataBase):
    pet_id: str
    device_id: str

class HealthData(HealthDataBase):
    id: str
    pet_id: str
    device_id: str

# Anomaly Alert schemas
class AnomalyAlertBase(BaseModel):
    type: str
    description: str
    severity: str # low, medium, high
    status: str # open, acknowledged, resolved

class AnomalyAlert(AnomalyAlertBase):
    id: str
    pet_id: str
    created_at: datetime

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Subscription schemas
class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PRO = "pro"

class SubscriptionBase(BaseModel):
    tier: SubscriptionTier
    status: str

class Subscription(SubscriptionBase):
    id: str
    user_id: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime

class CheckoutSessionCreate(BaseModel):
    tier: SubscriptionTier
    success_url: str
    cancel_url: str

class CheckoutSession(BaseModel):
    checkout_url: str

class IAPVerification(BaseModel):
    receipt_data: str
    product_id: str
    platform: str # ios or android

class IAPResponse(BaseModel):
    success: bool
    tier: str
    expiry_date: datetime
    subscription_id: str

# Practice schemas
class PracticeBase(BaseModel):
    name: str
    address: str
    license_info: str

class PracticeCreate(PracticeBase):
    pass

class Practice(PracticeBase):
    id: str
    owner_id: str
    created_at: datetime

# Push Token schemas
class PushTokenCreate(BaseModel):
    token: str
    platform: Optional[str] = None

class PushToken(BaseModel):
    id: str
    user_id: str
    token: str
    platform: str
    created_at: datetime
