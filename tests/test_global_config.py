import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from flask_smorest import Api
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from config_service.extentions import db
from config_service.models.global_config_model import GlobalConfigModel
from config_service.schemas.global_config_schema import GlobalConfigSchema
from config_service.resources.global_config import blp


class GlobalConfigTestCase(unittest.TestCase):
    """PyUnit test cases for Global Config endpoints."""

    def setUp(self):
        """Set up test client and app context."""
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["JWT_SECRET_KEY"] = "test-secret-key"
        self.app.config["API_TITLE"] = "Global Config API"
        self.app.config["API_VERSION"] = "v1"
        self.app.config["OPENAPI_VERSION"] = "3.0.2"
        self.app.config["PROPAGATE_EXCEPTIONS"] = True

        db.init_app(self.app)
        JWTManager(self.app)
        api = Api(self.app)
        api.register_blueprint(blp)

        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()
        self.user_id = 1

    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_auth_token(self, user_id=None):
        """Helper to create JWT token."""
        if user_id is None:
            user_id = self.user_id
        with self.app.app_context():
            return create_access_token(identity=str(user_id))

    def _get_headers(self, user_id=None, token=None):
        """Helper to create request headers with JWT."""
        if token is None:
            token = self._create_auth_token(user_id)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    @patch("config_service.resources.global_config.redis_client")
    def test_post_create_global_config(self, mock_redis):
        """Test POST /glbconfig to create new global config."""
        mock_redis.get.return_value = json.dumps({
            "token": self._create_auth_token(self.user_id)
        })

        payload = {
            "DAYSBEFORENOTBEFORE": 5,
            "DAYSBEFORENOTAFTER": 10,
            "ALLOWHANDPICK": 1,
            "ALLOWOVERPICK": 0,
            "INVGENMETHOD": "AUTO",
            "DAYSTOSHOW": 30,
            "DEFAULTSENDMETHODKEY": "EMAIL",
            "PDTCOMPORT": "COM1",
            "PDTCOMSPEED": 9600,
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["DAYSBEFORENOTAFTER"], 10)
        self.assertEqual(data["ALLOWHANDPICK"], 1)
        self.assertEqual(data["INVGENMETHOD"], "AUTO")

    @patch("config_service.resources.global_config.redis_client")
    def test_post_update_existing_global_config(self, mock_redis):
        """Test POST /glbconfig to update existing config."""
        token = self._create_auth_token(self.user_id)
        
        # Mock Redis session
        mock_redis.get.return_value = json.dumps({"token": token})

        # Create initial config
        with self.app.app_context():
            config = GlobalConfigModel(
                user_id=self.user_id,
                ALLOWHANDPICK=0,
                DAYSTOSHOW=20
            )
            db.session.add(config)
            db.session.commit()

        # Update config
        payload = {
            "ALLOWHANDPICK": 1,
            "DAYSTOSHOW": 30,
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["ALLOWHANDPICK"], 1)
        self.assertEqual(data["DAYSTOSHOW"], 30)

    @patch("config_service.resources.global_config.redis_client")
    def test_get_global_config(self, mock_redis):
        """Test GET /glbconfig to retrieve config."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        with self.app.app_context():
            config = GlobalConfigModel(
                user_id=self.user_id,
                DAYSBEFORENOTAFTER=10,
                ALLOWHANDPICK=1,
                PDTCOMPORT="COM1",
                INVGENMETHOD="AUTO",
                LABELPRINTERNAME="Zebra ZT230",
                CHECKEVERYMINUTES=15,
                ALLOWSPLITBYSTORE=1,
                BACKUPAFTERSHUTDOWN=1,
                BACKUPPROGRAM="BackupTool"
            )
            db.session.add(config)
            db.session.commit()

        response = self.client.get(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["user_id"], self.user_id)
        self.assertEqual(data["DAYSBEFORENOTAFTER"], 10)
        self.assertEqual(data["PDTCOMPORT"], "COM1")
        self.assertEqual(data["INVGENMETHOD"], "AUTO")
        self.assertEqual(data["LABELPRINTERNAME"], "Zebra ZT230")
        self.assertEqual(data["CHECKEVERYMINUTES"], 15)
        self.assertEqual(data["ALLOWSPLITBYSTORE"], 1)
        self.assertEqual(data["BACKUPAFTERSHUTDOWN"], 1)
        self.assertEqual(data["BACKUPPROGRAM"], "BackupTool")

    @patch("config_service.resources.global_config.redis_client")
    def test_get_global_config_not_found(self, mock_redis):
        """Test GET /glbconfig returns 404 when config doesn't exist."""
        token = self._create_auth_token(self.user_id)
        
        # Mock Redis session
        mock_redis.get.return_value = json.dumps({"token": token})

        response = self.client.get(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token)
        )

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("not found", data["message"].lower())

    def test_post_missing_authorization_header(self):
        """Test POST /glbconfig without Authorization header."""
        payload = {"DAYSTOSHOW": 30}

        response = self.client.post(
            "/glbconfig",
            data=json.dumps(payload),
            content_type="application/json"
        )

        # JWT required should reject
        self.assertEqual(response.status_code, 401)

    @patch("config_service.resources.global_config.redis_client")
    def test_post_invalid_session(self, mock_redis):
        """Test POST /glbconfig with invalid session in Redis."""
        token = self._create_auth_token(self.user_id)
        
        # Mock Redis to return no session
        mock_redis.get.return_value = None

        payload = {"DAYSTOSHOW": 30}

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("expired", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    def test_post_mismatched_token(self, mock_redis):
        """Test POST /glbconfig with token mismatch."""
        token = self._create_auth_token(self.user_id)
        
        # Mock Redis with different token
        mock_redis.get.return_value = json.dumps({
            "token": "different-token-xyz"
        })

        payload = {"DAYSTOSHOW": 30}

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("expired", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    def test_post_boolean_field_validation(self, mock_redis):
        """Test POST /glbconfig with valid boolean fields."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        payload = {
            "ALLOWHANDPICK": 1,
            "ALLOWOVERPICK": 0,
            "THIRDPARTYPACKER": 1,
            "ALLOWORDERFORWARDING": 0,
            "SHOWCOSTPRICE": 1,
            "ALLOWSPLITBYSTORE": 1,
            "CLEARNEWORDFLGONCMD": 1,
            "CLEARNEWORDFLGONDISP": 0,
            "CLEARNEWORDFLGONPRNT": 1,
            "AUTOIMPORTEXTORD": 0,
            "BACKUPAFTERSHUTDOWN": 1,
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["ALLOWHANDPICK"], 1)
        self.assertEqual(data["ALLOWOVERPICK"], 0)
        self.assertEqual(data["SHOWCOSTPRICE"], 1)
        self.assertEqual(data["ALLOWSPLITBYSTORE"], 1)
        self.assertEqual(data["CLEARNEWORDFLGONCMD"], 1)
        self.assertEqual(data["BACKUPAFTERSHUTDOWN"], 1)

    @patch("config_service.resources.global_config.redis_client")
    def test_post_string_fields(self, mock_redis):
        """Test POST /glbconfig with string fields."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        payload = {
            "PDTCOMPORT": "COM3",
            "PRINTERCOMPORT": "COM4",
            "LABELPRINTERNAME": "Zebra ZT230",
            "SCMLABELFORMAT": "Custom Format",
            "DEFAULTSENDMETHODKEY": "EMAIL",
            "INVGENMETHOD": "MANUAL",
            "EXTDLLNAME": "ext_orders.dll",
            "BACKUPCOMMAND": "/usr/bin/backup.sh",
            "BACKUPPROGRAM": "BackupTool",
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["PDTCOMPORT"], "COM3")
        self.assertEqual(data["LABELPRINTERNAME"], "Zebra ZT230")
        self.assertEqual(data["INVGENMETHOD"], "MANUAL")
        self.assertEqual(data["EXTDLLNAME"], "ext_orders.dll")
        self.assertEqual(data["BACKUPPROGRAM"], "BackupTool")

    @patch("config_service.resources.global_config.redis_client")
    def test_post_new_order_flags(self, mock_redis):
        """Test POST /glbconfig with new order flag fields."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        payload = {
            "NEWORDERACTION": 2,
            "DISPLAYNEWORDERFLAG": 1,
            "CLEARNEWORDFLGONCMD": 1,
            "CLEARNEWORDFLGONDISP": 0,
            "CLEARNEWORDFLGONPRNT": 1,
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["NEWORDERACTION"], 2)
        self.assertEqual(data["DISPLAYNEWORDERFLAG"], 1)
        self.assertEqual(data["CLEARNEWORDFLGONCMD"], 1)
        self.assertEqual(data["CLEARNEWORDFLGONDISP"], 0)
        self.assertEqual(data["CLEARNEWORDFLGONPRNT"], 1)

    @patch("config_service.resources.global_config.redis_client")
    def test_post_edi_and_splits(self, mock_redis):
        """Test POST /glbconfig with EDI and splits fields."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        payload = {
            "DEFAULTSENDMETHODKEY": "FTP",
            "CHECKEVERYMINUTES": 30,
            "ALLOWSPLITBYSTORE": 1,
            "MAXIMUMSPLITS": 4,
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["DEFAULTSENDMETHODKEY"], "FTP")
        self.assertEqual(data["CHECKEVERYMINUTES"], 30)
        self.assertEqual(data["ALLOWSPLITBYSTORE"], 1)
        self.assertEqual(data["MAXIMUMSPLITS"], 4)

    @patch("config_service.resources.global_config.redis_client")
    def test_post_shutdown_fields(self, mock_redis):
        """Test POST /glbconfig with shutdown/backup fields."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        payload = {
            "BACKUPAFTERSHUTDOWN": 1,
            "BACKUPCOMMAND": "/usr/local/bin/backup.sh",
            "BACKUPPROGRAM": "BackupTool",
        }

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["BACKUPAFTERSHUTDOWN"], 1)
        self.assertEqual(data["BACKUPCOMMAND"], "/usr/local/bin/backup.sh")
        self.assertEqual(data["BACKUPPROGRAM"], "BackupTool")

    def test_get_missing_authorization_header(self):
        """Test GET /glbconfig without Authorization header."""
        response = self.client.get("/glbconfig")
        self.assertEqual(response.status_code, 401)

    # ------------------------------------------------------------------
    # Targeted tests for uncovered lines
    # ------------------------------------------------------------------

    @patch("config_service.resources.global_config.redis_client")
    def test_post_malformed_authorization_header(self, mock_redis):
        """Covers line 23: auth header with != 2 parts triggers 401."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        response = self.client.post(
            "/glbconfig",
            headers={"Authorization": "InvalidHeader", "Content-Type": "application/json"},
            data=json.dumps({"DAYSTOSHOW": 10}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("invalid", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    def test_get_expired_session(self, mock_redis):
        """Covers line 29: Redis returns None → session expired on GET."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = None

        response = self.client.get(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token)
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("expired", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    def test_post_invalid_json_in_redis_session(self, mock_redis):
        """Covers lines 33-34: Redis returns non-JSON → invalid session data."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = "not-valid-json"

        response = self.client.post(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token),
            data=json.dumps({"DAYSTOSHOW": 10}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("invalid session", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    def test_get_token_mismatch(self, mock_redis):
        """Covers line 37: cached token != request token on GET."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": "completely-different-token"})

        response = self.client.get(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token)
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("expired", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    def test_get_global_config_not_found_404(self, mock_redis):
        """Covers lines 103-104: GET returns 404 when no config exists."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})

        response = self.client.get(
            "/glbconfig",
            headers=self._get_headers(self.user_id, token)
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("not found", data["message"].lower())

    @patch("config_service.resources.global_config.redis_client")
    @patch("config_service.resources.global_config.db")
    def test_post_sqlalchemy_error(self, mock_db, mock_redis):
        """Covers lines 76-79: SQLAlchemyError during commit → 500."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})
        mock_db.session.add.return_value = None
        mock_db.session.commit.side_effect = SQLAlchemyError("DB error")
        mock_db.session.rollback.return_value = None

        # Also patch the query to return None so the create branch is hit
        with patch("config_service.resources.global_config.GlobalConfigModel") as mock_model:
            mock_model.query.filter_by.return_value.first.return_value = None
            mock_model.return_value = MagicMock()

            response = self.client.post(
                "/glbconfig",
                headers=self._get_headers(self.user_id, token),
                data=json.dumps({"DAYSTOSHOW": 10}),
                content_type="application/json"
            )
        self.assertEqual(response.status_code, 500)

    @patch("config_service.resources.global_config.redis_client")
    @patch("config_service.resources.global_config.db")
    def test_post_integrity_error(self, mock_db, mock_redis):
        """Covers lines 73-75: IntegrityError during commit → 400."""
        token = self._create_auth_token(self.user_id)
        mock_redis.get.return_value = json.dumps({"token": token})
        mock_db.session.add.return_value = None
        mock_db.session.commit.side_effect = IntegrityError("stmt", "params", Exception("orig"))
        mock_db.session.rollback.return_value = None

        with patch("config_service.resources.global_config.GlobalConfigModel") as mock_model:
            mock_model.query.filter_by.return_value.first.return_value = None
            mock_model.return_value = MagicMock()

            response = self.client.post(
                "/glbconfig",
                headers=self._get_headers(self.user_id, token),
                data=json.dumps({"DAYSTOSHOW": 10}),
                content_type="application/json"
            )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
