import os
import psycopg2

# Render provee la URL de PostgreSQL en la variable de entorno DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # Conexión a PostgreSQL en la nube (Render)
        return psycopg2.connect(DATABASE_URL, sslmode='binary')
    else:
        # Conexión local de respaldo por si lo ejecutas en tu PC
        import sqlite3
        return sqlite3.connect('pocha_negocio.db')

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sintaxis compatible con PostgreSQL y SQLite para la creación de tablas
    if DATABASE_URL:
        # PostgreSQL
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                telefono TEXT,
                saldo_cta_cte REAL DEFAULT 0.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                proveedor_id INTEGER REFERENCES proveedores(id),
                costo REAL NOT NULL,
                margen_individual REAL,
                stock REAL NOT NULL,
                stock_minimo REAL DEFAULT 5.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id SERIAL PRIMARY KEY,
                fecha TEXT,
                cliente_id INTEGER REFERENCES clientes(id),
                tipo_pago TEXT,
                total REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id SERIAL PRIMARY KEY,
                venta_id INTEGER REFERENCES ventas(id),
                producto_id INTEGER REFERENCES productos(id),
                cantidad REAL,
                precio_unitario REAL,
                subtotal REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        cursor.execute("INSERT INTO config (clave, valor) VALUES ('margen_general', '30') ON CONFLICT (clave) DO NOTHING")
    else:
        # SQLite (Local)
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
