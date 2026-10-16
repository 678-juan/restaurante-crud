"""API REST del CRUD de productos de un restaurante (Flask)."""
import os

from flask import Flask, jsonify, request

from src.repositorio import ProductoRepositorio


def validar(datos):
    """Devuelve (datos_limpios, error)."""
    if not isinstance(datos, dict):
        return None, "El cuerpo debe ser un JSON válido"
    nombre = str(datos.get("nombre", "")).strip()
    if not nombre:
        return None, "El nombre es obligatorio"
    try:
        precio = float(datos.get("precio"))
    except (TypeError, ValueError):
        return None, "El precio debe ser un número"
    if precio <= 0:
        return None, "El precio debe ser mayor que cero"
    categoria = str(datos.get("categoria", "General")).strip() or "General"
    return {"nombre": nombre, "precio": precio, "categoria": categoria}, None


def create_app(ruta_db=None):
    app = Flask(__name__)
    repo = ProductoRepositorio(ruta_db or os.getenv("DB_PATH", ":memory:"))

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"})

    @app.post("/productos")
    def crear():
        datos, error = validar(request.get_json(silent=True))
        if error:
            return jsonify({"error": error}), 400
        return jsonify(repo.crear(**datos)), 201

    @app.get("/productos")
    def listar():
        texto = request.args.get("buscar", "").strip()
        return jsonify(repo.buscar(texto) if texto else repo.listar())

    @app.get("/productos/<int:producto_id>")
    def obtener(producto_id):
        producto = repo.obtener(producto_id)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify(producto)

    @app.put("/productos/<int:producto_id>")
    def actualizar(producto_id):
        datos, error = validar(request.get_json(silent=True))
        if error:
            return jsonify({"error": error}), 400
        producto = repo.actualizar(producto_id, **datos)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify(producto)

    @app.delete("/productos/<int:producto_id>")
    def eliminar(producto_id):
        if not repo.eliminar(producto_id):
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify({"mensaje": "Producto eliminado"})

    return app


# Punto de entrada para gunicorn: gunicorn "src.app:app"
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
