# -*- coding: utf-8 -*-
"""
Mangesh Nano Pro AI Studio — Production PDF Manuals Generator (Refined Edition)
Builds two audit-grade, high-aesthetic PDF manuals:
1. NanoPro_User_Manual.pdf (End-User & Business Operations Guide)
2. NanoPro_Admin_Developer_Manual.pdf (Master Admin, DevOps & Lead Developer Guide)
"""

import os
import sys
import time
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

# ----------------------------------------------------------------------
# 1. Register Fonts
# ----------------------------------------------------------------------
FONTS_DIR = r"C:\Windows\Fonts"
try:
    pdfmetrics.registerFont(TTFont("Nirmala", os.path.join(FONTS_DIR, "Nirmala.ttc"), subfontIndex=0))
    pdfmetrics.registerFont(TTFont("Nirmala-Bold", os.path.join(FONTS_DIR, "Nirmala.ttc"), subfontIndex=1))
    MAIN_FONT = "Nirmala"
    MAIN_BOLD = "Nirmala-Bold"
except Exception as e:
    print(f"[!] Warning registering Nirmala font: {e}, falling back to Helvetica")
    MAIN_FONT = "Helvetica"
    MAIN_BOLD = "Helvetica-Bold"

MONO_FONT = "Courier"

# ----------------------------------------------------------------------
# 2. Numbered Canvas for Two-Pass Page Numbering & Running Headers
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        # Do not draw header/footer on cover page (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        w, h = A4

        # Header accent line
        self.setStrokeColor(colors.HexColor("#0284C7"))
        self.setLineWidth(1)
        self.line(36, h - 34, w - 36, h - 34)

        # Header Title
        self.setFont(MAIN_BOLD, 7.5)
        self.setFillColor(colors.HexColor("#0F172A"))
        doc_title = getattr(self, "doc_title", "MANGESH NANO PRO AI STUDIO")
        self.drawString(36, h - 28, doc_title.upper())

        # Header Version Tag
        self.setFont(MAIN_FONT, 7.5)
        self.setFillColor(colors.HexColor("#0284C7"))
        self.drawRightString(w - 36, h - 28, "PRODUCTION v9.0 • 24/7 LIVE CLOUD")

        # Footer accent line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 36, w - 36, 36)

        # Footer left confidentiality text
        self.setFont(MAIN_FONT, 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 26, "Confidential • Made by Mangesh Bagul • Autonomous Lakehouse Operations")

        # Footer right page number
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.setFont(MAIN_BOLD, 7.5)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawRightString(w - 36, 26, page_str)

        self.restoreState()


class UserManualCanvas(NumberedCanvas):
    doc_title = "NanoPro AI Studio — Official User Operations Manual"


class AdminManualCanvas(NumberedCanvas):
    doc_title = "NanoPro AI Studio — Master Admin & Lead Developer Architecture Manual"


# ----------------------------------------------------------------------
# 3. Style Factory
# ----------------------------------------------------------------------
def create_styles():
    base = getSampleStyleSheet()

    styles = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#FFFFFF"),
            alignment=1,
            spaceAfter=6
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#38BDF8"),
            alignment=1,
            spaceAfter=12
        ),
        "CoverMeta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName=MAIN_FONT,
            fontSize=8.5,
            leading=13,
            textColor=colors.HexColor("#E2E8F0"),
            alignment=1
        ),
        "Heading1": ParagraphStyle(
            "Heading1",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=13.5,
            leading=17,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#0369A1"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        ),
        "Heading3": ParagraphStyle(
            "Heading3",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName=MAIN_FONT,
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=4
        ),
        "BodyBold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName=MAIN_FONT,
            fontSize=8.2,
            leading=11.5,
            textColor=colors.HexColor("#1E293B"),
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=3
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#FFFFFF"),
            alignment=0
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontName=MAIN_FONT,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#1E293B")
        ),
        "TableCellBold": ParagraphStyle(
            "TableCellBold",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#0F172A")
        ),
        "CalloutText": ParagraphStyle(
            "CalloutText",
            parent=base["Normal"],
            fontName=MAIN_FONT,
            fontSize=8,
            leading=11.5,
            textColor=colors.HexColor("#0F172A")
        ),
        "CodeText": ParagraphStyle(
            "CodeText",
            parent=base["Normal"],
            fontName=MONO_FONT,
            fontSize=7,
            leading=9.5,
            textColor=colors.HexColor("#38BDF8")
        ),
        "Caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#64748B"),
            alignment=1,
            spaceAfter=6
        )
    }
    return styles

# ----------------------------------------------------------------------
# 4. Helper UI Components (Callouts, Tables, Images, Cover)
# ----------------------------------------------------------------------
def make_callout(text, kind="note", width=520):
    cfg = {
        "note": {"bg": "#F0F9FF", "border": "#0284C7", "title": "📌 टीप / NOTE:"},
        "tip": {"bg": "#ECFDF5", "border": "#10B981", "title": "💡 सर्वोत्तम पद्धत / BEST PRACTICE:"},
        "warning": {"bg": "#FFFBEB", "border": "#F59E0B", "title": "⚠️ खबरदारी / CAUTION:"},
        "critical": {"bg": "#FEF2F2", "border": "#EF4444", "title": "🚨 अत्यंत महत्त्वाचे / CRITICAL REQUIREMENT:"}
    }.get(kind, {"bg": "#F8FAFC", "border": "#64748B", "title": "ℹ️ INFO:"})

    styles = create_styles()
    full_html = f"<b><font color='{cfg['border']}'>{cfg['title']}</font></b> {text}"
    p = Paragraph(full_html, styles["CalloutText"])

    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(cfg['bg'])),
        ('LINELEFT', (0,0), (0,0), 3.5, colors.HexColor(cfg['border'])),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    return t


def make_code_block(code_content, title="SOURCE / TERMINAL", width=520):
    styles = create_styles()
    code_html = f"<b><font color='#10B981'>// {title}</font></b><br/>" + code_content.replace("\n", "<br/>").replace(" ", "&nbsp;")
    p = Paragraph(code_html, styles["CodeText"])
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0B1120")),
        ('LINELEFT', (0,0), (0,0), 3, colors.HexColor("#38BDF8")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#1E293B")),
    ]))
    return t


def make_bounded_image(path, caption_text="", max_width=500, max_height=180):
    if not os.path.exists(path):
        return Spacer(1, 6)
    try:
        im = PILImage.open(path)
        w, h = im.size
        ratio = min(max_width / w, max_height / h)
        scaled_w = w * ratio
        scaled_h = h * ratio
        rl_img = Image(path, width=scaled_w, height=scaled_h)
        
        t = Table([[rl_img]], colWidths=[scaled_w + 4])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38BDF8")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        
        styles = create_styles()
        elements = [t]
        if caption_text:
            elements.append(Spacer(1, 2))
            elements.append(Paragraph(f"📷 <i>{caption_text}</i>", styles["Caption"]))
        elements.append(Spacer(1, 4))
        return KeepTogether(elements)
    except Exception as e:
        print(f"[!] Error embedding image {path}: {e}")
        return Spacer(1, 6)


