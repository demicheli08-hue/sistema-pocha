from flask import Blueprint, request, redirect, url_for
from database import get_db_connection

bp = Blueprint('main', __name__)

# --- PANTALLA PRINCIPAL / RESUMEN ---
@bp.route('/')
def index():
    conn = get_db_connection()
    total_productos = conn.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    stock_bajo = conn.execute('SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo').fetchone()[0]
    total_clientes = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
    total_proveedores = conn.execute('SELECT COUNT(*) FROM proveedores').fetchone()[0]
    conn.close()
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Almacén Natural Pocha - Panel</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .cards {{ display: flex; justify-content: space-around; margin: 30px 0; }}
            .card {{ background: #27ae60; color: white; padding: 20px; border-radius: 8px; text-align: center; width: 22%; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .card.warning {{ background: #e74c3c; }}
            .card h3 {{ margin: 0; font-size: 28px; }}
            .card p {{ margin: 5px 0 0; font-size: 14px; }}
            .menu {{ text-align: center; margin-top: 30px; }}
            .btn {{ display: inline-block; padding: 12px 25px; margin: 5px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: 0.3s; }}
            .btn:hover {{ background: #2980b9; }}
            .btn-green {{ background: #27ae60; }}
            .btn-green:hover {{ background: #219653; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌿 Almacén Natural Pocha - Panel de Control</h1>
            <p style="text-align: center; color: #7f8c8d;">Sistema de gestión, stock y ventas en la nube.</p>
            
            <div class="cards">
                <div class="card">
                    <h3>{total_productos}</h3>
                    <p>Productos</p>
                </div>
                <div class="card warning">
                    <h3>{stock_bajo}</h3>
                    <p>Stock Bajo</p>
                </div>
                <div class="card" style="background: #f39c12;">
                    <h3>{total_clientes}</h3>
                    <p>Clientes</p>
                </div>
                <div class="card" style="background: #8e44ad;">
                    <h3>{total_proveedores}</h3>
                    <p>Proveedores</p>
                </div>
            </div>

            <div class="menu">
                <a href="/productos" class="btn btn-green">📦 Ver Productos & Stock</a>
                <a href="/clientes" class="btn">👥 Ver Clientes (Cta. Cte.)</a>
                <a href="/proveedores" class="btn" style="background: #8e44ad;">🚚 Ver Proveedores</a>
            </div>
        </div>
    </body>
    </html>
    """

# --- PRODUCTOS & STOCK ---
@bp.route('/productos')
def productos():
    conn = get_db_connection()
    prods = conn.execute('''
        SELECT p.*, prov.nombre AS proveedor_nombre 
        FROM productos p 
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
    ''').fetchall()
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Productos - Pocha</title>
    <style>
        body { font-family: Arial; background: #f4f6f9; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background: #2c3e50; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        .btn-back { display: inline-block; padding: 10px 15px; background: #7f8c8d; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 15px; }
        .btn-del { color: #e74c3c; text-decoration: none; font-weight: bold; }
    </style>
    </head>
    <body>
    <div class="container">
        <a href="/" class="btn-back">← Volver al Panel</a>
        <h2>📦 Listado de Productos y Stock</h2>
        <table>
            <tr><th>ID</th><th>Producto</th><th>Proveedor</th><th>Costo</th><th>Stock</th><th>Stock Mín.</th><th>Acciones</th></tr>
    """
    for p in prods:
        prov = p['proveedor_nombre'] if p['proveedor_nombre'] else 'Sin Proveedor'
        html += f"<tr><td>{p['id']}</td><td><b>{p['nombre']}</b></td><td>{prov}</td><td>${p['costo']}</td><td>{p['stock']}</td><td>{p['stock_minimo']}</td><td><a href='/producto/eliminar/{p['id']}' class='btn-del' onclick='return confirm(\"¿Estás seguro de eliminar este producto?\");'>Eliminar</a></td></tr>"
    html += "</table></div></body></html>"
    return html

@bp.route('/producto/eliminar/<int:id>')
def eliminar_producto(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.productos'))


# --- CLIENTES ---
@bp.route('/clientes')
def clientes():
    conn = get_db_connection()
    clis = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Clientes - Pocha</title>
    <style>
        body { font-family: Arial; background: #f4f6f9; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background: #f39c12; color: white; }
        .btn-back { display: inline-block; padding: 10px 15px; background: #7f8c8d; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 15px; }
        .btn-del { color: #e74c3c; text-decoration: none; font-weight: bold; }
    </style>
    </head>
    <body>
    <div class="container">
        <a href="/" class="btn-back">← Volver al Panel</a>
        <h2>👥 Gestión de Clientes y Cuenta Corriente</h2>
        <table>
            <tr><th>ID</th><th>Nombre</th><th>Teléfono</th><th>Saldo Cta. Cte.</th><th>Acciones</th></tr>
    """
    for c in clis:
        html += f"<tr><td>{c['id']}</td><td><b>{c['nombre']}</b></td><td>{c['telefono']}</td><td>${c['saldo_cta_cte']}</td><td><a href='/cliente/eliminar/{c['id']}' class='btn-del' onclick='return confirm(\"¿Estás seguro de eliminar este cliente?\");'>Eliminar</a></td></tr>"
    html += "</table></div></body></html>"
    return html

@bp.route('/cliente/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.clientes'))


# --- PROVEEDORES ---
@bp.route('/proveedores')
def proveedores():
    conn = get_db_connection()
    provs = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Proveedores - Pocha</title>
    <style>
        body { font-family: Arial; background: #f4f6f9; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background: #8e44ad; color: white; }
        .btn-back { display: inline-block; padding: 10px 15px; background: #7f8c8d; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 15px; }
        .btn-del { color: #e74c3c; text-decoration: none; font-weight: bold; }
    </style>
    </head>
    <body>
    <div class="container">
        <a href="/" class="btn-back">← Volver al Panel</a>
        <h2>🚚 Gestión de Proveedores</h2>
        <table>
            <tr><th>ID</th><th>Nombre</th><th>Contacto</th><th>Teléfono</th><th>Acciones</th></tr>
    """
    for p in provs:
        html += f"<tr><td>{p['id']}</td><td><b>{p['nombre']}</b></td><td>{p['contacto']}</td><td>{p['telefono']}</td><td><a href='/proveedor/eliminar/{p['id']}' class='btn-del' onclick='return confirm(\"¿Estás seguro de eliminar este proveedor?\");'>Eliminar</a></td></tr>"
    html += "</table></div></body></html>"
    return html

@bp.route('/proveedor/eliminar/<int:id>')
def eliminar_proveedor(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM proveedores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.proveedores'))


def register_routes(app):
    app.register_blueprint(bp)
