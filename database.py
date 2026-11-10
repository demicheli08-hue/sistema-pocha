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
    
    # --- AUTO-CARGA DE DATOS SI LA TABLA ESTÁ VACÍA ---
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        # Proveedores de ejemplo
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('Natural Distribuciones', 'Carlos', '1122334455')")
        cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES ('Alimentos Andinos', 'Lucía', '1199887766')")
        
        # Clientes de ejemplo
        cursor.execute("INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES ('María Gómez', '1144332211', 0.0)")
        cursor.execute("INSERT INTO clientes (nombre, telefono, saldo_cta_cte) VALUES ('Juan Pérez', '1155667788', 1500.0)")
        
        # Productos de ejemplo
        cursor.execute("INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo) VALUES ('Almendras x 100g', 1, 1200.0, NULL, 25.0, 5.0)")
        cursor.execute("INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo) VALUES ('Nueces Peladas x 250g', 1, 2400.0, 35.0, 15.0, 4.0)")
        cursor.execute("INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo) VALUES ('Aceite de Coco Orgánico', 2, 4500.0, NULL, 10.0, 3.0)")
        cursor.execute("INSERT INTO productos (nombre, proveedor_id, costo, margen_individual, stock, stock_minimo) VALUES ('Azúcar Mascabo x 1kg', 2, 1100.0, 25.0, 30.0, 6.0)")

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME)
