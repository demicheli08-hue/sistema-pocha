from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db_connection

bp = Blueprint('main', __name__)

# --- GESTIÓN DE PROVEEDORES ---
@bp.route('/proveedores')
def proveedores():
    conn = get_db_connection()
    provs = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    return render_template('proveedores.html', proveedores=provs)

@bp.route('/proveedor/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        telefono = request.form['telefono']
        conn = get_db_connection()
        conn.execute('INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)', (nombre, contacto, telefono))
        conn.commit()
        conn.close()
        return redirect(url_for('main.proveedores'))
    return render_template('nuevo_proveedor.html')

@bp.route('/proveedor/eliminar/<int:id>')
def eliminar_proveedor(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM proveedores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.proveedores'))


# --- GESTIÓN DE CLIENTES ---
@bp.route('/clientes')
def clientes():
    conn = get_db_connection()
    clis = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clis)

@bp.route('/cliente/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        saldo = request.form.get('saldo_cta_cte', 0.0)
        conn = get_db_connection()
        conn.execute('INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES (?, ?, ?)', (nombre, telefono, saldo))
        conn.commit()
        conn.close()
        return redirect(url_for('main.clientes'))
    return render_template('nuevo_cliente.html')

@bp.route('/cliente/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.clientes'))
