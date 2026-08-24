import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function SchedulePreview({ data }) {
  const { t } = useTranslation();
  const [viewType, setViewType] = useState('teachers'); // 'teachers' or 'classes'
  const [selectedItem, setSelectedItem] = useState('');

  // استخراج قوائم الأسماء للـ Dropdown
  const teachersList = data?.teachers ? Object.keys(data.teachers) : [];
  const classesList = data?.classes ? Object.keys(data.classes) : [];

  // تحديد العنصر الافتراضي عند تغيير نوع العرض
  if (!selectedItem && teachersList.length > 0) setSelectedItem(teachersList[0]);

  const handleTypeChange = (type) => {
    setViewType(type);
    setSelectedItem(type === 'teachers' ? teachersList[0] : classesList[0]);
  };

  const days = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"];
  const hours = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"];

  // جلب بيانات الجدول المطلوب
  const currentSchedule = data?.[viewType]?.[selectedItem] || {};

  return (
    <div className="mt-8 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm text-right" dir="rtl">
      {/* شريط التحكم */}
      <div className="bg-slate-50 p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h3 className="font-bold text-lg text-slate-800">🔍 معاينة الجداول</h3>
        
        <div className="flex gap-4">
          <select 
            className="p-2 border border-slate-300 rounded-lg bg-white"
            value={viewType}
            onChange={(e) => handleTypeChange(e.target.value)}
          >
            <option value="teachers">جداول الأساتذة</option>
            <option value="classes">جداول الأقسام</option>
          </select>

          <select 
            className="p-2 border border-slate-300 rounded-lg bg-white min-w-[200px]"
            value={selectedItem}
            onChange={(e) => setSelectedItem(e.target.value)}
          >
            {(viewType === 'teachers' ? teachersList : classesList).map(item => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>
      </div>

      {/* رسم الجدول */}
      <div className="overflow-x-auto p-4">
        <table className="w-full text-sm text-center border-collapse">
          <thead>
            <tr>
              <th className="border border-slate-300 bg-blue-900 text-white p-2 w-24">الأيام \ الساعات</th>
              {hours.map(h => (
                <th key={h} className="border border-slate-300 bg-blue-800 text-white p-2 whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {days.map(day => (
              <tr key={day}>
                <td className="border border-slate-300 bg-slate-100 font-bold p-2">{day}</td>
                {hours.map(hour => {
                  const cellContent = currentSchedule[day]?.[hour] || "";
                  return (
                    <td key={hour} className="border border-slate-300 p-2 min-w-[120px] h-16 whitespace-pre-wrap align-middle">
                      {cellContent}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}