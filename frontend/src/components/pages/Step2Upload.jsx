import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

export default function Step2Upload({ onBack, onNext }) {
  const { t, i18n } = useTranslation();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploadStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    const currentLang = i18n.language.split('-')[0];

try {
      // 1. إرسال الملف إلى الخادم
      const response = await axios.post(`http://localhost:5000/api/upload-excel?lang=ar&has_it=false&has_art=false`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // 2. استخراج البيانات بنجاح
      const resultData = response.data.python_analysis || response.data;

      if (resultData && resultData.status === 'success') {
        
        // 3. إيقاف عجلة التحميل
        setUploadStatus('success'); 

        // 4. الانتقال الذكي للخطوة 3 (التوليد والنتائج)
        // يبحث الكود عن الدالة المتاحة في مشروعك ويقوم بتشغيلها
        if (typeof onNext === 'function') {
            onNext(resultData);
        } else if (typeof setStep === 'function') {
            if (typeof setScheduleData === 'function') {
                setScheduleData(resultData); // حفظ روابط الـ PDF
            }
            setStep(3); // الانتقال للخطوة الثالثة
        } else {
            // في حال كان اسم الدالة مختلفاً تماماً في مشروعك
            alert("✅ تم توليد الجداول بنجاح! يرجى المتابعة للخطوة الثالثة لرؤية النتائج.");
        }

      } else {
        setUploadStatus('error');
        alert("حدث خطأ في قراءة الاستجابة من الخادم.");
      }

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error'); // إيقاف التحميل وإظهار الخطأ
      const errorMsg = error.response?.data?.detail || "حدث خطأ أثناء الرفع";
      alert("تنبيه من الذكاء الاصطناعي ⚠️\n\n" + errorMsg);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 text-center">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept=".xlsx, .xls"
        className="hidden"
      />

      <div
        onClick={() => fileInputRef.current.click()}
        className={`border-2 border-dashed transition-colors cursor-pointer p-16 rounded-2xl flex flex-col items-center justify-center gap-4
          ${file ? 'border-green-400 bg-green-50' : 'border-blue-300 bg-blue-50 hover:bg-blue-100'}
        `}
      >
         <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm text-2xl">
           {file ? '✅' : '📊'}
         </div>
         <div>
           <p className={`font-bold text-lg ${file ? 'text-green-800' : 'text-blue-900'}`}>
             {file ? file.name : t('drag_drop')}
           </p>
           {!file && <p className="text-blue-600 text-sm mt-1">{t('click_to_browse')}</p>}

           {uploadStatus === 'uploading' && <p className="text-blue-600 mt-2 font-bold">{t('uploading')}</p>}
           {uploadStatus === 'success' && <p className="text-green-600 mt-2 font-bold">{t('upload_success')}</p>}
         </div>
      </div>

      <div className="flex gap-4">
         <button onClick={onBack} disabled={uploadStatus === 'uploading'} className="flex-1 bg-slate-100 text-slate-700 py-3.5 rounded-xl font-semibold hover:bg-slate-200 transition-colors disabled:opacity-50">
           {t('btn_back_settings')}
         </button>
         <button onClick={handleUpload} disabled={!file || uploadStatus === 'uploading' || uploadStatus === 'success'} className="flex-1 bg-blue-800 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors shadow-md disabled:bg-slate-400">
           {uploadStatus === 'success' ? 'تم الرفع' : t('btn_next_generate')}
         </button>
      </div>
    </div>
  );
}