from flask import render_template_string, request, redirect, url_for
from database import get_db_connection


def registrar_rutas_historial_cliente(app, base_layout):

    @app.route('/cliente_historial/<int:id>', methods=['GET'])
    def cliente_historial(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT nombre, telefono FROM clientes WHERE id = %s", (id,))
        c_info = cursor.fetchone()
        if not c_info:
            conn.close()
            return redirect(url_for('clientes'))

        cnombre, ctel = c_info

        fecha_desde = request.args.get('desde', '')
        fecha_hasta = request.args.get('hasta', '')

        # Obtener compras a Cta Cte (Debe) incluyendo el id de venta
        query_v = "SELECT id, fecha, total FROM ventas WHERE cliente_id = %s AND tipo_pago = 'Cuenta Corriente'"
        params_v = [id]
        if fecha_desde:
            query_v += " AND fecha >= %s"
            params_v.append(fecha_desde + " 00:00:00")
        if fecha_hasta:
            query_v += " AND fecha <= %s"
            params_v.append(fecha_hasta + " 23:59:59")

        cursor.execute(query_v, tuple(params_v))
        ventas_cli = cursor.fetchall()

        # Obtener pagos (Haber)
        query_p = "SELECT fecha, monto FROM pagos_cta_cte WHERE cliente_id = %s"
        params_p = [id]
        if fecha_desde:
            query_p += " AND fecha >= %s"
            params_p.append(fecha_desde + " 00:00:00")
        if fecha_hasta:
            query_p += " AND fecha <= %s"
            params_p.append(fecha_hasta + " 23:59:59")

        cursor.execute(query_p, tuple(params_p))
        pagos_cli = cursor.fetchall()

        movimientos = []
        for v in ventas_cli:
            venta_id = v[0]
            f_str = str(v[1]) if v[1] else ''
            monto_v = float(v[2]) if v[2] is not None else 0.0

            # Buscar descripción y precio unitario de los productos de esa venta
            cursor.execute('''
                SELECT p.nombre, d.cantidad, d.precio_unitario
                FROM detalle_ventas d
                LEFT JOIN productos p ON d.producto_id = p.id
                WHERE d.venta_id = %s
            ''', (venta_id,))
            detalles = cursor.fetchall()

            items_html = ""
            if detalles:
                lineas = []
                for det in detalles:
                    prod_nombre = det[0] or "Producto"
                    cant = float(det[1]) if det[1] is not None else 0.0
                    p_unit = float(det[2]) if det[2] is not None else 0.0
                    cant_str = f"{cant:g}"
                    lineas.append(f"• {prod_nombre} (x{cant_str}) — <strong>P. Unit:</strong> ${p_unit:.2f}")
                items_html = "<br><small class='text-muted'>" + "<br>".join(lineas) + "</small>"

            movimientos.append({
                'fecha': f_str,
                'tipo': f"Compra{items_html}",
                'debe': monto_v,
                'haber': 0.0
            })

        for p in pagos_cli:
            f_str = str(p[0]) if p[0] else ''
            monto_p = float(p[1]) if p[1] is not None else 0.0
            movimientos.append({
                'fecha': f_str,
                'tipo': 'Pago',
                'debe': 0.0,
                'haber': monto_p
            })

        conn.close()

        # Ordenar por fecha cronológicamente de forma segura
        movimientos.sort(key=lambda x: x['fecha'])

        filas_mov = ""
        subtotal_acumulado = 0.0

        for m in movimientos:
            subtotal_acumulado += float(m['debe'] - m['haber'])
            debe_str = f"${m['debe']:.2f}" if m['debe'] > 0 else "-"
            haber_str = f"${m['haber']:.2f}" if m['haber'] > 0 else "-"
            subtotal_str = f"${subtotal_acumulado:.2f}"

            cls_sub = "text-danger fw-bold" if subtotal_acumulado > 0 else "text-success fw-bold"

            filas_mov += f'''
            <tr>
                <td>{m['fecha']}</td>
                <td>{m['tipo']}</td>
                <td class="text-danger fw-bold">{debe_str}</td>
                <td class="text-success fw-bold">{haber_str}</td>
                <td class="{cls_sub}">{subtotal_str}</td>
            </tr>
            '''

        if not filas_mov:
            filas_mov = '<tr><td colspan="5" class="text-center text-muted">No hay movimientos en el periodo seleccionado.</td></tr>'
            csaldo_calculado = 0.0
        else:
            csaldo_calculado = subtotal_acumulado

        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2>Estado de Cuenta: {cnombre}</h2>
                <p class="text-muted mb-0">Teléfono: {ctel or '-'} | Saldo Actual: <strong class="text-danger">${csaldo_calculado:.2f}</strong></p>
            </div>
            <div>
                <a href="/clientes" class="btn btn-secondary me-2"><i class="fas fa-arrow-left me-1"></i> Volver</a>
                <button onclick="window.print();" class="btn btn-primary"><i class="fas fa-print me-1"></i> Imprimir Informe</button>
            </div>
        </div>

        <div class="card shadow-sm p-3 bg-white mb-4">
            <form method="GET" class="row g-3 align-items-end">
                <div class="col-md-4">
                    <label class="form-label">Desde Fecha</label>
                    <input type="date" name="desde" class="form-control" value="{fecha_desde}">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Hasta Fecha</label>
                    <input type="date" name="hasta" class="form-control" value="{fecha_hasta}">
                </div>
                <div class="col-md-4">
                    <button type="submit" class="btn btn-dark w-100"><i class="fas fa-filter me-1"></i> Filtrar Informe</button>
                </div>
            </form>
        </div>

        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Fecha y Hora</th>
                        <th>Concepto / Detalle</th>
                        <th>Debe</th>
                        <th>Haber</th>
                        <th>Subtotal (Saldo)</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_mov}
                </tbody>
            </table>
        </div>
        '''
        return render_template_string(base_layout('clientes', content))
