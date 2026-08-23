from fastapi import FastAPI, HTTPException
import subprocess
import os
from pathlib import Path

# تحديد مسار محرك FET-CL
BASE_DIR = Path(__file__).resolve().parent
FET_PATH = BASE_DIR / "fet-core" / "fet-cl.exe" # نستخدم .exe لأنك على ويندوز

app = FastAPI(title="JadwalAI Engine", version="1.0")

@app.get("/")
def read_root():
    """نقطة فحص حالة الخادم"""
    return {
        "status": "online",
        "message": "خادم محرك الجدول الذكي يعمل بنجاح!",
        "fet_exists": os.path.exists(FET_PATH)
    }

@app.get("/test-fet")
def test_fet_engine():
    """مسار لاختبار تشغيل FET-CL برمجياً"""
    if not os.path.exists(FET_PATH):
        raise HTTPException(status_code=500, detail="لم يتم العثور على محرك FET-CL")
    
    try:
        # تشغيل محرك FET كعملية خلفية (Subprocess)
        result = subprocess.run(
            [str(FET_PATH), "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "fet_version_output": result.stdout.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء تشغيل المحرك: {str(e)}")