from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from db import init_db, fetch_all, fetch_one, execute

load_dotenv()

ALLOWED_DIFICULTAD = {"bajo", "medio", "alto"}
ALLOWED_ESTADO = {"pendiente", "en proceso", "completado"}

def create_app():
    app = Flask(__name__)
    CORS(app)  # Permite peticiones desde el frontend (otro puerto)

    # Inicializa DB al arrancar
    init_db()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/retos")
    def listar_retos():
        categoria = request.args.get("categoria")
        dificultad = request.args.get("dificultad")

        base = "SELECT id, titulo, descripcion, categoria, dificultad, estado, created_at FROM retos"
        where = []
        params = []

        if categoria:
            where.append("categoria = %s")
            params.append(categoria)
        if dificultad:
            where.append("dificultad = %s")
            params.append(dificultad)

        if where:
            base += " WHERE " + " AND ".join(where)
        base += " ORDER BY created_at DESC, id DESC"

        data = fetch_all(base, params)
        return jsonify({"retos": data})

    @app.post("/retos")
    def crear_reto():
        payload = request.get_json(silent=True) or {}
        titulo = payload.get("titulo", "").strip()
        descripcion = payload.get("descripcion", "").strip()
        categoria = payload.get("categoria", "").strip()
        dificultad = payload.get("dificultad", "").strip().lower()
        estado = payload.get("estado", "pendiente").strip().lower()

        # Validaciones mínimas
        missing = [k for k,v in {
            "titulo": titulo, "descripcion": descripcion,
            "categoria": categoria, "dificultad": dificultad
        }.items() if not v]
        if missing:
            return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

        if dificultad not in ALLOWED_DIFICULTAD:
            return jsonify({"error": "dificultad inválida (bajo|medio|alto)"}), 400
        if estado not in ALLOWED_ESTADO:
            return jsonify({"error": "estado inválido (pendiente|en proceso|completado)"}), 400

        row = execute("""
            INSERT INTO retos (titulo, descripcion, categoria, dificultad, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, titulo, descripcion, categoria, dificultad, estado, created_at
        """, [titulo, descripcion, categoria, dificultad, estado])

        return jsonify(row), 201

    @app.put("/retos/<int:reto_id>")
    def actualizar_estado(reto_id):
        payload = request.get_json(silent=True) or {}
        estado = (payload.get("estado") or "").strip().lower()
        if not estado:
            return jsonify({"error": "Falta 'estado'"}), 400
        if estado not in ALLOWED_ESTADO:
            return jsonify({"error": "estado inválido (pendiente|en proceso|completado)"}), 400

        updated = execute("""
            UPDATE retos SET estado = %s
            WHERE id = %s
            RETURNING id, titulo, descripcion, categoria, dificultad, estado, created_at
        """, [estado, reto_id])

        if not updated:
            return jsonify({"error": "Reto no encontrado"}), 404
        return jsonify(updated)

    @app.delete("/retos/<int:reto_id>")
    def eliminar_reto(reto_id):
        deleted = execute("""
            DELETE FROM retos WHERE id = %s
            RETURNING id
        """, [reto_id])
        if not deleted:
            return jsonify({"error": "Reto no encontrado"}), 404
        return jsonify({"ok": True, "id": deleted["id"]})

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
