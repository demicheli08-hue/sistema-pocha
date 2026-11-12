from flask import render_template_string, request, redirect, url_for
import datetime
from database import get_db_connection
from ventas import registrar_rutas_ventas
from productos import registrar_rutas_productos
from proveedores import registrar_rutas_proveedores

def register_routes(app):
    
    def base_layout(active_page, content):
        return f'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Almacén Natural Pocha - Sistema de Gestión</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                body {{ background-color: #f4f6f9; }}
                .sidebar {{ background-color: #2c3e50; min-height: 100vh; color: white; }}
                .sidebar a {{ color: #bdc3c7; text-decoration: none; padding: 10px 15px; display: block; border-radius: 5px; margin-bottom: 5px; }}
                .sidebar a:hover, .sidebar a.active {{ background-color: #1abc9c; color: white; }}
                .card-stats {{ border-left: 4px solid #1abc9c; }}
                .table-responsive {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <!-- Menú Lateral -->
                    <div class="col-md-3 col-lg-2 sidebar p-3 d-none d-md-block">
                        <h4 class="text-center text-white mb-4"><i class="fas fa-seedling me-2"></i>Pocha Admin</h4>
                        <a href="/" class="{'active' if active_page == 'home' else ''}"><i class="fas fa-home me-2"></i> Inicio / Resumen</a>
                        <a href="/productos" class="{'active' if active_page == 'productos' else ''}"><i class="fas fa-box me-2"></i> Productos & Stock</a>
                        <a href="/ventas" class="{'active' if active_page == 'ventas' else ''}"><i class="fas fa-cash-register me-2"></i> Nueva Venta (Caja)</a>
                        <a href="/clientes" class="{'active' if active_page == 'clientes' else ''}"><i class="fas fa-users me-2"></i> Clientes (Cta. Cte.)</a>
                        <a href="/proveedores" class="{'active' if active_page == 'proveedores' else ''}"><i class="fas fa-truck me-2"></i> Proveedores & Pedidos</a>
                    </div>
                    
                    <!-- Contenido Principal -->
                    <div class="col-md-9 col-lg-10 ms-sm-auto px-md-4 py-4">
                        <nav class="navbar navbar-dark bg-dark d-md-none rounded mb-3 px-3">
                            <span class="navbar-brand">Pocha Almacén</span>
                            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mobileNav">
                                <span class="navbar-toggler-icon"></span>
                            </button>
                            <div class="collapse navbar-collapse" id="mobileNav">
                                <ul class="navbar-nav mt-2">
                                    <li class="nav-item"><a class="nav-link" href="/">Inicio</a></li>
                                    <li class="nav-item"><a class="nav-link" href="/productos">Productos & Stock</a></li>
                                    <li class="nav-item"><a class="nav-link" href="/ventas">Nueva Venta</a></li>
                                    <li class="nav-item"><a class="nav-link" href="/clientes">Clientes</a></li>
                                    <li class="nav-item"><a class="nav-link" href="/proveedores">Proveedores</a></li>
                                </ul>
                            </div>
                        </nav>
                        {content}
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        '''

    @app.route('/')
    def index():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_prod = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
        stock_bajo = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE saldo_cta_cte > 0")
        clientes_deuda = cursor.fetchone()[0]
        
        try:
            cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (datetime.date.today().strftime('%Y-%m-%d') + '%',))
            ventas_hoy = cursor.fetchone()[0] or 0.0
        except Exception:
            ventas_hoy = 0.0
            
        cursor.execute("SELECT valor FROM config WHERE clave = 'margen_general'")
        row_m = cursor.fetchone()
        margen_gral = row_m[0] if row_m else '30'
        conn.close()
        
        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Panel de Control Almacén Natural</h2>
            <span class="badge bg-success fs-6">Sistema Local Activo</span>
        </div>
        <div class="row g-4 mb-4">
            <div class="col-md-3">
                <div class="card card-stats shadow-sm p-3 bg-white">
                    <h6 class="text-muted">Total Productos</h6>
                    <h3>{total_prod}</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card card-stats border-danger shadow-sm p-3 bg-white" style="border-left-color: #e74c3c;">
                    <h6 class="text-muted">Productos Stock Bajo</h6>
                    <h3 class="text-danger">{stock_bajo}</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card card-stats border-warning shadow-sm p-3 bg-white" style="border-left-color: #f1c40f;">
                    <h6 class="text-muted">Ventas de Hoy</h6>
                    <h3>\${ventas_hoy:.2f}</h3>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card card-stats border-info shadow-sm p-3 bg-white" style="border-left-color: #3498db;">
                    <h6 class="text-muted">Clientes c/ Deuda</h6>
                    <h3>{clientes_deuda}</h3>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card shadow-sm p-3 bg-white">
                    <h5>Configuración General</h5>
                    <form action="/actualizar_margen" method="POST" class="mt-3">
                        <div class="mb-3">
                            <label class="form-label">Porcentaje de Ganancia General (%)</label>
                            <div class="input-group">
                                <input type="number" step="0.1" name="margen_general" class="form-control" value="{margen_gral}">
                                <button class="btn btn-primary" type="submit">Actualizar Margen</button>
                            </div>
                            <small class="text-muted">Se aplica a los productos sin margen individual.</small>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card shadow-sm p-3 bg-white">
                    <h5>Accesos Rápidos</h5>
                    <div class="d-grid gap-2 mt-3">
                        <a href="/ventas" class="btn btn-success btn-lg"><i class="fas fa-cash-register me-2"></i> Registrar Nueva Venta</a>
                        <a href="/productos" class="btn btn-outline-primary"><i class="fas fa-box me-2"></i> Cargar / Editar Productos</a>
                        <a href="/clientes" class="btn btn-outline-dark"><i class="fas fa-users me-2"></i> Ver Cuentas Corrientes</a>
                    </div>
                </div>
            </div>
        </div>
        '''
        return render_template_string(base_layout('home', content))

    @app.route('/actualizar_margen', methods=['POST'])
    def actualizar_margen():
        nuevo_margen = request.form['margen_general']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE config SET valor = ? WHERE clave = 'margen_general'", (nuevo_margen,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    @app.route('/clientes', methods=['GET', 'POST'])
    def clientes():
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            cursor.execute("INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES (?, ?, 0.0)", (nombre, telefono))
            conn.commit()
            conn.close()
            return redirect(url_for('clientes'))
            
        cursor.execute("SELECT id, nombre, telefono, saldo_cta_cte FROM clientes")
        clientes_list = cursor.fetchall()
        conn.close()
        
        filas_cli = ""
        modales_cli = ""
        for c in clientes_list:
            cid, cnombre, ctel, csaldo = c
            txt_saldo = f"\${csaldo:.2f}"
            cls_saldo = "text-danger fw-bold" if csaldo > 0 else "text-success"
            
            filas_cli += f'''
            <tr>
                <td><strong>{cnombre}</strong></td>
                <td>{ctel or '-'}</td>
                <td><span class="fs-5 {cls_saldo}">{txt_saldo}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-success me-1" data-bs-toggle="modal" data-bs-target="#pagoModal{cid}"><i class="fas fa-money-bill-wave me-1"></i> Registrar Pago</button>
                    <button class="btn btn-sm btn-outline-secondary me-1" data-bs-toggle="modal" data-bs-target="#editClienteModal{cid}"><i class="fas fa-edit"></i></button>
                    <a href="/eliminar_cliente/{cid}" class="btn btn-sm btn-outline-danger" onclick="return confirm('¿Eliminar cliente?');"><i class="fas fa-trash"></i></a>
                </td>
            </tr>
            '''
            modales_cli += f'''
            <div class="modal fade" id="pagoModal{cid}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form action="/pagar_cta_cte/{cid}" method="POST">
                            <div class="modal-header">
                                <h5 class="modal-title">Registrar Pago de: {cnombre}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>Saldo Actual: <strong>\${csaldo:.2f}</strong></p>
                                <div class="mb-3">
                                    <label class="form-label">Monto a Abonar (\$)</label>
                                    <input type="number" step="0.01" name="monto_pago" class="form-control" required>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                <button type="submit" class="btn btn-success">Acreditar Pago</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <div class="modal fade" id="editClienteModal{cid}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form action="/editar_cliente/{cid}" method="POST">
                            <div class="modal-header">
                                <h5 class="modal-title">Editar Cliente: {cnombre}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label">Nombre y Apellido</label>
                                    <input type="text" name="nombre" class="form-control" value="{cnombre}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Teléfono</label>
                                    <input type="text" name="telefono" class="form-control" value="{ctel or ''}">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            '''
            
        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Gestión de Clientes & Cuentas Corrientes</h2>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalNuevoCliente"><i class="fas fa-user-plus me-1"></i> Nuevo Cliente</button>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Cliente</th>
                        <th>Teléfono</th>
                        <th>Saldo Cuenta Corriente</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_cli}
                </tbody>
            </table>
        </div>
        {modales_cli}
        <div class="modal fade" id="modalNuevoCliente" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form action="/clientes" method="POST">
                        <div class="modal-header">
                            <h5 class="modal-title">Nuevo Cliente</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Nombre y Apellido</label>
                                <input type="text" name="nombre" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Teléfono</label>
                                <input type="text" name="telefono" class="form-control">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Guardar Cliente</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        '''
        return render_template_string(base_layout('clientes', content))

    @app.route('/pagar_cta_cte/<int:id>', methods=['POST'])
    def pagar_cta_cte(id):
        monto = float(request.form['monto_pago'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT saldo_cta_cte FROM clientes WHERE id = ?", (id,))
        s_actual = cursor.fetchone()[0] or 0.0
        nuevo_saldo = s_actual - monto
        cursor.execute("UPDATE clientes SET saldo_cta_cte = ? WHERE id = ?", (nuevo_saldo, id))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))

    @app.route('/editar_cliente/<int:id>', methods=['POST'])
    def editar_cliente(id):
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE clientes SET nombre = ?, telefono = ? WHERE id = ?", (nombre, telefono, id))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))

    @app.route('/eliminar_cliente/<int:id>')
    def eliminar_cliente(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))

    # Registrar sub-módulos
    registrar_rutas_ventas(app, base_layout)
    registrar_rutas_productos(app, base_layout)
    registrar_rutas_proveedores(app, base_layout)
