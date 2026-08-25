const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data'); // المكتبة الجديدة

const app = express();
const PORT = 5000; 

app.use(cors());
app.use(express.json());

const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
    destination: function (req, file, cb) { cb(null, uploadDir) },
    filename: function (req, file, cb) { cb(null, Date.now() + '-' + file.originalname) }
});
const upload = multer({ storage: storage });

app.get('/', (req, res) => res.json({ message: "بوابة Node.js تعمل!" }));

// ...
app.post('/api/upload-excel', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: "الرجاء رفع ملف إكسيل." });
        
        const lang = req.query.lang || 'ar';
        const hasIt = req.query.has_it || 'true';
        const hasArt = req.query.has_art || 'true';
        
        const formData = new FormData();
        formData.append('file', fs.createReadStream(req.file.path), req.file.originalname);
        
        // تمريرها إلى بايثون
        const pythonResponse = await axios.post(`http://127.0.0.1:8000/parse-excel/?lang=${lang}&has_it=${hasIt}&has_art=${hasArt}`, formData, {
            headers: { ...formData.getHeaders() }
        });
        
        fs.unlinkSync(req.file.path);
        res.json(pythonResponse.data);

    } catch (error) {
        if (req.file) fs.unlinkSync(req.file.path);
        
        // 🔴 استخراج رسالة بايثون الحقيقية وإرسالها لـ React
        const statusCode = error.response?.status || 500;
        const errorMessage = error.response?.data?.detail || "حدث خطأ داخلي في الخادم.";
        
        console.error('Python Error:', errorMessage);
        res.status(statusCode).json({ detail: errorMessage });
    }
});
// ...


// أضف هذا الكود قبل app.listen
app.get('/api/regenerate-pdf/:job_id', async (req, res) => {
    try {
        const lang = req.query.lang || 'ar';
        const jobId = req.params.job_id;
        
        const pythonResponse = await axios.get(`http://127.0.0.1:8000/regenerate-pdf/${jobId}?lang=${lang}`);
        res.json(pythonResponse.data);
    } catch (error) {
        res.status(500).json({ error: "فشل تحديث الجدول", details: error.message });
    }
});

// 🔴 جسر التحميل الآمن (يحل مشكلة حماية المتصفح CORS)
app.get('/api/download/:job_id/:filename', async (req, res) => {
    try {
        const { job_id, filename } = req.params;
        const response = await axios.get(`http://127.0.0.1:8000/download/${job_id}/${filename}`, {
            responseType: 'stream'
        });
        
        // إجبار المتصفح على تحميل الملف كـ PDF
        res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(filename)}"`);
        res.setHeader('Content-Type', 'application/pdf');
        
        response.data.pipe(res);
    } catch (error) {
        console.error("Download Error:", error.message);
        res.status(404).send("الملف غير موجود أو انتهت صلاحيته");
    }
});
app.listen(PORT, () => {
    console.log(`Node.js Server is running on http://localhost:${PORT}`);
});