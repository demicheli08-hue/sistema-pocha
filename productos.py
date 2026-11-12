from flask import Blueprint, render_template_string, request, redirect, url_for
from database import get_db_connection

productos_bp = Blueprint('productos_bp', __name__)

def registrar_rutas_productos(app, base_layout):

    @productos_bp.route('/productos')
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
                    <button class="btn btn-sm btn-outline-secondary me-1" data-bs-toggle="modal" data-bs-target="#editModal{pid}"><i class="fas fa-edit"></i></button>
                    <a href="/eliminar_producto/{pid}" class="btn btn-sm btn-outline-danger" onclick="return confirm('¿Eliminar producto?');"><i class="fas fa-trash"></i></a>
                </td>
            </tr>
            '''
            
            val_margen_ind_str = str(margen_ind) if margen_ind is not None else ''
            options_prov_edit = "".join([f'<option value="{p[0]}" {"selected" if p[0] == prov_id else ""}>{p[1]}</option>' for p in proveedores])
            
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
                                    <label class="form-label">Nombre del Producto</label>
                                    <input type="text" name="nombre" class="form-control" value="{pnombre}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Proveedor</label>
                                    <select name="proveedor_id" class="form-select">
                                        <option value="">Seleccione proveedor...</option>
                                        {options_prov_edit}
                                    </select>
                                </div>
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

    @productos_bp.route('/nuevo_producto', methods=['POST'])
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
        return redirect(url_for('productos_bp.productos'))

    @productos_bp.route('/editar_producto/<int:id>', methods=['POST'])
    def editar_producto(id):
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
            UPDATE productos SET nombre = ?, proveedor_id = ?, costo = ?, margen_individual = ?, stock = ?, stock_minimo = ?
            WHERE id = ?
        ''', (nombre, prov_id, costo, margen_ind, stock, stock_min, id))
        conn.commit()
        conn.close()
        return redirect(url_for('productos_bp.productos'))

    @productos_bp.route('/eliminar_producto/<int:id>')
    def eliminar_producto(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('productos_bp.productos'))

    app.register_blueprint(productos_bp)