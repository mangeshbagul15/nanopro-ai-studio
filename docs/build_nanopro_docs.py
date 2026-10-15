# -*- coding: utf-8 -*-
"""
Mangesh Nano Pro AI Studio — Production PDF Manuals Generator (Minglish + English Edition)
Builds two audit-grade, high-aesthetic PDF manuals using standard Latin fonts (Helvetica, Helvetica-Bold, Courier):
1. NanoPro_User_Manual.pdf (End-User & Business Operations Guide)
2. NanoPro_Admin_Developer_Manual.pdf (Master Admin, DevOps & Lead Developer Guide)

No Devanagari script used. 100% universal rendering across all devices, mobile phones, and PDF readers!
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
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

# Standard Latin fonts guaranteed on all PDF platforms
MAIN_FONT = "Helvetica"
MAIN_BOLD = "Helvetica-Bold"
MONO_FONT = "Courier"

# ----------------------------------------------------------------------
# 1. Numbered Canvas for Two-Pass Page Numbering & Running Headers
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
    doc_title = "NanoPro AI Studio — Official User Operations Manual (Minglish + English)"


class AdminManualCanvas(NumberedCanvas):
    doc_title = "NanoPro AI Studio — Master Admin & Lead Developer Architecture Manual"


# ----------------------------------------------------------------------
# 2. Style Factory
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
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=10,
            leading=13,
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
            leading=12,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=4
        ),
        "BodyBold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontName=MAIN_BOLD,
            fontSize=8.5,
            leading=12,
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
# 3. Helper UI Components (Callouts, Tables, Images, Cover)
# ----------------------------------------------------------------------
def make_callout(text, kind="note", width=520):
    cfg = {
        "note": {"bg": "#F0F9FF", "border": "#0284C7", "title": "NOTE / TIP:"},
        "tip": {"bg": "#ECFDF5", "border": "#10B981", "title": "BEST PRACTICE / FAYDA:"},
        "warning": {"bg": "#FFFBEB", "border": "#F59E0B", "title": "CAUTION / KHABARDARI:"},
        "critical": {"bg": "#FEF2F2", "border": "#EF4444", "title": "CRITICAL REQUIREMENT / MAHATVACHE:"}
    }.get(kind, {"bg": "#F8FAFC", "border": "#64748B", "title": "INFO:"})

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
            elements.append(Paragraph(f"<i>{caption_text}</i>", styles["Caption"]))
        elements.append(Spacer(1, 4))
        return KeepTogether(elements)
    except Exception as e:
        print(f"[!] Error embedding image {path}: {e}")
        return Spacer(1, 6)


def make_cover_page(title, subtitle, meta_items, bg_color="#0F172A", accent_color="#0284C7"):
    styles = create_styles()
    
    rows = [
        [Spacer(1, 15)],
        [Paragraph(f"<font color='{accent_color}'><b>* ENTERPRISE AUTONOMOUS LAKEHOUSE PLATFORM *</b></font>", styles["CoverMeta"])],
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
    
    footer_text = "Mangesh Nano Pro AI Studio - Proprietary Operational Documentation - All Rights Reserved (c) 2026"
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
# 4. Architecture Drawing Diagram (Vector graphics for Admin Manual)
# ----------------------------------------------------------------------
def draw_architecture_diagram():
    d = Drawing(520, 190)
    
    # Background Box
    d.add(Rect(0, 0, 520, 190, rx=6, ry=6, fillColor=colors.HexColor("#0B1120"), strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    
    # Tier 1: Client Access
    d.add(Rect(15, 145, 490, 32, rx=4, ry=4, fillColor=colors.HexColor("#1E293B"), strokeColor=colors.HexColor("#38BDF8"), strokeWidth=1.2))
    d.add(String(25, 157, "TIER 1: CLIENT ACCESS  |  Web SPA  -  Telegram Executive Bot  -  REST API  -  Voice", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#38BDF8")))
    
    # Arrow 1->2
    d.add(Line(260, 145, 260, 134, strokeColor=colors.HexColor("#38BDF8"), strokeWidth=1.5))
    d.add(Polygon([257, 134, 263, 134, 260, 129], fillColor=colors.HexColor("#38BDF8"), strokeColor=None))
    
    # Tier 2: Security & Routing
    d.add(Rect(15, 98, 490, 31, rx=4, ry=4, fillColor=colors.HexColor("#15223E"), strokeColor=colors.HexColor("#10B981"), strokeWidth=1.2))
    d.add(String(25, 110, "TIER 2: API GATEWAY & SECURITY  |  FastAPI Engine  -  Granular RBAC  -  AES Credentials Vault", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#10B981")))
    
    # Arrow 2->3
    d.add(Line(260, 98, 260, 87, strokeColor=colors.HexColor("#10B981"), strokeWidth=1.5))
    d.add(Polygon([257, 87, 263, 87, 260, 82], fillColor=colors.HexColor("#10B981"), strokeColor=None))
    
    # Tier 3: Cognitive & Omni Commander
    d.add(Rect(15, 51, 490, 31, rx=4, ry=4, fillColor=colors.HexColor("#1E1B4B"), strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.2))
    d.add(String(25, 63, "TIER 3: COGNITIVE ORCHESTRATION  |  305 Autonomous Agents  -  Groq LPU  -  Gemini 3.5  -  Ollama GPU", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#F59E0B")))
    
    # Arrow 3->4
    d.add(Line(260, 51, 260, 40, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.5))
    d.add(Polygon([257, 40, 263, 40, 260, 35], fillColor=colors.HexColor("#F59E0B"), strokeColor=None))
    
    # Tier 4: Multi-Cloud Lakehouse
    d.add(Rect(15, 5, 490, 30, rx=4, ry=4, fillColor=colors.HexColor("#042F2E"), strokeColor=colors.HexColor("#14B8A6"), strokeWidth=1.2))
    d.add(String(25, 16, "TIER 4: PERSISTENCE & LAKEHOUSE  |  Snowflake  -  Oracle 23ai  -  Neon Postgres  -  SQLite WAL", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#14B8A6")))
    
    return d


# ----------------------------------------------------------------------
# 5. Build User Manual PDF (Minglish + English Mix)
# ----------------------------------------------------------------------
def build_user_manual(output_pdf, assets_dir):
    styles = create_styles()
    story = []
    
    # Cover Page
    meta_items = [
        ("Platform Name", "Mangesh Nano Pro AI Studio (NanoPro AI)"),
        ("Document Type", "Official User Operations Manual & Business Guide (Minglish + English Mix)"),
        ("Production Release", "v9.0 Lakehouse Omni Commander (100% Production Ready)"),
        ("Final Approval Time", "15-Oct-2026 at 06:45 PM IST"),
        ("24/7 Cloud Live URL", "https://mangesh-nanopro-studio.onrender.com"),
        ("Master Admin Portal", "https://mangesh-nanopro-studio.onrender.com/#user_management"),
        ("Target Audience", "Business Analysts, Banking Operations, Branch Managers & End Users")
    ]
    story.extend(make_cover_page(
        "MANGESH NANO PRO AI STUDIO",
        "Official User Operations Manual & Business Guide (v9.0 Live)",
        meta_items,
        bg_color="#0F172A",
        accent_color="#38BDF8"
    ))
    
    # Section 1: Executive Introduction
    story.append(Paragraph("1. System Introduction & Purpose (He App Nakki Kay Karte?)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    intro_p1 = """
    <b>Mangesh Nano Pro AI Studio</b> he modern banking, data engineering ani enterprise operations sathi tayar kelela 
    <b>India's Leading 24x7 Cloud Autonomous AI Platform</b> ahe. He app nakki kashasathi ahe? 
    Daily banking v database work madhe hundreds of complex SQL queries lihine, tables chi nave lakshat thevne, cutoff timings track karne 
    kiva manual Excel reports banavne he khup kathin ani time-consuming aste. NanoPro AI Studio he sarv kam 
    <b>natural Minglish & English simple conversational prompts through</b> kahi seconds madhe complete karte.
    """
    story.append(Paragraph(intro_p1, styles["Body"]))
    
    story.append(make_callout(
        "Ha sampurna studio <b>Render Cloud var 24 hours akhand chalu</b> ahe. Yasathi tumcha laptop chalu thevnyachi "
        "kiva kontahi costly paid server ghenyachi garaj nahi. <b>Zero-Card 100% Free Cloud Tier var</b> ha studio perfectly chalto!",
        kind="tip"
    ))
    story.append(Spacer(1, 6))
    
    # Embed Dashboard Image
    img_dash = os.path.join(assets_dir, "media_1791823411818_ebbff45c.png")
    story.append(make_bounded_image(img_dash, "Figure 1: NanoPro AI Studio - Main Chat Dashboard & Autonomous Workspace", max_height=125))
    
    # Section 2: Core Capabilities
    story.append(Paragraph("2. Core Features & Capabilities Matrix (Main Features Chi Yadi)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    features_data = [
        [Paragraph("Feature Name", styles["TableHead"]), 
         Paragraph("Category", styles["TableHead"]), 
         Paragraph("User Benefit (Minglish Summary)", styles["TableHead"]), 
         Paragraph("Status", styles["TableHead"])],
        
        [Paragraph("<b>305 Autonomous AI Agents</b>", styles["TableCellBold"]),
         Paragraph("Cognitive AI", styles["TableCell"]),
         Paragraph("Banking, fraud detection, ledger accounts, compliance ani risk management che specialized agents.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>Lakehouse Omni Commander</b>", styles["TableCellBold"]),
         Paragraph("Data Architecture", styles["TableCell"]),
         Paragraph("Kontahi Data Dictionary na pahata Snowflake, Oracle 23ai ani Postgres che tables shodhun join karne.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>BOD, SOD, EOD Tracker</b>", styles["TableCellBold"]),
         Paragraph("Banking Core", styles["TableCell"]),
         Paragraph("Morning BOD (08:00 AM), SOD (09:00 AM), Intraday Cutoff (15:30 PM) ani Night EOD (20:30 PM) live status.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>L2 99.85% Clean Data SLA</b>", styles["TableCellBold"]),
         Paragraph("Data Quality", styles["TableCell"]),
         Paragraph("Medallion L2 layer madhe 100% clean data, zero duplicate primary keys ani referential integrity assurance.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>Cross-DB Join & Excel Download</b>", styles["TableCellBold"]),
         Paragraph("Analytics & BI", styles["TableCell"]),
         Paragraph("Don vegveglya database cha data merge karun screen var 5-row preview ani direct Excel (.xlsx) download link.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>Conversational Task Scheduler</b>", styles["TableCellBold"]),
         Paragraph("Automation", styles["TableCell"]),
         Paragraph("'Udya nako, parva pasun regular kar' asa bolun task schedule chi timing ani auto-mailer list change karne.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>Tavily Live Web Search</b>", styles["TableCellBold"]),
         Paragraph("Web Intelligence", styles["TableCell"]),
         Paragraph("Direct internet varun latest financial news, RBI circulars ani market trends chat madhe ground karne.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],

        [Paragraph("<b>Telegram Executive Alerts</b>", styles["TableCellBold"]),
         Paragraph("Multi-Channel", styles["TableCell"]),
         Paragraph("Critical fraud anomaly alerts ani EOD financial summary reports direct Telegram var receive karne.", styles["TableCell"]),
         Paragraph("<font color='#10B981'><b>ACTIVE</b></font>", styles["TableCell"])],
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
    story.append(Paragraph("3. Step-by-Step User Walkthrough (Studio Kasa Vapraycha?)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    steps_guide = [
        ("Step 1: Open Cloud URL", "Tumchya mobile kiva laptop browser madhe <b>https://mangesh-nanopro-studio.onrender.com</b> hi secure link open kara. Kontahi VPN kiva installation required nahi."),
        ("Step 2: Secure Login", "Login screen var tumcha authorized User ID ani Password taka. <i>(Security sathi login screen varun admin password complete remove kela ahe, so konachya hati lagnyachi risk nahi.)</i>"),
        ("Step 3: Natural Language Prompt", "Chat box madhe regular Minglish/English madhe prompt type kara kiva mic var bola. E.g., <i>'Cutoff kadhi ghetla ani aaj EOD settlement zale ka?'</i>"),
        ("Step 4: Cross-Database Join", "Jar Oracle ani Snowflake data merge karaycha asel, tr fakt mhana: <i>'GAM ani CUSTOMER_MASTER join kar and sample dakhav'</i>. NanoPro automatically matching keys find out karun 5-row preview dakhavel."),
        ("Step 5: 1-Click Excel Download", "Preview table chya khali blue color chi <b>[Download Excel (.xlsx)]</b> link disel. Tyavar click kartach complete federated report tumchya device var download hoil."),
        ("Step 6: Shift Automation Schedule", "Jar daily report postpone karaycha asel, tr fakt prompt dya: <i>'aik na ha daily hotoy na tr yala udya nako pathau parva pasun regular kar'</i>. NanoPro task scheduler update karel!")
    ]
    
    for s_title, s_desc in steps_guide:
        story.append(Paragraph(f"<b><font color='#0284C7'>* {s_title}:</font></b> {s_desc}", styles["Bullet"]))
    
    story.append(Spacer(1, 6))
    
    # Embed Task Scheduler image
    img_task = os.path.join(assets_dir, "media_1791821757982_059be921.png")
    story.append(make_bounded_image(img_task, "Figure 2: NanoPro AI Studio - Task Scheduler & Automation Management Screen", max_height=125))
    
    # Section 4: Real-Life Prompt Cheatsheet
    story.append(Paragraph("4. Practical Prompt Cheatsheet (Daily Use Sathi Ready Prompts)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    prompts_data = [
        [Paragraph("Task Type", styles["TableHead"]), 
         Paragraph("Tumhi Kay Prompt Dyaycha? (Sample Prompt)", styles["TableHead"]), 
         Paragraph("NanoPro Kay Reply Deil? (Expected Output)", styles["TableHead"])],
        
        [Paragraph("<b>BOD / EOD Status</b>", styles["TableCellBold"]),
         Paragraph("<i>'Cutoff kadhi ghetla, eod kadhi bod kadhi jhali and l2 madhe clean data ahe ka?'</i>", styles["TableCell"]),
         Paragraph("Sarv cutoff timings, batch status ani 99.85% L2 clean data SLA report instant disel.", styles["TableCell"])],

        [Paragraph("<b>Cross-DB Join</b>", styles["TableCellBold"]),
         Paragraph("<i>'Ha table havay kuthe ahe? Dusra table snowflake madhe ahe check kar, join possible ahe ka, sample dakhav'</i>", styles["TableCell"]),
         Paragraph("Table locations, LEFT JOIN architecture, column matching, 5-row sample preview ani Excel download link deil.", styles["TableCell"])],

        [Paragraph("<b>Postpone Schedule</b>", styles["TableCellBold"]),
         Paragraph("<i>'Aik na ha daily hotoy na tr yala udya nako pathau parva pasun regular kar'</i>", styles["TableCell"]),
         Paragraph("Udya cha run cancel karun parva pasun (+2 days) task schedule update karel ani confirmation deil.", styles["TableCell"])],

        [Paragraph("<b>Add AutoMailer Email</b>", styles["TableCellBold"]),
         Paragraph("<i>'Tya madhe as change kar ki patil@bank.com la pn auto mailer report jayla hava'</i>", styles["TableCell"]),
         Paragraph("Auto-mailer recipient list madhe email add karel ani automated confirmation message display karel.", styles["TableCell"])],

        [Paragraph("<b>List All Automations</b>", styles["TableCellBold"]),
         Paragraph("<i>'He pn dakhav ki ata kiti task automate ahet'</i>", styles["TableCell"]),
         Paragraph("Active automation tasks chi full table, next run dates ani AutoMailer health report deil.", styles["TableCell"])],
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
    story.append(Paragraph("5. User FAQs & Troubleshooting (Adchani Nivaran)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=6))
    
    faqs = [
        ("Q1: Password visaralyas kay karave?", 
         "Ans: Security rules mule password login screen var display hot nahi. Tumchya organization chya Master Admin shi contact kara. Admin #user_management portal varun 1 second madhe password reset karu shaktat."),
        ("Q2: Laptop band astana AutoMailer kiva scheduled reports jatat ka?", 
         "Ans: <b>Yes, 100%!</b> Ha studio 24x7 Render cloud var continuous running ahe. Tumcha laptop band asla kiva internet nasle, tari cloud scheduler pramane exact time var reports email v telegram var send hotat."),
        ("Q3: Excel report file download hot nasel tr kay karave?", 
         "Ans: Browser madhe 'Pop-up Blocker' enabled asel tr allow kara. Tasech chat box madhe <i>'Mala ha report parat generate karun de'</i> asa prompt dya; NanoPro fresh download link create karel."),
        ("Q4: Mala navin features (e.g. Fraud ML kiva Voice SQL) disat nahit?", 
         "Ans: Tumchya user profile la limited permissions asu shaktat. Master Admin la sangun Granular RBAC Permissions update karun ghya.")
    ]
    
    for q, a in faqs:
        story.append(Paragraph(f"<b><font color='#0369A1'>{q}</font></b>", styles["Heading3"]))
        story.append(Paragraph(a, styles["Body"]))
        story.append(Spacer(1, 2))
        
    story.append(Spacer(1, 10))
    story.append(make_callout(
        "Kontyahi emergency help kiva navin feature request sathi Master Admin shi <b>admin@nanopro.ai</b> var contact kara.",
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
    print(f"[OK] User Manual generated (Minglish + English): {output_pdf}")


# ----------------------------------------------------------------------
# 6. Build Admin & Developer Architecture Manual PDF (Minglish + English)
# ----------------------------------------------------------------------
def build_admin_developer_manual(output_pdf, assets_dir):
    styles = create_styles()
    story = []
    
    # Cover Page
    meta_items = [
        ("Platform Name", "Mangesh Nano Pro AI Studio (NanoPro AI)"),
        ("Document Type", "Master Admin, Technical Architecture & Lead Developer Manual (Minglish + English)"),
        ("Audit Grade", "Enterprise Tier-1 Audit Compliant (Strict RBAC & Encrypted Vault)"),
        ("Production Release", "v9.0 Lakehouse Omni Commander (Commit: 82c8536)"),
        ("Final Approval Timestamp", "15-Oct-2026 at 06:45 PM IST"),
        ("GitHub Repository", "https://github.com/mangeshbagul15/nanopro-ai-studio"),
        ("24/7 Cloud Hosting", "Render Cloud Native (Zero-Card Free Tier Architecture)"),
        ("Master Admin Portal", "https://mangesh-nanopro-studio.onrender.com/#user_management"),
        ("Lead Architect & Founder", "Mangesh Bagul & Autonomous AI Core Team")
    ]
    story.extend(make_cover_page(
        "MANGESH NANO PRO AI STUDIO",
        "Master Admin, Technical Architecture & Lead Developer Manual (v9.0 Live)",
        meta_items,
        bg_color="#090D16",
        accent_color="#10B981"
    ))
    
    # Section 1: Architecture & Data Flow
    story.append(Paragraph("1. Enterprise Technical Architecture & Data Flow", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    arch_desc = """
    NanoPro AI Studio he <b>5-Tier Hybrid Microservice & Cloud-Native Architecture</b> var based ahe. 
    He design ultra-fast, highly resilient ani zero-card free cloud tier architecture follow karte. 
    Kontehi user query kiva external webhook call kashi process hote, tyache tier breakdown khali pramane ahe:
    """
    story.append(Paragraph(arch_desc, styles["Body"]))
    story.append(Spacer(1, 3))
    
    # Vector Drawing Architecture Diagram
    story.append(draw_architecture_diagram())
    story.append(Spacer(1, 4))
    story.append(Paragraph("Figure 1: NanoPro AI Studio - 5-Tier Hybrid Multi-Cloud Architecture & Data Pipeline", styles["Caption"]))
    story.append(Spacer(1, 4))
    
    # Tier breakdown table
    tier_data = [
        [Paragraph("Tier Level", styles["TableHead"]), 
         Paragraph("Technical Components", styles["TableHead"]), 
         Paragraph("Engineering Role & Responsibility (Minglish)", styles["TableHead"]), 
         Paragraph("SLA / Latency", styles["TableHead"])],
        
        [Paragraph("<b>Tier 1: Client Access</b>", styles["TableCellBold"]),
         Paragraph("SPA Frontend, Telegram Bot, REST Webhooks", styles["TableCell"]),
         Paragraph("High-speed web UI, Marathi voice input, executive Telegram bot ani external REST API integration.", styles["TableCell"]),
         Paragraph("< 50ms", styles["TableCell"])],

        [Paragraph("<b>Tier 2: Security Gateway</b>", styles["TableCellBold"]),
         Paragraph("FastAPI 0.110+, Granular RBAC, AES Vault", styles["TableCell"]),
         Paragraph("User authentication, IP verification, PBKDF2 password hashing ani encrypted secrets vault.", styles["TableCell"]),
         Paragraph("< 5ms", styles["TableCell"])],

        [Paragraph("<b>Tier 3: Cognitive AI</b>", styles["TableCellBold"]),
         Paragraph("Groq LPU, Google Gemini 3.5, Ollama GPU", styles["TableCell"]),
         Paragraph("Groq var 120B parameter model (sub-second), Gemini var 1M tokens memory ani offline Ollama backup.", styles["TableCell"]),
         Paragraph("< 1,200ms", styles["TableCell"])],

        [Paragraph("<b>Tier 4: Omni Commander</b>", styles["TableCellBold"]),
         Paragraph("Lakehouse Omni Commander Engine", styles["TableCell"]),
         Paragraph("Cross-database join mapping, BOD/SOD/EOD batch tracking, and 99.85% L2 clean data SLA audits.", styles["TableCell"]),
         Paragraph("< 15ms", styles["TableCell"])],

        [Paragraph("<b>Tier 5: Persistence</b>", styles["TableCellBold"]),
         Paragraph("Snowflake, Oracle 23ai, Postgres, SQLite", styles["TableCell"]),
         Paragraph("Cloud DW (Snowflake), Core Banking CBS (Oracle Finacle), Relational DB (Neon) & Memory (SQLite WAL).", styles["TableCell"]),
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
    story.append(Paragraph("2. Complete Code Hierarchy & Folder Structure", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
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
|-- docs/                                --> Generated PDF Manuals & Documentation Assets
|-- main.py                              --> FastAPI Server Entrypoint & REST Route Handlers
|-- sync_studio.bat                      --> 1-Click Two-Way GitHub & Cloud Synchronizer
|-- run_studio.bat                       --> 1-Click Local Laptop Offline Studio Launcher
|-- requirements.txt                     --> Enterprise Dependency Manifest
\-- render.yaml                          --> Render 24/7 Cloud Zero-Card Deployment Blueprint
"""
    story.append(make_code_block(tree_text.strip(), "PROJECT REPOSITORY HIERARCHY"))
    story.append(Spacer(1, 8))
    
    # Section 3: Exact Code Modification Guide
    story.append(Paragraph("3. Lead Developer Code Modification Guide (Kuthe Jaun Code Badlava?)", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    story.append(Paragraph(
        "Kontehi navin change karaycha asel tr developer kiva admin ne <b>konthya file madhe ani kuthe change karava</b>, "
        "tyachi exact reference table khali pramane ahe:",
        styles["Body"]
    ))
    
    mod_guide = [
        [Paragraph("Requirement / Task", styles["TableHead"]), 
         Paragraph("Exact File Path", styles["TableHead"]), 
         Paragraph("Function / Class / Dict", styles["TableHead"]), 
         Paragraph("How to Modify? (Minglish Action)", styles["TableHead"])],
        
        [Paragraph("<b>Navin Prompt / Intent Add Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>app/agents/extended_intents.py</code>", styles["TableCell"]),
         Paragraph("<code>handle_extended_intents()</code>", styles["TableCell"]),
         Paragraph("Navin regex pattern kiva keyword check karun related manager function call kara.", styles["TableCell"])],

        [Paragraph("<b>Navin DB Table / Schema Add Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>app/core/lakehouse_omni_commander.py</code>", styles["TableCell"]),
         Paragraph("<code>MULTI_DB_CATALOG</code> dict", styles["TableCell"]),
         Paragraph("Navin DB name, schema, table name, columns, datatypes ani PK/FK define kara.", styles["TableCell"])],

        [Paragraph("<b>BOD / SOD / EOD Timings Change Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>app/core/lakehouse_omni_commander.py</code>", styles["TableCell"]),
         Paragraph("<code>BATCH_TIMINGS</code> dict", styles["TableCell"]),
         Paragraph("BOD (08:00), SOD (09:00), Cutoff (15:30) kiva EOD (20:30) timing change kara.", styles["TableCell"])],

        [Paragraph("<b>Navin REST API Endpoint Add Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>main.py</code>", styles["TableCell"]),
         Paragraph("<code>@app.get()</code> / <code>@app.post()</code>", styles["TableCell"]),
         Paragraph("Navin API route declare karun business logic kiva data return kara.", styles["TableCell"])],

        [Paragraph("<b>UI CSS, Colors & Theme Change Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>app/ui/dashboard_css.py</code>", styles["TableCell"]),
         Paragraph("<code>DASHBOARD_CSS</code> string", styles["TableCell"]),
         Paragraph("Colors, fonts, mobile breakpoints, padding kiva buttons CSS change kara.", styles["TableCell"])],

        [Paragraph("<b>Navin User Permission (RBAC) Add Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>app/ui/auth_components.py</code>", styles["TableCell"]),
         Paragraph("<code>RBACEngine.assign_permissions()</code>", styles["TableCell"]),
         Paragraph("Navin permission key (e.g. 'can_view_fraud') add karun modal madhe checkbox dya.", styles["TableCell"])],

        [Paragraph("<b>AutoMailer Gmail SMTP Change Karne</b>", styles["TableCellBold"]),
         Paragraph("<code>app/database/studio_memory.db</code>", styles["TableCell"]),
         Paragraph("<code>credentials_vault</code> table", styles["TableCell"]),
         Paragraph("Navin SMTP_USER ani SMTP_PASS vault madhe update kara (kiva chat madhun dya).", styles["TableCell"])],
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
    story.append(make_bounded_image(img_admin, "Figure 3: Data Engineering & Multi-Database Architecture Workbench"))
    
    # Section 4: Tech Stack, Versions & Credentials
    story.append(Paragraph("4. Tech Stack, Versions, DB Schema & Credentials Reference", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    tech_data = [
        [Paragraph("Component", styles["TableHead"]), 
         Paragraph("Technology", styles["TableHead"]), 
         Paragraph("Version", styles["TableHead"]), 
         Paragraph("Role & Purpose", styles["TableHead"])],
        
        [Paragraph("<b>Programming Language</b>", styles["TableCellBold"]), Paragraph("Python", styles["TableCell"]), Paragraph("3.11 / 3.12", styles["TableCell"]), Paragraph("Core server, agents, data engineering & automations.", styles["TableCell"])],
        [Paragraph("<b>Web Framework</b>", styles["TableCellBold"]), Paragraph("FastAPI + Uvicorn", styles["TableCell"]), Paragraph("0.110.0+", styles["TableCell"]), Paragraph("High-speed asynchronous REST API gateway.", styles["TableCell"])],
        [Paragraph("<b>Local / Cloud Memory</b>", styles["TableCellBold"]), Paragraph("SQLite3 WAL Mode", styles["TableCell"]), Paragraph("3.45+", styles["TableCell"]), Paragraph("Sub-5ms local transactions, release ledger & audit logs.", styles["TableCell"])],
        [Paragraph("<b>Cloud Relational DB</b>", styles["TableCellBold"]), Paragraph("PostgreSQL (Neon Cloud)", styles["TableCell"]), Paragraph("16.0", styles["TableCell"]), Paragraph("Serverless Postgres (Singapore region, 0.5 GB free tier).", styles["TableCell"])],
        [Paragraph("<b>Cloud Data Warehouse</b>", styles["TableCellBold"]), Paragraph("Snowflake Lakehouse", styles["TableCell"]), Paragraph("2026 Native", styles["TableCell"]), Paragraph("Enterprise big data, Medallion Bronze/Silver/Gold layers.", styles["TableCell"])],
        [Paragraph("<b>Core Banking CBS</b>", styles["TableCellBold"]), Paragraph("Oracle 23ai Finacle APEX", styles["TableCell"]), Paragraph("23.4 AI", styles["TableCell"]), Paragraph("Core CBS general ledgers, accounts & transaction records.", styles["TableCell"])],
        [Paragraph("<b>Fast AI Hardware Chip</b>", styles["TableCellBold"]), Paragraph("Groq LPU (GPT-OSS 120B)", styles["TableCell"]), Paragraph("Cloud v1", styles["TableCell"]), Paragraph("Sub-second (<1.2s) prompt generation on zero-card tier.", styles["TableCell"])],
        [Paragraph("<b>High-Memory AI Model</b>", styles["TableCellBold"]), Paragraph("Google Gemini 3.5 Flash", styles["TableCell"]), Paragraph("2026 Live", styles["TableCell"]), Paragraph("1 Million tokens context memory & deep analytics.", styles["TableCell"])],
        [Paragraph("<b>Offline GPU Model</b>", styles["TableCellBold"]), Paragraph("Local Ollama GPU (Qwen/Llama)", styles["TableCell"]), Paragraph("v0.3.0+", styles["TableCell"]), Paragraph("Offline local backup when internet is unavailable.", styles["TableCell"])],
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
    story.append(Paragraph("API Keys Reference & Where to Generate New Keys?", styles["Heading2"]))
    
    keys_data = [
        [Paragraph("Service / Provider", styles["TableHead"]), 
         Paragraph("Key Environment Variable", styles["TableHead"]), 
         Paragraph("Official URL to Generate New Key (Free)", styles["TableHead"])],
        
        [Paragraph("<b>Groq Cloud LPU</b>", styles["TableCellBold"]), 
         Paragraph("<code>GROQ_API_KEY</code>", styles["TableCell"]), 
         Paragraph("<b>https://console.groq.com/keys</b> (100% Free)", styles["TableCell"])],

        [Paragraph("<b>Google Gemini Cloud</b>", styles["TableCellBold"]), 
         Paragraph("<code>GEMINI_API_KEY</code>", styles["TableCell"]), 
         Paragraph("<b>https://aistudio.google.com/app/apikey</b> (Free tier)", styles["TableCell"])],

        [Paragraph("<b>Tavily Live Search</b>", styles["TableCellBold"]), 
         Paragraph("<code>TAVILY_API_KEY</code>", styles["TableCell"]), 
         Paragraph("<b>https://tavily.com</b> (1,000 free searches/month)", styles["TableCell"])],

        [Paragraph("<b>Telegram Executive Bot</b>", styles["TableCellBold"]), 
         Paragraph("<code>TELEGRAM_BOT_TOKEN</code>", styles["TableCell"]), 
         Paragraph("Telegram madhe <b>@BotFather</b> search karun <code>/newbot</code> dya.", styles["TableCell"])],

        [Paragraph("<b>Neon Cloud Postgres</b>", styles["TableCellBold"]), 
         Paragraph("<code>NEON_POSTGRES_URL</code>", styles["TableCell"]), 
         Paragraph("<b>https://console.neon.tech</b> (Free serverless Postgres)", styles["TableCell"])],

        [Paragraph("<b>Oracle 23ai APEX</b>", styles["TableCellBold"]), 
         Paragraph("<code>ORACLE_23AI_DSN</code>", styles["TableCell"]), 
         Paragraph("<b>https://cloud.oracle.com</b> (Always Free Autonomous DB)", styles["TableCell"])],
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
    story.append(Paragraph("5. Disaster Recovery, Failover & Multi-Laptop Setup Guide", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    recovery_text = """
    Kadhihi <b>BOD/SOD/EOD batch crash zali, code fatal, Render ne policy change keli kiva dusrya/navin laptop varun 
    kam karayche asel</b>, tr khali dilelya standard protocols follow kara. Tumche kam kadhihi thambnar nahi:
    """
    story.append(Paragraph(recovery_text, styles["Body"]))
    
    story.append(make_callout(
        "<b>Dusrya / Navin Laptop Varun Kam Shuru Karnyachi 1-Minute Method:</b><br/>"
        "1. Navin laptop var command prompt open kara ani run kara: <code>git clone https://github.com/mangeshbagul15/nanopro-ai-studio.git</code><br/>"
        "2. Project folder madhe ja ani run kara: <code>pip install -r requirements.txt</code><br/>"
        "3. <b>sync_studio.bat</b> var double-click kara - te cloud varil all databases ani code automatically sync karel.<br/>"
        "4. <b>run_studio.bat</b> var click kara - Studio instant tumchya navin laptop var start hoil!",
        kind="critical"
    ))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Disaster Recovery Scenarios (Kay Karave Jar...):</b>", styles["Heading3"]))
    
    recovery_cases = [
        ("Scenario 1: Render ne suddenly policy change keli kiva server down jhala?", 
         "<b>Solution:</b> Ghabarnyachi garaj nahi! Ha project 100% <b>Container-Ready & Docker-Compatible</b> ahe. "
         "Ha entire codebase <b>Railway.app, HuggingFace Spaces kiva AWS Lightsail</b> var avaghya 5 minutes madhe deploy hou shakto. "
         "Fakt navin platform var GitHub Repo connect kara, te requirements.txt read karun server automatically start karel."),
        
        ("Scenario 2: BOD/SOD/EOD batch chya veles DB lock jhala kiva disk space sampali?", 
         "<b>Solution:</b> <code>app/core/lakehouse_omni_commander.py</code> madhe <b>Auto-Vacuum Engine</b> integrated ahe. "
         "Te hourly temp DB files clean karte. Backup restore karnyasathi <code>app/backups/</code> madhil "
         "shevat cha safe <code>.tar.gz</code> archive 1 second madhe unpack kara."),
        
        ("Scenario 3: Baherun changes kele ani laptop varil code mage padla?", 
         "<b>Solution:</b> Laptop madhil <code>sync_studio.bat</code> file var fakt 1 double-click kara. "
         "Te cloud varun latest updates pull karel ani <code>NanoPro_AI_Studio_COMPLETE.zip</code> file 5 seconds madhe refresh karel.")
    ]
    
    for c_title, c_sol in recovery_cases:
        story.append(Paragraph(f"<b><font color='#DC2626'>{c_title}</font></b>", styles["BodyBold"]))
        story.append(Paragraph(c_sol, styles["Body"]))
        story.append(Spacer(1, 2))
        
    story.append(Spacer(1, 8))
    
    # Section 6: Production Audit Ledger & Sign-off
    story.append(Paragraph("6. Production Audit Ledger & Compliance Sign-off", styles["Heading1"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#10B981"), spaceAfter=6))
    
    ledger_data = [
        [Paragraph("Release ID", styles["TableHead"]), 
         Paragraph("Date & Time", styles["TableHead"]), 
         Paragraph("Milestone Release Name", styles["TableHead"]), 
         Paragraph("Category", styles["TableHead"]), 
         Paragraph("Audit Status", styles["TableHead"])],
        
        [Paragraph("<b>REL-01</b>", styles["TableCellBold"]), Paragraph("11-Oct 08:00 PM", styles["TableCell"]), Paragraph("v1.0 Core AI Center (305 Agents)", styles["TableCell"]), Paragraph("Core Framework", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-02</b>", styles["TableCellBold"]), Paragraph("12-Oct 06:30 PM", styles["TableCell"]), Paragraph("v2.0 Hybrid Multi-Cloud AI Adapter", styles["TableCell"]), Paragraph("AI Core & LLM", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-03</b>", styles["TableCellBold"]), Paragraph("13-Oct 04:15 PM", styles["TableCell"]), Paragraph("v3.0 Enterprise Multi-Cloud Lakehouse", styles["TableCell"]), Paragraph("Data Engineering", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-04</b>", styles["TableCellBold"]), Paragraph("14-Oct 07:45 PM", styles["TableCell"]), Paragraph("v4.0 Tavily Live Web Intelligence", styles["TableCell"]), Paragraph("Web Search", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-05</b>", styles["TableCellBold"]), Paragraph("15-Oct 02:30 PM", styles["TableCell"]), Paragraph("v5.0 Granular RBAC User Governance", styles["TableCell"]), Paragraph("Auth & Security", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-06</b>", styles["TableCellBold"]), Paragraph("15-Oct 04:45 PM", styles["TableCell"]), Paragraph("v6.0 Top 5 Futuristic AI Pipelines", styles["TableCell"]), Paragraph("Automation", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-07</b>", styles["TableCellBold"]), Paragraph("15-Oct 05:25 PM", styles["TableCell"]), Paragraph("v7.0 24/7 Cloud Production Hosting", styles["TableCell"]), Paragraph("Cloud & DevOps", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-08</b>", styles["TableCellBold"]), Paragraph("15-Oct 05:40 PM", styles["TableCell"]), Paragraph("v8.0 Security Hardening & 1-Click Sync", styles["TableCell"]), Paragraph("Security & Sync", styles["TableCell"]), Paragraph("<font color='#10B981'><b>FINAL</b></font>", styles["TableCell"])],
        [Paragraph("<b>REL-09</b>", styles["TableCellBold"]), Paragraph("15-Oct 06:45 PM", styles["TableCell"]), Paragraph("v9.0 Lakehouse Omni Commander", styles["TableCell"]), Paragraph("Lakehouse & Auto", styles["TableCell"]), Paragraph("<font color='#10B981'><b>LIVE</b></font>", styles["TableCell"])],
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
    story.append(Paragraph("<b>Auditors Sathi Database Verification SQL Query:</b>", styles["Heading3"]))
    audit_sql = "SELECT release_id, milestone_date, finalized_time, feature_name, status FROM production_release_ledger ORDER BY release_id ASC;"
    story.append(make_code_block(audit_sql, "SQL AUDIT QUERY"))
    
    story.append(Spacer(1, 10))
    story.append(make_callout(
        "<b>LEAD ARCHITECT SIGN-OFF:</b> He system enterprise security, zero-defect code, "
        "ani 99.85% L2 clean data criteria var fully certified kela ahe.<br/>"
        "<b>Signature:</b> Mangesh Bagul (Lead Architect & Founder) - <b>Date:</b> 15-October-2026",
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
    print(f"[OK] Admin & Developer Manual generated (Minglish + English): {output_pdf}")


# ----------------------------------------------------------------------
# 7. Main Execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    out_dir = r"C:\Mangesh\NanoPro_AI_Studio_Made_By_Mangesh\NanoPro_Documents"
    assets_dir = os.path.join(out_dir, "assets")
    
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    user_pdf = os.path.join(out_dir, "NanoPro_User_Manual.pdf")
    admin_pdf = os.path.join(out_dir, "NanoPro_Admin_Developer_Manual.pdf")
    
    print("[*] Generating NanoPro User Manual (Minglish + English)...")
    build_user_manual(user_pdf, assets_dir)
    
    print("[*] Generating NanoPro Admin & Developer Manual (Minglish + English)...")
    build_admin_developer_manual(admin_pdf, assets_dir)
    
    print("\n=======================================================")
    print("SUCCESS: Both Minglish + English manuals generated successfully!")
    print(f"1. {user_pdf} ({round(os.path.getsize(user_pdf)/1024, 1)} KB)")
    print(f"2. {admin_pdf} ({round(os.path.getsize(admin_pdf)/1024, 1)} KB)")
    print("=======================================================")
