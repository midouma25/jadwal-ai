import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import Stepper from '../ui/Stepper';
import Step1Settings from './Step1Settings';
import Step2Upload from './Step2Upload';
import SchedulePreview from './SchedulePreview'; 

export default function GeneratorWizard() {
  const { t, i18n } = useTranslation();
  const [currentStep, setCurrentStep] = useState(1);

  const [pdfUrls, setPdfUrls] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [scheduleData, setScheduleData] = useState(null);

  const [formData, setFormData] = useState({
    schoolType: 'middle', afternoonStart: '13:00', pedagogicalDay: 'half',
    peLocation: 'yard', roomElasticity: true, autoOffDays: true
  });

  useEffect(() => {
    if (currentStep === 3 && jobId) {
      const fetchNewPdf = async () => {
        try {
          const currentLang = i18n.language.split('-')[0];
          const res = await axios.get(`http://localhost:5000/api/regenerate-pdf/${jobId}?lang=${currentLang}`);
          setPdfUrls(res.data.pdf_urls);
          // تحديث بيانات المعاينة أيضاً عند تغيير اللغة
          if (res.data.schedule_data) {
              setScheduleData(res.data.schedule_data);
          }
        } catch(e) {
          console.error("خطأ في تحديث الـ PDF", e);
        }
      };
      fetchNewPdf();
    }
  }, [i18n.language, currentStep, jobId]);

  return (
    <main className="max-w-4xl mx-auto mt-12 p-8 bg-white rounded-2xl shadow-sm border border-slate-200">
      <h2 className="text-2xl font-bold text-center mb-10 text-slate-800">{t('new_schedule')}</h2>

      <Stepper currentStep={currentStep} />

      <div className="py-4">
        {currentStep === 1 && (
          <Step1Settings
            formData={formData}
            setFormData={setFormData}
            onNext={() => setCurrentStep(2)}
          />
        )}

        {currentStep === 2 && (
          <Step2Upload
            onBack={() => setCurrentStep(1)}
            onNext={(urls, id, data) => {
              setPdfUrls(urls);
              setJobId(id);
              setScheduleData(data);
              setCurrentStep(3);
            }}
          />
        )}

        {currentStep === 3 && (
          <div className="space-y-6 animate-in fade-in duration-500 text-center">
            {!pdfUrls ? (
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center gap-4">
                <div className="w-12 h-12 border-4 border-slate-200 border-t-blue-800 rounded-full animate-spin"></div>
                <p className="text-slate-600 font-medium">{t('generating')}</p>
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded-xl p-10 flex flex-col items-center justify-center gap-4">
                <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center text-white text-3xl shadow-md">✓</div>
                <h3 className="text-xl font-bold text-green-800">{t('success_title')}</h3>
                <p className="text-green-700 font-medium">{t('success_desc')}</p>

                <div className="flex flex-col sm:flex-row gap-4 mt-4 w-full justify-center">
                  <a href={pdfUrls.teachers} target="_blank" rel="noreferrer" className="flex-1 bg-blue-700 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-800 transition-colors shadow-lg">
                    {t('download_teachers')}
                  </a>
                  <a href={pdfUrls.classes} target="_blank" rel="noreferrer" className="flex-1 bg-emerald-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-emerald-700 transition-colors shadow-lg">
                    {t('download_classes')}
                  </a>
                </div>
              </div>
            )}

            {/* 🔴 لوحة المعاينة الحية */}
            {scheduleData && <SchedulePreview data={scheduleData} />}

            <button
              onClick={() => {
                setCurrentStep(1);
                setPdfUrls(null);
                setJobId(null);
                setScheduleData(null);
              }}
              className="mt-6 bg-slate-100 text-slate-700 py-2.5 px-8 rounded-lg font-medium hover:bg-slate-200 transition-colors"
            >
              {t('btn_cancel')}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}