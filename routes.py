from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db_connection

bp = Blueprint('main', __name__)

# --- PANTALLA PRINCIPAL / RESUMEN ---
@bp.route('/')
def index():
    conn = get_db_connection()
    total_productos = conn.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    stock_bajo = conn.execute('SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo').fetchone()[0]
    total_clientes = conn.execute('SELECT COUNT(*) FROM clientes WHERE saldo_cta_cte > 0').fetchone()[0]
    
    # Margen general actual
    margen_config = conn.execute("SELECT valor FROM config WHERE clave = 'margen_general'").fetchone()
    margen_general = margen_config[0] if margen_config else "30"
    
    conn.close()
    return render_template('index.html', 
                           total_productos=total_productos, 
                           stock_bajo=stock_bajo, 
                           total_clientes=total_clientes,
                           margen_general=margen_general)

# --- PRODUCTOS & STOCK ---
@bp.route('/productos')
def productos():
    conn = get_db_connection()
    prods = conn.execute('''
        SELECT p.*, prov.nombre AS proveedor_nombre 
        FROM productos p 
        LEFT JOIN proveedores prov ON p.proveedor_id = prov.id
    ''').fetchall()
    proveedores = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    return render_template('productos.html', productos=prods, proveedores=proveedores)

@bp.route('/producto/nuevo', methods=['POST'])
def nuevo_producto():
    nombre = request.form['nombre']
    proveedor_id = request.form['proveedor_id']
    costo = float(request.form['costo'])
    margen_individual = request.form.get('margen_individual')
    stock = float(request.form['stock'])
    stock_minimo = float(request.form.get('stock_minimo', 5.0))
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, proveedor_id, costo, margen_individual if margen_individual else None, stock, stock_minimo))
    conn.commit()
    conn.close()
    return redirect(url_for('main.productos'))

@bp.route('/producto/eliminar/<int:id>')
def eliminar_producto(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.productos'))

# --- NUEVA VENTA (CAJA) ---
@bp.route('/ventas', methods=['GET', 'POST'])
def ventas():
    conn = get_db_connection()
    if request.method == 'POST':
        # Lógica básica de venta
        pass
    productos = conn.execute('SELECT * FROM productos WHERE stock > 0').fetchall()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('ventas.html', productos=productos, clientes=clientes)

# --- CLIENTES (CTA. CTE.) ---
@bp.route('/clientes')
def clientes():
    conn = get_db_connection()
    clis = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clis)

@bp.route('/cliente/nuevo', methods=['POST'])
def nuevo_cliente():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    saldo = request.form.get('saldo_cta_cte', 0.0)
    conn = get_db_connection()
    conn.execute('INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES (?, ?, ?)', (nombre, telefono, saldo))
    conn.commit()
    conn.close()
    return redirect(url_for('main.clientes'))

@bp.route('/cliente/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.clientes'))

# --- PROVEEDORES & PEDIDOS ---
@bp.route('/proveedores')
def proveedores():
    conn = get_db_connection()
    provs = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    return render_template('proveedores.html', proveedores=provs)

@bp.route('/proveedor/nuevo', methods=['POST'])
def nuevo_proveedor():
    nombre = request.form['nombre']
    contacto = request.form['contacto']
    telefono = request.form['telefono']
    conn = get_db_connection()
    conn.execute('INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)', (nombre, contacto, telefono))
    conn.commit()
    conn.close()
    return redirect(url_for('main.proveedores'))

@bp.route('/proveedor/eliminar/<int:id>')
def eliminar_proveedor(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM proveedores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.proveedores'))

def register_routes(app):
    app.register_blueprint(bp)
