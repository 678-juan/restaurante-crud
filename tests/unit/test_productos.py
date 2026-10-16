import pytest

from src.app import create_app
from src.repositorio import ProductoRepositorio


@pytest.fixture
def repo():
    return ProductoRepositorio(":memory:")


@pytest.fixture
def client():
    app = create_app(":memory:")
    app.config["TESTING"] = True
    return app.test_client()


# ───────── Pruebas de la capa de datos ─────────
def test_crear_producto(repo):
    p = repo.crear("Hamburguesa", 15000, "Platos fuertes")
    assert p["id"] == 1
    assert p["nombre"] == "Hamburguesa"


def test_listar_productos(repo):
    repo.crear("Pizza", 20000)
    repo.crear("Jugo de mora", 6000, "Bebidas")
    assert len(repo.listar()) == 2


def test_buscar_por_nombre_y_categoria(repo):
    repo.crear("Jugo de mora", 6000, "Bebidas")
    repo.crear("Pizza", 20000, "Platos fuertes")
    assert [p["nombre"] for p in repo.buscar("jugo")] == ["Jugo de mora"]
    assert [p["nombre"] for p in repo.buscar("Platos")] == ["Pizza"]
    assert repo.buscar("xyz") == []


def test_actualizar_producto(repo):
    p = repo.crear("Pizza", 20000)
    nuevo = repo.actualizar(p["id"], "Pizza grande", 25000, "Platos fuertes")
    assert nuevo["nombre"] == "Pizza grande"
    assert nuevo["precio"] == 25000


def test_actualizar_inexistente(repo):
    assert repo.actualizar(99, "X", 1, "Y") is None


def test_eliminar_producto(repo):
    p = repo.crear("Pizza", 20000)
    assert repo.eliminar(p["id"]) is True
    assert repo.obtener(p["id"]) is None
    assert repo.eliminar(p["id"]) is False


# ───────── Pruebas de la API ─────────
def test_salud(client):
    assert client.get("/salud").get_json() == {"estado": "ok"}


def test_api_crud_completo(client):
    r = client.post("/productos", json={"nombre": "Pizza", "precio": 20000})
    assert r.status_code == 201
    pid = r.get_json()["id"]

    assert client.get(f"/productos/{pid}").status_code == 200

    r = client.put(f"/productos/{pid}", json={"nombre": "Pizza XL", "precio": 30000})
    assert r.get_json()["nombre"] == "Pizza XL"

    assert len(client.get("/productos?buscar=XL").get_json()) == 1

    assert client.delete(f"/productos/{pid}").status_code == 200
    assert client.get(f"/productos/{pid}").status_code == 404


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"precio": 100},                       # sin nombre
        {"nombre": "  ", "precio": 100},       # nombre vacío
        {"nombre": "Pizza", "precio": "abc"},  # precio no numérico
        {"nombre": "Pizza", "precio": -5},     # precio negativo
    ],
)
def test_api_validaciones(client, cuerpo):
    assert client.post("/productos", json=cuerpo).status_code == 400


def test_api_404(client):
    assert client.get("/productos/999").status_code == 404
    assert client.put("/productos/999", json={"nombre": "A", "precio": 1}).status_code == 404
    assert client.delete("/productos/999").status_code == 404
