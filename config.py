import os

class Config(object):
    TESTING = True

class ProductionConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='production'
    DOMAINS =['liabilities', 'esg']
    DOMAINS_THRESHOLD = [98, 80]
    FUNCTIONS = ['Financial', 'Sustainability']
    DEFAULT_DOMAIN = 'esg'
    DEFAULT_FUNCTION = 'Sustainability'
    DB_HOST = '34.93.121.15'
    DB_USER = 'root'
    DB_PASSWORD = 'Nu123456$$'
    DB_NAME = 'lca_prod'

class DevelopmentConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='development'
    DOMAINS =['liabilities', 'esg']
    DOMAINS_THRESHOLD = [98, 80]
    FUNCTIONS = ['Financial', 'Sustainability']
    DEFAULT_DOMAIN = 'esg'
    DEFAULT_FUNCTION = 'Sustainability'
    DB_HOST = '34.93.121.15'
    DB_USER = 'root'
    DB_PASSWORD = 'Nu123456$$'
    DB_NAME = 'lca_dev'

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True



