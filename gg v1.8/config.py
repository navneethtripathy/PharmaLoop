import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    DATABASE = 'pharmaloop.db'
    JWT_EXPIRATION_HOURS = 24

    DISTANCE_COST_PER_KM = 5
    MIN_DISCOUNT_PERCENT = 10
    MAX_DISCOUNT_PERCENT = 40
    URGENCY_THRESHOLD_DAYS = 30

    MEDICINE_BASE_PRICE = 100
    HANDLING_COST = 50
