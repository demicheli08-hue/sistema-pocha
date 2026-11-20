from urllib.parse import quote
import datetime
from flask import render_template_string, request, redirect, url_for
from database import get_db_connection


def _limpiar_telefono_wa(tel):
    if not tel:
        return ""
    digitos = "".join(ch for ch in str(tel) if ch.isdigit())
    return digitos


def registrar_rutas_proveedores(app, base_layout):

    @app.route('/proveedores', methods=['GET', 'POST'])
    def proveedores():
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            contacto = request.form.get('contacto', '').strip()
            telefono = request.form.get('telefono', '').strip()

            try:
                cursor.execute(
                    "INSERT INTO proveedores (nombre, contacto, telefono) VALUES (%s, %s, %s)",
                    (nombre, contacto if contacto else None, telefono if telefono else None)
                )
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error al guardar proveedor: {e}")
            finally:
                conn.close()
            return redirect(url_for('proveedores'))

        try:
            cursor.execute("SELECT id, nombre, contacto, telefono FROM proveedores ORDER BY nombre ASC")
            proveedores_list = cursor.fetchall()
        except Exception as e:
            conn.rollback()
            print(f"Error al listar proveedores: {e}")
            proveedores_list = []
        finally:
            conn.close()

        filas_prov = ""
        modales_prov = ""

        for p in proveedores_list:
            pid, pnombre, pcontacto, ptel = p

            filas_prov += f'''
            <tr>
                <td><strong>{pnombre}</strong></td>
                <td>{pcontacto or '-'}</td>
                <td>{ptel or '-'}</td>
                <td>
                    <a href="/pedido_proveedor/{pid}" class="btn btn-sm btn-outline-primary me-1">
                        <i class="fas fa-clipboard-list me-1"></i> Generar Pedido
                    </a>
                    <button class="btn btn-sm btn-outline-secondary me-1" data-bs-toggle="modal" data-bs-target="#editProveedorModal{pid}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <a href="/eliminar_proveedor/{pid}" class="btn btn-sm btn-outline-danger" onclick="return confirm('¿Eliminar proveedor?');">
                        <i class="fas fa-trash"></i>
                    </a>
                </td>
            </tr>
            '''

            modales_prov += f'''
            <div class="modal fade" id="editProveedorModal{pid}" tabindex="-1">
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
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalNuevoProveedor">
                <i class="fas fa-truck me-1"></i> Nuevo Proveedor
            </button>
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

        <div class="modal fade" id="modalNuevoProveedor" tabindex="-1">
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

    @app.route('/pedido_proveedor/<int:id>', methods=['GET', 'POST'])
    def pedido_proveedor(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre, contacto, telefono FROM proveedores WHERE id = %s", (id,))
        prov = cursor.fetchone()
        if not prov:
            conn.close()
            return redirect(url_for('proveedores'))

        pid, pnombre, pcontacto, ptel = prov
        solo_bajo_stock = request.args.get('bajo_stock', '') == '1'

        # Buscar productos asignados al proveedor; si no tiene ninguno, mostrar todos
        cursor.execute('''
            SELECT id, nombre, costo, stock, stock_minimo
            FROM productos
            WHERE proveedor_id = %s
            ORDER BY nombre ASC
        ''', (pid,))
        productos_prov = cursor.fetchall()

        usando_todos = False
        if not productos_prov:
            usando_todos = True
            cursor.execute('''
                SELECT id, nombre, costo, stock, stock_minimo
                FROM productos
                ORDER BY nombre ASC
            ''')
            productos_prov = cursor.fetchall()

        conn.close()

        cantidades_ingresadas = {}
        if request.method == 'POST':
            for prod in productos_prov:
                prod_id = prod[0]
                raw_cant = request.form.get(f"cant_{prod_id}", "").strip()
                if raw_cant:
                    try:
                        val = float(raw_cant)
                        if val > 0:
                            cantidades_ingresadas[prod_id] = val
                    except ValueError:
                        pass

        filas_carga = ""
        for prod in productos_prov:
            prod_id, prod_nom, prod_costo, prod_stock, prod_min = prod
            stock_val = float(prod_stock) if prod_stock is not None else 0.0
            min_val = float(prod_min) if prod_min is not None else 5.0
            costo_val = float(prod_costo) if prod_costo is not None else 0.0

            if solo_bajo_stock and stock_val > min_val:
                continue

            sugerido = max(0.0, round(min_val - stock_val, 2))
            if request.method == 'POST':
                valor_input = cantidades_ingresadas.get(prod_id, 0.0)
            else:
                valor_input = sugerido if solo_bajo_stock else 0.0

            valor_input_str = f"{valor_input:g}" if valor_input > 0 else ""
            estado_stock = (
                f'<span class="badge bg-danger">Stock: {stock_val:g} (Mín: {min_val:g})</span>'
                if stock_val <= min_val
                else f'<span class="badge bg-light text-dark border">Stock: {stock_val:g}</span>'
            )

            filas_carga += f'''
            <tr>
                <td><strong>{prod_nom}</strong></td>
                <td>{estado_stock}</td>
                <td>${costo_val:.2f}</td>
                <td style="max-width: 150px;">
                    <input type="number" step="0.01" min="0" name="cant_{prod_id}" class="form-control form-control-sm" value="{valor_input_str}" placeholder="0">
                </td>
            </tr>
            '''

        if not filas_carga:
            filas_carga = '''
            <tr>
                <td colspan="4" class="text-center text-muted py-3">
                    No hay productos para mostrar con el filtro actual.
                </td>
            </tr>
            '''

        # Armar resumen imprimible y mensaje para WhatsApp / Mail
        items_pedido = []
        total_estimado = 0.0
        for prod in productos_prov:
            prod_id, prod_nom, prod_costo, _, _ = prod
            if prod_id in cantidades_ingresadas:
                cant = cantidades_ingresadas[prod_id]
                costo_val = float(prod_costo) if prod_costo is not None else 0.0
                subt = cant * costo_val
                total_estimado += subt
                items_pedido.append((prod_nom, cant, costo_val, subt))

        fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
        lineas_texto = [
            f"*Pedido de Mercadería — Almacén Natural Pocha*",
            f"Fecha: {fecha_hoy}",
            f"Proveedor: {pnombre}" + (f" ({pcontacto})" if pcontacto else ""),
            "----------------------------------------"
        ]

        filas_resumen = ""
        if items_pedido:
            for nom, cant, costo_u, subt in items_pedido:
                cant_str = f"{cant:g}"
                lineas_texto.append(f"• {nom} — Cant: {cant_str} (Costo ref: ${costo_u:.2f})")
                filas_resumen += f'''
                <tr>
                    <td><strong>{nom}</strong></td>
                    <td>{cant_str}</td>
                    <td>${costo_u:.2f}</td>
                    <td class="fw-bold">${subt:.2f}</td>
                </tr>
                '''
        else:
            lineas_texto.append("(Cargá cantidades mayores a 0 y hacé clic en 'Preparar Pedido')")
            filas_resumen = '''
            <tr>
                <td colspan="4" class="text-center text-muted py-3">
                    Ingresá cantidades en la tabla de arriba y tocá <strong>Preparar Pedido</strong> para generar la orden.
                </td>
            </tr>
            '''

        lineas_texto.append("----------------------------------------")
        lineas_texto.append(f"*Costo estimado total:* ${total_estimado:.2f}")
        texto_pedido = "\n".join(lineas_texto)
        texto_wa_encoded = quote(texto_pedido)
        tel_limpio = _limpiar_telefono_wa(ptel)
        url_whatsapp = f"https://wa.me/{tel_limpio}?text={texto_wa_encoded}" if tel_limpio else f"https://wa.me/?text={texto_wa_encoded}"

        aviso_catalogo = (
            '<div class="alert alert-info py-2">Este proveedor aún no tiene productos asignados: se muestra todo el catálogo disponible.</div>'
            if usando_todos else ""
        )

        content = f'''
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
            <div>
                <h2>Pedido a Proveedor: {pnombre}</h2>
                <p class="text-muted mb-0">
                    Contacto: <strong>{pcontacto or '-'}</strong> | Teléfono: <strong>{ptel or '-'}</strong> | Fecha: <strong>{fecha_hoy}</strong>
                </p>
            </div>
            <div>
                <a href="/proveedores" class="btn btn-secondary me-2">
                    <i class="fas fa-arrow-left me-1"></i> Volver
                </a>
                <button onclick="window.print();" class="btn btn-primary">
                    <i class="fas fa-print me-1"></i> Imprimir / Guardar PDF
                </button>
            </div>
        </div>

        {aviso_catalogo}

        <div class="card shadow-sm p-3 bg-white mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                <h5 class="mb-0">1. Seleccionar Cantidades a Pedir</h5>
                <div>
                    <a href="/pedido_proveedor/{pid}?bajo_stock=1" class="btn btn-sm btn-outline-warning me-1">
                        <i class="fas fa-exclamation-triangle me-1"></i> Sugerir Stock Bajo
                    </a>
                    <a href="/pedido_proveedor/{pid}" class="btn btn-sm btn-outline-dark">
                        Ver Todos
                    </a>
                </div>
            </div>

            <form method="POST">
                <div class="table-responsive shadow-none p-0">
                    <table class="table table-hover align-middle mb-3">
                        <thead class="table-light">
                            <tr>
                                <th>Producto</th>
                                <th>Stock</th>
                                <th>Costo Ref.</th>
                                <th>Cantidad a Pedir</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_carga}
                        </tbody>
                    </table>
                </div>
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-check me-1"></i> Preparar Pedido para Enviar / Imprimir
                </button>
            </form>
        </div>

        <div class="card shadow-sm p-3 bg-white mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                <h5 class="mb-0">2. Resumen del Pedido ({pnombre})</h5>
                <div>
                    <button type="button" onclick="copiarPedido();" class="btn btn-sm btn-outline-dark me-2">
                        <i class="fas fa-copy me-1"></i> Copiar Texto (Mail / Chat)
                    </button>
                    <a href="{url_whatsapp}" target="_blank" rel="noopener" class="btn btn-sm btn-success">
                        <i class="fab fa-whatsapp me-1"></i> Enviar por WhatsApp
                    </a>
                </div>
            </div>

            <div class="table-responsive shadow-none p-0 mb-3">
                <table class="table table-bordered align-middle mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Costo Unit. Ref.</th>
                            <th>Subtotal Ref.</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_resumen}
                    </tbody>
                    <tfoot>
                        <tr class="table-light">
                            <td colspan="3" class="text-end fw-bold">TOTAL ESTIMADO:</td>
                            <td class="fw-bold text-primary fs-5">${total_estimado:.2f}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <label class="form-label fw-bold">Texto listo para WhatsApp o Correo Electrónico:</label>
            <textarea id="textoPedidoBox" class="form-control" rows="7" readonly>{texto_pedido}</textarea>
        </div>

        <script>
            function copiarPedido() {{
                const box = document.getElementById('textoPedidoBox');
                box.select();
                box.setSelectionRange(0, 99999);
                navigator.clipboard.writeText(box.value).then(() => {{
                    alert('Pedido copiado al portapapeles. Ya podés pegarlo en tu correo o WhatsApp.');
                }}).catch(() => {{
                    document.execCommand('copy');
                    alert('Pedido copiado al portapapeles.');
                }});
            }}
        </script>
        '''
        return render_template_string(base_layout('proveedores', content))

    @app.route('/editar_proveedor/<int:id>', methods=['POST'])
    def editar_proveedor(id):
        nombre = request.form.get('nombre', '').strip()
        contacto = request.form.get('contacto', '').strip()
        telefono = request.form.get('telefono', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE proveedores SET nombre = %s, contacto = %s, telefono = %s WHERE id = %s",
                (nombre, contacto if contacto else None, telefono if telefono else None, id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error al editar proveedor: {e}")
        finally:
            conn.close()
        return redirect(url_for('proveedores'))

    @app.route('/eliminar_proveedor/<int:id>')
    def eliminar_proveedor(id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM proveedores WHERE id = %s", (id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar proveedor: {e}")
        finally:
            conn.close()
        return redirect(url_for('proveedores'))
