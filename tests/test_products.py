"""
Tests de caracterizacion de /products.
"""

import pytest

from tests.conftest import auth_headers


def test_get_products_sin_token_da_401(client):
    resp = client.get('/products')
    assert resp.status_code == 401


def test_get_products_con_token_valido_devuelve_lista(client, auth_headers):
    resp = client.get('/products', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_product_por_id(client, auth_headers):
    resp = client.get('/products/1', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['id'] == 1


def test_get_product_que_no_existe_da_404(client, auth_headers):
    resp = client.get('/products/9999', headers=auth_headers)
    assert resp.status_code == 404


def test_filtrar_por_categoria(client, auth_headers):
    resp = client.get('/products?category=men', headers=auth_headers)
    assert resp.status_code == 200
    categorias = {p['category'] for p in resp.get_json()}
    assert categorias == {'men'}


def test_crear_producto_con_token_y_datos_validos(client, auth_headers):
    resp = client.post('/products', headers=auth_headers,
                       json={'name': 'Camisa nueva', 'category': 'men', 'price': 25.0})
    assert resp.status_code == 201
    assert resp.get_json()['product']['name'] == 'Camisa nueva'


@pytest.mark.xfail(reason='bug 2: POST /products es el unico metodo que no valida el token',
                   strict=True)
def test_bug2_crear_producto_sin_token_deberia_dar_401(client):
    resp = client.post('/products', json={'name': 'x', 'category': 'men', 'price': 5})
    assert resp.status_code == 401


@pytest.mark.xfail(reason='bug 4: hay ids duplicados en db.json (21 y 23) porque los ids '
                          'se calculan con len() + 1', strict=True)
def test_bug4_los_ids_de_los_productos_deberian_ser_unicos(client, auth_headers):
    resp = client.get('/products', headers=auth_headers)
    ids = [p['id'] for p in resp.get_json()]
    assert len(ids) == len(set(ids))


@pytest.mark.xfail(reason='bug 8: el filtro por categoria le gana al id, asi que '
                          '/products/1?category=women devuelve una lista y no el producto 1',
                   strict=True)
def test_bug8_el_id_deberia_tener_prioridad_sobre_el_filtro(client, auth_headers):
    resp = client.get('/products/1?category=women', headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body, dict)
    assert body['id'] == 1
