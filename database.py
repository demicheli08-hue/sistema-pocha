import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, 'pocha_negocio.db')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            saldo_cta_cte REAL DEFAULT 0.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
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
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente_id INTEGER,
            tipo_pago TEXT,
            total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
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
        CREATE TABLE IF NOT EXISTS config (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO config (clave, valor) VALUES ('margen_general', '30')")
    
    # --- AUTO-CARGA DE DATOS REALES DEL EXCEL SI LA TABLA ESTÁ VACÍA ---
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        # Proveedores del Excel
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('BIOSALUD', 'General', '1100000001')")
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('PECANES ARGENTINOS', 'General', '1100000002')")
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('NUTRIMIX', 'General', '1100000003')")
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('CHAYA FRUTOS SECOS', 'General', '1100000004')")
        
        # Clientes de ejemplo
        cursor.execute("INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES ('Romina', '1144332211', 0.0)")
        cursor.execute("INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES ('María Gómez', '1155667788', 1500.0)")
        
        # Productos extraídos del Excel (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo)
        productos_excel = [
            ("Chía (1kg)", 1, 7458.0, 75.0, 10.0, 3.0),
            ("Lino (1kg)", 2, 2100.0, 75.0, 15.0, 3.0),
            ("Lino Dorado (1kg)", 3, 2550.0, 75.0, 10.0, 3.0),
            ("Sésamo Blanco", 1, 6171.0, 75.0, 8.0, 2.0),
            ("Sésamo Integral", 1, 1906.0, 75.0, 12.0, 3.0),
            ("Sésamo Negro", 1, 7874.0, 75.0, 5.0, 2.0),
            ("Urucum", 1, 2166.0, 75.0, 10.0, 2.0),
            ("Trigo Sarraceno", 1, 4711.0, 75.0, 6.0, 2.0),
            ("Quinoa Mix (1kg)", 1, 8030.0, 75.0, 10.0, 3.0),
            ("Girasol", 1, 3500.0, 75.0, 15.0, 4.0),
            ("Calabaza", 1, 11500.0, 75.0, 8.0, 2.0),
            ("Mix de Semillas", 1, 4168.0, 75.0, 20.0, 5.0),
            ("Amapola", 1, 13890.0, 75.0, 5.0, 2.0),
            ("Amaranto", 1, 9027.0, 75.0, 7.0, 2.0),
            ("Psyllium", 1, 14453.0, 75.0, 4.0, 2.0),
            ("Mix Tradicional (500g)", 4, 4800.0, 30.0, 15.0, 4.0),
            ("Mix Tradicional c/ Banana (500g)", 4, 6500.0, 30.0, 12.0, 3.0),
            ("Mix Premium (500g)", 4, 8300.0, 30.0, 10.0, 3.0),
            ("Nueces (500g)", 4, 8000.0, 30.0, 10.0, 3.0),
            ("Almendras (500g)", 4, 10500.0, 30.0, 15.0, 4.0),
            ("Arándanos Deshidratados (500g)", 4, 10755.0, 30.0, 10.0, 3.0),
            ("Ciruelas Deshidratadas (500g)", 4, 4500.0, 30.0, 12.0, 3.0),
            ("Castañas de Cajú (200g)", 4, 4200.0, 30.0, 10.0, 3.0),
            ("Granola Crocante (500g)", 4, 8200.0, 30.0, 8.0, 2.0)
        ]
        
        for p in productos_excel:
            cursor.execute("""
                INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, p)

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME)
