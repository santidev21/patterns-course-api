"""
Tests de caracterizacion de /categories.
"""

import pytest

from tests.conftest import auth_headers


def test_get_categories_sin_token_da_401(client):
    resp = client.get('/categories')
    assert resp.status_code == 401


def test_get_categories_con_token_devuelve_lista(client, auth_headers):
    resp = client.get('/categories', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_categoria_por_id(client, auth_headers):
    resp = client.get('/categories/1', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['id'] == 1


def test_crear_categoria(client, auth_headers):
    resp = client.post('/categories', headers=auth_headers, json={'name': 'deportiva'})
    assert resp.status_code == 201


@pytest.mark.xfail(reason='bug 5: la validacion de duplicados compara un string contra una '
                          'lista de dicts, nunca es True, asi que se pueden crear categorias '
                          'repetidas', strict=True)
def test_bug5_no_se_deberia_poder_crear_una_categoria_duplicada(client, auth_headers):
    client.post('/categories', headers=auth_headers, json={'name': 'men'})
    resp = client.post('/categories', headers=auth_headers, json={'name': 'men'})
    assert resp.status_code == 400


def test_eliminar_categoria_existente(client, auth_headers):
    """Hoy funciona por accidente: el filtro roto no se nota porque
    remove_category si escribe el archivo bien. Lo dejo como guardia
    para asegurarnos de que el refactor no lo rompa."""
    resp = client.delete('/categories', headers=auth_headers, json={'name': 'men'})
    assert resp.status_code == 200
    resp = client.get('/categories', headers=auth_headers)
    nombres = [c['name'] for c in resp.get_json()]
    assert 'men' not in nombres


@pytest.mark.xfail(reason='bug 7: la ruta /categories/<id> solo funciona con GET; POST y '
                          'DELETE no reciben category_id y revientan con TypeError (500)',
                   strict=True)
def test_bug7_post_sobre_categoria_por_id_no_deberia_dar_500(client, auth_headers):
    resp = client.post('/categories/1', headers=auth_headers, json={'name': 'x'})
    assert resp.status_code in (405, 404)
