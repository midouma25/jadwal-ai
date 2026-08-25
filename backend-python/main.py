from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import subprocess
import os
import traceback
from pathlib import Path
import pandas as pd
import io
from core.xml_builder import FETXMLBuilder
from core.pdf_engine import PDFGenerator
from core.fet_parser import FETParser

BASE_DIR = Path(__file__).resolve().parent
FET_PATH = BASE_DIR / "fet-core" / "fet-cl.exe"
TEMP_DIR = BASE_DIR / "temp_jobs"
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI(title="JadwalAI Engine", version="1.0")

@app.get("/")
def read_root():
    return {"status": "online"}

# أضفنا has_it و has_art لاستقبالها من React
@app.post("/parse-excel/")
async def parse_excel(lang: str = "ar", has_it: str = "true", has_art: str = "true", file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df_classes = pd.read_excel(io.BytesIO(contents), sheet_name='الأقسام')
        df_teachers = pd.read_excel(io.BytesIO(contents), sheet_name='الأساتذة')
        df_assignments = pd.read_excel(io.BytesIO(contents), sheet_name='الإسناد')
        
        # نمرر المفاتيح هنا
        builder = FETXMLBuilder(df_classes, df_teachers, df_assignments, has_it=has_it, has_art=has_art)
        fet_xml_content = builder.build()
        # ... باقي الدالة كما هي
        
        job_id = f"job_{os.urandom(4).hex()}"
        job_dir = TEMP_DIR / job_id
        os.makedirs(job_dir, exist_ok=True)
        
        input_file = job_dir / f"{job_id}.fet"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(fet_xml_content)
            
        # 🔴 الإصلاح هنا: حذفنا --warn=false المرفوضة
        command = [str(FET_PATH), f"--inputfile={str(input_file)}", f"--outputdir={str(job_dir)}"]
        process = subprocess.run(command, capture_output=True, text=True, timeout=120)
        
        if process.returncode != 0:
            return {"status": "error", "message": "فشل FET", "details": process.stderr or process.stdout}
            
# داخل دالة parse_excel بعد process.returncode != 0
        parser = FETParser(str(job_dir), job_id)
        teachers_schedules, classes_schedules = parser.get_all_schedules()
        
        pdf_engine = PDFGenerator(str(job_dir), lang)
        teachers_file, classes_file, merged_classes = pdf_engine.generate_all_pdfs(teachers_schedules, classes_schedules)
        
# 🔴 توجيه الروابط نحو بوابة Node.js الآمنة
        base_url = f"http://localhost:5000/api/download/{job_id}"
            
        return {
            "status": "success",
            "message": "تم توليد الجداول بنجاح!",
            "job_id": job_id,
            "pdf_urls": {
                "teachers": f"{base_url}/{teachers_file}",
                "classes": f"{base_url}/{classes_file}"
            },
            "schedule_data": {
                "teachers": teachers_schedules,
                "classes": classes_schedules  
            }
        }
    except ValueError as ve:
        # التقاط الخطأ البيداغوجي (مثل أستاذ جديد يدرس 4 متوسط) وإرساله كخطأ 400
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{job_id}/{filename}")
def download_pdf(job_id: str, filename: str):
    file_path = TEMP_DIR / job_id / filename
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
    raise HTTPException(status_code=404, detail="الملف غير موجود")

@app.get("/regenerate-pdf/{job_id}")
def regenerate_pdf(job_id: str, lang: str = "ar"):
    try:
        job_dir = TEMP_DIR / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail="الجدول غير موجود")
        
        parser = FETParser(str(job_dir), job_id)
        teachers_schedules, classes_schedules = parser.get_all_schedules()
        
        pdf_engine = PDFGenerator(str(job_dir), lang)
        teachers_file, classes_file, merged_classes = pdf_engine.generate_all_pdfs(teachers_schedules, classes_schedules)
        
        base_url = f"http://127.0.0.1:8000/download/{job_id}"
            
        return {
            "status": "success",
            "message": "تم توليد الجداول بنجاح!",
            "job_id": job_id,
            "pdf_urls": {
                "teachers": f"{base_url}/{teachers_file}",
                "classes": f"{base_url}/{classes_file}"
            },
            "schedule_data": {
                "teachers": teachers_schedules,
                "classes": merged_classes  # 🔴 نرسل الجداول المدمجة لكي تظهر أنيقة في الموقع!
            }
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{job_id}/{filename}")
def download_pdf(job_id: str, filename: str):
    file_path = TEMP_DIR / job_id / filename
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
    raise HTTPException(status_code=404, detail="الملف غير موجود")

# أضف هذا الكود في أسفل ملف main.py
@app.get("/regenerate-pdf/{job_id}")
def regenerate_pdf(job_id: str, lang: str = "ar"):
    try:
        job_dir = TEMP_DIR / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail="الجدول غير موجود")
        
        parser = FETParser(str(job_dir), job_id)
        teacher_schedule = parser.get_teacher_schedule("أحمد")
        
        pdf_engine = PDFGenerator(str(job_dir), lang)
        pdf_filename = pdf_engine.generate_teacher_schedule("أحمد", teacher_schedule)
        
        download_url = f"http://127.0.0.1:8000/download/{job_id}/{pdf_filename}"
        return {"status": "success", "pdf_url": download_url}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))