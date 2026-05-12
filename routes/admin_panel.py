from typing import Any

import pymysql
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from database import get_db_connection
from utils.security import get_current_user, get_password_hash

def _require_admin(user: dict = Depends(get_current_user)) -> dict:
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id_usuario, rol, estado
                FROM usuarios
                WHERE id_usuario = %s
                ''',
                (user.get('user_id'),),
            )
            row = cursor.fetchone()
    finally:
        connection.close()

    if row is None or not bool(row.get('estado', 1)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Usuario sin permisos',
        )

    rol = int(row.get('rol', 0) or 0)
    if rol < 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Usuario sin permisos',
        )

    return row


router = APIRouter(dependencies=[Depends(_require_admin)])


class UsuarioAdminCreate(BaseModel):
    nombre: str = Field(min_length=1)
    apellido: str = Field(min_length=1)
    usuario: str | None = None
    correo: str = Field(min_length=3)
    telefono: str | None = None
    identidad: str | None = None
    num_identidad: str | None = None
    rol: int = 1
    estado: int = 1
    direccion: str | None = None
    clave: str = Field(min_length=6)


class UsuarioAdminUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    usuario: str | None = None
    correo: str | None = None
    telefono: str | None = None
    identidad: str | None = None
    num_identidad: str | None = None
    rol: int | None = None
    estado: int | None = None
    direccion: str | None = None
    clave: str | None = None


class SalonAdminCreate(BaseModel):
    nombre: str = Field(min_length=1)
    zona: str = Field(min_length=1)
    capacidad: int = Field(gt=0)
    precio: float = Field(ge=0)
    nivel: int | None = None
    id_categoria: int = Field(gt=0)
    slug: str = Field(min_length=1)
    foto: str | None = None
    video: str | None = None
    descripcion: str = Field(min_length=1)
    politicas: str | None = None
    estado: int = 1


class SalonAdminUpdate(BaseModel):
    nombre: str | None = None
    zona: str | None = None
    capacidad: int | None = None
    precio: float | None = None
    nivel: int | None = None
    id_categoria: int | None = None
    slug: str | None = None
    foto: str | None = None
    video: str | None = None
    descripcion: str | None = None
    politicas: str | None = None
    estado: int | None = None


class ReservaAdminCreate(BaseModel):
    codigo: str | None = None
    subtotal: float = Field(ge=0)
    descuento: float = Field(default=0, ge=0)
    monto: float = Field(ge=0)
    abono: float = Field(default=0, ge=0)
    num_transaccion: str | None = None
    asistentes: int = Field(gt=0)
    motivo: str | None = None
    garantia: str | None = None
    notas: str | None = None
    estado: str = 'Pendiente'
    fecha: str
    id_salon: int = Field(gt=0)
    id_usuario: int = Field(gt=0)
    id_franja_horaria: int = Field(gt=0)
    id_metodo: int | None = None


class ReservaAdminUpdate(BaseModel):
    codigo: str | None = None
    subtotal: float | None = None
    descuento: float | None = None
    monto: float | None = None
    abono: float | None = None
    num_transaccion: str | None = None
    asistentes: int | None = None
    motivo: str | None = None
    garantia: str | None = None
    notas: str | None = None
    estado: str | None = None
    fecha: str | None = None
    id_salon: int | None = None
    id_usuario: int | None = None
    id_franja_horaria: int | None = None
    id_metodo: int | None = None


class CategoriaAdminCreate(BaseModel):
    nombre: str = Field(min_length=1)
    estado: int = 1


class CategoriaAdminUpdate(BaseModel):
    nombre: str | None = None
    estado: int | None = None


class FranjaAdminCreate(BaseModel):
    nombre: str = Field(min_length=1)
    hora_inicio: str
    hora_fin: str
    estado: int = 1


class FranjaAdminUpdate(BaseModel):
    nombre: str | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    estado: int | None = None


class MetodoAdminCreate(BaseModel):
    nombre: str = Field(min_length=1)
    estado: int = 1


class MetodoAdminUpdate(BaseModel):
    nombre: str | None = None
    estado: int | None = None


class CierreAdminCreate(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    motivo: str | None = None
    estado: int = 1


class CierreAdminUpdate(BaseModel):
    fecha_inicio: str | None = None
    fecha_fin: str | None = None
    motivo: str | None = None
    estado: int | None = None


class EmpresaUpdate(BaseModel):
    NIT: str
    nombre: str
    telefono: str
    direccion: str
    correo: str
    mensaje: str
    politicas: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    instagram: str | None = None
    whatsapp: str


def _apply_limit(rows: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None:
        return rows
    return rows[: max(0, int(limit))]


def _raise_integrity_error(exc: pymysql.MySQLError) -> None:
    raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/usuarios')
def list_usuarios(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM usuarios ORDER BY id_usuario DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/usuarios')
def create_usuario(payload: UsuarioAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            hashed = get_password_hash(payload.clave)
            cursor.execute(
                '''
                INSERT INTO usuarios (
                    identidad,
                    num_identidad,
                    nombre,
                    apellido,
                    usuario,
                    correo,
                    telefono,
                    direccion,
                    clave,
                    rol,
                    estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    payload.identidad,
                    payload.num_identidad,
                    payload.nombre,
                    payload.apellido,
                    payload.usuario,
                    payload.correo,
                    payload.telefono,
                    payload.direccion,
                    hashed,
                    payload.rol,
                    payload.estado,
                ),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/usuarios/{usuario_id}')
