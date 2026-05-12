from fastapi import APIRouter

from database import get_db_connection
from models import CategoriaOut, FranjaHorariaOut, MetodoOut

router = APIRouter()


@router.get('/catalogos/categorias', response_model=list[CategoriaOut])
def listar_categorias():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id_categoria, nombre
                FROM categorias
                WHERE estado = 1
                ORDER BY nombre ASC
                '''
            )
            rows = cursor.fetchall()

        return [
            CategoriaOut(id=int(row['id_categoria']), nombre=row['nombre'])
            for row in rows
        ]
    finally:
        connection.close()


@router.get('/catalogos/franjas-horarias', response_model=list[FranjaHorariaOut])
def listar_franjas_horarias():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    id_franja_horaria,
                    nombre,
                    TIME_FORMAT(hora_inicio, '%H:%i') AS hora_inicio,
                    TIME_FORMAT(hora_fin, '%H:%i') AS hora_fin
                FROM franjas_horarias
                WHERE estado = 1
                ORDER BY hora_inicio ASC
                '''
            )
            rows = cursor.fetchall()

        return [
            FranjaHorariaOut(
                id=int(row['id_franja_horaria']),
                nombre=row['nombre'],
                hora_inicio=str(row['hora_inicio']),
                hora_fin=str(row['hora_fin']),
            )
            for row in rows
        ]
    finally:
        connection.close()


@router.get('/catalogos/metodos', response_model=list[MetodoOut])
def listar_metodos():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id_metodo, nombre
                FROM metodos
                WHERE estado = 1
                ORDER BY nombre ASC
                '''
            )
            rows = cursor.fetchall()

        return [MetodoOut(id=int(row['id_metodo']), nombre=row['nombre']) for row in rows]
    finally:
        connection.close()
