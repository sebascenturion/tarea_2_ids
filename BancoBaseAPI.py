from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from models.modelsBase import Cliente, Cuenta, Pago, init_db
import sqlite3



app = FastAPI()

# Conexión y configuración de la base de datos
DATABASE = "bancobase.db"
init_db(DATABASE)


#TODO Recursos a implementar
# 1 - Cliente
# Registrar - POST /clientes
# listar - GET /clientes
# consultar- GET /clientes/{pk} 
# actualizar- PUT /clientes/{pk}
# eliminar - DELETE /clientes/{pk}

@app.post("/clientes/", response_model=Cliente)
def create_cliente(cliente: Cliente):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clientes (cedula, nombre, apellido)
            VALUES (?, ?, ?)
        ''', (cliente.cedula, cliente.nombre, cliente.apellido))
        conn.commit()
        cliente.id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Cliente con esta cedula ya existe")
    conn.close()
    return cliente

@app.get("/clientes/", response_model=List[Cliente])
def read_clientes(skip: int = 0, limit: int = 10):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, cedula, nombre, apellido
        FROM clientes
        LIMIT ? OFFSET ?
    ''', (limit, skip))
    rows = cursor.fetchall()
    conn.close()
    return [Cliente(id=row[0], cedula=row[1], nombre=row[2], apellido=row[3]) for row in rows]

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def read_cliente(cliente_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, cedula, nombre, apellido
        FROM clientes
        WHERE id = ?
    ''', (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return Cliente(id=row[0], cedula=row[1], nombre=row[2], apellido=row[3])

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def update_cliente(cliente_id: int, cliente: Cliente):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE clientes
        SET cedula = ?, nombre = ?, apellido = ?
        WHERE id = ?
    ''', (cliente.cedula, cliente.nombre, cliente.apellido, cliente_id))
    conn.commit()
    conn.close()
    cliente.id = cliente_id
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente

@app.delete("/clientes/{cliente_id}")
def delete_cliente(cliente_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM clientes
        WHERE id = ?
    ''', (cliente_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return {"message": "Cliente deleted"}

# 2 - Cuenta 
# - POST /cuentas
# - GET /cuentas
# - GET /cuentas/{pk} 
# - PUT /cuentas/{pk}
# - DELETE /cuentas/{pk}
# Función para verificar si un número de cuenta ya existe, excluyendo un ID específico
def check_unique_account_number(cuenta: int, exclude_id: int = None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM cuentas WHERE cuenta = ?"
    params = [cuenta]
    if exclude_id is not None:
        query += " AND id != ?"
        params.append(exclude_id)
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count == 0


# Función para verificar si un cliente existe
def check_existing_client(cliente_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*)
        FROM clientes
        WHERE id = ?
    ''', (cliente_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

@app.post("/cuentas/", response_model=Cuenta)
def create_cuenta(cuenta: Cuenta):
    if not cuenta.cuenta:
        raise HTTPException(status_code=400, detail="El número de cuenta es requerido")
    if not check_unique_account_number(cuenta.cuenta):
        raise HTTPException(status_code=400, detail="El número de cuenta ya existe")
    if not check_existing_client(cuenta.cliente_id):
        raise HTTPException(status_code=400, detail="El cliente no existe")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO cuentas (cliente_id, cuenta)
            VALUES (?, ?)
        ''', (cuenta.cliente_id, cuenta.cuenta))
        conn.commit()
        cuenta.id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Número de cuenta duplicado")
    conn.close()
    return cuenta

@app.get("/cuentas/", response_model=List[Cuenta])
def read_cuentas(skip: int = 0, limit: int = 10):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, cliente_id, cuenta
        FROM cuentas
        LIMIT ? OFFSET ?
    ''', (limit, skip))
    rows = cursor.fetchall()
    conn.close()
    return [Cuenta(id=row[0], cliente_id=row[1], cuenta=row[2]) for row in rows]

@app.get("/cuentas/{cuenta_id}", response_model=Cuenta)
def read_cuenta(cuenta_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, cliente_id, cuenta
        FROM cuentas
        WHERE id = ?
    ''', (cuenta_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return Cuenta(id=row[0], cliente_id=row[1], cuenta=row[2])

@app.put("/cuentas/{cuenta_id}", response_model=Cuenta)
def update_cuenta(cuenta_id: int, cuenta: Cuenta):
    if not cuenta.cuenta:
        raise HTTPException(status_code=400, detail="El número de cuenta es requerido")
    if not check_unique_account_number(cuenta.cuenta, exclude_id=cuenta_id):
        raise HTTPException(status_code=400, detail="El número de cuenta ya existe")
    if not check_existing_client(cuenta.cliente_id):
        raise HTTPException(status_code=400, detail="El cliente no existe")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE cuentas
        SET cliente_id = ?, cuenta = ?
        WHERE id = ?
    ''', (cuenta.cliente_id, cuenta.cuenta, cuenta_id))
    conn.commit()
    conn.close()
    cuenta.id = cuenta_id
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

@app.delete("/cuentas/{cuenta_id}")
def delete_cuenta(cuenta_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM cuentas
        WHERE id = ?
    ''', (cuenta_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return {"message": "Cuenta eliminada"}



# 3 - Pago 
# - POST /pagos
# - GET /pagos
# - GET /pagos/{pk} 
# - PUT /pagos/{pk}
# - DELETE /pagos/{pk}