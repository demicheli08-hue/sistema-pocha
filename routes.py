from flask import render_template_string, request, redirect, url_for
import datetime
from database import get_db_connection

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

    @app.route('/productos')
    def productos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM config WHERE clave = 'margen_general'")
        row_m = cursor.fetchone()
        margen_gral = float(row_m[0]) if row_m and row_m[0] else 30.0
        
        cursor.execute("SELECT p.id, p.nombre, p.proveedor_id, p.costo, p.margen_individual, p.stock, p.stock_minimo FROM productos p")
        prods = cursor.fetchall()
        
        cursor.execute("SELECT id, nombre FROM proveedores")
        proveedores = cursor.fetchall()
        prov_dict = {p[0]: p[1] for p in proveedores} if proveedores else {}
        conn.close()
        
        filas_tabla = ""
        modales = ""
        
        for prod in prods:
            pid = prod[0]
            pnombre = prod[1] if len(prod) > 1 and prod[1] else "Sin Nombre"
            prov_id = prod[2] if len(prod) > 2 else None
            costo = float(prod[3]) if len(prod) > 3 and prod[3] is not None else 0.0
            margen_ind = float(prod[4]) if len(prod) > 4 and prod[4] is not None else None
            stock = float(prod[5]) if len(prod) > 5 and prod[5] is not None else 0.0
            stock_min = float(prod[6]) if len(prod) > 6 and prod[6] is not None else 3.0
            
            margen_aplicado = margen_ind if margen_ind is not None else margen_gral
            precio_venta = costo * (1 + margen_aplicado / 100.0)
            prov_txt = prov_dict.get(prov_id, 'Sin Proveedor')
            
            badge_margen = '<span class="badge bg-info text-dark">Ind.</span>' if margen_ind is not None else '<span class="badge bg-secondary">Gral.</span>'
            estado_stock = '<span class="badge bg-danger">¡Stock Bajo!</span>' if stock <= stock_min else '<span class="badge bg-success">Óptimo</span>'
            tr_class = 'table-danger' if stock <= stock_min else ''
            
            filas_tabla += f'''
            <tr class="{tr_class}">
                <td><strong>{pnombre}</strong></td>
                <td>{prov_txt}</td>
                <td>\${costo:.2f}</td>
                <td>{margen_aplicado}% {badge_margen}</td>
                <td><strong>\${precio_venta:.2f}</strong></td>
                <td>{stock}</td>
                <td>{estado_stock}</td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#editModal{pid}"><i class="fas fa-edit"></i></button>
                    <a href="/eliminar_producto/{pid}" class="btn btn-sm btn-outline-danger" onclick="return confirm('¿Eliminar producto?');"><i class="fas fa-trash"></i></a>
                </td>
            </tr>
            '''
            
            val_margen_ind_str = str(margen_ind) if margen_ind is not None else ''
            modales += f'''
            <div class="modal fade" id="editModal{pid}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form action="/editar_producto/{pid}" method="POST">
                            <div class="modal-header">
                                <h5 class="modal-title">Editar: {pnombre}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label">Costo (\$)</label>
                                    <input type="number" step="0.01" name="costo" class="form-control" value="{costo}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Margen Individual % (Vacío usa General)</label>
                                    <input type="number" step="0.1" name="margen_individual" class="form-control" value="{val_margen_ind_str}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Stock Actual</label>
                                    <input type="number" step="0.1" name="stock" class="form-control" value="{stock}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Stock Mínimo</label>
                                    <input type="number" step="0.1" name="stock_minimo" class="form-control" value="{stock_min}" required>
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

        options_prov = "".join([f'<option value="{p[0]}">{p[1]}</option>' for p in proveedores]) if proveedores else ''
        
        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Gestión de Productos & Stock</h2>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalNuevoProd"><i class="fas fa-plus me-1"></i> Nuevo Producto</button>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Producto</th>
                        <th>Proveedor</th>
                        <th>Costo</th>
                        <th>Margen %</th>
                        <th>Precio Venta</th>
                        <th>Stock</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_tabla}
                </tbody>
            </table>
        </div>
        {modales}
        <div class="modal fade" id="modalNuevoProd" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form action="/nuevo_producto" method="POST">
                        <div class="modal-header">
                            <h5 class="modal-title">Agregar Nuevo Producto</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Nombre del Producto</label>
                                <input type="text" name="nombre" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Proveedor</label>
                                <select name="proveedor_id" class="form-select">
                                    <option value="">Seleccione proveedor...</option>
                                    {options_prov}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Precio Costo (\$)</label>
                                <input type="number" step="0.01" name="costo" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Margen Individual % (Opcional)</label>
                                <input type="number" step="0.1" name="margen_individual" class="form-control" placeholder="Ej: 35 (Vacío = usa general)">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Stock Inicial</label>
                                <input type="number" step="0.1" name="stock" class="form-control" value="10" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Stock Mínimo</label>
                                <input type="number" step="0.1" name="stock_minimo" class="form-control" value="3" required>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Guardar Producto</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        '''
        return render_template_string(base_layout('productos', content))

    @app.route('/nuevo_producto', methods=['POST'])
    def nuevo_producto():
        nombre = request.form['nombre']
        prov_id = request.form['proveedor_id'] or None
        costo = float(request.form['costo'])
        margen_ind = request.form['margen_individual']
        margen_ind = float(margen_ind) if margen_ind != '' else None
        stock = float(request.form['stock'])
        stock_min = float(request.form['stock_minimo'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, prov_id, costo, margen_ind, stock, stock_min))
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))

    @app.route('/editar_producto/<int:id>', methods=['POST'])
    def editar_producto(id):
        costo = float(request.form['costo'])
        margen_ind = request.form['margen_individual']
        margen_ind = float(margen_ind) if margen_ind != '' else None
        stock = float(request.form['stock'])
        stock_min = float(request.form['stock_minimo'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE productos SET costo = ?, margen_individual = ?, stock = ?, stock_minimo = ?
            WHERE id = ?
        ''', (costo, margen_ind, stock, stock_min, id))
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))

    @app.route('/eliminar_producto/<int:id>')
    def eliminar_producto(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))

    @app.route('/ventas', methods=['GET', 'POST'])
    def ventas():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM config WHERE clave = 'margen_general'")
        row_m = cursor.fetchone()
        margen_gral = float(row_m[0]) if row_m else 30.0
        
        cursor.execute("SELECT id, nombre, costo, margen_individual, stock FROM productos WHERE stock > 0")
        prods_raw = cursor.fetchall()
        cursor.execute("SELECT id, nombre FROM clientes")
        clientes = cursor.fetchall()
        
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id') or None
            tipo_pago = request.form.get('tipo_pago')
            productos_ids = request.form.getlist('producto_id[]')
            cantidades = request.form.getlist('cantidad[]')
            total_venta = 0.0
            items_a_comprar = []
            
            for pid_str, cant_str in zip(productos_ids, cantidades):
                if not pid_str or not cant_str:
                    continue
                pid = int(pid_str)
                cant = float(cant_str)
                cursor.execute("SELECT costo, margen_individual, stock FROM productos WHERE id = ?", (pid,))
                res_p = cursor.fetchone()
                if not res_p:
                    continue
                costo, margen_ind, stock_actual = res_p
                margen = margen_ind if margen_ind is not None else margen_gral
                precio_unit = costo * (1 + margen / 100.0)
                subtotal = precio_unit * cant
                total_venta += subtotal
                items_a_comprar.append((pid, cant, precio_unit, subtotal))
                
            if items_a_comprar:
                fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO ventas (fecha, cliente_id, tipo_pago, total) VALUES (?, ?, ?, ?)",
                               (fecha_actual, cliente_id, tipo_pago, total_venta))
                venta_id = cursor.lastrowid
                for pid, cant, p_unit, sub in items_a_comprar:
                    cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                                   (venta_id, pid, cant, p_unit, sub))
                    cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cant, pid))
                    
                if tipo_pago == 'Cuenta Corriente' and cliente_id:
                    cursor.execute("SELECT saldo_cta_cte FROM clientes WHERE id = ?", (cliente_id,))
                    s_ant = cursor.fetchone()[0] or 0.0
                    nuevo_s = s_ant + total_venta
                    cursor.execute("UPDATE clientes SET saldo_cta_cte = ? WHERE id = ?", (nuevo_s, cliente_id))
                    
                conn.commit()
            conn.close()
            return redirect(url_for('ventas'))
            
        options_prod = "".join([f'<option value="{p[0]}">{p[1]} (Stock: {p[4]})</option>' for p in prods_raw])
        options_cli = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in clientes])
        
        content = f'''
        <h2 class="mb-4"><i class="fas fa-cash-register me-2"></i> Módulo de Ventas / Caja</h2>
        <div class="row">
            <div class="col-md-8">
                <div class="card shadow-sm p-4 bg-white">
                    <form action="/ventas" method="POST" id="formVenta">
                        <h5 class="mb-3">Detalle de la Venta</h5>
                        <div id="itemsContainer">
                            <div class="row mb-3 item-row">
                                <div class="col-md-6">
                                    <label class="form-label">Producto</label>
                                    <select name="producto_id[]" class="form-select" required>
                                        <option value="">Seleccione producto...</option>
                                        {options_prod}
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Cantidad</label>
                                    <input type="number" step="0.1" name="cantidad[]" class="form-control" value="1" required>
                                </div>
                                <div class="col-md-2 d-flex align-items-end">
                                    <button type="button" class="btn btn-outline-danger w-100 remove-row"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                        <button type="button" id="addRow" class="btn btn-outline-secondary mb-3"><i class="fas fa-plus me-1"></i> Agregar otro producto</button>
                        <hr>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Forma de Pago</label>
                                <select name="tipo_pago" id="tipoPago" class="form-select" required>
                                    <option value="Efectivo">Efectivo</option>
                                    <option value="Tarjeta Débito">Tarjeta Débito</option>
                                    <option value="Tarjeta Crédito">Tarjeta Crédito</option>
                                    <option value="Transferencia">Transferencia</option>
                                    <option value="Cuenta Corriente">Cuenta Corriente (Fiado)</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3" id="divCliente" style="display:none;">
                                <label class="form-label">Cliente (Cuenta Corriente)</label>
                                <select name="cliente_id" class="form-select">
                                    <option value="">Seleccione cliente...</option>
                                    {options_cli}
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-success btn-lg w-100 mt-3"><i class="fas fa-check-circle me-2"></i> Finalizar y Cobrar</button>
                    </form>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card shadow-sm p-3 bg-light">
                    <h5>Consejos de Caja</h5>
                    <p class="text-muted small">Al finalizar la venta, el stock se descuenta automáticamente y se actualizan las cuentas corrientes si corresponde.</p>
                </div>
            </div>
        </div>
        <script>
            document.getElementById('addRow').addEventListener('click', function() {{
                const container = document.getElementById('itemsContainer');
                const firstRow = container.querySelector('.item-row');
                const newRow = firstRow.cloneNode(true);
                newRow.querySelector('input').value = '1';
                container.appendChild(newRow);
            }});
            document.addEventListener('click', function(e) {{
                if (e.target.closest('.remove-row')) {{
                    const rows = document.querySelectorAll('.item-row');
                    if (rows.length > 1) {{
                        e.target.closest('.item-row').remove();
                    }}
                }}
            }});
            document.getElementById('tipoPago').addEventListener('change', function() {{
                const divCliente = document.getElementById('divCliente');
                divCliente.style.display = (this.value === 'Cuenta Corriente') ? 'block' : 'none';
            }});
        </script>
        '''
        conn.close()
        return render_template_string(base_layout('ventas', content))

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
                    <button class="btn btn-sm btn-outline-success" data-bs-toggle="modal" data-bs-target="#pagoModal{cid}"><i class="fas fa-money-bill-wave me-1"></i> Registrar Pago</button>
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

    @app.route('/eliminar_cliente/<int:id>')
    def eliminar_cliente(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT saldo_cta_cte FROM clientes WHERE id = ?", (id,))
        res = cursor.fetchone()
        if res and res[0] > 0:
            # Opcional: Permitir eliminar igual o advertir
            pass
        cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))

    @app.route('/proveedores', methods=['GET', 'POST'])
    def proveedores():
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            contacto = request.form['contacto']
            telefono = request.form['telefono']
            cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)", (nombre, contacto, telefono))
            conn.commit()
            conn.close()
            return redirect(url_for('proveedores'))
            
        cursor.execute("SELECT id, nombre, contacto, telefono FROM proveedores")
        provs = cursor.fetchall()
        conn.close()
        
        filas_prov = "".join([f'<tr><td><strong>{p[1]}</strong></td><td>{p[2] or "-"}</td><td>{p[3] or "-"}</td><td><a href="/eliminar_proveedor/{p[0]}" class="btn btn-sm btn-outline-danger" onclick="return confirm(\'¿Eliminar proveedor?\");"><i class="fas fa-trash"></i></a></td></tr>' for p in provs])
        
        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Gestión de Proveedores & Pedidos</h2>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalNuevoProv"><i class="fas fa-truck me-1"></i> Nuevo Proveedor</button>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Proveedor</th>
                        <th>Contacto</th>
                        <th>Teléfono</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_prov}
                </tbody>
            </table>
        </div>
        <div class="modal fade" id="modalNuevoProv" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form action="/proveedores" method="POST">
                        <div class="modal-header">
                            <h5 class="modal-title">Nuevo Proveedor</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Nombre del Proveedor</label>
                                <input type="text" name="nombre" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Persona de Contacto</label>
                                <input type="text" name="contacto" class="form-control">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Teléfono</label>
                                <input type="text" name="telefono" class="form-control">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Guardar Proveedor</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        '''
        return render_template_string(base_layout('proveedores', content))

    @app.route('/eliminar_proveedor/<int:id>')
    def eliminar_proveedor(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proveedores WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('proveedores'))
