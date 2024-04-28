from dotenv import load_dotenv
import os


# class Config:
#     JWT_SECRET_KEY = 'change-me-fd0e02667fe62206a40ed9d1c75b0d8a'
#     SECRET_KEY = 'change-me-bea091d14d4247a694461b1816e13b'

#     SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'

#     MAIL_SERVER = 'smtp-relay.brevo.com'
#     MAIL_PORT = 587
#     MAIL_USERNAME = 'stefanmartinuk@gmail.com'
#     MAIL_PASSWORD = 'XYC8jAQMw2D05mkK'
#     MAIL_USE_TLS = True
#     MAIL_USE_SSL = False


# class OAuthConfig:
#     GOOGLE_CLIENT_ID = '60844738170-egvfjsn6201f21qa4jdm2rja61h2j3cq.apps.googleusercontent.com'  # noqa
#     GOOGLE_CLIENT_SECRET = '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'
#     GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'  # noqa


# Load environment variables from .env file
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
