"""Capa de datos: CRUD de productos del restaurante usando SQLite."""
import sqlite3
import threading


class ProductoRepositorio:
    def __init__(self, ruta_db=":memory:"):
        self._conn = sqlite3.connect(ruta_db, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL DEFAULT 'General',
                precio REAL NOT NULL
            )"""
        )
        self._conn.commit()

    # CREATE
    def crear(self, nombre, precio, categoria="General"):
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO productos (nombre, categoria, precio) VALUES (?, ?, ?)",
                (nombre, categoria, precio),
            )
            self._conn.commit()
            return self.obtener(cur.lastrowid)

    # READ
    def obtener(self, producto_id):
        fila = self._conn.execute(
            "SELECT * FROM productos WHERE id = ?", (producto_id,)
        ).fetchone()
        return dict(fila) if fila else None

    def listar(self):
        filas = self._conn.execute("SELECT * FROM productos ORDER BY id").fetchall()
        return [dict(f) for f in filas]

    # SEARCH
    def buscar(self, texto):
        patron = f"%{texto}%"
        filas = self._conn.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? OR categoria LIKE ? ORDER BY id",
            (patron, patron),
        ).fetchall()
        return [dict(f) for f in filas]

    # UPDATE
    def actualizar(self, producto_id, nombre, precio, categoria):
        with self._lock:
            cur = self._conn.execute(
                "UPDATE productos SET nombre = ?, categoria = ?, precio = ? WHERE id = ?",
                (nombre, categoria, precio, producto_id),
            )
            self._conn.commit()
            if cur.rowcount == 0:
                return None
            return self.obtener(producto_id)

    # DELETE
    def eliminar(self, producto_id):
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM productos WHERE id = ?", (producto_id,)
            )
            self._conn.commit()
            return cur.rowcount > 0
