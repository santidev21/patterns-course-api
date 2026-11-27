"""
Tests de caracterizacion de /favorites.
"""

import pytest

from tests.conftest import auth_headers


def test_get_favorites_sin_token_da_401(client):
    resp = client.get('/favorites')
    assert resp.status_code == 401


def test_get_favorites_con_token_devuelve_lista(client, auth_headers):
    resp = client.get('/favorites', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


@pytest.mark.xfail(reason='bug 3: el recurso conecta a favorites.json que no existe, asi que '
                          'add_favorite falla en silencio y el favorito nunca se guarda',
                   strict=True)
def test_bug3a_el_favorito_agregado_deberia_persistir(client, auth_headers):
    client.post('/favorites', headers=auth_headers,
                json={'user_id': 1, 'product_id': 2})
    resp = client.get('/favorites', headers=auth_headers)
    favoritos = resp.get_json()
    assert {'user_id': 1, 'product_id': 2} in favoritos


@pytest.mark.xfail(reason='bug 3: DELETE /favorites llama a self.db.save_favorites() y ese '
                          'metodo no existe, da AttributeError (500)', strict=True)
def test_bug3b_eliminar_favorito_deberia_dar_200(client, auth_headers):
    resp = client.delete('/favorites', headers=auth_headers,
                         json={'user_id': 1, 'product_id': 2})
    assert resp.status_code == 200
