import sqlite3

DB_NAME = 'pocha_negocio.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME)