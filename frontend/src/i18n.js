import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import arTranslations from './locales/ar.json';
import frTranslations from './locales/fr.json';
import enTranslations from './locales/en.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      ar: { translation: arTranslations },
      fr: { translation: frTranslations },
      en: { translation: enTranslations }
    },
    lng: "ar", // اللغة الافتراضية
    fallbackLng: "fr",
    interpolation: {
      escapeValue: false 
    }
  });

export default i18n;