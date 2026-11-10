from flask import Blueprint, render_template_string, request, redirect, url_for
import datetime
from database import get_db_connection

# Creamos un Blueprint separado para ventas
ventas_bp = Blueprint('ventas_bp', __name__)

def registrar_rutas_ventas(app, base_layout):

    @ventas_bp.route('/ventas', methods=['GET', 'POST'])
    def ventas():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM config WHERE clave = 'margen_general'")
        row_m = cursor.fetchone()
        margen_gral = float(row_m[0]) if row_m else 30.0
        
        # Obtenemos productos con stock > 0
        cursor.execute("SELECT id, nombre, costo, margen_individual, stock FROM productos WHERE stock > 0")
        prods_raw = cursor.fetchall()
        
        options_prod = ""
        for p in prods_raw:
            pid, pnombre, costo, margen_ind, stock = p
            margen = margen_ind if margen_ind is not None else margen_gral
            precio_vta = costo * (1 + margen / 100.0)
            options_prod += f'<option value="{pid}" data-precio="{precio_vta}">{pnombre} (Stock: {stock}) - ${precio_vta:.2f}</option>'

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
            return redirect(url_for('ventas_bp.ventas'))
            
        options_cli = "".join([f'<option value="{c[0]}">{c[1]}</option>' for c in clientes])
        
        content = f'''
        <h2 class="mb-4"><i class="fas fa-cash-register me-2"></i> Módulo de Ventas / Caja</h2>
        <div class="row">
            <div class="col-md-8">
                <div class="card shadow-sm p-4 bg-white">
                    <form action="/ventas" method="POST" id="formVenta">
                        <h5 class="mb-3">Detalle de la Venta</h5>
                        <div id="itemsContainer">
                            <div class="row mb-3 item-row align-items-center">
                                <div class="col-md-5">
                                    <label class="form-label">Producto</label>
                                    <select name="producto_id[]" class="form-select producto-select" required>
                                        <option value="">Seleccione producto...</option>
                                        {options_prod}
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">Cantidad</label>
                                    <input type="number" step="0.1" name="cantidad[]" class="form-control cantidad-input" value="1" required>
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">Precio U.</label>
                                    <input type="text" class="form-control precio-unitario" readonly value="\$0.00">
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">Subtotal</label>
                                    <input type="text" class="form-control subtotal-item fw-bold text-success" readonly value="\$0.00">
                                </div>
                                <div class="col-md-1 d-flex align-items-end mt-4">
                                    <button type="button" class="btn btn-outline-danger remove-row"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                        <button type="button" id="addRow" class="btn btn-outline-secondary mb-3"><i class="fas fa-plus me-1"></i> Agregar otro producto</button>
                        
                        <hr>
                        
                        <!-- Total General -->
                        <div class="d-flex justify-content-between align-items-center bg-light p-3 rounded mb-3">
                            <h4 class="mb-0 text-dark">TOTAL GENERAL:</h4>
                            <h3 class="mb-0 text-success fw-bold" id="totalGeneral">\$0.00</h3>
                        </div>

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
                    <p class="text-muted small">El subtotal y el total general se calculan automáticamente. Al finalizar la venta, el stock se descuenta al instante y se actualizan las cuentas corrientes si corresponde.</p>
                </div>
            </div>
        </div>
        <script>
            function calcularTotales() {{
                let totalGeneral = 0;
                document.querySelectorAll('.item-row').forEach(row => {{
                    const select = row.querySelector('.producto-select');
                    const cantidadInput = row.querySelector('.cantidad-input');
                    const precioInput = row.querySelector('.precio-unitario');
                    const subtotalInput = row.querySelector('.subtotal-item');
                    
                    const option = select.options[select.selectedIndex];
                    const precio = option && option.dataset.precio ? parseFloat(option.dataset.precio) : 0;
                    const cantidad = parseFloat(cantidadInput.value) || 0;
                    const subtotal = precio * cantidad;
                    
                    precioInput.value = '$' + precio.toFixed(2);
                    subtotalInput.value = '$' + subtotal.toFixed(2);
                    totalGeneral += subtotal;
                }});
                document.getElementById('totalGeneral').innerText = '$' + totalGeneral.toFixed(2);
            }}

            document.getElementById('addRow').addEventListener('click', function() {{
                const container = document.getElementById('itemsContainer');
                const firstRow = container.querySelector('.item-row');
                const newRow = firstRow.cloneNode(true);
                newRow.querySelector('.cantidad-input').value = '1';
                newRow.querySelector('.producto-select').selectedIndex = 0;
                newRow.querySelector('.precio-unitario').value = '$0.00';
                newRow.querySelector('.subtotal-item').value = '$0.00';
                container.appendChild(newRow);
                calcularTotales();
            }});

            document.addEventListener('change', function(e) {{
                if (e.target.classList.contains('producto-select') || e.target.classList.contains('cantidad-input')) {{
                    calcularTotales();
                }}
            }});

            document.addEventListener('input', function(e) {{
                if (e.target.classList.contains('cantidad-input')) {{
                    calcularTotales();
                }}
            }});

            document.addEventListener('click', function(e) {{
                if (e.target.closest('.remove-row')) {{
                    const rows = document.querySelectorAll('.item-row');
                    if (rows.length > 1) {{
                        e.target.closest('.item-row').remove();
                        calcularTotales();
                    }}
                }}
            }});

            document.getElementById('tipoPago').addEventListener('change', function() {{
                const divCliente = document.getElementById('divCliente');
                divCliente.style.display = (this.value === 'Cuenta Corriente') ? 'block' : 'none';
            }});

            window.onload = calcularTotales;
        </script>
        '''
        conn.close()
        return render_template_string(base_layout('ventas', content))

    app.register_blueprint(ventas_bp)