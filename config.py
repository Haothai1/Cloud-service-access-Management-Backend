from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    
    # Auth0
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    
    # AWS
    AWS_BUCKET_NAME: str
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str
    ELASTICSEARCH_PORT: int
    
    # RabbitMQ
    RABBITMQ_URL: str
    
    # Redis
    REDIS_URL: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 