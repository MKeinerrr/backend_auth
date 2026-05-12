from datetime import date, datetime

from pydantic import BaseModel, Field


class UsuarioAuth(BaseModel):
    usuario: str = Field(min_length=1)
    password: str = Field(min_length=6)


class UsuarioRegistro(BaseModel):
    nombre: str = Field(min_length=1)
    apellido: str = Field(min_length=1)
    usuario: str = Field(min_length=1)
    correo: str = Field(min_length=5)
    password: str = Field(min_length=6, pattern=r'^\S+$')
    identidad: str | None = None
    num_identidad: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    foto_url: str | None = None


class PasswordResetRequest(BaseModel):
    usuario: str = Field(min_length=1)
    new_password: str = Field(min_length=6, pattern=r'^\S+$')


class Usuario(BaseModel):
    id_usuario: int | None = None
    nombre: str
    apellido: str
    usuario: str | None = None
    correo: str
    telefono: str | None = None
    direccion: str | None = None
    foto_url: str | None = None
    estado: bool | None = None
    creado_en: datetime | None = None


class SalonOut(BaseModel):
    id: int
    nombre: str
    zona: str
    nivel: int | None = None
    capacidad: int
    precio: float
    slug: str
    foto: str | None = None
    video: str | None = None
    descripcion: str
    politicas: str | None = None
    estado: bool
    categoria_id: int
    categoria: str
    calificacion: float
    badges: list[str]


class ReservaCreate(BaseModel):
    salon_id: int = Field(gt=0)
    fecha: date
    franja_horaria_id: int = Field(gt=0)
    asistentes: int = Field(gt=0)
    descuento: float | None = Field(default=0, ge=0)
    abono: float | None = Field(default=0, ge=0)
    motivo: str | None = None
    garantia: str | None = None
    notas: str | None = None
    metodo_id: int | None = Field(default=None, gt=0)
    num_transaccion: str | None = None


class ReservaOut(BaseModel):
    id: int
    codigo: str
    salon_id: int
    fecha: date
    franja_horaria_id: int
    asistentes: int
    estado: str
    subtotal: float
    descuento: float
    monto: float
    abono: float
    notas: str | None = None


class ReservaHistorialOut(BaseModel):
    id: int
    codigo: str
    salon_id: int
    salon: str
    fecha: date
    franja_horaria: str
    asistentes: int
    estado: str
    monto: float
    abono: float
    notas: str | None = None
    creado_en: datetime


class CategoriaOut(BaseModel):
    id: int
    nombre: str


class FranjaHorariaOut(BaseModel):
    id: int
    nombre: str
    hora_inicio: str
    hora_fin: str


class MetodoOut(BaseModel):
    id: int
    nombre: str


class PerfilOut(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    usuario: str | None = None
    correo: str
    telefono: str | None = None
    direccion: str | None = None
    foto_url: str | None = None


class PerfilUpdate(BaseModel):
    usuario: str | None = Field(default=None, min_length=1)
    telefono: str | None = None
    direccion: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=6, pattern=r'^\S+$')
    new_password: str = Field(min_length=6, pattern=r'^\S+$')


class MetodoBilleteraIn(BaseModel):
    metodo_id: int = Field(gt=0)
    alias: str | None = None
    numero: str | None = None


class MetodoBilleteraOut(BaseModel):
    id: int
    metodo_id: int
    metodo: str
    alias: str | None = None
    numero: str | None = None
    estado: bool
    creado_en: datetime | None = None
