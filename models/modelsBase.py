from typing import Optional, Union
from pydantic import BaseModel
import sqlite3



def init_db(nombre_db: str):
    conn = sqlite3.connect(nombre_db)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT UNIQUE,
            nombre TEXT,
            apellido TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            cuenta INTEGER,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()



class Cliente(BaseModel):
    id: Union[int, None] = None
    cedula: str
    nombre: str = None
    apellido: str= None

class Cuenta(BaseModel):
    id: Optional[int] = None
    cliente_id: int
    cuenta: int

class Pago(BaseModel):
    id: int
    cliente_id: int
    cuenta_id: int
    numero_factura: str
    monto: float
    moneda: str