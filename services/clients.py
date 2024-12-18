import stripe
from elasticsearch import Elasticsearch
import pika
import redis
from auth0.authentication import GetToken
from config import get_settings
import boto3

settings = get_settings()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize Elasticsearch
es_client = Elasticsearch(
    [f"{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"]
)

# Initialize Redis
redis_client = redis.from_url(settings.REDIS_URL)

# AWS S3 client function
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

# Auth0 client
def get_auth0_token():
    get_token = GetToken(settings.AUTH0_DOMAIN)
    return get_token.client_credentials(
        settings.AUTH0_CLIENT_ID,
        settings.AUTH0_CLIENT_SECRET,
        f"https://{settings.AUTH0_DOMAIN}/api/v2/"
    )

# RabbitMQ connection
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(
        pika.URLParameters(settings.RABBITMQ_URL)
    )
    return connection.channel() 