def update_usuario(usuario_id: int, payload: UsuarioAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    if 'clave' in data and data['clave']:
        data['clave'] = get_password_hash(data['clave'])
    elif 'clave' in data:
        data.pop('clave')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [usuario_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'UPDATE usuarios SET {sets} WHERE id_usuario = %s', values)
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/usuarios/{usuario_id}')
def delete_usuario(usuario_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM usuarios WHERE id_usuario = %s', (usuario_id,))
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/salones')
def list_salones(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM salones ORDER BY id_salon DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/salones')
def create_salon(payload: SalonAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO salones (
                    nombre,
                    zona,
                    nivel,
                    capacidad,
                    precio,
                    slug,
                    foto,
                    video,
                    descripcion,
                    politicas,
                    estado,
                    id_categoria
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    payload.nombre,
                    payload.zona,
                    payload.nivel,
                    payload.capacidad,
                    payload.precio,
                    payload.slug,
                    payload.foto,
                    payload.video,
                    payload.descripcion,
                    payload.politicas,
                    payload.estado,
                    payload.id_categoria,
                ),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/salones/{salon_id}')
def update_salon(salon_id: int, payload: SalonAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [salon_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'UPDATE salones SET {sets} WHERE id_salon = %s', values)
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/salones/{salon_id}')
def delete_salon(salon_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM salones WHERE id_salon = %s', (salon_id,))
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/reservas')
def list_reservas(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM reservas ORDER BY id_reserva DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/reservas')
def create_reserva(payload: ReservaAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO reservas (
                    codigo,
                    subtotal,
                    descuento,
                    monto,
                    abono,
                    num_transaccion,
                    asistentes,
                    motivo,
                    garantia,
                    notas,
                    estado,
                    fecha,
                    id_salon,
                    id_usuario,
                    id_franja_horaria,
                    id_metodo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    payload.codigo or 'TMP',
                    payload.subtotal,
                    payload.descuento,
                    payload.monto,
                    payload.abono,
                    payload.num_transaccion,
                    payload.asistentes,
                    payload.motivo,
                    payload.garantia,
                    payload.notas,
                    payload.estado,
                    payload.fecha,
                    payload.id_salon,
                    payload.id_usuario,
                    payload.id_franja_horaria,
                    payload.id_metodo,
                ),
            )
            reserva_id = cursor.lastrowid
            if not payload.codigo:
                cursor.execute(
                    'UPDATE reservas SET codigo = %s WHERE id_reserva = %s',
                    (f'RES-{int(reserva_id):06d}', reserva_id),
                )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/reservas/{reserva_id}')
def update_reserva(reserva_id: int, payload: ReservaAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [reserva_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'UPDATE reservas SET {sets} WHERE id_reserva = %s', values)
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/reservas/{reserva_id}')
def delete_reserva(reserva_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM reservas WHERE id_reserva = %s', (reserva_id,))
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/calificaciones')
def list_calificaciones(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM calificaciones ORDER BY id_calificacion DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.delete('/calificaciones/{calificacion_id}')
def delete_calificacion(calificacion_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM calificaciones WHERE id_calificacion = %s',
                (calificacion_id,),
            )
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/categorias')
def list_categorias(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM categorias ORDER BY id_categoria DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/categorias')
def create_categoria(payload: CategoriaAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO categorias (nombre, estado) VALUES (%s, %s)',
                (payload.nombre, payload.estado),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/categorias/{categoria_id}')
def update_categoria(categoria_id: int, payload: CategoriaAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [categoria_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE categorias SET {sets} WHERE id_categoria = %s',
                values,
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/categorias/{categoria_id}')
def delete_categoria(categoria_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM categorias WHERE id_categoria = %s', (categoria_id,))
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/franjas-horarias')
def list_franjas(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM franjas_horarias ORDER BY id_franja_horaria DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/franjas-horarias')
def create_franja(payload: FranjaAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO franjas_horarias (nombre, hora_inicio, hora_fin, estado)
                VALUES (%s, %s, %s, %s)
                ''',
                (payload.nombre, payload.hora_inicio, payload.hora_fin, payload.estado),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/franjas-horarias/{franja_id}')
def update_franja(franja_id: int, payload: FranjaAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [franja_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE franjas_horarias SET {sets} WHERE id_franja_horaria = %s',
                values,
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/franjas-horarias/{franja_id}')
def delete_franja(franja_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM franjas_horarias WHERE id_franja_horaria = %s',
                (franja_id,),
            )
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/metodos')
def list_metodos(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM metodos ORDER BY id_metodo DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/metodos')
def create_metodo(payload: MetodoAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO metodos (nombre, estado) VALUES (%s, %s)',
                (payload.nombre, payload.estado),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/metodos/{metodo_id}')
def update_metodo(metodo_id: int, payload: MetodoAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [metodo_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE metodos SET {sets} WHERE id_metodo = %s',
                values,
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/metodos/{metodo_id}')
def delete_metodo(metodo_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM metodos WHERE id_metodo = %s', (metodo_id,))
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/periodos-cierre')
def list_cierres(limit: int | None = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM periodos_cierre ORDER BY id_periodo_cierre DESC')
            rows = cursor.fetchall()
        return _apply_limit(rows, limit)
    finally:
        connection.close()


@router.post('/periodos-cierre')
def create_cierre(payload: CierreAdminCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO periodos_cierre (fecha_inicio, fecha_fin, motivo, estado)
                VALUES (%s, %s, %s, %s)
                ''',
                (payload.fecha_inicio, payload.fecha_fin, payload.motivo, payload.estado),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.put('/periodos-cierre/{cierre_id}')
def update_cierre(cierre_id: int, payload: CierreAdminUpdate):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    sets = ', '.join(f"{key} = %s" for key in data.keys())
    values = list(data.values()) + [cierre_id]

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE periodos_cierre SET {sets} WHERE id_periodo_cierre = %s',
                values,
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()


@router.delete('/periodos-cierre/{cierre_id}')
def delete_cierre(cierre_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM periodos_cierre WHERE id_periodo_cierre = %s',
                (cierre_id,),
            )
        connection.commit()
        return {'success': True}
    finally:
        connection.close()


@router.get('/empresa')
def get_empresa():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM empresa LIMIT 1')
            row = cursor.fetchone()
        return row or {}
    finally:
        connection.close()


@router.put('/empresa')
def update_empresa(payload: EmpresaUpdate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO empresa (
                    NIT,
                    nombre,
                    telefono,
                    direccion,
                    correo,
                    mensaje,
                    politicas,
                    facebook,
                    twitter,
                    instagram,
                    whatsapp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nombre = VALUES(nombre),
                    telefono = VALUES(telefono),
                    direccion = VALUES(direccion),
                    correo = VALUES(correo),
                    mensaje = VALUES(mensaje),
                    politicas = VALUES(politicas),
                    facebook = VALUES(facebook),
                    twitter = VALUES(twitter),
                    instagram = VALUES(instagram),
                    whatsapp = VALUES(whatsapp)
                ''',
                (
                    payload.NIT,
                    payload.nombre,
                    payload.telefono,
                    payload.direccion,
                    payload.correo,
                    payload.mensaje,
                    payload.politicas,
                    payload.facebook,
                    payload.twitter,
                    payload.instagram,
                    payload.whatsapp,
                ),
            )
        connection.commit()
        return {'success': True}
    except pymysql.MySQLError as exc:
        connection.rollback()
        _raise_integrity_error(exc)
    finally:
        connection.close()
