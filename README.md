# CRUD de productos de un restaurante + Pipeline CI/CD

API REST mínima (Flask + SQLite) para agregar, editar, buscar y eliminar productos.

## Ejecutar local
    pip install -r requirements.txt
    python -m src.app            # http://localhost:8000
    pytest tests/unit/ -v        # pruebas unitarias

## Endpoints
| Método | Ruta | Acción |
|---|---|---|
| POST | /productos | Agregar |
| GET | /productos?buscar=texto | Listar / buscar |
| GET | /productos/<id> | Consultar uno |
| PUT | /productos/<id> | Editar |
| DELETE | /productos/<id> | Eliminar |
| GET | /salud | Health check |

## Pipeline
`.github/workflows/ci-cd.yml`: push -> Build & Test -> Docker Build & Push (GHCR) -> Deploy + smoke test.
