import pandas as pd

classes_list = []
levels = ['1 متوسط', '2 متوسط', '3 متوسط', '4 متوسط']
for niv in range(1, 5):
    for i in range(1, 4):
        classes_list.append([f'{niv}م{i}', levels[niv-1], '-', 35])
df_classes = pd.DataFrame(classes_list, columns=['اسم القسم', 'المستوى', 'الشعبة', 'عدد التلاميذ'])

profs_data = [
    ['أحمد', 'اللغة العربية'], ['العربي', 'اللغة العربية'], ['فاطمة', 'اللغة العربية'], ['عمار', 'اللغة العربية'],
    ['مراد', 'الرياضيات'], ['يحيى', 'الرياضيات'], ['حسيبة', 'الرياضيات'], ['محمد', 'الرياضيات'],
    ['الحواس', 'اللغة الفرنسية'], ['مريم', 'اللغة الفرنسية'], ['مالك', 'اللغة الفرنسية'],
    ['ياسين', 'اللغة الإنجليزية'], ['فضيلة', 'اللغة الإنجليزية'], ['نسيمة', 'اللغة الإنجليزية'],
    ['مصطفى', 'العلوم الطبيعية والحياة'], ['باجي', 'العلوم الطبيعية والحياة'],
    ['رضا', 'العلوم الفيزيائية والتكنولوجيا'], ['عيسات', 'العلوم الفيزيائية والتكنولوجيا'],
    ['طالب', 'التاريخ والجغرافيا'], ['عقبي', 'التاريخ والجغرافيا'], ['مفدي', 'التاريخ والجغرافيا'],
    ['ابن باديس', 'التربية الإسلامية'], ['الإبراهيمي', 'التربية الإسلامية'],
    ['علي', 'التربية البدنية والرياضية'], ['رابح', 'التربية البدنية والرياضية'],
    ['حساني', 'المعلوماتية'], ['زليخة', 'المعلوماتية'], 
    ['الجزائرية', 'التربية التشكيلية أو الموسيقية']
]

teachers_list = []
for p in profs_data: teachers_list.append([p[0], p[1], 20, 'أساسي', ''])
df_teachers = pd.DataFrame(teachers_list, columns=['اسم الأستاذ', 'المادة', 'النصاب الأقصى', 'الرتبة', 'الأيام المحظورة'])

assignments = []
classes_names = df_classes['اسم القسم'].tolist()
classes_123 = [c for c in classes_names if not c.startswith('4')]
classes_4 = [c for c in classes_names if c.startswith('4')]

def assign_subject(subject, teacher_names, classes_array, hours_single, hours_double, split_type='لا يوجد'):
    per_teacher = max(1, len(classes_array) // len(teacher_names))
    for i, cls in enumerate(classes_array):
        teacher = teacher_names[min(i // per_teacher, len(teacher_names) - 1)]
        assignments.append([teacher, cls, subject, hours_single, hours_double, split_type])

t_ar = [p[0] for p in profs_data if p[1] == 'اللغة العربية']
t_math = [p[0] for p in profs_data if p[1] == 'الرياضيات']
t_fr = [p[0] for p in profs_data if p[1] == 'اللغة الفرنسية']
t_en = [p[0] for p in profs_data if p[1] == 'اللغة الإنجليزية']
t_sc = [p[0] for p in profs_data if p[1] == 'العلوم الطبيعية والحياة']
t_ph = [p[0] for p in profs_data if p[1] == 'العلوم الفيزيائية والتكنولوجيا']
t_hg = [p[0] for p in profs_data if p[1] == 'التاريخ والجغرافيا']
t_is = [p[0] for p in profs_data if p[1] == 'التربية الإسلامية']
t_pe = [p[0] for p in profs_data if p[1] == 'التربية البدنية والرياضية']
t_it = [p[0] for p in profs_data if p[1] == 'المعلوماتية']
t_art = [p[0] for p in profs_data if p[1] == 'التربية التشكيلية أو الموسيقية']

# 🔴 الحسبة البيداغوجية الدقيقة للحصص النظرية (1، 2، 3 متوسط) لتكوين 28 ساعة
assign_subject('اللغة العربية', t_ar, classes_123, 3, 1, 'تناوب')
assign_subject('الرياضيات', t_math, classes_123, 2, 1, 'تناوب')
assign_subject('اللغة الفرنسية', t_fr, classes_123, 2, 0, 'تناوب')
assign_subject('اللغة الإنجليزية', t_en, classes_123, 3, 0, 'تناوب')
assign_subject('العلوم الطبيعية والحياة', t_sc, classes_123, 1, 0, 'مخبر')
assign_subject('العلوم الفيزيائية والتكنولوجيا', t_ph, classes_123, 1, 0, 'مخبر')
assign_subject('التاريخ والجغرافيا', t_hg, classes_123, 3, 0, 'لا يوجد')
assign_subject('التربية الإسلامية', t_is, classes_123, 1, 0, 'لا يوجد')
assign_subject('التربية البدنية والرياضية', t_pe, classes_123, 0, 1, 'لا يوجد')
assign_subject('المعلوماتية', t_it, classes_123, 1, 0, 'لا يوجد')
assign_subject('التربية التشكيلية أو الموسيقية', t_art, classes_123, 1, 0, 'لا يوجد')

# 🔴 الحسبة للرابعة متوسط (شهادة)
assign_subject('اللغة العربية', t_ar, classes_4, 2, 1, 'تعاكس')
assign_subject('الرياضيات', t_math, classes_4, 2, 1, 'تعاكس')
assign_subject('اللغة الفرنسية', t_fr, classes_4, 2, 0, 'تناوب')
assign_subject('اللغة الإنجليزية', t_en, classes_4, 3, 0, 'تناوب')
assign_subject('العلوم الطبيعية والحياة', t_sc, classes_4, 1, 0, 'مخبر')
assign_subject('العلوم الفيزيائية والتكنولوجيا', t_ph, classes_4, 1, 0, 'مخبر')
assign_subject('التاريخ والجغرافيا', t_hg, classes_4, 3, 0, 'لا يوجد')
assign_subject('التربية الإسلامية', t_is, classes_4, 1, 0, 'لا يوجد')
assign_subject('التربية البدنية والرياضية', t_pe, classes_4, 0, 1, 'لا يوجد')
assign_subject('المعلوماتية', t_it, classes_4, 1, 0, 'لا يوجد')
assign_subject('التربية التشكيلية أو الموسيقية', t_art, classes_4, 1, 0, 'لا يوجد')

df_assignments = pd.DataFrame(assignments, columns=['الأستاذ', 'القسم', 'المادة', 'حصص فردية (1سا)', 'حصص مزدوجة (2سا)', 'نوع التفويج'])
with pd.ExcelWriter('official_cem_data.xlsx', engine='openpyxl') as writer:
    df_classes.to_excel(writer, sheet_name='الأقسام', index=False)
    df_teachers.to_excel(writer, sheet_name='الأساتذة', index=False)
    df_assignments.to_excel(writer, sheet_name='الإسناد', index=False)
print("تم توليد الإكسيل الرياضي الدقيق!")