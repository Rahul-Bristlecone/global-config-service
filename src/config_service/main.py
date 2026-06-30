import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_cors import CORS

from config_service.extentions.db import db

# Import all models to register them with SQLAlchemy
from config_service.models.global_config_model import GlobalConfigModel
from config_service.resources.global_config import blp as GlobalConfigBp

# This is called factory pattern

def create_app(db_url=None):
    config_service = Flask(__name__)
    config_service.config["CORS_AUTOMATIC_OPTIONS"] = True
    config_service.config["PROPAGATE_EXCEPTIONS"] = True
    config_service.config["API_TITLE"] = "Global Config Service API"
    config_service.config["API_VERSION"] = "v1"
    config_service.config["OPENAPI_VERSION"] = "3.0.3"
    config_service.config["OPENAPI_URL_PREFIX"] = "/"
    config_service.config['TESTING'] = True
    config_service.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    config_service.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # Configure CORS for production
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins]
    
    CORS(
        config_service,
        origins=allowed_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        intercept_exceptions=True
    )

    """ 
        for SQLite, local database file is created in the data directory of the config service application.
        This is useful for development and testing purposes, as it allows the application to run without needing an 
        external database server. (not to be used in production)
        
        config_service.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/config_data.db"
    """

    # *** for SQLite - app directory is created inside container for data persistence but containers are ephemeral ***
    # config_service.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////app/config_service/src/config_service/data/config_data.db"

    """
        for MySQL, the database is created in a separate container and the config service container connects to it 
        using the MySQL driver.
        Note: The database connection string is in the format:
        "mysql+pymysql://<username>:<password>@<host>/<database_name>"
        where:
        - <username> is the MySQL username
        - <password> is the MySQL password
        - <host> is the hostname or IP address of the MySQL server
        - <database_name> is the name of the database to connect to
    """

    SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
                               f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('MYSQL_DATABASE')}")
    
    print("Connecting to DB:", SQLALCHEMY_DATABASE_URI)  # helpful for debugging

    config_service.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    db.init_app(config_service)  # db is SQLAlchemy extension

    with config_service.app_context():
        db.create_all()

    api = Api(config_service)

    """
        Note: As the config service is consuming (validating) JWT tokens, the following code configures JWT 
        (JSON Web Token) handling for the config service. JWT is a compact, URL-safe means of representing 
        claims to be transferred securely between two parties.
    
        According to JWT best practices and documentation:
        1. Assign a secret key (JWT_SECRET_KEY) that matches the issuing service's key. 
        This key is used to verify and trust that incoming JWT tokens were genuinely issued by the correct application.
        2. Initialize JWTManager with the Flask application; it handles JWT tokens and their validation lifecycle.
        3. JWT_SECRET_KEY is used to verify the cryptographic signature of incoming JWT tokens —
        this validation ensures that the token has not been forged or tampered with.
        4. JWT_TOKEN_LOCATION specifies where the application should look for JWT tokens in each request 
        (e.g., headers, cookies).
    
        *** To check if a token is valid and not forged or tampered with, the service recalculates the token's 
        cryptographic signature using the shared secret key. The newly computed signature is compared with the 
        signature part of the token; if they match, the token is authentic and untampered.
        (Note: JWT signatures are verified, not decrypted—JWT does not use decryption for this process.)
        ***
    """

    config_service.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    config_service.config["JWT_TOKEN_LOCATION"] = ["headers"]
    JWTManager(config_service)

    @config_service.route("/health")
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "global-config-service"}), 200

    # Register blueprints
    api.register_blueprint(GlobalConfigBp)

    return config_service
