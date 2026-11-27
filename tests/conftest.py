"""
Fixture compartida para los tests de caracterizacion.

La idea es simple: la app original siempre abre el archivo 'db.json' relativo
al directorio de trabajo, asi que copiamos el db.json original a un directorio
temporal y hacemos chdir ahi para no ensuciar el archivo real en cada test.
"""

import shutil

import pytest

from app import app


TOKEN_VALIDO = 'abcd1234'  # el que espera is_valid_token
USERNAME = 'student'
PASSWORD = 'desingp'


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Client de Flask apuntando a una copia temporal de db.json."""
    shutil.copy('db.json', tmp_path / 'db.json')
    monkeypatch.chdir(tmp_path)
    with app.test_client() as c:
        yield c


@pytest.fixture
def auth_headers():
    """Headers con el token estatico que la app original considera valido."""
    return {'Authorization': TOKEN_VALIDO}


def login(client):
    """Hace login contra /auth y devuelve el token que genera la app."""
    resp = client.post('/auth', json={'username': USERNAME, 'password': PASSWORD})
    assert resp.status_code == 200
    return resp.get_json()['token']
