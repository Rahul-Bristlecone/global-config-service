import json
from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from config.extentions import db, redis_client
from config.models.global_config_model import GlobalConfigModel
from config.schemas.global_config_schema import GlobalConfigSchema

# Create blueprint for Global Config
blp = Blueprint("global_config", __name__, description="Operations on global configuration")


def validate_active_session(user_id):
    """
    Validate that the user has an active session in Redis.
    Checks that the JWT token matches the cached session token.
    """
    auth_header = request.headers.get("Authorization", "")
    token_parts = auth_header.split()
    if len(token_parts) != 2:
        abort(401, message="Missing or invalid authorization token")

    token = token_parts[1]
    cached_session = redis_client.get(f"session:{user_id}")
    if not cached_session:
        abort(401, message="Session expired or revoked")

    try:
        session_data = json.loads(cached_session)
        cached_token = session_data.get("token")
    except Exception:
        abort(401, message="Invalid session data")

    if cached_token != token:
        abort(401, message="Session expired or revoked")


def get_user_config_or_create(user_id):
    """
    Retrieve user's global config by user_id.
    If not found, return None (will be created).
    """
    config = GlobalConfigModel.query.filter_by(user_id=user_id).first()
    return config


def save_config_from_payload(config_data):
    """
    Shared logic to save global config.
    Validates JWT, checks Redis session, and persists or updates the config.
    """
    user_id = int(get_jwt_identity())
    validate_active_session(user_id)

    # Try to get existing config
    config = get_user_config_or_create(user_id)

    if config:
        # Update existing config
        for key, value in config_data.items():
            if key not in ["user_id"]:
                setattr(config, key, value)
    else:
        # Create new config
        config = GlobalConfigModel(user_id=user_id, **config_data)

    try:
        db.session.add(config)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message="Configuration already exists for this user")
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message="Error saving configuration to database")

    return config


# -------------------------------
# Endpoint: /glbconfig
# Save/Update Global Config
# -------------------------------
@blp.route("/glbconfig")
class GlobalConfigResource(MethodView):
    @jwt_required()
    @blp.arguments(GlobalConfigSchema(partial=True))
    @blp.response(201, GlobalConfigSchema)
    def post(self, config_data):
        """Save or update global configuration for the authenticated user."""
        return save_config_from_payload(config_data)

    @jwt_required()
    @blp.response(200, GlobalConfigSchema)
    def get(self):
        """Retrieve global configuration for the authenticated user."""
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)

        config = get_user_config_or_create(user_id)
        if not config:
            abort(404, message="Global configuration not found for this user")

        return config
