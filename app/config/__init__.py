from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-key')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///db.sqlite3')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'example@mail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'password')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true') == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false') == 'false'


class OAuthConfig:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'default-client-id')
    GOOGLE_CLIENT_SECRET = os.getenv(
        'GOOGLE_CLIENT_SECRET', 'default-client-secret')
    GOOGLE_DISCOVERY_URL = os.getenv(
        'GOOGLE_DISCOVERY_URL', 'https://accounts.google.com/.well-known/openid-configuration')  # noqa
