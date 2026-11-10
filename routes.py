from flask import Blueprint, redirect, url_for
from database import get_db_connection

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    conn = get_db_connection()
    total_productos = conn.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    total_clientes = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
    total_proveedores = conn.execute('SELECT COUNT(*) FROM proveedores').fetchone()[0]
    conn.close()
    
    return f"""
    <div style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h1 style="color: #2c3e50;">🌿 Almacén Natural Pocha - Sistema Online 🚀</h1>
        <p style="font-size: 18px; color: #555;">El sistema de gestión y control de stock está funcionando correctamente en la nube.</p>
        <hr style="width: 50%; margin: 20px auto;">
        <h3>📊 Resumen del Sistema:</h3>
        <ul style="list-style: none; padding: 0; font-size: 16px;">
            <li>📦 <b>Productos registrados:</b> {total_productos}</li>
            <li>👥 <b>Clientes activos:</b> {total_clientes}</li>
            <li>🚚 <b>Proveedores:</b> {total_proveedores}</li>
        </ul>
        <br>
        <a href="/proveedores" style="padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">Ver Proveedores</a>
        <a href="/clientes" style="padding: 10px 20px; background: #2ecc71; color: white; text-decoration: none; border-radius: 5px;">Ver Clientes</a>
    </div>
    """

@bp.route('/proveedores')
def proveedores():
    conn = get_db_connection()
    provs = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    
    html = "<h2>Gestión de Proveedores</h2><table border='1' cellpadding='8' style='border-collapse: collapse;'><tr><th>ID</th><th>Nombre</th><th>Contacto</th><th>Teléfono</th></tr>"
    for p in provs:
        html += f"<tr><td>{p['id']}</td><td>{p['nombre']}</td><td>{p['contacto']}</td><td>{p['telefono']}</td></tr>"
    html += "</table><br><a href='/'>← Volver al Inicio</a>"
    return html

@bp.route('/clientes')
def clientes():
    conn = get_db_connection()
    clis = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    
    html = "<h2>Gestión de Clientes</h2><table border='1' cellpadding='8' style='border-collapse: collapse;'><tr><th>ID</th><th>Nombre</th><th>Teléfono</th><th>Saldo Cta. Cte.</th></tr>"
    for c in clis:
        html += f"<tr><td>{c['id']}</td><td>{c['nombre']}</td><td>{c['telefono']}</td><td>${c['saldo_cta_cte']}</td></tr>"
    html += "</table><br><a href='/'>← Volver al Inicio</a>"
    return html

def register_routes(app):
    app.register_blueprint(bp)
