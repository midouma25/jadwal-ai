import xml.etree.ElementTree as ET
import pandas as pd

class FETXMLBuilder:
    def __init__(self, df_classes: pd.DataFrame, df_teachers: pd.DataFrame, df_assignments: pd.DataFrame):
        self.df_classes = df_classes
        self.df_teachers = df_teachers
        self.df_assignments = df_assignments
        self.fet = ET.Element("fet", version="7.10.1")
        self.activity_id = 1
        self.activity_group_id = 1
        
        # ثوابت الأيام والساعات لتسهيل برمجتها في القيود
        self.days = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        self.hours_morning = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00"]
        self.hours_afternoon = ["13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"]
        self.all_hours = self.hours_morning + self.hours_afternoon

    def build(self) -> str:
        # 1. إعدادات المؤسسة
        ET.SubElement(self.fet, "Institution_Name").text = "الجدول الذكي - مؤسسة تجريبية"
        ET.SubElement(self.fet, "Comments").text = "تم التوليد آليا عبر منصة الجدول الذكي"
        
        # 2. الأيام والساعات
        days_list = ET.SubElement(self.fet, "Days_List")
        ET.SubElement(days_list, "Number_of_Days").text = str(len(self.days))
        for d in self.days:
            day = ET.SubElement(days_list, "Day")
            ET.SubElement(day, "Name").text = d

        hours_list = ET.SubElement(self.fet, "Hours_List")
        ET.SubElement(hours_list, "Number_of_Hours").text = str(len(self.all_hours))
        for h in self.all_hours:
            hour = ET.SubElement(hours_list, "Hour")
            ET.SubElement(hour, "Name").text = h

        # 3. المواد
        subjects_list = ET.SubElement(self.fet, "Subjects_List")
        unique_subjects = self.df_assignments['المادة'].unique()
        for subj in unique_subjects:
            subject = ET.SubElement(subjects_list, "Subject")
            ET.SubElement(subject, "Name").text = str(subj)

        # 4. علامات الأنشطة
        ET.SubElement(self.fet, "Activity_Tags_List")

        # 5. الأساتذة
        teachers_list = ET.SubElement(self.fet, "Teachers_List")
        for _, row in self.df_teachers.iterrows():
            teacher = ET.SubElement(teachers_list, "Teacher")
            ET.SubElement(teacher, "Name").text = str(row['اسم الأستاذ'])

        # 6. الأقسام
        students_list = ET.SubElement(self.fet, "Students_List")
        levels = self.df_classes['المستوى'].unique()
        
        for level in levels:
            year = ET.SubElement(students_list, "Year")
            ET.SubElement(year, "Name").text = str(level)
            ET.SubElement(year, "Number_of_Students").text = "0"
            
            classes_in_level = self.df_classes[self.df_classes['المستوى'] == level]
            for _, row in classes_in_level.iterrows():
                class_name = str(row['اسم القسم'])
                student_count = str(row['عدد التلاميذ'])
                
                group = ET.SubElement(year, "Group")
                ET.SubElement(group, "Name").text = class_name
                ET.SubElement(group, "Number_of_Students").text = student_count
                
                subgroup = ET.SubElement(group, "Subgroup")
                ET.SubElement(subgroup, "Name").text = class_name + "_فوج"
                ET.SubElement(subgroup, "Number_of_Students").text = student_count

        ET.SubElement(self.fet, "Equipment_List")
        ET.SubElement(self.fet, "Rooms_List")
        ET.SubElement(self.fet, "Buildings_List")

        # 7. الأنشطة (الحصص)
        activities_list = ET.SubElement(self.fet, "Activities_List")
        
        for _, row in self.df_assignments.iterrows():
            teacher_name = str(row['الأستاذ'])
            subject_name = str(row['المادة'])
            class_name = str(row['القسم'])
            
            single_hours = int(row.get('حصص فردية (1سا)', 0))
            if single_hours > 0:
                current_group_id = self.activity_group_id
                self.activity_group_id += 1
                for _ in range(single_hours):
                    self._create_activity(activities_list, teacher_name, subject_name, class_name, "1", str(single_hours), str(current_group_id))

            double_hours = int(row.get('حصص مزدوجة (2سا)', 0))
            if double_hours > 0:
                current_group_id = self.activity_group_id
                self.activity_group_id += 1
                for _ in range(double_hours):
                    self._create_activity(activities_list, teacher_name, subject_name, class_name, "2", str(double_hours * 2), str(current_group_id))

        # 8. قيود الزمان (التحديث العبقري هنا 🚀)
        time_constraints = ET.SubElement(self.fet, "Time_Constraints_List")
        
        constraint_t = ET.SubElement(time_constraints, "ConstraintBasicCompulsoryTime")
        ET.SubElement(constraint_t, "Weight_Percentage").text = "100"

        # 🟢 القيد الأول: راحة مساء الثلاثاء إجبارية لجميع المؤسسة
        break_constraint = ET.SubElement(time_constraints, "ConstraintBreakTimes")
        ET.SubElement(break_constraint, "Weight_Percentage").text = "100"
        ET.SubElement(break_constraint, "Number_of_Break_Times").text = str(len(self.hours_afternoon))
        for h in self.hours_afternoon:
            bt = ET.SubElement(break_constraint, "Break_Time")
            ET.SubElement(bt, "Day").text = "الثلاثاء"
            ET.SubElement(bt, "Hour").text = h

        # 🟢 القيد الثاني: الأيام المحظورة للأساتذة (من ملف الإكسيل)
        for _, row in self.df_teachers.iterrows():
            teacher_name = str(row['اسم الأستاذ'])
            blocked_text = str(row.get('الأيام المحظورة', ''))
            
            # تجاهل الخلايا الفارغة
            if pd.isna(blocked_text) or blocked_text.strip() in ['', 'nan', 'None']:
                continue
                
            not_available_times = []
            for d in self.days:
                if d in blocked_text:
                    if "صباح" in blocked_text:
                        hours_to_block = self.hours_morning
                    elif "مساء" in blocked_text:
                        hours_to_block = self.hours_afternoon
                    else:
                        hours_to_block = self.all_hours # اليوم كاملاً
                        
                    for h in hours_to_block:
                        not_available_times.append((d, h))
                        
            if not_available_times:
                constraint = ET.SubElement(time_constraints, "ConstraintTeacherNotAvailableTimes")
                ET.SubElement(constraint, "Weight_Percentage").text = "100"
                ET.SubElement(constraint, "Teacher").text = teacher_name
                ET.SubElement(constraint, "Number_of_Not_Available_Times").text = str(len(not_available_times))
                for day, hour in not_available_times:
                    time_xml = ET.SubElement(constraint, "Not_Available_Time")
                    ET.SubElement(time_xml, "Day").text = day
                    ET.SubElement(time_xml, "Hour").text = hour
