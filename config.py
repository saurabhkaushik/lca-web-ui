import os

class Config(object):
    TESTING = True

class ProductionConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='production'
    AI_SERVICE_URL='https://lca-ai-services-i7kp7xmhka-el.a.run.app'
    DOMAINS =['liabilities', 'esg']
    FUNCTIONS = ['Financial', 'Sustainability']
    DEFAULT_DOMAIN = 'esg'
    DEFAULT_FUNCTION = 'Sustainability'
    DB_HOST = '34.170.168.203'
    DB_USER = 'root'
    DB_PASSWORD = 'nu123456'
    DB_NAME = 'lca_db'
    DATA_ENV = 'cloud'

class DevelopmentConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='development'
    AI_SERVICE_URL='http://34.93.6.90'
    #AI_SERVICE_URL='https://lca-ai-services-i7kp7xmhka-el.a.run.app'
    #AI_SERVICE_URL='http://law-service-app:8081' 
    #AI_SERVICE_URL='http://127.0.0.1:8081'    
    DOMAINS =['liabilities', 'esg']
    FUNCTIONS = ['Financial', 'Sustainability']
    DEFAULT_DOMAIN = 'esg'
    DEFAULT_FUNCTION = 'Sustainability'
    DB_HOST = '34.170.168.203'
    DB_USER = 'root'
    DB_PASSWORD = 'nu123456'
    DB_NAME = 'lca_db'
    DATA_ENV = 'local' 

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True



