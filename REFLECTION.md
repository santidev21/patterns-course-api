# REFLECTION.md — Actividad 2: Refactorización con patrones de diseño

**Curso:** Patrones de Diseño — UTB
**Actividad:** Hacia un código más legible y mantenible en el tiempo
**Repositorio:** https://github.com/santidev21/patterns-course-api

> ⚠️ Este documento lo voy actualizando durante todo el proceso. Al final (Fase 4)
> queda completo con los diagramas, métricas después y las decisiones de diseño.

---

## 1. El proyecto

Es una API REST de una tienda hecha con Flask y Flask-RESTful: productos,
categorías, favoritos y un login que devuelve un token falso. Los datos se
guardan en un archivo `db.json`. El código original está en el commit inicial
(tag `v1.0-original`) y el refactor va en la rama `refactor`.

Según el README original, los endpoints son: `POST /auth`, `GET/POST /products`,
`GET/POST/DELETE /categories` y (sin documentar) `GET/POST/DELETE /favorites`.

## 2. Bugs encontrados en el código original

Los descubrí ejecutando la app y probando endpoint por endpoint con
Insomnia/Postman (capturas en la sección 6). Después escribí tests de
caracterización que documentan el comportamiento actual: **15 tests pasan y
9 quedan marcados con `xfail`** (uno por bug), en `tests/`.

| # | Bug | Dónde | Qué pasa |
|---|-----|-------|----------|
| 1 | El login devuelve un token que no sirve | `endpoints/auth.py:10` | `/auth` entrega `abcd12345` pero `is_valid_token` valida `abcd1234` → todo da 401 |
| 2 | `POST /products` no pide token | `endpoints/products.py:42` | Es el único método que no valida auth, cualquiera puede crear productos |
| 3 | Favoritos roto por dos lados | `endpoints/favorites.py:12,69` | Conecta a `favorites.json` que no existe (los favoritos están en `db.json`), `add_favorite` falla en silencio y `DELETE` llama a `save_favorites()` que no existe → 500 |
| 4 | IDs duplicados | `db.json` (productos 21 y 23 repetidos) | Los IDs se calculan con `len() + 1` en vez de `max(id) + 1` |
| 5 | La validación de categoría duplicada no sirve | `endpoints/categories.py:50` | Compara un string contra una lista de dicts → nunca es `True` → se crean duplicados |
| 6 | `DELETE /categories` funciona de milagro | `endpoints/categories.py:72,85` | Hay un `parse_args()` muerto antes del `add_argument`, y el filtro compara `cat["name"]` contra un dict. Hoy "funciona" porque `remove_category` sí escribe el archivo bien, pero el estado en memoria queda mal y el primer parse no hace nada |
| 7 | `POST/DELETE /categories/<id>` da 500 | `endpoints/categories.py:34,65` | Los métodos no reciben `category_id` → `TypeError` |
| 8 | `GET /products` prioriza mal | `endpoints/products.py:30` | El filtro `?category=` le gana al id: `/products/1?category=women` devuelve una lista y no el producto 1. Además hay un `parse_args()` que no se usa |
| 9 | `POST /auth` sin body da error feo | `endpoints/auth.py:6` | `request.json.get(...)` revienta si no llega JSON → Flask responde 415 en HTML, debería ser un 400 en JSON |

## 3. Code smells y problemas de diseño

