from flask import Blueprint, render_template_string, request, redirect, url_for
from database import get_db_connection

proveedores_bp = Blueprint('proveedores_bp', __name__)

def registrar_rutas_proveedores(app, base_layout):

    @proveedores_bp.route('/proveedores', methods=['GET', 'POST'])
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
            return redirect(url_for('proveedores_bp.proveedores'))
            
        cursor.execute("SELECT id, nombre, contacto, telefono FROM proveedores")
        provs = cursor.fetchall()
        conn.close()
        
        filas_prov = ""
        modales_prov = ""
        for p in provs:
            pid, pnombre, pcontacto, ptel = p
            filas_prov += f'''
            <tr>
                <td><strong>{pnombre}</strong></td>
                <td>{pcontacto or "-"}</td>
                <td>{ptel or "-"}</td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary me-1" data-bs-toggle="modal" data-bs-target="#editProvModal{pid}"><i class="fas fa-edit"></i></button>
                    <a href="/eliminar_proveedor/{pid}" class="btn btn-sm btn-outline-danger" onclick="return confirm('¿Eliminar proveedor?');"><i class="fas fa-trash"></i></a>
                </td>
            </tr>
            '''
            modales_prov += f'''
            <div class="modal fade" id="editProvModal{pid}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form action="/editar_proveedor/{pid}" method="POST">
                            <div class="modal-header">
                                <h5 class="modal-title">Editar Proveedor: {pnombre}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label">Nombre del Proveedor</label>
                                    <input type="text" name="nombre" class="form-control" value="{pnombre}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Persona de Contacto</label>
                                    <input type="text" name="contacto" class="form-control" value="{pcontacto or ''}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Teléfono</label>
                                    <input type="text" name="telefono" class="form-control" value="{ptel or ''}">
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
        {modales_prov}
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

    @proveedores_bp.route('/editar_proveedor/<int:id>', methods=['POST'])
    def editar_proveedor(id):
        nombre = request.form['nombre']
        contacto = request.form['contacto']
        telefono = request.form['telefono']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE proveedores SET nombre = ?, contacto = ?, telefono = ? WHERE id = ?", (nombre, contacto, telefono, id))
        conn.commit()
        conn.close()
        return redirect(url_for('proveedores_bp.proveedores'))

    @proveedores_bp.route('/eliminar_proveedor/<int:id>')
    def eliminar_proveedor(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proveedores WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('proveedores_bp.proveedores'))

    app.register_blueprint(proveedores_bp)