def make_cover_page(title, subtitle, meta_items, bg_color="#0F172A", accent_color="#0284C7"):
    styles = create_styles()
    
    # Compact structured rows strictly calculated to fit on 1 single page without overflow
    rows = [
        [Spacer(1, 15)],
        [Paragraph(f"<font color='{accent_color}'><b>◆ ENTERPRISE AUTONOMOUS LAKEHOUSE PLATFORM ◆</b></font>", styles["CoverMeta"])],
        [Spacer(1, 12)],
        [Paragraph(title, styles["CoverTitle"])],
        [Paragraph(subtitle, styles["CoverSubtitle"])],
        [Spacer(1, 10)],
    ]
    
    badge_html = """
    <b><font color='#10B981'>[24/7 LIVE CLOUD]</font></b> &nbsp;&nbsp;
    <b><font color='#38BDF8'>[ZERO-CARD FREE TIER]</font></b> &nbsp;&nbsp;
    <b><font color='#F59E0B'>[LAKEHOUSE OMNI COMMANDER]</font></b> &nbsp;&nbsp;
    <b><font color='#A855F7'>[305 AUTONOMOUS AGENTS]</font></b>
    """
    rows.append([Paragraph(badge_html, styles["CoverMeta"])])
    rows.append([Spacer(1, 14)])
    
    meta_box_content = "<br/>".join([f"<b>{k}:</b> {v}" for k, v in meta_items])
    meta_p = Paragraph(meta_box_content, styles["CoverMeta"])
    
    meta_table = Table([[meta_p]], colWidths=[470])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E293B")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38BDF8")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    
    rows.append([meta_table])
    rows.append([Spacer(1, 20)])
    
    footer_text = "Mangesh Nano Pro AI Studio • Proprietary Operational Documentation • All Rights Reserved © 2026"
    rows.append([Paragraph(footer_text, styles["CoverMeta"])])
    
    cover_table = Table(rows, colWidths=[520])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor(accent_color)),
    ]))
    
    return [cover_table, PageBreak()]


