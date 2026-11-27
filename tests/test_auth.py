"""
Tests de caracterizacion de /auth.

Cada test documenta como funciona el endpoint HOY (nov 2026, antes del
refactor). Los bugs conocidos estan marcados con xfail y numerados para
que coincidan con el inventario del REFLECTION.md.
"""

import pytest

from tests.conftest import USERNAME, PASSWORD, login


def test_login_con_credenciales_correctas_devuelve_token(client):
    resp = client.post('/auth', json={'username': USERNAME, 'password': PASSWORD})
    assert resp.status_code == 200
    body = resp.get_json()
    assert 'token' in body


def test_login_con_contrasena_mala_da_401(client):
    resp = client.post('/auth', json={'username': USERNAME, 'password': 'incorrecta'})
    assert resp.status_code == 401


@pytest.mark.xfail(reason='bug 1: el token que devuelve el login (abcd12345) no coincide '
                          'con el que valida is_valid_token (abcd1234), asi que todo da 401',
                   strict=True)
def test_bug1_el_token_del_login_deberia_servir_para_los_endpoints(client):
    """Con el token que te da /auth, GET /products deberia responder 200."""
    token = login(client)
    resp = client.get('/products', headers={'Authorization': token})
    assert resp.status_code == 200


@pytest.mark.xfail(reason='bug 9: POST /auth sin body devuelve 415 en HTML de Flask, '
                          'deberia ser un 400 en JSON', strict=True)
def test_bug9_login_sin_body_deberia_dar_400_en_json(client):
    resp = client.post('/auth')
    assert resp.status_code == 400
    assert resp.is_json
