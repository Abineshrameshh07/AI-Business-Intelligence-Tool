"""Run it with:
    uvicorn main:app --reload
"""

import os
import shutil
from pathlib import Path
import pandas as pd

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import init_db, get_db, Upload
from analysis import analyze_csv, analyze_docx, analyze_sql


app = FastAPI(title="AI BI System - Step 1: Upload & Storage")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


ALLOWED_EXTENSIONS = {".csv", ".docx", ".sql", ".xlsx", ".txt"}


@app.on_event("startup")
def on_startup():
    """Create database tables when the server starts."""
    init_db()


@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts a file upload, saves it to disk, and stores a record in the DB.
    Returns the new upload's ID and metadata.
    """
    ext = Path(file.filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # Save file to disk. We prefix with a placeholder id-like timestamp to avoid
    # overwriting files with the same name from different users.
    dest_path = UPLOAD_DIR / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Record it in the database
    new_upload = Upload(
        filename=file.filename,
        file_type=ext.replace(".", ""),
        file_path=str(dest_path),
        status="uploaded",
    )
    db.add(new_upload)
    db.commit()
    db.refresh(new_upload)  # refresh so new_upload.id is populated

    return {
        "id": new_upload.id,
        "filename": new_upload.filename,
        "file_type": new_upload.file_type,
        "status": new_upload.status,
        "uploaded_at": new_upload.uploaded_at,
    }

@app.get("/drilldown")
def drilldown(upload_id: int, column: str, value: str, db: Session = Depends(get_db)):
    """
    Returns all rows where a specific column matches a specific value.
    Works for CSV, DOCX (with table), and SQL files.
    Reads from the pre-parsed JSON file saved during analysis.
    """
    import json

    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Look for the pre-parsed JSON file saved during analysis
    parsed_path = upload.file_path + ".parsed.json"

    if not os.path.exists(parsed_path):
        raise HTTPException(
            status_code=400,
            detail="No parsed data found. Please re-analyze this file first."
        )

    with open(parsed_path, "r") as f:
        rows = json.load(f)

    # Filter rows where the clicked column matches the clicked value
    filtered = [row for row in rows if str(row.get(column, "")) == str(value)]

    if not filtered:
        raise HTTPException(
            status_code=404,
            detail=f"No rows found where {column} = {value}"
        )

    return filtered

@app.get("/uploads")
def list_uploads(db: Session = Depends(get_db)):
    """Returns all uploaded files, most recent first."""
    uploads = db.query(Upload).order_by(Upload.id.desc()).all()
    return uploads


@app.get("/uploads/{upload_id}")
def get_upload(upload_id: int, db: Session = Depends(get_db)):
    """Returns details for a single upload, or 404 if not found."""
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload


@app.post("/analyze/{upload_id}")
@app.post("/analyze/{upload_id}")
def analyze_upload(upload_id: int, db: Session = Depends(get_db)):
    """
    Runs analysis on a previously uploaded file and returns chart-ready data.
    """
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        if upload.file_type == "csv":
            result = analyze_csv(upload.file_path)
        elif upload.file_type == "docx":
            result = analyze_docx(upload.file_path)
        elif upload.file_type == "sql":
            result = analyze_sql(upload.file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Analysis for '{upload.file_type}' files isn't supported yet.",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Couldn't analyze this file: {str(e)}")

    result["upload_id"] = upload_id
    upload.status = "analyzed"
    db.commit()
    return result


@app.get("/")
def root():
    return {"message": "AI BI System backend is running. Try POST /upload"}
    