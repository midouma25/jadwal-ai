const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

const app = express();
// سنستخدم المنفذ 5000 لكي لا يتعارض مع خادم Python الذي يعمل على 8000
const PORT = 5000; 

// إعدادات الـ Middleware
app.use(cors());
app.use(express.json());

// إنشاء مجلد مؤقت لحفظ ملفات الإكسيل المرفوعة
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// إعداد مكتبة Multer لمعالجة الملفات
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadDir)
    },
    filename: function (req, file, cb) {
        // إضافة طابع زمني لمنع تداخل أسماء الملفات
        cb(null, Date.now() + '-' + file.originalname)
    }
});
const upload = multer({ storage: storage });

// 1. نقطة فحص خادم Node.js
app.get('/', (req, res) => {
    res.json({ message: "بوابة Node.js (API Gateway) تعمل بنجاح!" });
});

// 2. نقطة لاختبار الاتصال بخادم Python
app.get('/api/check-python', async (req, res) => {
    try {
        // نحاول الاتصال بالخادم الذي تركناه يعمل في النافذة الأخرى
        const response = await axios.get('http://127.0.0.1:8000/');
        res.json({ 
            message: "تم الاتصال بخادم Python بنجاح! 🤝", 
            python_response: response.data 
        });
    } catch (error) {
        res.status(500).json({ error: "فشل الاتصال بخادم Python. تأكد من تشغيله." });
    }
});

// 3. نقطة استقبال ملف الإكسيل من React
app.post('/api/upload-excel', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "الرجاء رفع ملف إكسيل." });
        }
        
        console.log("تم استلام الملف:", req.file.filename);
        
        // لاحقاً هنا سنرسل الملف إلى Python، لكن الآن نؤكد الاستلام فقط
        res.json({ 
            message: "تم استلام ملف الإكسيل بنجاح!", 
            filename: req.file.filename 
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Node.js Server is running on http://localhost:${PORT}`);
});