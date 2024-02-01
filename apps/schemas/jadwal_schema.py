from datetime import date, time
from pydantic import BaseModel
from typing import Optional
from apps.helpers.generator import identity_generator

class JadwalSchema(BaseModel):
    kd_jadwal: str = identity_generator()
    tanggal: date
    waktu_mulai: time
    waktu_selesai: time
    kelas: str
    ruangan: str
    materi: str
    kd_matkul: str

    class Config:
        orm_mode = True
