import React from 'react';
import { useTranslation } from 'react-i18next';

export default function Navbar() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    document.documentElement.dir = lng === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lng;
  };

  return (
    <nav className="bg-white shadow-sm border-b border-slate-200 px-6 py-4 flex justify-between items-center">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-800 rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-inner">
          J
        </div>
        <h1 className="text-2xl font-bold text-blue-900 tracking-tight">{t('app_title')}</h1>
      </div>
      <div className="flex gap-4 items-center">
        <select 
          className="border border-slate-300 rounded-md px-3 py-1.5 text-sm bg-white text-slate-700 outline-none focus:border-blue-500 transition-colors cursor-pointer"
          onChange={(e) => changeLanguage(e.target.value)}
          defaultValue={i18n.language}
        >
          <option value="ar">العربية</option>
          <option value="fr">Français</option>
          <option value="en">English</option>
        </select>
        <button className="bg-blue-800 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium transition-all shadow-sm hover:shadow">
          {t('login')}
        </button>
      </div>
    </nav>
  );
}