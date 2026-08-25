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
        if not self.activities_xml or not self.input_fet.exists():
            return {}, {}

        activities_info = {}
        input_tree = ET.parse(self.input_fet)
        for act in input_tree.findall(".//Activity"):
            act_id_elem = act.find("Id")
            if act_id_elem is not None:
                act_id = act_id_elem.text.strip()
                t_elem = act.find("Teacher")
                s_elem = act.find("Students")
                subj_elem = act.find("Subject")
                dur_elem = act.find("Duration")
                
                activities_info[act_id] = {
                    "teacher": t_elem.text.strip() if t_elem is not None else "",
                    "students": s_elem.text.strip() if s_elem is not None else "",
                    "subject": subj_elem.text.strip() if subj_elem is not None else "",
                    "duration": int(dur_elem.text.strip()) if dur_elem is not None else 1
                }

        teachers_schedules = {}
        classes_schedules = {}
        hours_list = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"]

        result_tree = ET.parse(self.activities_xml)
        for act in result_tree.findall(".//Activity"):
            act_id_elem = act.find("Id")
            if act_id_elem is not None and act_id_elem.text.strip() in activities_info:
                act_id = act_id_elem.text.strip()
                day = act.find("Day").text.strip()
                start_hour = act.find("Hour").text.strip()
                info = activities_info[act_id]
                
                try:
                    start_idx = hours_list.index(start_hour)
                    for d in range(info["duration"]):
                        if start_idx + d < len(hours_list):
                            hour = hours_list[start_idx + d]
                            
                            if info["teacher"]:
                                if info["teacher"] not in teachers_schedules: teachers_schedules[info["teacher"]] = {}
                                if day not in teachers_schedules[info["teacher"]]: teachers_schedules[info["teacher"]][day] = {}
                                existing_t = teachers_schedules[info["teacher"]][day].get(hour, "")
                                new_val_t = f"{info['subject']}\n{info['students']}"
                                if new_val_t not in existing_t:
                                    teachers_schedules[info["teacher"]][day][hour] = f"{existing_t}\n---\n{new_val_t}" if existing_t else new_val_t

                            if info["students"]:
                                base_student = info["students"].split(" فوج")[0].strip() 
                                if base_student not in classes_schedules: classes_schedules[base_student] = {}
                                if day not in classes_schedules[base_student]: classes_schedules[base_student][day] = {}
                                existing_c = classes_schedules[base_student][day].get(hour, "")
                                
                                subgroup_str = ""
                                if "فوج A" in info["students"]: subgroup_str = "(A)"
                                elif "فوج B" in info["students"]: subgroup_str = "(B)"
                                
                                new_val_c = f"{info['subject']} {subgroup_str}\n{info['teacher']}"
                                if new_val_c not in existing_c:
                                    classes_schedules[base_student][day][hour] = f"{existing_c}\n---\n{new_val_c}" if existing_c else new_val_c
                except ValueError:
                    pass
        return teachers_schedules, classes_schedules