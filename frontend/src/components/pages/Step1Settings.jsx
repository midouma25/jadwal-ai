import React from 'react';
import { useTranslation } from 'react-i18next';

export default function Step1Settings({ formData, setFormData, onNext }) {
  const { t } = useTranslation();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 text-right">
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-blue-800 text-sm">
        {t('settings_desc')}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* نوع المؤسسة */}
        <div className="space-y-2">
          <label className="font-semibold text-slate-700">{t('school_type')}</label>
          <select name="schoolType" value={formData.schoolType} onChange={handleChange} className="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-blue-500 bg-white">
            <option value="middle">{t('middle_school')}</option>
            <option value="high">{t('high_school')}</option>
          </select>
        </div>

        {/* توقيت المساء */}
        <div className="space-y-2">
          <label className="font-semibold text-slate-700">{t('afternoon_start')}</label>
          <select name="afternoonStart" value={formData.afternoonStart} onChange={handleChange} className="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-blue-500 bg-white">
            <option value="13:00">13:00</option>
            <option value="13:30">13:30</option>
          </select>
        </div>

        {/* اليوم البيداغوجي */}
        <div className="space-y-2">
          <label className="font-semibold text-slate-700">{t('pedagogical_day')}</label>
          <select name="pedagogicalDay" value={formData.pedagogicalDay} onChange={handleChange} className="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-blue-500 bg-white">
            <option value="half">{t('half_day')}</option>
            <option value="full">{t('full_day')}</option>
          </select>
        </div>
        
        {/* التربية البدنية */}
        <div className="space-y-2">
          <label className="font-semibold text-slate-700">{t('pe_location')}</label>
          <select name="peLocation" value={formData.peLocation} onChange={handleChange} className="w-full border border-slate-300 rounded-lg p-3 outline-none focus:border-blue-500 bg-white">
            <option value="yard">{t('school_yard')}</option>
            <option value="stadium">{t('external_stadium')}</option>
          </select>
        </div>
      </div>

      {/* الخيارات الذكية (Toggles) */}
      <div className="space-y-4 pt-4 border-t border-slate-200">
        <label className="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" name="roomElasticity" checked={formData.roomElasticity} onChange={handleChange} className="w-5 h-5 accent-blue-800 cursor-pointer" />
          <span className="text-slate-700 font-medium">{t('room_elasticity')}</span>
        </label>
        
        <label className="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" name="autoOffDays" checked={formData.autoOffDays} onChange={handleChange} className="w-5 h-5 accent-blue-800 cursor-pointer" />
          <span className="text-slate-700 font-medium">{t('auto_off_days')}</span>
        </label>
      </div>

      <button onClick={onNext} className="w-full mt-6 bg-blue-800 text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors shadow-md">
        {t('btn_next_upload')}
      </button>
    </div>
  );
}