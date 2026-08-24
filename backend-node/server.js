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
        
        // ⚠️ قراءة اللغة من الرابط
        const lang = req.query.lang || 'ar';
        
        const formData = new FormData();
        formData.append('file', fs.createReadStream(req.file.path), req.file.originalname);
        
        // ⚠️ تمرير اللغة إلى بايثون عبر الرابط لضمان وصولها 100%
        const pythonResponse = await axios.post(`http://127.0.0.1:8000/parse-excel/?lang=${lang}`, formData, {
            headers: { ...formData.getHeaders() }
        });
        
        fs.unlinkSync(req.file.path);
        
        res.json({ message: "تمت معالجة الملف بنجاح!", python_analysis: pythonResponse.data });
        
    } catch (error) {
        console.error("خطأ:", error.message);
        res.status(500).json({ error: "حدث خطأ أثناء معالجة الملف", details: error.message });
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


app.listen(PORT, () => {
    console.log(`Node.js Server is running on http://localhost:${PORT}`);
});