| Smell | Dónde | Por qué es un problema | Patrón que propongo |
|-------|-------|------------------------|---------------------|
| Código duplicado (validación de token 8 veces, `is_valid_token` en 3 archivos) | `endpoints/*.py` | Cualquier cambio de auth hay que hacerlo en 8 sitios | Decorator (`@require_auth`) + Strategy |
| God class / CRUD duplicado | `utils/database_connection.py` | Una sola clase mezcla conexión y acceso a datos de 3 entidades, con `get_/add_` casi idénticos | Repository + Template Method |
| SRP violado en los Resources | `endpoints/*.py` | Cada Resource mezcla HTTP, validación, reglas de negocio y persistencia | Service Layer (Facade) |
| Acoplamiento alto + rendimiento | `endpoints/*.py` | Flask-RESTful crea el Resource por request y cada uno abre y relee `db.json` completo | Singleton para la conexión |
| Magic strings | `db.json`, token, credenciales hardcodeadas | Cambiar algo implica buscar por todo el código | `config.py` centralizado |
| Manejo de errores pobre | `utils/database_connection.py` | `print()` y fallos silenciosos en vez de excepciones o logging | Excepciones propias + error handler |
| Código muerto | `app.py:11-13`, imports sin usar, `print("*****")` en `categories.py:44`, `db_bck.json` | Ruido que confunde y puede ejecutar trabajo inútil | Limpieza |
| Inconsistencias | `mensaje` vs `message`, typos (`acces`, `wrond`) | API poco profesional, clientes no saben qué esperar | Contrato de respuesta uniforme |
| Sin validaciones de negocio | precio negativo, categoría inexistente al crear producto | Datos basura en la BD | Reglas en el Service Layer |
| Sin `requirements.txt` ni tests | raíz | Nadie puede reproducir el entorno ni garantizar que sigue funcionando | Entorno + tests de caracterización (ya hechos) |
| `reqparse` deprecado | `endpoints/*.py` | Flask-RESTful lo marca deprecado; además causa el bug 6 | `request.get_json()` + validación manual |

## 4. Métricas antes del refactor

Corridas sobre el código original (nov 2026):

| Herramienta | Resultado |
|-------------|-----------|
| Tests de caracterización | 15 pasan, 9 xfail (los 9 bugs) |
| pylint | **6.27/10** (avisa de duplicate-code, imports sin usar, etc.) |
| radon (complejidad ciclomática) | Promedio A (3.24) — el código es corto, el problema es el diseño |
| radon (maintainability index) | A en todos los módulos |

El MI y la complejidad salen bien porque son archivos chicos; donde de verdad
se nota el problema es en la duplicación (pylint) y en los bugs. Al final
comparo estos números con los del código refactorizado.

## 5. Plan de trabajo

1. ✅ Entorno: `.gitignore`, `requirements.txt` / `requirements-dev.txt`, venv
2. ✅ Tests de caracterización con los bugs marcados como `xfail`
3. ✅ Inventario inicial (este documento)
4. ⏳ Limpieza: código muerto + `config.py` + fix del token
5. ⏳ Capa de datos: Singleton + Repository + Template Method
6. ⏳ Modelos + Factory (IDs con `max() + 1`)
7. ⏳ Auth: Strategy + Decorator
8. ⏳ Service Layer con reglas de negocio
9. ⏳ Resources delgados + App Factory + inyección de dependencias
10. ⏳ Manejo de errores y logging
11. ⏳ Tests finales (quitar xfails) + README
12. ⏳ Diagramas, métricas después, decisiones → este documento
13. ⏳ Revisión con un compañero (PR en GitHub)
14. ⏳ Reflexión final

## 6. Capturas de pantalla

<!-- TODO: pegar capturas de Insomnia/Postman del estado original:
     1. POST /auth devolviendo abcd12345 y luego GET /products con ese token dando 401 (bug 1)
     2. POST /products sin token creando el producto igual (bug 2)
     3. DELETE /favorites dando 500 (bug 3)
     4. POST /categories duplicada devolviendo 201 (bug 5)
     5. POST /categories/1 dando 500 (bug 7)
     6. GET /products/1?category=women devolviendo una lista (bug 8) -->

## 7. Supuestos y decisiones (se van llenando)

- [ ] Se mantiene JSON como almacenamiento (no meto SQL: la actividad es de patrones, no de base de datos).
- [ ] Se respeta el contrato de la API salvo los fixes de bugs (mismos paths, mismos campos).
- [ ] El token sigue siendo falso pero centralizado en config; la idea de la actividad es el diseño, no la seguridad real.
- [ ] `reqparse` se elimina (deprecado) → `request.get_json()`.
- [ ] `db_bck.json`: decisión pendiente (ver commit de limpieza).
- [ ] Por qué no usé más patrones (Observer, Chain of Responsibility...): pendiente de escribir al final.

<!-- TODO (Fase 4): tabla problema → patrón → commit con enlaces,
     diagramas Mermaid antes/después, métricas después, reflexión final. -->
