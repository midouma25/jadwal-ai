import xml.etree.ElementTree as ET
import pandas as pd

class FETXMLBuilder:
    def __init__(self, df_classes: pd.DataFrame, df_teachers: pd.DataFrame, df_assignments: pd.DataFrame, has_it: str = "true", has_art: str = "true"):
        self.df_classes = df_classes
        self.df_teachers = df_teachers
        self.df_assignments = df_assignments
        self.has_it = str(has_it).lower() == 'true'
        self.has_art = str(has_art).lower() == 'true'
        self.fet = ET.Element("fet", version="7.10.1")
        self.activity_id = 1
        
        self.days = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        self.hours_morning = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00"]
        self.hours_afternoon = ["13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"]
        self.all_hours = self.hours_morning + self.hours_afternoon
        
        self.activities_list = None
        self.sport_act_ids = []
        self.assignments_groups = []
        self.same_time_pairs = []
        self.consecutive_pairs = []

    def _create_act(self, teacher, subject, students, duration="1"):
        act_id = str(self.activity_id)
        self.activity_id += 1
        act = ET.SubElement(self.activities_list, "Activity")
        ET.SubElement(act, "Teacher").text = str(teacher)
        ET.SubElement(act, "Subject").text = str(subject)
        ET.SubElement(act, "Students").text = str(students)
        ET.SubElement(act, "Active").text = "true"
        ET.SubElement(act, "Id").text = act_id
        ET.SubElement(act, "Activity_Group_Id").text = "0"
        ET.SubElement(act, "Duration").text = str(duration)
        ET.SubElement(act, "Total_Duration").text = str(duration)
        return act_id

    def build(self) -> str:
        new_teachers = self.df_teachers[self.df_teachers['الرتبة'].astype(str).str.contains('جديد', na=False)]['اسم الأستاذ'].tolist()
        for _, row in self.df_assignments.iterrows():
            t_name, c_name = str(row.get('الأستاذ', '')), str(row.get('القسم', ''))
            if t_name in new_teachers and c_name.startswith('4'):
                raise ValueError(f"قيد بيداغوجي: لا يمكن إسناد قسم الشهادة ({c_name}) للأستاذ المبتدئ ({t_name}).")

        if not self.has_it:
            self.df_assignments = self.df_assignments[~self.df_assignments['المادة'].astype(str).str.contains('معلوماتية|إعلام', na=False, regex=True)]
        if not self.has_art:
            self.df_assignments = self.df_assignments[~self.df_assignments['المادة'].astype(str).str.contains('تشكيلية|موسيقية|رسم', na=False, regex=True)]

        ET.SubElement(self.fet, "Institution_Name").text = "الجدول الذكي"
        ET.SubElement(self.fet, "Comments").text = "منصة الجدول الذكي"
        
        days_list = ET.SubElement(self.fet, "Days_List")
        ET.SubElement(days_list, "Number_of_Days").text = str(len(self.days))
        for d in self.days: ET.SubElement(ET.SubElement(days_list, "Day"), "Name").text = d

        hours_list = ET.SubElement(self.fet, "Hours_List")
        ET.SubElement(hours_list, "Number_of_Hours").text = str(len(self.all_hours))
        for h in self.all_hours: ET.SubElement(ET.SubElement(hours_list, "Hour"), "Name").text = h

        subjects_list = ET.SubElement(self.fet, "Subjects_List")
        for subj in self.df_assignments['المادة'].unique():
            if str(subj) != 'nan': ET.SubElement(ET.SubElement(subjects_list, "Subject"), "Name").text = str(subj)

        ET.SubElement(self.fet, "Activity_Tags_List")

        teachers_list = ET.SubElement(self.fet, "Teachers_List")
        for _, row in self.df_teachers.iterrows():
            if str(row['اسم الأستاذ']) != 'nan': ET.SubElement(ET.SubElement(teachers_list, "Teacher"), "Name").text = str(row['اسم الأستاذ'])

        students_list = ET.SubElement(self.fet, "Students_List")
        for level in self.df_classes['المستوى'].unique():
            if str(level) == 'nan': continue
            year = ET.SubElement(students_list, "Year")
            ET.SubElement(year, "Name").text = str(level)
            ET.SubElement(year, "Number_of_Students").text = "0"
            for _, row in self.df_classes[self.df_classes['المستوى'] == level].iterrows():
                c_name, student_cnt = str(row['اسم القسم']), int(row.get('عدد التلاميذ', 30))
                group = ET.SubElement(year, "Group")
                ET.SubElement(group, "Name").text = c_name
                ET.SubElement(group, "Number_of_Students").text = str(student_cnt)
                
                sg_a = ET.SubElement(group, "Subgroup")
                ET.SubElement(sg_a, "Name").text = c_name + " فوج A"
                ET.SubElement(sg_a, "Number_of_Students").text = str(student_cnt // 2)
                sg_b = ET.SubElement(group, "Subgroup")
                ET.SubElement(sg_b, "Name").text = c_name + " فوج B"
                ET.SubElement(sg_b, "Number_of_Students").text = str(student_cnt - (student_cnt // 2))

        ET.SubElement(self.fet, "Equipment_List")
        ET.SubElement(self.fet, "Rooms_List")
        ET.SubElement(self.fet, "Buildings_List")

        self.activities_list = ET.SubElement(self.fet, "Activities_List")

        for class_name in self.df_classes['اسم القسم'].unique():
            if str(class_name) == 'nan': continue
            class_assigns = self.df_assignments[self.df_assignments['القسم'] == class_name].to_dict('records')
            
            labs = [a for a in class_assigns if str(a.get('نوع التفويج', '')) == 'مخبر']
            swaps = [a for a in class_assigns if str(a.get('نوع التفويج', '')) == 'تعاكس']
            alts = [a for a in class_assigns if str(a.get('نوع التفويج', '')) == 'تناوب']
            
            # 1. المخابر (الآن نصنعها ونلصقها بأمان تام)
            if len(labs) >= 2:
                act1 = self._create_act(labs[0]['الأستاذ'], labs[0]['المادة'], class_name+" فوج A", "1")
                act2 = self._create_act(labs[1]['الأستاذ'], labs[1]['المادة'], class_name+" فوج B", "1")
                act3 = self._create_act(labs[0]['الأستاذ'], labs[0]['المادة'], class_name+" فوج B", "1")
                act4 = self._create_act(labs[1]['الأستاذ'], labs[1]['المادة'], class_name+" فوج A", "1")
                self.same_time_pairs.extend([(act1, act2), (act3, act4)])
                self.consecutive_pairs.append((act1, act3)) # 🔴 إجبار التتالي الصحيح
                
            # 2. تعاكس الرابعة متوسط
            if len(swaps) >= 2:
                act1 = self._create_act(swaps[0]['الأستاذ'], swaps[0]['المادة'], class_name+" فوج A", "1")
                act2 = self._create_act(swaps[1]['الأستاذ'], swaps[1]['المادة'], class_name+" فوج B", "1")
                act3 = self._create_act(swaps[0]['الأستاذ'], swaps[0]['المادة'], class_name+" فوج B", "1")
                act4 = self._create_act(swaps[1]['الأستاذ'], swaps[1]['المادة'], class_name+" فوج A", "1")
                self.same_time_pairs.extend([(act1, act2), (act3, act4)])
                self.consecutive_pairs.append((act1, act3)) # 🔴 إجبار التتالي الصحيح
                
            # 3. تناوب (عربية/رياضيات و فرنسية/إنجليزية)
            if len(alts) >= 2:
                for i in range(0, len(alts)-1, 2):
                    act1 = self._create_act(alts[i]['الأستاذ'], alts[i]['المادة'], class_name+" فوج A", "1")
                    act2 = self._create_act(alts[i+1]['الأستاذ'], alts[i+1]['المادة'], class_name+" فوج B", "1")
                    self.same_time_pairs.append((act1, act2))
                
            # 4. الحصص الفردية والمزدوجة
            for a in class_assigns:
                grp = []
                for _ in range(int(a.get('حصص فردية (1سا)', 0))):
                    act_id = self._create_act(a.get('الأستاذ', ''), a.get('المادة', ''), class_name, "1")
                    grp.append(act_id)
                for _ in range(int(a.get('حصص مزدوجة (2سا)', 0))):
                    act_id = self._create_act(a.get('الأستاذ', ''), a.get('المادة', ''), class_name, "2")
                    grp.append(act_id)
                    if 'رياضية' in str(a.get('المادة', '')): self.sport_act_ids.append(act_id)
                
                if len(grp) > 1: self.assignments_groups.append(grp)

        time_constraints = ET.SubElement(self.fet, "Time_Constraints_List")
        ET.SubElement(ET.SubElement(time_constraints, "ConstraintBasicCompulsoryTime"), "Weight_Percentage").text = "100"

        # قيود التزامن (نفس الوقت)
        for a1, a2 in self.same_time_pairs:
            c_same = ET.SubElement(time_constraints, "ConstraintActivitiesSameStartingTime")
            ET.SubElement(c_same, "Weight_Percentage").text = "100"
            ET.SubElement(c_same, "Number_of_Activities").text = "2"
            ET.SubElement(c_same, "Activity_Id").text = str(a1)
            ET.SubElement(c_same, "Activity_Id").text = str(a2)

        # 🔴 الحل الجذري للتتالي (بدون MinDays الخاطئة)
        for a1, a2 in self.consecutive_pairs:
            c_cons = ET.SubElement(time_constraints, "ConstraintTwoActivitiesConsecutive")
            ET.SubElement(c_cons, "Weight_Percentage").text = "100"
            ET.SubElement(c_cons, "First_Activity_Id").text = str(a1)
            ET.SubElement(c_cons, "Second_Activity_Id").text = str(a2)

        for act_ids_group in self.assignments_groups:
            c_spread = ET.SubElement(time_constraints, "ConstraintMinDaysBetweenActivities")
            ET.SubElement(c_spread, "Weight_Percentage").text = "100"
            ET.SubElement(c_spread, "Consecutive_If_Same_Day").text = "true"
            ET.SubElement(c_spread, "Number_of_Activities").text = str(len(act_ids_group))
            for a_id in act_ids_group: ET.SubElement(c_spread, "Activity_Id").text = str(a_id)
            ET.SubElement(c_spread, "MinDays").text = "1"

        allowed_pe_times = []
        for d in self.days: allowed_pe_times.extend([(d, "08:00-09:00"), (d, "10:00-11:00"), (d, "13:00-14:00")])
        for act_id in self.sport_act_ids:
            c_pe = ET.SubElement(time_constraints, "ConstraintActivityPreferredStartingTimes")
            ET.SubElement(c_pe, "Weight_Percentage").text = "100"
            ET.SubElement(c_pe, "Activity_Id").text = str(act_id)
            ET.SubElement(c_pe, "Number_of_Preferred_Starting_Times").text = str(len(allowed_pe_times))
            for d, h in allowed_pe_times:
                time_xml = ET.SubElement(c_pe, "Preferred_Starting_Time")
                ET.SubElement(time_xml, "Day").text = d
                ET.SubElement(time_xml, "Hour").text = h

        for teacher_name in self.df_teachers['اسم الأستاذ'].unique():
            if str(teacher_name) == 'nan': continue
            c_max = ET.SubElement(time_constraints, "ConstraintTeacherMaxHoursDaily")
            ET.SubElement(c_max, "Weight_Percentage").text = "100"
            ET.SubElement(c_max, "Teacher_Name").text = str(teacher_name)
            ET.SubElement(c_max, "Maximum_Hours_Daily").text = "5"
            
            c_min = ET.SubElement(time_constraints, "ConstraintTeacherMinHoursDaily")
            ET.SubElement(c_min, "Weight_Percentage").text = "100"
            ET.SubElement(c_min, "Teacher_Name").text = str(teacher_name)
            ET.SubElement(c_min, "Minimum_Hours_Daily").text = "2"
            ET.SubElement(c_min, "Allow_Empty_Days").text = "true"
            
            c_tgaps = ET.SubElement(time_constraints, "ConstraintTeacherMaxGapsPerDay")
            ET.SubElement(c_tgaps, "Weight_Percentage").text = "100"
            ET.SubElement(c_tgaps, "Teacher_Name").text = str(teacher_name)
            ET.SubElement(c_tgaps, "Max_Gaps").text = "2"

        break_constraint = ET.SubElement(time_constraints, "ConstraintBreakTimes")
        ET.SubElement(break_constraint, "Weight_Percentage").text = "100"
        ET.SubElement(break_constraint, "Number_of_Break_Times").text = str(len(self.hours_afternoon))
        for h in self.hours_afternoon:
            bt = ET.SubElement(break_constraint, "Break_Time")
            ET.SubElement(bt, "Day").text = "الثلاثاء"
            ET.SubElement(bt, "Hour").text = h

        for class_name in self.df_classes['اسم القسم'].unique():
            if str(class_name) == 'nan': continue
            c_gaps = ET.SubElement(time_constraints, "ConstraintStudentsSetMaxGapsPerDay")
            ET.SubElement(c_gaps, "Weight_Percentage").text = "100"
            ET.SubElement(c_gaps, "Max_Gaps").text = "0"
            ET.SubElement(c_gaps, "Students").text = str(class_name)

        space_constraints = ET.SubElement(self.fet, "Space_Constraints_List")
        ET.SubElement(ET.SubElement(space_constraints, "ConstraintBasicCompulsorySpace"), "Weight_Percentage").text = "100"

        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + ET.tostring(self.fet, encoding="unicode")