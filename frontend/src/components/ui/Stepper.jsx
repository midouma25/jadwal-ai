import React from 'react';
import { useTranslation } from 'react-i18next';

export default function Stepper({ currentStep }) {
  const { t } = useTranslation();

  const steps = [
    { num: 1, label: t('step_1') },
    { num: 2, label: t('step_2') },
    { num: 3, label: t('step_3') },
  ];

  return (
    <div className="flex justify-between items-center mb-12 relative px-4">
      {steps.map((step, index) => (
        <React.Fragment key={step.num}>
          {/* دائرة الخطوة */}
          <div className="flex flex-col items-center z-10 w-24">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-colors ${currentStep >= step.num ? 'bg-blue-800 text-white shadow-md' : 'bg-slate-100 text-slate-400 border border-slate-200'}`}>
              {step.num}
            </div>
            <span className={`text-sm mt-3 font-semibold text-center ${currentStep >= step.num ? 'text-blue-900' : 'text-slate-400'}`}>
              {step.label}
            </span>
          </div>
          
          {/* خط التوصيل (لا يظهر بعد الخطوة الأخيرة) */}
          {index < steps.length - 1 && (
            <div className="flex-1 h-1 bg-slate-100 mx-2 rounded-full overflow-hidden">
              <div className={`h-full bg-blue-800 transition-all duration-500 ${currentStep > step.num ? 'w-full' : 'w-0'}`}></div>
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}