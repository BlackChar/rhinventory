import pytest

from flask import Flask
from flask.testing import FlaskClient
from flask_login import login_user

from rhinventory.app import create_app
from rhinventory.extensions import db
from rhinventory.db import User, Organization
from rhinventory.models.asset import Asset, AssetCategory

class TestAppConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    GITHUB_CLIENT_ID = None
    GITHUB_CLIENT_SECRET = None
    FILES_DIR = "files"
    SECRET_KEY = "abc"


@pytest.fixture()
def app():
    app = create_app(config_object=TestAppConfig)

    with app.app_context():
        db.create_all()

        user = User(username="pytest", read_access=True, write_access=True, admin=True)
        db.session.add(user)

        org = Organization(name="Testing z.s.")
        db.session.add(org)

        db.session.commit()

        user_id = user.id

    @app.login_manager.request_loader
    def load_user_from_request(request):
        return User.query.get(user_id)
    
    yield app

    del app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_index(client: FlaskClient):
    response = client.get("/admin/")
    assert response.status_code == 200
    assert "Vítejte" in response.data.decode('utf-8')


def test_asset_list(client: FlaskClient):
    response = client.get("/admin/asset/")
    assert response.status_code == 200


def test_asset_new(client: FlaskClient):
    url = "/admin/asset/new/"
    asset_name = "Test Object 123"

    client.get(url)
    response = client.post(url, data={
        "organization": "1",
        "category": AssetCategory.game.name,
        "name": asset_name,
    }, follow_redirects=False)
    assert response.status_code in (302, 200)

    response = client.get("/admin/asset/")
    assert response.status_code == 200
    assert asset_name in response.data.decode('utf-8')

    response = client.get("/admin/asset/details/?id=1")
    assert response.status_code == 200
    assert asset_name in response.data.decode('utf-8')

    response = client.get("/admin/asset/edit/?id=1")
    assert response.status_code == 200
    assert asset_name in response.data.decode('utf-8')


def test_transaction_list(client: FlaskClient):
    response = client.get("/admin/transaction/")
    assert response.status_code == 200


def test_file_list(client: FlaskClient):
    response = client.get("/admin/file/")
    assert response.status_code == 200


def test_file_upload(client: FlaskClient):
    response = client.get("/admin/file/upload/")
    assert response.status_code == 200

