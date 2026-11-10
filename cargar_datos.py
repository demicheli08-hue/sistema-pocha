import sqlite3

DB_NAME = 'pocha_negocio.db'

def precargar_todo():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Crear todas las tablas desde cero
    cursor.execute('DROP TABLE IF EXISTS detalle_ventas')
    cursor.execute('DROP TABLE IF EXISTS ventas')
    cursor.execute('DROP TABLE IF EXISTS productos')
    cursor.execute('DROP TABLE IF EXISTS clientes')
    cursor.execute('DROP TABLE IF EXISTS proveedores')
    cursor.execute('DROP TABLE IF EXISTS config')

    cursor.execute('''
        CREATE TABLE proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            saldo_cta_cte REAL DEFAULT 0.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            proveedor_id INTEGER,
            costo REAL NOT NULL,
            margen_individual REAL,
            stock REAL NOT NULL,
            stock_minimo REAL DEFAULT 5.0,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente_id INTEGER,
            tipo_pago TEXT,
            total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            producto_id INTEGER,
            cantidad REAL,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE config (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    cursor.execute("INSERT INTO config (clave, valor) VALUES ('margen_general', '30')")
    conn.commit()

    # 2. Insertar Proveedores
    proveedores = [
        ("Oveja Negra", "Ventas", "3800000000"),
        ("BIOSALUD", "Distribución", "3800000000"),
        ("PECANES ARGENTINOS", "Ventas", "3800000000"),
        ("NUTRIMIX", "Ventas", "3800000000"),
        ("CHAYA FRUTOS SECOS", "Ventas", "3800000000")
    ]
    cursor.executemany("INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)", proveedores)
    conn.commit()

    cursor.execute("SELECT id, nombre FROM proveedores")
    prov_map = {nombre: pid for pid, nombre in cursor.fetchall()}

    # 3. Insertar Productos (Oveja Negra y El Árbol de la Abuela unificados)
    productos_totales = [
        # Oveja Negra
        ("Mix Tradicional (500g)", prov_map.get("Oveja Negra"), 4800.0, 10, 3),
        ("Mix Tradicional c/ Banana (500g)", prov_map.get("Oveja Negra"), 6500.0, 10, 3),
        ("Mix Premium (500g)", prov_map.get("Oveja Negra"), 8300.0, 10, 3),
        ("Nueces (500g)", prov_map.get("Oveja Negra"), 8000.0, 10, 3),
        ("Almendras (500g)", prov_map.get("Oveja Negra"), 10500.0, 10, 3),
        ("Arándanos Deshidratados (500g)", prov_map.get("Oveja Negra"), 10755.0, 10, 3),
        ("Ciruelas Deshidratadas (500g)", prov_map.get("Oveja Negra"), 4500.0, 10, 3),
        ("Castañas de Cajú (200g)", prov_map.get("Oveja Negra"), 4200.0, 10, 3),
        ("Almendras (200g)", prov_map.get("Oveja Negra"), 4400.0, 10, 3),
        ("Granola Crocante (500g)", prov_map.get("Oveja Negra"), 8200.0, 10, 3),
        ("Almohaditas Rellenas (500g)", prov_map.get("Oveja Negra"), 3500.0, 10, 3),
        ("Semillas de Zapallo (130g)", prov_map.get("Oveja Negra"), 2000.0, 10, 3),
        # El Árbol de la Abuela / Biosalud / Semillas / Frutos Secos
        ("Chía (1kg)", prov_map.get("BIOSALUD"), 5130.0, 15, 3),
        ("Lino (1kg)", prov_map.get("PECANES ARGENTINOS"), 2100.0, 15, 3),
        ("Lino Dorado (1kg)", prov_map.get("NUTRIMIX"), 2550.0, 15, 3),
        ("Sésamo Blanco", prov_map.get("BIOSALUD"), 6171.0, 15, 3),
        ("Sésamo Integral", prov_map.get("BIOSALUD"), 1906.0, 15, 3),
        ("Sésamo Negro", prov_map.get("BIOSALUD"), 7874.0, 15, 3),
        ("Urucum", prov_map.get("BIOSALUD"), 2166.0, 15, 3),
        ("Trigo Sarraceno", prov_map.get("BIOSALUD"), 4711.0, 15, 3),
        ("Quinoa Mix (1kg)", prov_map.get("BIOSALUD"), 8030.0, 15, 3),
        ("Girasol", prov_map.get("BIOSALUD"), 3500.0, 15, 3)
    ]

    for p in productos_totales:
        cursor.execute("INSERT INTO productos (nombre, proveedor_id, costo, stock, stock_minimo) VALUES (?, ?, ?, ?, ?)", p)

    conn.commit()
    conn.close()
    print("¡Base de datos creada y precargada con éxito absoluto!")

if __name__ == '__main__':
    precargar_todo()