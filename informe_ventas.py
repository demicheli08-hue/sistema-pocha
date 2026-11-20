from flask import render_template_string, request
import datetime
from database import get_db_connection


def registrar_rutas_informe_ventas(app, base_layout):

    @app.route('/informe_ventas', methods=['GET'])
    def informe_ventas():
        hoy_str = datetime.date.today().strftime('%Y-%m-%d')
        fecha_sel = request.args.get('fecha', hoy_str) or hoy_str

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT v.id, v.fecha, v.tipo_pago, v.total, c.nombre
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE v.fecha LIKE %s
                ORDER BY v.fecha ASC, v.id ASC
            ''', (f"{fecha_sel}%",))
            ventas_dia = cursor.fetchall()

            filas_html = ""
            total_general_dia = 0.0

            for v in ventas_dia:
                venta_id, fecha_v, tipo_pago, total_v, cliente_nom = v
                total_v_float = float(total_v) if total_v is not None else 0.0
                total_general_dia += total_v_float

                forma_pago_str = tipo_pago or "-"
                cliente_str = f" — <em>{cliente_nom}</em>" if cliente_nom else ""

                cursor.execute('''
                    SELECT p.nombre, d.cantidad, d.precio_unitario, d.subtotal
                    FROM detalle_ventas d
                    LEFT JOIN productos p ON d.producto_id = p.id
                    WHERE d.venta_id = %s
                    ORDER BY d.id ASC
                ''', (venta_id,))
                detalles = cursor.fetchall()

                if detalles:
                    for det in detalles:
                        prod_nombre = det[0] or "Producto"
                        cant = float(det[1]) if det[1] is not None else 0.0
                        p_unit = float(det[2]) if det[2] is not None else 0.0
                        subt = (
                            float(det[3])
                            if det[3] is not None
                            else (cant * p_unit)
                        )
                        cant_str = f"{cant:g}"

                        filas_html += f'''
                        <tr>
                            <td>#{venta_id}<br><small class="text-muted">{fecha_v}{cliente_str}</small></td>
                            <td><strong>{prod_nombre}</strong></td>
                            <td>{cant_str}</td>
                            <td>${p_unit:.2f}</td>
                            <td class="fw-bold">${subt:.2f}</td>
                            <td><span class="badge bg-secondary">{forma_pago_str}</span></td>
                        </tr>
                        '''
                else:
                    filas_html += f'''
                    <tr>
                        <td>#{venta_id}<br><small class="text-muted">{fecha_v}{cliente_str}</small></td>
                        <td colspan="3" class="text-muted">Venta sin detalle de ítems</td>
                        <td class="fw-bold">${total_v_float:.2f}</td>
                        <td><span class="badge bg-secondary">{forma_pago_str}</span></td>
                    </tr>
                    '''

            if not filas_html:
                filas_html = '''
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        No hay ventas registradas para la fecha seleccionada.
                    </td>
                </tr>
                '''

        except Exception as e:
            conn.rollback()
            filas_html = f'''
            <tr>
                <td colspan="6" class="text-center text-danger py-4">
                    Error al cargar el informe: {e}
                </td>
            </tr>
            '''
            total_general_dia = 0.0
        finally:
            conn.close()

        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2>Informe de Ventas Diarias</h2>
                <p class="text-muted mb-0">Fecha: <strong>{fecha_sel}</strong> | Total del Día: <strong class="text-success">${total_general_dia:.2f}</strong></p>
            </div>
            <div>
                <button onclick="window.print();" class="btn btn-primary">
                    <i class="fas fa-print me-1"></i> Imprimir Informe
                </button>
            </div>
        </div>

        <div class="card shadow-sm p-3 bg-white mb-4">
            <form method="GET" class="row g-3 align-items-end">
                <div class="col-md-6">
                    <label class="form-label">Seleccionar Fecha</label>
                    <input type="date" name="fecha" class="form-control" value="{fecha_sel}">
                </div>
                <div class="col-md-6">
                    <button type="submit" class="btn btn-dark w-100">
                        <i class="fas fa-search me-1"></i> Ver Ventas del Día
                    </button>
                </div>
            </form>
        </div>

        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Venta / Hora</th>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio Unitario</th>
                        <th>Subtotal</th>
                        <th>Forma de Pago</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
                <tfoot>
                    <tr class="table-light">
                        <td colspan="4" class="text-end fw-bold">TOTAL GENERAL DEL DÍA:</td>
                        <td colspan="2" class="fw-bold text-success fs-5">${total_general_dia:.2f}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        '''
        return render_template_string(base_layout('informe_ventas', content))