# ... (بعد كود الأيام المحظورة للأساتذة مباشرة) ...

        # 9. القيود البيداغوجية الصارمة (الجودة والراحة)
        
        # أ. منع الفراغات للتلاميذ (0 فجوات إطلاقاً)
        for class_name in self.df_classes['اسم القسم'].unique():
            c_gaps = ET.SubElement(time_constraints, "ConstraintStudentsSetMaxGapsPerDay")
            ET.SubElement(c_gaps, "Weight_Percentage").text = "100"
            ET.SubElement(c_gaps, "Max_Gaps").text = "0"
            ET.SubElement(c_gaps, "Students").text = str(class_name)

        # ب. قيود راحة الأستاذ (سقف 5 سا، حد أدنى 2 سا، فجوات محدودة)
        for teacher_name in self.df_teachers['اسم الأستاذ'].unique():
            # سقف العمل 5 ساعات يوميا كحد أقصى
            c_max = ET.SubElement(time_constraints, "ConstraintTeacherMaxHoursDaily")
            ET.SubElement(c_max, "Weight_Percentage").text = "100"
            ET.SubElement(c_max, "Teacher_Name").text = str(teacher_name)
            ET.SubElement(c_max, "Maximum_Hours_Daily").text = "5"
            
            # الحد الأدنى ساعتان (يمنع استدعاء الأستاذ لحصة يتيمة في نصف اليوم)
            c_min = ET.SubElement(time_constraints, "ConstraintTeacherMinHoursDaily")
            ET.SubElement(c_min, "Weight_Percentage").text = "100"
            ET.SubElement(c_min, "Teacher_Name").text = str(teacher_name)
            ET.SubElement(c_min, "Minimum_Hours_Daily").text = "2"
            ET.SubElement(c_min, "Allow_Empty_Days").text = "true"
            
            # تقليص الفجوات للأستاذ (يُسمح بفجوتين كحد أقصى يومياً لتفادي انسداد المحرك)
            c_tgaps = ET.SubElement(time_constraints, "ConstraintTeacherMaxGapsPerDay")
            ET.SubElement(c_tgaps, "Weight_Percentage").text = "100"
            ET.SubElement(c_tgaps, "Teacher_Name").text = str(teacher_name)
            ET.SubElement(c_tgaps, "Max_Gaps").text = "2"

        # ... (نكمل مع Space_Constraints_List كما كان) ...
        space_constraints = ET.SubElement(self.fet, "Space_Constraints_List")
        constraint_s = ET.SubElement(space_constraints, "ConstraintBasicCompulsorySpace")
        ET.SubElement(constraint_s, "Weight_Percentage").text = "100"

        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + ET.tostring(self.fet, encoding="unicode")

    def _create_activity(self, parent, teacher, subject, students, duration, total_duration, group_id):
        act = ET.SubElement(parent, "Activity")
        ET.SubElement(act, "Teacher").text = teacher
        ET.SubElement(act, "Subject").text = subject
        ET.SubElement(act, "Students").text = students
        ET.SubElement(act, "Active").text = "true"
        ET.SubElement(act, "Id").text = str(self.activity_id)
        ET.SubElement(act, "Activity_Group_Id").text = group_id
        ET.SubElement(act, "Duration").text = duration
        ET.SubElement(act, "Total_Duration").text = total_duration
        self.activity_id += 1