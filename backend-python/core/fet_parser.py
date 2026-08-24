import xml.etree.ElementTree as ET
from pathlib import Path

class FETParser:
    def __init__(self, job_dir: str, job_id: str):
        self.job_dir = Path(job_dir)
        self.job_id = job_id
        self.input_fet = self.job_dir / f"{job_id}.fet"
        
        xml_files = list(self.job_dir.rglob("*_activities.xml"))
        self.activities_xml = xml_files[0] if xml_files else None

    def get_all_schedules(self):
        """يُرجع جداول جميع الأساتذة وجميع الأقسام"""
        if not self.activities_xml or not self.input_fet.exists():
            print("⚠️ تحذير: ملفات XML للنتيجة غير موجودة")
            return {}, {}

        # 1. استخراج كل الأنشطة من الملف الأصلي (المادة، الأستاذ، القسم)
        activities_info = {}
        input_tree = ET.parse(self.input_fet)
        for act in input_tree.findall(".//Activity"):
            act_id_elem = act.find("Id")
            if act_id_elem is not None:
                act_id = act_id_elem.text.strip()
                t_elem = act.find("Teacher")
                s_elem = act.find("Students")
                subj_elem = act.find("Subject")
                
                activities_info[act_id] = {
                    "teacher": t_elem.text.strip() if t_elem is not None else "",
                    "students": s_elem.text.strip() if s_elem is not None else "",
                    "subject": subj_elem.text.strip() if subj_elem is not None else ""
                }

        teachers_schedules = {}
        classes_schedules = {}

        # 2. مطابقتها مع ملف النتائج لاستخراج (اليوم والساعة)
        result_tree = ET.parse(self.activities_xml)
        for act in result_tree.findall(".//Activity"):
            act_id_elem = act.find("Id")
            
            if act_id_elem is not None and act_id_elem.text.strip() in activities_info:
                act_id = act_id_elem.text.strip()
                day = act.find("Day").text.strip()
                hour = act.find("Hour").text.strip()
                
                info = activities_info[act_id]
                teacher, students, subject = info["teacher"], info["students"], info["subject"]
                
                # بناء جدول الأستاذ (المادة والقسم)
                if teacher:
                    if teacher not in teachers_schedules: teachers_schedules[teacher] = {}
                    if day not in teachers_schedules[teacher]: teachers_schedules[teacher][day] = {}
                    teachers_schedules[teacher][day][hour] = f"{subject}\n{students}"
                    
                # بناء جدول القسم (المادة والأستاذ)
                if students:
                    if students not in classes_schedules: classes_schedules[students] = {}
                    if day not in classes_schedules[students]: classes_schedules[students][day] = {}
                    classes_schedules[students][day][hour] = f"{subject}\n{teacher}"
        
        return teachers_schedules, classes_schedules