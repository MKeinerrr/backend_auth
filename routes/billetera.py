import pymysql
from fastapi import APIRouter, Depends, HTTPException

from database import get_db_connection
from models import MetodoBilleteraIn, MetodoBilleteraOut
from utils.security import get_current_user

router = APIRouter()


@router.get('/metodos', response_model=list[MetodoBilleteraOut])
def list_metodos_billetera(user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    um.id_usuario_metodo,
                    um.id_metodo,
                    m.nombre AS metodo,
                    um.alias,
                    um.numero,
                    um.estado,
                    um.creado_en
                FROM usuarios_metodos um
                INNER JOIN metodos m ON m.id_metodo = um.id_metodo
                WHERE um.id_usuario = %s AND um.estado = 1
                ORDER BY um.creado_en DESC
                ''',
                (int(user['user_id']),),
            )
            rows = cursor.fetchall()

        return [
            MetodoBilleteraOut(
                id=int(row['id_usuario_metodo']),
                metodo_id=int(row['id_metodo']),
                metodo=row['metodo'],
                alias=row.get('alias'),
                numero=row.get('numero'),
                estado=bool(row['estado']),
                creado_en=row.get('creado_en'),
            )
            for row in rows
        ]
    finally:
        connection.close()


@router.post('/metodos', response_model=MetodoBilleteraOut)
def add_metodo_billetera(
    payload: MetodoBilleteraIn,
    user: dict = Depends(get_current_user),
):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id_metodo, nombre FROM metodos WHERE id_metodo = %s AND estado = 1',
                (payload.metodo_id,),
            )
            metodo = cursor.fetchone()
            if metodo is None:
                raise HTTPException(status_code=404, detail='Metodo no encontrado')

            cursor.execute(
                '''
                INSERT INTO usuarios_metodos (
                    id_usuario,
                    id_metodo,
                    alias,
                    numero,
                    estado
                ) VALUES (%s, %s, %s, %s, 1)
                ''',
                (
                    int(user['user_id']),
                    payload.metodo_id,
                    payload.alias,
                    payload.numero,
                ),
            )
            metodo_id = int(cursor.lastrowid)

        connection.commit()

        return MetodoBilleteraOut(
            id=metodo_id,
            metodo_id=payload.metodo_id,
            metodo=metodo['nombre'],
            alias=payload.alias,
            numero=payload.numero,
            estado=True,
            creado_en=None,
        )
    except pymysql.MySQLError as exc:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail='No se pudo guardar el metodo',
        ) from exc
    finally:
        connection.close()


@router.delete('/metodos/{usuario_metodo_id}')
def delete_metodo_billetera(
    usuario_metodo_id: int,
    user: dict = Depends(get_current_user),
):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                DELETE FROM usuarios_metodos
                WHERE id_usuario_metodo = %s AND id_usuario = %s
                ''',
                (usuario_metodo_id, int(user['user_id'])),
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail='Metodo no encontrado')
        connection.commit()
        return {'success': True}
    finally:
        connection.close()
