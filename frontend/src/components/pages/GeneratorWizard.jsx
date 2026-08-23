import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Stepper from '../ui/Stepper';

export default function GeneratorWizard() {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <main className="max-w-4xl mx-auto mt-12 p-8 bg-white rounded-2xl shadow-sm border border-slate-200">
      <h2 className="text-2xl font-bold text-center mb-10 text-slate-800">{t('new_schedule')}</h2>
      
      <Stepper currentStep={currentStep} />

      <div className="py-4">
        {/* الخطوة 1: الإعدادات */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 text-center text-blue-800">
              <p className="font-medium">{t('settings_desc')}</p>
            </div>
            <button onClick={() => setCurrentStep(2)} className="w-full bg-blue-800 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors shadow-md">
              {t('btn_next_upload')}
            </button>
          </div>
        )}
        
        {/* الخطوة 2: رفع البيانات */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 text-center">
            <div className="border-2 border-dashed border-blue-300 bg-blue-50 hover:bg-blue-100 transition-colors cursor-pointer p-16 rounded-2xl flex flex-col items-center justify-center gap-4">
               <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm text-blue-500 text-2xl">📊</div>
               <div>
                 <p className="text-blue-900 font-bold text-lg">{t('drag_drop')}</p>
                 <p className="text-blue-600 text-sm mt-1">{t('click_to_browse')}</p>
               </div>
            </div>
            <div className="flex gap-4">
               <button onClick={() => setCurrentStep(1)} className="flex-1 bg-slate-100 text-slate-700 py-3.5 rounded-xl font-semibold hover:bg-slate-200 transition-colors">
                 {t('btn_back_settings')}
               </button>
               <button onClick={() => setCurrentStep(3)} className="flex-1 bg-blue-800 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors shadow-md">
                 {t('btn_next_generate')}
               </button>
            </div>
          </div>
        )}
        
        {/* الخطوة 3: التوليد */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 text-center">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center gap-4">
              <div className="w-12 h-12 border-4 border-slate-200 border-t-blue-800 rounded-full animate-spin"></div>
              <p className="text-slate-600 font-medium">{t('generating')}</p>
            </div>
            <button onClick={() => setCurrentStep(1)} className="bg-slate-100 text-slate-700 py-2.5 px-8 rounded-lg font-medium hover:bg-slate-200 transition-colors">
              {t('btn_cancel')}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}