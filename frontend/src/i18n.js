// src/i18n.js
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

i18n.use(initReactI18next).init({
  resources: {
    en: {
      translation: {
        title: "🌱 Indian Crop Data Explorer",
        state: "State",
        district: "District",
        crop: "Crop",
        selectState: "Select State",
        selectDistrict: "Select District",
        selectCrop: "Select Crop",
        dark: "🌙 Dark",
        light: "☀️ Light",
        year: "Year",
        season: "Season",
        area: "Area",
        production: "Production",
        yield: "Yield",
      },
    },
    hi: {
      translation: {
        title: "🌱 भारतीय फ़सल डेटा खोजक",
        state: "राज्य",
        district: "ज़िला",
        crop: "फ़सल",
        selectState: "राज्य चुनें",
        selectDistrict: "ज़िला चुनें",
        selectCrop: "फ़सल चुनें",
        dark: "🌙 डार्क",
        light: "☀️ लाइट",
        year: "साल",
        season: "मौसम",
        area: "क्षेत्रफल",
        production: "उत्पादन",
        yield: "उपज",
      },
    },
    ta: {
      translation: {
        title: "🌱 இந்திய பயிர் தரவு ஆராய்ச்சி",
        state: "மாநிலம்",
        district: "மாவட்டம்",
        crop: "பயிர்",
        selectState: "மாநிலத்தைத் தேர்ந்தெடுக்கவும்",
        selectDistrict: "மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",
        selectCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
        dark: "🌙 இருள்",
        light: "☀️ வெளிச்சம்",
        year: "ஆண்டு",
        season: "பருவம்",
        area: "பரப்பு",
        production: "உற்பத்தி",
        yield: "மிகுதி",
      },
    },
  },
  lng: "en", // default
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
