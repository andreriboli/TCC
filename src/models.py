from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class Curso:
    id: int
    shortname: str
    fullname: str
    category: int
    progress: float
    completed: bool
    startdate: datetime
    enddate: datetime
    lastaccess: datetime
    tempo_medio_conclusao: float

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    cursos: List[Curso]
    total_cursos: int
    cursos_completados: int
    media_progresso: float
    primeiro_acesso: datetime
    ultimo_acesso: datetime

@dataclass
class VimeoVideo:
    id: int
    title: str
    description: str
    duration: int
    upload_date: datetime
    views: int
    likes: int
