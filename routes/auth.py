from fastapi import APIRouter, Depends, HTTPException

from database import get_db_connection
from models import (
    PasswordChangeRequest,
    PasswordResetRequest,
    PerfilOut,
    PerfilUpdate,
    UsuarioAuth,
    UsuarioRegistro,
)
from utils.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter()


@router.post('/registro')
def registro(data: UsuarioRegistro):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id_usuario FROM usuarios WHERE usuario = %s OR correo = %s',
                (data.usuario, data.correo),
            )
            existing = cursor.fetchone()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail='El usuario o correo ya existe',
                )

            password_hash = get_password_hash(data.password)
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
                    foto_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    data.identidad,
                    data.num_identidad,
                    data.nombre,
                    data.apellido,
                    data.usuario,
                    data.correo,
                    data.telefono,
                    data.direccion,
                    password_hash,
                    data.foto_url,
                ),
            )
        connection.commit()

        return {'success': True, 'message': 'Usuario creado exitosamente'}
    finally:
        connection.close()


@router.post('/login')
def login(data: UsuarioAuth):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id_usuario, usuario, correo, clave, estado
                FROM usuarios
                WHERE usuario = %s OR correo = %s
                ''',
                (data.usuario, data.usuario),
            )
            user = cursor.fetchone()

        if user is None or not verify_password(data.password, user['clave']):
            raise HTTPException(status_code=401, detail='Credenciales incorrectas')

        if not bool(user.get('estado', 1)):
            raise HTTPException(status_code=403, detail='Usuario inactivo')

        subject = user['usuario'] or user['correo']
        token = create_access_token(user_id=user['id_usuario'], username=subject)

        return {
            'success': True,
            'message': 'Autenticación exitosa',
            'usuario': subject,
            'token': token,
        }
    finally:
        connection.close()


@router.post('/forgot-password')
def forgot_password(data: PasswordResetRequest):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id_usuario FROM usuarios WHERE usuario = %s OR correo = %s',
                (data.usuario, data.usuario),
            )
            user = cursor.fetchone()

            if user is None:
                raise HTTPException(status_code=404, detail='Usuario no encontrado')

            password_hash = get_password_hash(data.new_password)
            cursor.execute(
                'UPDATE usuarios SET clave = %s WHERE id_usuario = %s',
                (password_hash, user['id_usuario']),
            )

        connection.commit()
        return {'success': True, 'message': 'Contraseña actualizada exitosamente'}
    finally:
        connection.close()


@router.get('/perfil', response_model=PerfilOut)
def get_profile(user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    id_usuario,
                    nombre,
                    apellido,
                    usuario,
                    correo,
                    telefono,
                    direccion,
                    foto_url
                FROM usuarios
                WHERE id_usuario = %s
                ''',
                (int(user['user_id']),),
            )
            row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')

        return PerfilOut(
            id_usuario=int(row['id_usuario']),
            nombre=row['nombre'],
            apellido=row['apellido'],
            usuario=row.get('usuario'),
            correo=row['correo'],
            telefono=row.get('telefono'),
            direccion=row.get('direccion'),
            foto_url=row.get('foto_url'),
        )
    finally:
        connection.close()


@router.put('/perfil', response_model=PerfilOut)
def update_profile(payload: PerfilUpdate, user: dict = Depends(get_current_user)):
    data = payload.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail='No hay campos para actualizar')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if 'usuario' in data:
                cursor.execute(
                    '''
                    SELECT id_usuario
                    FROM usuarios
                    WHERE usuario = %s AND id_usuario <> %s
                    ''',
                    (data['usuario'], int(user['user_id'])),
                )
                if cursor.fetchone() is not None:
                    raise HTTPException(
                        status_code=400,
                        detail='El usuario ya existe',
                    )

            sets = ', '.join(f"{key} = %s" for key in data.keys())
            values = list(data.values()) + [int(user['user_id'])]
            cursor.execute(
                f'UPDATE usuarios SET {sets} WHERE id_usuario = %s',
                values,
            )
        connection.commit()
    finally:
        connection.close()

    return get_profile(user)


@router.post('/change-password')
def change_password(
    payload: PasswordChangeRequest,
    user: dict = Depends(get_current_user),
):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT clave FROM usuarios WHERE id_usuario = %s',
                (int(user['user_id']),),
            )
            row = cursor.fetchone()

            if row is None or not verify_password(
                payload.current_password,
                row['clave'],
            ):
                raise HTTPException(status_code=400, detail='Clave actual invalida')

            new_hash = get_password_hash(payload.new_password)
            cursor.execute(
                'UPDATE usuarios SET clave = %s WHERE id_usuario = %s',
                (new_hash, int(user['user_id'])),
            )

        connection.commit()
        return {'success': True, 'message': 'Contraseña actualizada'}
    finally:
        connection.close()
