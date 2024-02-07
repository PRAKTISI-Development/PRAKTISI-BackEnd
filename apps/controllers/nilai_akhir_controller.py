import pandas as pd
from io import BytesIO
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from fastapi.responses import StreamingResponse

from apps.database import get_db
from apps.helpers.response import response
from apps.schemas.akumulasi_schema import *
from apps.schemas.nilai_akhir_schema import NilaiAkhirSchema
from apps.models.nilai_akhir import NilaiAkhir as NilaiAkhirModel

def create_nilai_akhir(nilai_akhir_data: NilaiAkhirSchema, db: Session = Depends(get_db)):
    db_nilai_akhir = NilaiAkhirModel(**nilai_akhir_data.model_dump())
    db.add(db_nilai_akhir)
    db.commit()
    db.refresh(db_nilai_akhir)
    return db_nilai_akhir


# on progress
def get_akumulasi(request, kd_matkul: str, db: Session = Depends(get_db)):
    try:
        params = kd_matkul
        query = text(f"call akumulasi_nilai_dan_kehadiran('{params}')")
        result = db.execute(query)
        
        data_rows = result.fetchall()
        column_names = result.keys()

        list_of_dicts = []

        for row in data_rows:
            data_dict = {}
            for column_name, value in zip(column_names, row):
                data_dict[column_name] = value
            list_of_dicts.append(data_dict)

        return response(request, status_code=200, success=True, msg="success get data", data=list_of_dicts)

    except HTTPException as e:
        return response(request, status_code=e.status_code, success=False, msg=e.detail, data=None)

def save_excel(request, kd_matkul: str, db: Session = Depends(get_db)):
    try:
        # Eksekusi query
        query = text(f"call akumulasi_nilai_dan_kehadiran('{kd_matkul}')")
        result = db.execute(query)

        # Ambil data dan nama kolom
        data = result.fetchall()
        column_names = result.keys()

        # Buat DataFrame dari hasil query
        df = pd.DataFrame(data, columns=column_names)

        # Ambil nilai praktikum
        praktikum_value = data[0][list(column_names).index('praktikum')]

        # Buat file Excel dalam bentuk buffer
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # Buat response StreamingResponse
        response = StreamingResponse(iter([excel_buffer.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Atur header Content-Disposition dengan nama file
        filename = f"Akumulasi {praktikum_value}.xlsx"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        # Atur Refresh header untuk redirect setelah download
        redirect_url = f"/v1/nilai_akhir/akumulasi/{kd_matkul}"
        response.headers["Refresh"] = f"1; url={redirect_url}"

        return response
    
    except HTTPException as e:
        return response(request, status_code=e.status_code, success=False, msg=e.detail, data=None)
# end progress



def get_nilai_akhir(usersid: str, kd_matkul: str, db: Session = Depends(get_db)):
    nilai_akhir = db.query(NilaiAkhirModel).filter(
        NilaiAkhirModel.usersid == usersid,
        NilaiAkhirModel.kd_matkul == kd_matkul
    ).first()
    
    if nilai_akhir is None:
        raise HTTPException(status_code=404, detail="Nilai Akhir not found")
    
    return nilai_akhir

def get_all_nilai_akhir(db: Session = Depends(get_db)):
    nilai_akhir_list = db.query(NilaiAkhirModel).all()
    return nilai_akhir_list

def update_nilai_akhir(nilai_akhir_data: NilaiAkhirModel, usersid: str, kd_matkul: str, db: Session = Depends(get_db)):
    db_nilai_akhir = db.query(NilaiAkhirModel).filter(
        NilaiAkhirModel.usersid == usersid,
        NilaiAkhirModel.kd_matkul == kd_matkul
    ).first()
    
    if db_nilai_akhir is None:
        raise HTTPException(status_code=404, detail="Nilai Akhir not found")
    
    for key, value in nilai_akhir_data.dict().items():
        setattr(db_nilai_akhir, key, value)
    
    db.commit()
    db.refresh(db_nilai_akhir)
    return db_nilai_akhir

def delete_nilai_akhir(usersid: str, kd_matkul: str, db: Session = Depends(get_db)):
    db_nilai_akhir = db.query(NilaiAkhirModel).filter(
        NilaiAkhirModel.usersid == usersid,
        NilaiAkhirModel.kd_matkul == kd_matkul
    ).first()
    
    if db_nilai_akhir is None:
        raise HTTPException(status_code=404, detail="Nilai Akhir not found")

    db.delete(db_nilai_akhir)
    db.commit()