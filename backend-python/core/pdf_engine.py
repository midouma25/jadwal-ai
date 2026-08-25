import os
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import arabic_reshaper
from bidi.algorithm import get_display

class PDFGenerator:
    def __init__(self, job_dir: str, lang: str = 'ar'):
        self.job_dir = job_dir
        self.lang = lang
        self.font_path = "C:\\Windows\\Fonts\\arial.ttf"
        pdfmetrics.registerFont(TTFont('Arabic', self.font_path))
        
        self.t = {
            'republic': "الجمهورية الجزائرية الديمقراطية الشعبية",
            'ministry': "وزارة التربية الوطنية",
            'teacher_title': "جدول توقيت الأستاذ:",
            'class_title': "جدول توقيت القسم:",
            'season': "الموسم الدراسي: 2026 - 2027",
            'days': ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"],
            'headers': ["الأيام", "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"],
            'footer': "تم التوليد آلياً عبر الذكاء الاصطناعي - منصة الجدول الذكي",
            'dir': 'rtl'
        }
        self.styles = getSampleStyleSheet()
        self.custom_header = ParagraphStyle('CustomHeader', parent=self.styles['Normal'], alignment=TA_CENTER, fontName='Arabic', fontSize=14)
        self.custom_title = ParagraphStyle('CustomTitle', parent=self.styles['Heading1'], alignment=TA_CENTER, fontName='Arabic', fontSize=18, spaceAfter=10)
        self.custom_footer = ParagraphStyle('CustomFooter', parent=self.styles['Normal'], alignment=TA_CENTER, fontName='Arabic', fontSize=10, textColor=colors.gray)

    def _format_text(self, text):
        if not text or str(text) == 'nan': return ""
        text_str = str(text)
        text_str = text_str.replace('?', '').replace('$', '').replace('+', '').replace('_', '')
        text_str = text_str.replace(' م ', 'م').replace(' م', 'م')
        
        # 🔴 اختصارات ذكية لمنع انفجار الخلايا
        text_str = text_str.replace('التربية التشكيلية أو الموسيقية', 'رسم')
        text_str = text_str.replace('العلوم الطبيعية والحياة', 'علوم')
        text_str = text_str.replace('العلوم الفيزيائية والتكنولوجيا', 'فيزياء')
        text_str = text_str.replace('التربية البدنية والرياضية', 'رياضة')
        text_str = text_str.replace('التاريخ والجغرافيا', 'تاريخ وجغرافيا')
        text_str = text_str.replace('التربية الإسلامية', 'إسلامية')
        text_str = text_str.replace('اللغة الإنجليزية', 'إنجليزية')
        text_str = text_str.replace('اللغة الفرنسية', 'فرنسية')
        text_str = text_str.replace('اللغة العربية', 'عربية')
        text_str = text_str.replace('المعلوماتية', 'إعلام آلي')
        
        lines = text_str.split('\n')
        processed = []
        for line in lines:
            line = line.strip()
            if not line: continue
            reshaped = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped, base_dir='R')
            processed.append(bidi_text)
            
        return '\n'.join(processed)

    def _get_professional_style(self):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4F72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # 🔴 الاعتماد الكلي على TableStyle لحل مشكلة المربعات
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (-1, 1), (-1, -1), colors.HexColor('#F8FAFC')) if self.t['dir'] == 'rtl' else ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F8FAFC')),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1B4F72')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])

    def draw_text(self, c, text, x, y, font_size=12, align='right'):
        processed = self._format_text(text)
        c.setFont('Arabic', font_size)
        if align == 'right': c.drawRightString(x, y, processed)
        elif align == 'center': c.drawCentredString(x, y, processed)
        else: c.drawString(x, y, processed)

    def _build_table(self, schedule_data):
        hours_list = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"]
        data = []
        headers_row = [self._format_text(self.t['headers'][0])] + [self._format_text(h) for h in hours_list]
        if self.t['dir'] == 'rtl': headers_row.reverse()
        data.append(headers_row)
        
        for day in self.t['days']:
            row_cells = []
            for h in hours_list:
                content = schedule_data.get(day, {}).get(h, "")
                row_cells.append(self._format_text(content))
            
            day_label = self._format_text(day)
            if self.t['dir'] == 'rtl':
                row_cells.reverse()
                row = row_cells + [day_label]
            else:
                row = [day_label] + row_cells
            data.append(row)
            
        col_widths = [85] * 8 + [70] if self.t['dir'] == 'rtl' else [70] + [85] * 8
        t = Table(data, colWidths=col_widths)
        t.setStyle(self._get_professional_style())
        return t

    def _draw_single_page(self, c, title_text, schedule_data, width, height):
        self.draw_text(c, self.t['republic'], width/2, height - 30, 14, 'center')
        self.draw_text(c, self.t['ministry'], width/2, height - 50, 14, 'center')
        if self.t['dir'] == 'rtl':
            self.draw_text(c, title_text, width - 50, height - 85, 16, 'right')
            self.draw_text(c, self.t['season'], 50, height - 85, 12, 'left')
        else:
            self.draw_text(c, title_text, 50, height - 85, 16, 'left')
            self.draw_text(c, self.t['season'], width - 50, height - 85, 12, 'right')

        t = self._build_table(schedule_data)
        t.wrapOn(c, width, height)
        col_widths = [85] * 8 + [70] if self.t['dir'] == 'rtl' else [70] + [85] * 8
        t.drawOn(c, (width - sum(col_widths)) / 2, height - 420)
        self.draw_text(c, self.t['footer'], width/2, 30, 10, 'center')

    def generate_all_pdfs(self, teachers_schedules, classes_schedules):
        w, h = landscape(A4)
        
        teachers_pdf = os.path.join(self.job_dir, f"teachers_schedules_{self.lang}.pdf")
        tc = canvas.Canvas(teachers_pdf, pagesize=landscape(A4))
        for teacher, data in teachers_schedules.items():
            title = f"{self.t.get('teacher_title', 'جدول توقيت الأستاذ:')} {teacher}"
            self._draw_single_page(tc, title, data, w, h)
            tc.showPage()
        tc.save()

        classes_pdf = os.path.join(self.job_dir, f"classes_schedules_{self.lang}.pdf")
        doc_c = SimpleDocTemplate(classes_pdf, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements_c = []
        
        for class_name, schedule in classes_schedules.items():
            elements_c.append(Paragraph(self._format_text(self.t.get('republic', 'الجمهورية الجزائرية الديمقراطية الشعبية')), self.custom_header))
            elements_c.append(Paragraph(self._format_text(self.t.get('ministry', 'وزارة التربية الوطنية')), self.custom_header))
            elements_c.append(Spacer(1, 10))
            elements_c.append(Paragraph(self._format_text(f"{self.t.get('class_title', 'جدول توقيت القسم:')} {class_name}"), self.custom_title))
            elements_c.append(Spacer(1, 10))
            
            table = self._build_table(schedule)
            elements_c.append(table)
            
            elements_c.append(Spacer(1, 20))
            elements_c.append(Paragraph(self._format_text(self.t.get('season', 'الموسم الدراسي: 2026 - 2027')), self.custom_footer))
            elements_c.append(Paragraph(self._format_text(self.t.get('footer', 'تم التوليد آلياً عبر الذكاء الاصطناعي - منصة الجدول الذكي')), self.custom_footer))
            elements_c.append(PageBreak())

        doc_c.build(elements_c)
        return os.path.basename(teachers_pdf), os.path.basename(classes_pdf), classes_schedules