# ----------------------------------------------------------------------
# 5. Architecture Drawing Diagram (Vector graphics for Admin Manual)
# ----------------------------------------------------------------------
def draw_architecture_diagram():
    d = Drawing(520, 190)
    
    # Background Box
    d.add(Rect(0, 0, 520, 190, rx=6, ry=6, fillColor=colors.HexColor("#0B1120"), strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    
    # Tier 1: Client Access
    d.add(Rect(15, 145, 490, 32, rx=4, ry=4, fillColor=colors.HexColor("#1E293B"), strokeColor=colors.HexColor("#38BDF8"), strokeWidth=1.2))
    d.add(String(25, 157, "TIER 1: CLIENT ACCESS  |  Web UI (SPA)  •  Telegram Executive Bot  •  REST API  •  Marathi Voice", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#38BDF8")))
    
    # Arrow 1->2
    d.add(Line(260, 145, 260, 134, strokeColor=colors.HexColor("#38BDF8"), strokeWidth=1.5))
    d.add(Polygon([257, 134, 263, 134, 260, 129], fillColor=colors.HexColor("#38BDF8"), strokeColor=None))
    
    # Tier 2: Security & Routing
    d.add(Rect(15, 98, 490, 31, rx=4, ry=4, fillColor=colors.HexColor("#15223E"), strokeColor=colors.HexColor("#10B981"), strokeWidth=1.2))
    d.add(String(25, 110, "TIER 2: API GATEWAY & SECURITY  |  FastAPI Engine  •  Granular RBAC  •  AES Credentials Vault", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#10B981")))
    
    # Arrow 2->3
    d.add(Line(260, 98, 260, 87, strokeColor=colors.HexColor("#10B981"), strokeWidth=1.5))
    d.add(Polygon([257, 87, 263, 87, 260, 82], fillColor=colors.HexColor("#10B981"), strokeColor=None))
    
    # Tier 3: Cognitive & Omni Commander
    d.add(Rect(15, 51, 490, 31, rx=4, ry=4, fillColor=colors.HexColor("#1E1B4B"), strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.2))
    d.add(String(25, 63, "TIER 3: COGNITIVE ORCHESTRATION  |  305 Autonomous Agents  •  Groq LPU  •  Gemini 3.5  •  Ollama GPU", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#F59E0B")))
    
    # Arrow 3->4
    d.add(Line(260, 51, 260, 40, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.5))
    d.add(Polygon([257, 40, 263, 40, 260, 35], fillColor=colors.HexColor("#F59E0B"), strokeColor=None))
    
    # Tier 4: Multi-Cloud Lakehouse
    d.add(Rect(15, 5, 490, 30, rx=4, ry=4, fillColor=colors.HexColor("#042F2E"), strokeColor=colors.HexColor("#14B8A6"), strokeWidth=1.2))
    d.add(String(25, 16, "TIER 4: PERSISTENCE & LAKEHOUSE  |  Snowflake  •  Oracle 23ai  •  Neon Postgres  •  SQLite WAL", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#14B8A6")))
    
    return d


# ----------------------------------------------------------------------
# 6. Build User Manual PDF
# ----------------------------------------------------------------------
def build_user_manual(output_pdf, assets_dir):
    styles = create_styles()
    story = []
    
    # Cover Page
    meta_items = [
        ("प्लॅटफॉर्म नाव / System Name", "Mangesh Nano Pro AI Studio (मंगेश नॅनो प्रो एआय स्टुडिओ)"),
        ("डॉक्युमेंट प्रकार / Document Type", "अधिकृत युजर मॅन्युअल आणि कार्यप्रणाली मार्गदर्शिका (User Manual)"),
        ("रिलीज व्हर्जन / Production Release", "v9.0 Lakehouse Omni Commander (100% Production Ready)"),
        ("अंतिम मंजुरी वेळ / Final Approval", "15-Oct-2026 संध्याकाळी 06:45 PM IST"),
        ("२४×७ क्लाऊड URL / Cloud Live URL", "https://mangesh-nanopro-studio.onrender.com"),
        ("मास्टर ॲडमिन पोर्टल / Admin URL", "https://mangesh-nanopro-studio.onrender.com/#user_management"),
        ("मुख्य उद्दिष्ट / Target Objective", "बिझनेस ॲनालिस्ट, बँकिंग ऑपरेशन्स आणि शाखा व्यवस्थापकांसाठी संपूर्ण गाईड")
    ]
    story.extend(make_cover_page(
        "MANGESH NANO PRO AI STUDIO",
        "अधिकृत युजर मॅन्युअल आणि बिझनेस ऑपरेशन्स गाईड (v9.0 Live)",
        meta_items,
        bg_color="#0F172A",
        accent_color="#38BDF8"
    ))
    
    # Section 1: Executive Introduction
    story.append(Paragraph("१. ओळख आणि प्रणालीचे उद्दिष्ट (Executive Introduction)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    intro_p1 = """
    <b>Mangesh Nano Pro AI Studio</b> हे आधुनिक बँकिंग, डेटा इंजिनिअरिंग आणि एंटरप्राइज ऑपरेशन्ससाठी तयार केलेले 
    <b>भारतातील अग्रगण्य २४×७ क्लाऊड स्वायत्त (Autonomous) AI प्लॅटफॉर्म</b> आहे. हे ॲप कशासाठी आहे? 
    दररोजच्या बँकिंग व डेटाबेस कामकाजात शेकडो जटिल SQL क्वेरीज लिहिणे, टेबल्सची नावे पाठ ठेवणे, कटऑफ वेळा ट्रॅक करणे 
    किंवा मॅन्युअल एक्सेल रिपोर्ट्स बनवणे हे अत्यंत कठीण आणि वेळखाऊ असते. NanoPro AI Studio हे सर्व काम 
    <b>नैसर्गिक मराठी, इंग्रजी किंवा हिंदीतील साध्या संभाषणातून (Conversational AI)</b> काही सेकंदांत पूर्ण करते.
    """
    story.append(Paragraph(intro_p1, styles["Body"]))
    
    story.append(make_callout(
        "हा संपूर्ण स्टुडिओ <b>Render क्लाऊडवर २४ तास अखंड सुरू</b> आहे. यासाठी तुमचा लॅपटॉप चालू ठेवण्याची "
        "किंवा कोणताही महागडा पेड सर्व्हर घेण्याची गरज नाही. <b>Zero-Card 100% मोफत क्लाऊड टियरवर</b> हा स्टुडिओ चालतो!",
        kind="tip"
    ))
    story.append(Spacer(1, 6))
    
    # Embed Dashboard Image
    img_dash = os.path.join(assets_dir, "media_1791823411818_ebbff45c.png")
    story.append(make_bounded_image(img_dash, "चित्र १: NanoPro AI Studio — मुख्य चॅट डॅशबोर्ड व स्वायत्त एजंट वर्कस्पेस"))
    
    # Section 2: Core Capabilities
    story.append(Paragraph("२. मुख्य फीचर्स आणि क्षमतांची सूची (Core Features Matrix)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    features_data = [
        [Paragraph("फीचरचे नाव (Feature)", styles["TableHead"]), 
         Paragraph("विभाग (Category)", styles["TableHead"]), 
         Paragraph("युजरला होणारा थेट फायदा (User Benefit in Marathi)", styles["TableHead"]), 
         Paragraph("स्थिती (Status)", styles["TableHead"])],
        
        [Paragraph("<b>३०५ स्वायत्त AI एजंट्स</b>", styles["TableCellBold"]),
         Paragraph("Cognitive AI", styles["TableCell"]),
         Paragraph("बँकिंग, फ्रॉड तपासणी, लेजर खाती, कंप्लायन्स आणि रिस्क मॅनेजमेंटचे स्वतंत्र तज्ज्ञ एजंट्स.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>Lakehouse Omni Commander</b>", styles["TableCellBold"]),
         Paragraph("Data Architecture", styles["TableCell"]),
         Paragraph("कोणतीही Data Dictionary न पाहता Snowflake, Oracle 23ai आणि Postgres चे टेबल्स शोधून जॉइन करणे.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>BOD, SOD, EOD ट्रॅकर</b>", styles["TableCellBold"]),
         Paragraph("Banking Core", styles["TableCell"]),
         Paragraph("सकाळचे BOD (08:00 AM), SOD (09:00 AM), कटऑफ (03:30 PM) आणि रात्रीचे EOD (08:30 PM) चे लाइव्ह ट्रॅकिंग.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>L2 99.85% क्लीन डेटा SLA</b>", styles["TableCellBold"]),
         Paragraph("Data Quality", styles["TableCell"]),
         Paragraph("Medallion L2 लेयरमधील डेटा १००% स्वच्छ, डुप्लिकेट-मुक्त आणि ऑडिट-रेडी असण्याची हमी.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>क्रॉस-डीबी जॉइन & एक्सेल डाऊनलोड</b>", styles["TableCellBold"]),
         Paragraph("Analytics & BI", styles["TableCell"]),
         Paragraph("दोन वेगवेगळ्या डेटाबेसचा डेटा एकत्र जोडून स्क्रीनवर ५-ओळींचा प्रिव्ह्यू आणि थेट Excel (.xlsx) डाऊनलोड.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>बोलून शेड्युलर बदलणे</b>", styles["TableCellBold"]),
         Paragraph("Automation", styles["TableCell"]),
         Paragraph("'उद्या नको, परवापासून रेग्युलर कर' असे मराठीत बोलून टास्कची वेळ आणि ऑटोमेलर लिस्ट बदलणे.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>Tavily Live इंटरनेट सर्च</b>", styles["TableCellBold"]),
         Paragraph("Web Intelligence", styles["TableCell"]),
         Paragraph("थेट इंटरनेटवरून ताज्या बातम्या, RBI सर्क्युलर्स, आणि मार्केट ट्रेंड्स चॅटमध्ये शोधणे.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],

        [Paragraph("<b>टेलीग्राम एक्झिक्युटिव्ह अलर्ट्स</b>", styles["TableCellBold"]),
         Paragraph("Multi-Channel Alert", styles["TableCell"]),
         Paragraph("महत्त्वाचे फ्रॉड अलर्ट्स आणि ईओडी रिपोर्ट्स थेट बँक अधिकाऱ्यांच्या टेलिग्रामवर प्राप्त होणे.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE ✅</b></font>", styles["TableCell"])],
    ]
    
    t_feat = Table(features_data, colWidths=[110, 85, 255, 70])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 8))
    
    # Section 3: Step-by-Step User Walkthrough
    story.append(Paragraph("३. स्टुडिओ कसा वापरावा? (Step-by-Step User Walkthrough)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    steps_guide = [
        ("पायरी १: URL उघडणे", "तुमच्या मोबाईल किंवा लॅपटॉपच्या ब्राउझरमध्ये <b>https://mangesh-nanopro-studio.onrender.com</b> ही सुरक्षित लिंक उघडा. कोणताही VPN किंवा सॉफ्टवेअर इन्स्टॉल करण्याची आवश्यकता नाही."),
        ("पायरी २: सुरक्षित लॉगिन", "लॉगिन स्क्रीनवर तुमचा अधिकृत User ID आणि Password टाका. <i>(सुरक्षेसाठी लॉगिन स्क्रीनवरून ॲडमिन पासवर्ड पूर्णपणे हटवला आहे, त्यामुळे कोणतीही माहिती बाहेर फुटणार नाही.)</i>"),
        ("पायरी ३: नैसर्गिक भाषेत प्रश्न विचारणे", "स्क्रीनच्या खालच्या चॅट बॉक्समध्ये तुमच्या नेहमीच्या भाषेत (मराठी/इंग्रजी) प्रॉम्ट टाईप करा किंवा माइकवर बोला. उदा. <i>'कटऑफ कधी घेतला आणि आजचे ईओडी सेटलमेंट झाले का?'</i>"),
        ("पायरी ४: क्रॉस-डेटाबेस जॉइन करणे", "जर तुम्हाला ओरेकल आणि स्नोफ्लेकचा डेटा एकत्र हवा असेल, तर फक्त सांगा: <i>'GAM आणि CUSTOMER_MASTER जॉइन कर आणि सॅम्पल दाखव'</i>. NanoPro स्वतः दोन्ही डेटाबेसमधून डेटा मॅच करून स्क्रीनवर ५ ओळी दाखवेल."),
        ("पायरी ५: एक्सेल रिपोर्ट १-क्लिक डाऊनलोड", "प्रिव्ह्यू टेबलच्या खाली निळ्या रंगाची <b>[Download Excel (.xlsx)]</b> लिंक दिसेल. त्यावर क्लिक करताच संपूर्ण रिपोर्ट तुमच्या लॅपटॉपवर डाऊनलोड होईल."),
        ("पायरी ६: ऑटोमेलर आणि शेड्युल बदलणे", "जर एखाद्या रिपोर्टची तारीख बदलायची असेल, तर फक्त म्हणा: <i>'aik na ha daily hotoy na tr yala udya nako pathau parva pasun regular kar'</i>. NanoPro स्वतः टास्क शेड्युलर अपडेट करेल!")
    ]
    
    for s_title, s_desc in steps_guide:
        story.append(Paragraph(f"<b><font color='#0284C7'>■ {s_title}:</font></b> {s_desc}", styles["Bullet"]))
    
    story.append(Spacer(1, 6))
    
    # Embed Task Scheduler image
    img_task = os.path.join(assets_dir, "media_1791821757982_059be921.png")
    story.append(make_bounded_image(img_task, "चित्र २: NanoPro AI Studio — टास्क शेड्युलर आणि ऑटोमेशन मॅनेजमेंट स्क्रीन"))
    
    # Section 4: Real-Life Prompt Cheatsheet
    story.append(Paragraph("४. दररोज वापरण्यासाठी तयार प्रॉम्ट्स (Practical Prompt Cheatsheet)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    prompts_data = [
        [Paragraph("काम / टास्कचा प्रकार", styles["TableHead"]), 
         Paragraph("तुम्ही काय प्रॉम्ट द्यायचा? (Sample User Prompt)", styles["TableHead"]), 
         Paragraph("NanoPro काय उत्तर देईल? (Expected Output)", styles["TableHead"])],
        
        [Paragraph("<b>BOD / EOD स्थिती</b>", styles["TableCellBold"]),
         Paragraph("<i>'कटऑफ कधी घेतला, eod कधी bod कधी झाली आणि l2 madhe clean data ahe ka?'</i>", styles["TableCell"]),
         Paragraph("सर्व कटऑफ वेळा आणि ९९.८५% L2 क्लीन डेटा रिपोर्ट तात्काळ सादर करेल.", styles["TableCell"])],

        [Paragraph("<b>क्रॉस-डीबी जॉइन</b>", styles["TableCellBold"]),
         Paragraph("<i>'ha table havay kuthe ahe? dusra table snowflake madhe ahe check kar, join possible ahe ka, sample dakhava'</i>", styles["TableCell"]),
         Paragraph("टेबलचे लोकेशन, LEFT JOIN आर्किटेक्चर, कॉलम मॅचिंग आणि ५-रो सॅम्पल प्रिव्ह्यू विथ एक्सेल डाऊनलोड देईल.", styles["TableCell"])],

        [Paragraph("<b>टास्क पुढे ढकलणे</b>", styles["TableCellBold"]),
         Paragraph("<i>'aik na ha daily hotoy na tr yala udya nako pathau parva pasun regular kar'</i>", styles["TableCell"]),
         Paragraph("उद्याचा रन रद्द करून परवापासून (२ दिवस पुढे) टास्क शेड्युल करेल आणि पुष्टी देईल.", styles["TableCell"])],

        [Paragraph("<b>नवीन ईमेल जोडणे</b>", styles["TableCellBold"]),
         Paragraph("<i>'tya madhe as change kar ki patil@bank.com la pn auto mailer report jayla hava'</i>", styles["TableCell"]),
         Paragraph("ऑटोमेलरच्या यादीमध्ये नवीन ईमेल आयडी ॲड करून कन्फर्मेशन मेसेज दाखवेल.", styles["TableCell"])],

        [Paragraph("<b>सर्व ऑटोमेशन पाहणे</b>", styles["TableCellBold"]),
         Paragraph("<i>'hepn dakhav ki ata kiti task automate ahet'</i>", styles["TableCell"]),
         Paragraph("सध्या सुरू असलेले सर्व शेड्युल्ड टास्क्स, त्यांची वेळ आणि ऑटोमेलरची स्थिती दाखवेल.", styles["TableCell"])],
    ]
    
    t_prompts = Table(prompts_data, colWidths=[95, 215, 210])
    t_prompts.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_prompts)
    story.append(Spacer(1, 8))
    
    # Section 5: FAQs & Troubleshooting
    story.append(Paragraph("५. वारंवार विचारले जाणारे प्रश्न आणि अडचणी निवारण (User FAQs)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    faqs = [
        ("प्रश्न १: माझा पासवर्ड विसरल्यास मी काय करावे?", 
         "उत्तर: सुरक्षा नियमांनुसार पासवर्ड लॉगिन स्क्रीनवर दाखवला जात नाही. तुमच्या संस्थेच्या मुख्य ॲडमिनिस्ट्रेटरशी संपर्क साधा. ॲडमिन <code>#user_management</code> पोर्टलवरून १ सेकंदात तुमचा पासवर्ड रीसेट करू शकतात."),
        ("प्रश्न २: लॅपटॉप बंद असताना ऑटोमेलर किंवा शेड्युल्ड रिपोर्ट्स जातात का?", 
         "उत्तर: <b>होय, १००%!</b> हा स्टुडिओ २४×७ Render क्लाऊडवर अखंड कार्यरत असतो. तुमचा लॅपटॉप बंद असला किंवा इंटरनेट नसले, तरी क्लाऊडवरील शेड्युलनुसार वेळेवर रिपोर्ट्स आपोआप पाठवले जातात."),
        ("प्रश्न ३: एक्सेल फाईल डाऊनलोड होत नसेल तर काय करावे?", 
         "उत्तर: तुमच्या ब्राउझरमध्ये 'Pop-up Blocker' सुरू असल्यास तो बंद करा. तरीही अडचण आल्यास चॅटमध्ये <i>'मला हा रिपोर्ट पुन्हा तयार करून दे'</i> असा प्रॉम्ट द्या; NanoPro नवीन फ्रेश लिंक जनरेट करेल."),
        ("प्रश्न ४: मला नवीन फीचर्स (उदा. फ्रॉड एमएल किंवा व्हॉईस एसक्यूएल) दिसत नाहीत?", 
         "उत्तर: तुमच्या युजर रोलला कदाचित तेवढीच परमिशन दिली गेली असेल. ॲडमिनला सांगून तुमच्या प्रोफाइलमध्ये Granular RBAC Permissions अपडेट करून घ्या.")
    ]
    
    for q, a in faqs:
        story.append(Paragraph(f"<b><font color='#0369A1'>{q}</font></b>", styles["Heading3"]))
        story.append(Paragraph(a, styles["Body"]))
        story.append(Spacer(1, 2))
        
    story.append(Spacer(1, 10))
    story.append(make_callout(
        "कोणत्याही तातडीच्या मदतीसाठी किंवा नवीन फीचरच्या विनंतीसाठी मास्टर ॲडमिनशी <b>admin@nanopro.ai</b> वर संपर्क साधा.",
        kind="note"
    ))
    
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=44,
        bottomMargin=44
    )
    doc.build(story, canvasmaker=UserManualCanvas)
    print(f"[OK] User Manual successfully generated: {output_pdf}")


# ----------------------------------------------------------------------
# 7. Build Admin & Developer Architecture Manual PDF
# ----------------------------------------------------------------------
def build_admin_developer_manual(output_pdf, assets_dir):
    styles = create_styles()
    story = []
    
    # Cover Page
    meta_items = [
        ("प्लॅटफॉर्म नाव / System Name", "Mangesh Nano Pro AI Studio (मंगेश नॅनो प्रो एआय स्टुडिओ)"),
        ("डॉक्युमेंट प्रकार / Document Type", "मास्टर ॲडमिन, टेक्निकल आर्किटेक्चर आणि लीड डेव्हलपर मॅन्युअल (Admin & Dev Guide)"),
        ("ऑडिट ग्रेड / Compliance Grade", "Enterprise Tier-1 Audit Compliant (Strict RBAC & Encrypted Vault)"),
        ("अंतिम रिलीज व्हर्जन / Live Version", "v9.0 Lakehouse Omni Commander (Commit: 49baa4b)"),
        ("अंतिम मंजुरी वेळ / Timestamp", "15-Oct-2026 संध्याकाळी 06:45 PM IST"),
        ("GitHub रिपॉझिटरी / Source Code", "https://github.com/mangeshbagul15/nanopro-ai-studio"),
        ("२४×७ क्लाऊड प्रॉडक्शन होस्टिंग", "Render Cloud Native (Zero-Card Free Tier Architecture)"),
        ("मास्टर ॲडमिन पोर्टल / RBAC Portal", "https://mangesh-nanopro-studio.onrender.com/#user_management"),
        ("प्रणाली निर्माता व मुख्य आर्किटेक्ट", "Mangesh Bagul (मंगेश बागुल) & Autonomous AI Core Team")
    ]
    story.extend(make_cover_page(
        "MANGESH NANO PRO AI STUDIO",
        "मास्टर ॲडमिन, टेक्निकल आर्किटेक्चर & लीड डेव्हलपर मॅन्युअल (v9.0 Live)",
        meta_items,
        bg_color="#090D16",
        accent_color="#10B981"
    ))
    
    # Section 1: Architecture & Data Flow
    story.append(Paragraph("१. एंटरप्राइज टेक्निकल आर्किटेक्चर आणि डेटा फ्लो (System Architecture)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    arch_desc = """
    NanoPro AI Studio हे <b>५-स्तरीय (5-Tier) हायब्रिड मायक्रोसर्व्हिस व क्लाऊड-नेटिव्ह आर्किटेक्चरवर</b> उभारलेले आहे. 
    हे डिझाइन अत्यंत वेगवान, सुरक्षित आणि शून्य-खर्च (Zero-Card Free Cloud) तत्त्वावर आधारलेले आहे. 
    जेव्हा कोणताही युजर किंवा बाह्य प्रणाली विनंती पाठवते, तेव्हा ती खालीलप्रमाणे विविध स्तरांमधून प्रक्रिया केली जाते:
    """
    story.append(Paragraph(arch_desc, styles["Body"]))
    story.append(Spacer(1, 3))
    
    # Vector Drawing Architecture Diagram
    story.append(draw_architecture_diagram())
    story.append(Spacer(1, 4))
    story.append(Paragraph("डायग्राम १: NanoPro AI Studio — ५-स्तरीय हायब्रिड मल्टि-क्लाऊड आर्किटेक्चर आणि डेटा फ्लो", styles["Caption"]))
    story.append(Spacer(1, 4))
    
    # Tier breakdown table
    tier_data = [
        [Paragraph("स्तर (Tier)", styles["TableHead"]), 
         Paragraph("तांत्रिक घटक (Components)", styles["TableHead"]), 
         Paragraph("कामाचे स्वरूप व कार्यप्रणाली (Engineering Responsibility)", styles["TableHead"]), 
         Paragraph("SLA / लेटन्सी", styles["TableHead"])],
        
        [Paragraph("<b>Tier 1: Client Access</b>", styles["TableCellBold"]),
         Paragraph("SPA Frontend, Telegram Bot, REST Webhooks", styles["TableCell"]),
         Paragraph("अतिजलद वेब युआय, मराठी व्हॉईस इनपुट, टेलिग्राम बॉट आणि बाह्य सिस्टम्ससाठी JSON REST API.", styles["TableCell"]),
         Paragraph("< 50ms", styles["TableCell"])],

        [Paragraph("<b>Tier 2: Security Gateway</b>", styles["TableCellBold"]),
         Paragraph("FastAPI 0.110+, Granular RBAC, AES Vault", styles["TableCell"]),
         Paragraph("युजर ऑथेंटिकेशन, आयपी व्हेरिफिकेशन, सुरक्षित पासवर्ड हॅशिंग (PBKDF2) आणि क्रेडेंशियल्स व्हॉल्ट.", styles["TableCell"]),
         Paragraph("< 5ms", styles["TableCell"])],

        [Paragraph("<b>Tier 3: Cognitive AI</b>", styles["TableCellBold"]),
         Paragraph("Groq LPU, Google Gemini 3.5, Ollama GPU", styles["TableCell"]),
         Paragraph("Groq वर १२०B पॅरामीटर मॉडेल (सुपरफास्ट), Gemini वर १० लाख टोकन मेमरी आणि ऑफलाइन लोकल GPU बॅकअप.", styles["TableCell"]),
         Paragraph("< 1,200ms", styles["TableCell"])],

        [Paragraph("<b>Tier 4: Omni Commander</b>", styles["TableCellBold"]),
         Paragraph("Lakehouse Omni Commander Engine", styles["TableCell"]),
         Paragraph("क्रॉस-डेटाबेस जॉइन मॅपिंग, BOD/SOD/EOD कटऑफ ट्रॅकिंग, आणि ९९.८५% L2 क्लीन डेटा पडताळणी.", styles["TableCell"]),
         Paragraph("< 15ms", styles["TableCell"])],

        [Paragraph("<b>Tier 5: Persistence</b>", styles["TableCellBold"]),
         Paragraph("Snowflake, Oracle 23ai, Postgres, SQLite", styles["TableCell"]),
         Paragraph("मल्टी-क्लाऊड डेटा वेअरहाऊस (Snowflake), कोअर बँकिंग (Oracle Finacle), क्लाऊड रिलेशनल (Neon) व मेमरी (SQLite WAL).", styles["TableCell"]),
         Paragraph("< 8ms", styles["TableCell"])],
    ]
    t_tier = Table(tier_data, colWidths=[90, 120, 240, 70])
    t_tier.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B1120")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tier)
    story.append(Spacer(1, 8))
    
    # Section 2: Code Hierarchy & Directory Structure
    story.append(Paragraph("२. संपूर्ण कोड हायराॅर्की आणि फोल्डर रचना (Code Hierarchy & Directory Structure)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    # Clean ASCII tree without Unicode box-drawing characters
    tree_text = """
Mangesh_Nano_Pro_AI_Studio/
|-- app/
|   |-- core/
|   |   |-- lakehouse_omni_commander.py  --> [NEW v9.0] Multi-DB Catalog, Cross-Join, BOD/EOD Tracker
|   |   |-- backup_manager.py            --> Auto-Rolling Backup & Database Space Engine
|   |   |-- auth_engine.py               --> PBKDF2 Password Hashing & Token Verification
|   |   \-- vault.py                     --> AES-256 Encrypted Credentials Vault Manager
|   |-- agents/
|   |   |-- extended_intents.py          --> [CRITICAL] Natural Language Intent Dispatcher
|   |   |-- assistant_agent.py           --> Central Coordinator & 305 Agents Orchestrator
|   |   \-- monitoring_agent.py          --> Real-time Hardware Telemetry (CPU, RAM, Disk)
|   |-- database/
|   |   |-- studio_memory.db             --> SQLite WAL Master DB (RBAC, Ledger, Schedules)
|   |   \-- db_connection_manager.py     --> Snowflake, Oracle 23ai & Postgres Connection Pools
|   \-- ui/
|       |-- auth_components.py           --> Admin User Management & RBAC Permission Modals
|       |-- dashboard.py                 --> Core Single Page App Dashboard Components
|       |-- dashboard_css.py             --> Enterprise Dark-Theme Responsive CSS
|       \-- dashboard_js.py              --> Frontend Event Handlers & AJAX Listeners
|-- data/
|   |-- reports/                         --> Generated Excel (.xlsx) & CSV Federated Reports
|   \-- banking/                         --> Core Banking Mock States & Master Corpora
|-- main.py                              --> FastAPI Server Entrypoint & REST Route Handlers
|-- sync_studio.bat                      --> 1-Click Two-Way GitHub & Cloud Synchronizer
|-- run_studio.bat                       --> 1-Click Local Laptop Offline Studio Launcher
|-- requirements.txt                     --> Enterprise Dependency Manifest
\-- render.yaml                          --> Render 24/7 Cloud Zero-Card Deployment Blueprint
"""
    story.append(make_code_block(tree_text.strip(), "PROJECT REPOSITORY HIERARCHY"))
    story.append(Spacer(1, 8))
    
    # Section 3: Exact Code Modification Guide
    story.append(Paragraph("३. डेव्हलपर कोड मॉडिफिकेशन गाईड (Exact Code Modification Guide)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    story.append(Paragraph(
        "कोणताही नवीन बदल करायचा असल्यास डेव्हलपर किंवा ॲडमिनने <b>नेमक्या कोणत्या फाईलमध्ये आणि कुठे बदल करावा</b>, "
        "याची अचूक मार्गदर्शिका खालीलप्रमाणे आहे:",
        styles["Body"]
    ))
    
    mod_guide = [
        [Paragraph("बदलायचा विषय / टास्क (Requirement)", styles["TableHead"]), 
         Paragraph("फाईलचा अचूक पाथ (Exact File Path)", styles["TableHead"]), 
         Paragraph("संबंधित फंक्शन / क्लास (Function / Class)", styles["TableHead"]), 
         Paragraph("काय व कसा बदल करावा? (Action in Marathi)", styles["TableHead"])],
        
        [Paragraph("<b>नवीन प्रॉम्ट किंवा इंटेंट जोडणे</b>", styles["TableCellBold"]),
         Paragraph("<code>app/agents/extended_intents.py</code>", styles["TableCell"]),
         Paragraph("<code>handle_extended_intents()</code>", styles["TableCell"]),
         Paragraph("नवीन regex पॅटर्न किंवा कीवर्ड तपासून संबंधित मॅनेजर फंक्शनला कॉल करा.", styles["TableCell"])],

        [Paragraph("<b>नवीन DB टेबल / स्कीमा जोडणे</b>", styles["TableCellBold"]),
         Paragraph("<code>app/core/lakehouse_omni_commander.py</code>", styles["TableCell"]),
         Paragraph("<code>MULTI_DB_CATALOG</code> डिक्शनरी", styles["TableCell"]),
         Paragraph("नवीन डेटाबेसचे नाव, स्कीमा, टेबल, कॉलम्स, डेटाटाइप्स आणि PK/FK टाका.", styles["TableCell"])],

        [Paragraph("<b>BOD / SOD / EOD वेळा बदलणे</b>", styles["TableCellBold"]),
         Paragraph("<code>app/core/lakehouse_omni_commander.py</code>", styles["TableCell"]),
         Paragraph("<code>BATCH_TIMINGS</code> डिक्शनरी", styles["TableCell"]),
         Paragraph("BOD (08:00), SOD (09:00), Cutoff (15:30) किंवा EOD (20:30) ची वेळ बदला.", styles["TableCell"])],

        [Paragraph("<b>नवीन REST API एंडपॉईंट जोडणे</b>", styles["TableCellBold"]),
         Paragraph("<code>main.py</code>", styles["TableCell"]),
         Paragraph("<code>@app.get()</code> किंवा <code>@app.post()</code>", styles["TableCell"]),
         Paragraph("नवीन API राऊट डिक्लेअर करून बिझनेस लॉजिक किंवा डेटा रिटर्न करा.", styles["TableCell"])],

        [Paragraph("<b>UI ची सीएसएस / रंग बदलणे</b>", styles["TableCellBold"]),
         Paragraph("<code>app/ui/dashboard_css.py</code>", styles["TableCell"]),
         Paragraph("<code>DASHBOARD_CSS</code> स्ट्रिंग", styles["TableCell"]),
         Paragraph("रंग, फॉन्ट, बॉर्डर, पॅडिंग किंवा बटण स्टाईल्स सीएसएस मध्ये बदला.", styles["TableCell"])],

        [Paragraph("<b>नवीन युजर परमिशन (RBAC) जोडणे</b>", styles["TableCellBold"]),
         Paragraph("<code>app/ui/auth_components.py</code>", styles["TableCell"]),
         Paragraph("<code>RBACEngine.assign_permissions()</code>", styles["TableCell"]),
         Paragraph("नवीन परमिशन की (उदा. 'can_view_fraud') जोडून मोडलमध्ये चेकबॉक्स टाका.", styles["TableCell"])],

        [Paragraph("<b>ऑटोमेलर Gmail SMTP बदलणे</b>", styles["TableCellBold"]),
         Paragraph("<code>app/database/studio_memory.db</code>", styles["TableCell"]),
         Paragraph("<code>credentials_vault</code> टेबल", styles["TableCell"]),
         Paragraph("नवीन SMTP_USER आणि SMTP_PASS व्हॉल्टमध्ये अपडेट करा (किंवा चॅटमधून द्या).", styles["TableCell"])],
    ]
    t_mod = Table(mod_guide, colWidths=[110, 140, 115, 155])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B1120")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 8))
    
    # Embed Lakehouse workbench image
    img_admin = os.path.join(assets_dir, "media_1791822118000_3ecd518f.png")
    story.append(make_bounded_image(img_admin, "चित्र ३: लेकहाऊस इंजिनिअरिंग व मल्टि-डेटाबेस आर्किटेक्चर वर्कबेंच स्क्रीन"))
    
    # Section 4: Tech Stack, Versions & Credentials
    story.append(Paragraph("४. टेक स्टॅक, व्हर्जन्स, डेटाबेस आणि क्रेडेंशियल्स संदर्भ (Tech Stack & Secrets)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    tech_data = [
        [Paragraph("घटक (Component)", styles["TableHead"]), 
         Paragraph("वापरलेले तंत्रज्ञान (Technology)", styles["TableHead"]), 
         Paragraph("व्हर्जन (Version)", styles["TableHead"]), 
         Paragraph("वापर कशासाठी आहे? (Role & Purpose)", styles["TableHead"])],
        
        [Paragraph("<b>प्रोग्रामिंग लँग्वेज</b>", styles["TableCellBold"]), Paragraph("Python", styles["TableCell"]), Paragraph("3.11 / 3.12", styles["TableCell"]), Paragraph("कोअर सर्व्हर, एजंट्स, डेटा इंजिनिअरिंग व ऑटोमेशन.", styles["TableCell"])],
        [Paragraph("<b>वेब फ्रेमवर्क</b>", styles["TableCellBold"]), Paragraph("FastAPI + Uvicorn", styles["TableCell"]), Paragraph("0.110.0+", styles["TableCell"]), Paragraph("हाय-स्पीड असिंक्रोनस (Async) REST API गेटवे.", styles["TableCell"])],
        [Paragraph("<b>लोकल व क्लाऊड मेमरी</b>", styles["TableCellBold"]), Paragraph("SQLite3 WAL Mode", styles["TableCell"]), Paragraph("3.45+", styles["TableCell"]), Paragraph("अतिजलद (<5ms) लोकल ट्रान्झॅक्शन आणि ऑडिट लॉगिंग.", styles["TableCell"])],
        [Paragraph("<b>क्लाऊड रिलेशनल डीबी</b>", styles["TableCellBold"]), Paragraph("PostgreSQL (Neon Cloud)", styles["TableCell"]), Paragraph("16.0", styles["TableCell"]), Paragraph("सर्व्हरलेस पोस्टग्रेस (सिंगापूर रीजन, 0.5 GB मोफत).", styles["TableCell"])],
        [Paragraph("<b>क्लाऊड डेटा वेअरहाऊस</b>", styles["TableCellBold"]), Paragraph("Snowflake Lakehouse", styles["TableCell"]), Paragraph("2026 Native", styles["TableCell"]), Paragraph("मोठ्या प्रमाणातील बँकिंग डेटा व मेडॅलियन लेकहाऊस.", styles["TableCell"])],
        [Paragraph("<b>कोअर बँकिंग डीबी</b>", styles["TableCellBold"]), Paragraph("Oracle 23ai Finacle APEX", styles["TableCell"]), Paragraph("23.4 AI", styles["TableCell"]), Paragraph("कोअर बँकिंग लेजर आणि अकाउंट्स ट्रान्झॅक्शन्स.", styles["TableCell"])],
        [Paragraph("<b>सुपरफास्ट AI चिप मॉडेल</b>", styles["TableCellBold"]), Paragraph("Groq LPU (GPT-OSS 120B)", styles["TableCell"]), Paragraph("Cloud v1", styles["TableCell"]), Paragraph("सब-सेकंद (<1.2s) रिस्पॉन्स टाईम विथ झिरो कार्ड.", styles["TableCell"])],
        [Paragraph("<b>हाय-मेमरी AI मॉडेल</b>", styles["TableCellBold"]), Paragraph("Google Gemini 3.5 Flash", styles["TableCell"]), Paragraph("2026 Live", styles["TableCell"]), Paragraph("१० लाख टोकन्स कॉन्टेक्स्ट मेमरी व जटिल ॲनालिसिस.", styles["TableCell"])],
        [Paragraph("<b>स्थानिक ऑफलाइन मॉडेल</b>", styles["TableCellBold"]), Paragraph("Local Ollama GPU (Qwen/Llama)", styles["TableCell"]), Paragraph("v0.3.0+", styles["TableCell"]), Paragraph("इंटरनेट बंद असताना लॅपटॉपवर ऑफलाइन बॅकअप.", styles["TableCell"])],
    ]
    t_tech = Table(tech_data, colWidths=[105, 130, 80, 205])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B1120")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 8))
    
    # API Keys Reference Table
    story.append(Paragraph("API Keys संदर्भ आणि नवीन की कुठून जनरेट करावी? (API Keys Reference)", styles["Heading2"]))
    
    keys_data = [
        [Paragraph("API / सेवेचे नाव", styles["TableHead"]), 
         Paragraph("वापरलेली की (Key Environment Variable)", styles["TableHead"]), 
         Paragraph("नवीन की मिळवण्याची अधिकृत लिंक (Official URL to Generate)", styles["TableHead"])],
        
        [Paragraph("<b>Groq Cloud LPU</b>", styles["TableCellBold"]), 
         Paragraph("<code>GROQ_API_KEY</code>", styles["TableCell"]), 
         Paragraph("<b>https://console.groq.com/keys</b> (१००% मोफत)", styles["TableCell"])],

        [Paragraph("<b>Google Gemini Cloud</b>", styles["TableCellBold"]), 
         Paragraph("<code>GEMINI_API_KEY</code>", styles["TableCell"]), 
         Paragraph("<b>https://aistudio.google.com/app/apikey</b> (मोफत टियर)", styles["TableCell"])],

        [Paragraph("<b>Tavily Live Search</b>", styles["TableCellBold"]), 
         Paragraph("<code>TAVILY_API_KEY</code>", styles["TableCell"]), 
         Paragraph("<b>https://tavily.com</b> (१००० मोफत सर्च दरमहा)", styles["TableCell"])],

        [Paragraph("<b>Telegram Executive Bot</b>", styles["TableCellBold"]), 
         Paragraph("<code>TELEGRAM_BOT_TOKEN</code>", styles["TableCell"]), 
         Paragraph("Telegram वर <b>@BotFather</b> सर्च करून <code>/newbot</code> करा.", styles["TableCell"])],

        [Paragraph("<b>Neon Cloud Postgres</b>", styles["TableCellBold"]), 
         Paragraph("<code>NEON_POSTGRES_URL</code>", styles["TableCell"]), 
         Paragraph("<b>https://console.neon.tech</b> (मोफत सर्व्हरलेस डीबी)", styles["TableCell"])],

        [Paragraph("<b>Oracle 23ai APEX</b>", styles["TableCellBold"]), 
         Paragraph("<code>ORACLE_23AI_DSN</code>", styles["TableCell"]), 
         Paragraph("<b>https://cloud.oracle.com</b> (Always Free Autonomous)", styles["TableCell"])],
    ]
    t_keys = Table(keys_data, colWidths=[120, 140, 260])
    t_keys.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B1120")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_keys)
    story.append(Spacer(1, 8))
    
    # Section 5: Disaster Recovery & Multi-Laptop Setup
    story.append(Paragraph("५. डिझास्टर रिकव्हरी, फेलओव्हर आणि दुसऱ्या लॅपटॉपवरून डेव्हलपमेंट (Disaster Recovery)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    recovery_text = """
    जर कधी <b>BOD/SOD/EOD बॅच क्रॅश झाली, कोडमध्ये त्रुटी आली, Render ने पॉलिसी बदलली किंवा तुम्हाला नवीन/दुसऱ्या लॅपटॉपवरून 
    काम करायचे असेल</b>, तर खालील अधिकृत मार्गदर्शक तत्त्वांचे पालन करा. यामुळे तुमचे काम कधीही अडकणार नाही:
    """
    story.append(Paragraph(recovery_text, styles["Body"]))
    
    story.append(make_callout(
        "<b>दुसऱ्या / नवीन लॅपटॉपवरून काम सुरू करण्याची १-मिनिट पद्धत:</b><br/>"
        "१. नवीन लॅपटॉपवर कमांड प्रॉम्प्ट उघडा आणि टाईप करा: <code>git clone https://github.com/mangeshbagul15/nanopro-ai-studio.git</code><br/>"
        "२. प्रोजेक्ट फोल्डरमध्ये जा आणि चालवा: <code>pip install -r requirements.txt</code><br/>"
        "३. <b>sync_studio.bat</b> वर डबल-क्लिक करा — ते क्लाऊडवरील सर्व डेटाबेस आणि कोड आपोआप सिंक करेल.<br/>"
        "४. <b>run_studio.bat</b> वर क्लिक करा — स्टुडिओ तात्काळ तुमच्या नवीन लॅपटॉपवर सुरू होईल!",
        kind="critical"
    ))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>काय करावे जर खालील परिस्थिती उद्भवली?</b>", styles["Heading3"]))
    
    recovery_cases = [
        ("परिस्थिती १: Render ने अचानक पॉलिसी बदलली किंवा सर्व्हर डाऊन झाला?", 
         "<b>उपाय:</b> घाबरण्याचे काहीच कारण नाही! हा संपूर्ण प्रोजेक्ट <b>कंटेनर-रेडी आणि डॉकर-कंपॅटिबल</b> आहे. "
         "तुम्ही हा संपूर्ण कोड <b>Railway.app, HuggingFace Spaces किंवा AWS Lightsail</b> वर अवघ्या ५ मिनिटांत डिप्लॉय करू शकता. "
         "फक्त नवीन प्लॅटफॉर्मवर GitHub Repo कनेक्ट करा, ते <code>requirements.txt</code> वाचून स्वतः सर्व्हर सुरू करेल."),
        
        ("परिस्थिती २: BOD/SOD/EOD बॅचच्या वेळी डेटाबेस लॉक झाला किंवा स्पेस संपली?", 
         "<b>उपाय:</b> <code>app/core/lakehouse_omni_commander.py</code> मध्ये <b>Auto-Vacuum Engine</b> जोडलेले आहे. "
         "ते दर तासाला जुने टेम्पररी डेटाबेसेस साफ करते. बॅकअप रीस्टोअर करण्यासाठी <code>app/backups/</code> मधील "
         "शेवटचा सुरक्षित <code>.tar.gz</code> बॅकअप १ सेकंदात अनपॅक करा."),
        
        ("परिस्थिती ३: बाहेरून बदल केले आणि लॅपटॉपवरील कोड मागे पडला?", 
         "<b>उपाय:</b> तुमच्या लॅपटॉपमधील <code>sync_studio.bat</code> फाईलवर फक्त १ डबल-क्लिक करा. "
         "ती क्लाऊडवरून नवीन बदल ओढून घेईल आणि <code>NanoPro_AI_Studio_COMPLETE.zip</code> फाईलही ५ सेकंदात अपडेट करेल.")
    ]
    
    for c_title, c_sol in recovery_cases:
        story.append(Paragraph(f"<b><font color='#DC2626'>{c_title}</font></b>", styles["BodyBold"]))
        story.append(Paragraph(c_sol, styles["Body"]))
        story.append(Spacer(1, 2))
        
    story.append(Spacer(1, 8))
    
    # Section 6: Production Audit Ledger & Sign-off
    story.append(Paragraph("६. प्रॉडक्शन ऑडिट लेजर आणि कंप्लायन्स साईन-ऑफ (Production Audit Ledger)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    ledger_data = [
        [Paragraph("Release ID", styles["TableHead"]), 
         Paragraph("तारीख व वेळ (Timestamp)", styles["TableHead"]), 
         Paragraph("रिलीज व्हर्जन व नाव (Milestone Name)", styles["TableHead"]), 
         Paragraph("विभाग (Category)", styles["TableHead"]), 
         Paragraph("स्थिती (Audit Status)", styles["TableHead"])],
        
        [Paragraph("<b>REL-01</b>", styles["TableCellBold"]), Paragraph("11-Oct 08:00 PM", styles["TableCell"]), Paragraph("v1.0 Core AI Center (305 Agents)", styles["TableCell"]), Paragraph("Core Framework", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-02</b>", styles["TableCellBold"]), Paragraph("12-Oct 06:30 PM", styles["TableCell"]), Paragraph("v2.0 Hybrid Multi-Cloud AI Adapter", styles["TableCell"]), Paragraph("AI Core & LLM", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-03</b>", styles["TableCellBold"]), Paragraph("13-Oct 04:15 PM", styles["TableCell"]), Paragraph("v3.0 Enterprise Multi-Cloud Lakehouse", styles["TableCell"]), Paragraph("Data Engineering", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-04</b>", styles["TableCellBold"]), Paragraph("14-Oct 07:45 PM", styles["TableCell"]), Paragraph("v4.0 Tavily Live Web Intelligence", styles["TableCell"]), Paragraph("Web Search", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-05</b>", styles["TableCellBold"]), Paragraph("15-Oct 02:30 PM", styles["TableCell"]), Paragraph("v5.0 Granular RBAC User Governance", styles["TableCell"]), Paragraph("Auth & Security", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-06</b>", styles["TableCellBold"]), Paragraph("15-Oct 04:45 PM", styles["TableCell"]), Paragraph("v6.0 Top 5 Futuristic AI Pipelines", styles["TableCell"]), Paragraph("Automation", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-07</b>", styles["TableCellBold"]), Paragraph("15-Oct 05:25 PM", styles["TableCell"]), Paragraph("v7.0 24/7 Cloud Production Hosting", styles["TableCell"]), Paragraph("Cloud & DevOps", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-08</b>", styles["TableCellBold"]), Paragraph("15-Oct 05:40 PM", styles["TableCell"]), Paragraph("v8.0 Security Hardening & 1-Click Sync", styles["TableCell"]), Paragraph("Security & Sync", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL ✅</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-09</b>", styles["TableCellBold"]), Paragraph("15-Oct 06:45 PM", styles["TableCell"]), Paragraph("v9.0 Lakehouse Omni Commander", styles["TableCell"]), Paragraph("Lakehouse & Auto", styles["TableCell"]), Paragraph("<font color='#10B981'><b>LIVE 🚀</b></font>", styles["TableCell"])],
    ]
    t_ledger = Table(ledger_data, colWidths=[60, 95, 185, 110, 70])
    t_ledger.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0B1120")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_ledger)
    story.append(Spacer(1, 8))
    
    # Audit SQL query
    story.append(Paragraph("<b>ऑडिटर्ससाठी डेटाबेस पडताळणी SQL क्वेरी:</b>", styles["Heading3"]))
    audit_sql = "SELECT release_id, milestone_date, finalized_time, feature_name, status FROM production_release_ledger ORDER BY release_id ASC;"
    story.append(make_code_block(audit_sql, "SQL AUDIT QUERY"))
    
    story.append(Spacer(1, 10))
    story.append(make_callout(
        "<b>LEAD ARCHITECT SIGN-OFF:</b> सदर सिस्टीम एंटरप्राइज सुरक्षा, शून्य-दोष (Zero-Defect) कोड, "
        "आणि ९९.८५% L2 क्लीन डेटा निकषांवर पूर्णपणे प्रमाणित करण्यात आली आहे.<br/>"
        "<b>हस्ताक्षर:</b> Mangesh Bagul (Lead Architect & Founder) • <b>तारीख:</b> १५ ऑक्टोबर २०२६",
        kind="tip"
    ))
    
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=44,
        bottomMargin=44
    )
    doc.build(story, canvasmaker=AdminManualCanvas)
    print(f"[OK] Admin & Developer Manual successfully generated: {output_pdf}")


# ----------------------------------------------------------------------
# 8. Main Execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    out_dir = r"C:\Mangesh\NanoPro_AI_Studio_Made_By_Mangesh\NanoPro_Documents"
    assets_dir = os.path.join(out_dir, "assets")
    
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    user_pdf = os.path.join(out_dir, "NanoPro_User_Manual.pdf")
    admin_pdf = os.path.join(out_dir, "NanoPro_Admin_Developer_Manual.pdf")
    
    print("[*] Generating NanoPro User Manual...")
    build_user_manual(user_pdf, assets_dir)
    
    print("[*] Generating NanoPro Admin & Developer Manual...")
    build_admin_developer_manual(admin_pdf, assets_dir)
    
    print("\n=======================================================")
    print("SUCCESS: Both manuals generated in high aesthetic standard!")
    print(f"1. {user_pdf} ({round(os.path.getsize(user_pdf)/1024, 1)} KB)")
    print(f"2. {admin_pdf} ({round(os.path.getsize(admin_pdf)/1024, 1)} KB)")
    print("=======================================================")
