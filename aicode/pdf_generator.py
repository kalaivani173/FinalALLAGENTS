"""
PDF Generator for NPCI Product Kit
Generates PDFs matching the official NPCI circular template format.
Sections: Circular, Product Note, Tech Specs, Test Cases, XSD, Sample Payloads
"""

import os
import json
import io
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Preformatted, Image as RLImage
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Paths ─────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parent
_LOGO_PATH = str(_BASE / "artifacts" / "npci_logo.jpeg")
_LOGO_EXISTS = os.path.isfile(_LOGO_PATH)

# ── Colours matching NPCI brand ───────────────────────────
NPCI_PURPLE = colors.HexColor("#4B0082")
NPCI_DARK   = colors.HexColor("#1A1A2E")
NPCI_GRAY   = colors.HexColor("#666666")
NPCI_LIGHT  = colors.HexColor("#F5F5F5")
NPCI_BORDER = colors.HexColor("#CCCCCC")
GREEN_OK    = colors.HexColor("#006400")
RED_ERR     = colors.HexColor("#8B0000")
BLUE_LINK   = colors.HexColor("#003366")

PAGE_W, PAGE_H = A4
MARGIN_L = 2.2 * cm
MARGIN_R = 2.2 * cm
MARGIN_T = 2.0 * cm
MARGIN_B = 2.2 * cm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


# ── Shared styles ─────────────────────────────────────────
def _styles():
    base = getSampleStyleSheet()
    S = {}
    S["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                                leading=15, textColor=NPCI_DARK,
                                alignment=TA_JUSTIFY, spaceAfter=6)
    S["body_left"] = ParagraphStyle("body_left", fontName="Helvetica", fontSize=10,
                                    leading=15, textColor=NPCI_DARK,
                                    alignment=TA_LEFT, spaceAfter=4)
    S["bold"] = ParagraphStyle("bold", fontName="Helvetica-Bold", fontSize=10,
                                leading=14, textColor=NPCI_DARK, spaceAfter=4)
    S["h1"] = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13,
                              leading=18, textColor=NPCI_PURPLE,
                              spaceAfter=8, spaceBefore=8)
    S["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11,
                              leading=16, textColor=NPCI_DARK,
                              spaceAfter=6, spaceBefore=6,
                              underlineWidth=0.5)
    S["h3"] = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10,
                              leading=14, textColor=NPCI_PURPLE,
                              spaceAfter=4, spaceBefore=6)
    S["small"] = ParagraphStyle("small", fontName="Helvetica", fontSize=8,
                                 leading=11, textColor=NPCI_GRAY)
    S["center"] = ParagraphStyle("center", fontName="Helvetica", fontSize=10,
                                  leading=14, alignment=TA_CENTER, textColor=NPCI_DARK)
    S["center_bold"] = ParagraphStyle("center_bold", fontName="Helvetica-Bold",
                                       fontSize=11, leading=16, alignment=TA_CENTER,
                                       textColor=NPCI_DARK)
    S["code"] = ParagraphStyle("code", fontName="Courier", fontSize=8,
                                leading=12, textColor=NPCI_DARK,
                                backColor=NPCI_LIGHT, leftIndent=8,
                                rightIndent=8, spaceBefore=4, spaceAfter=4)
    S["subject"] = ParagraphStyle("subject", fontName="Helvetica-Bold", fontSize=11,
                                   leading=16, textColor=NPCI_DARK,
                                   alignment=TA_CENTER, spaceAfter=10,
                                   underline=True)
    S["right"] = ParagraphStyle("right", fontName="Helvetica", fontSize=10,
                                  alignment=TA_RIGHT, textColor=NPCI_DARK, leading=14)
    return S


# ── NPCI Header (logo + doc reference) ───────────────────
def _npci_header(story, ref_no, date_str, S):
    """Add the standard NPCI header: logo right, ref left, date right."""
    if _LOGO_EXISTS:
        try:
            logo = RLImage(_LOGO_PATH, width=3.5*cm, height=1.6*cm)
        except Exception:
            logo = Paragraph("<b>NPCI</b>", S["center_bold"])
    else:
        logo = Paragraph("<b>NPCI</b>", S["center_bold"])

    header_data = [[
        Paragraph(f"<b>{ref_no}</b>", S["body_left"]),
        logo,
    ]]
    header_table = Table(header_data, colWidths=[CONTENT_W * 0.6, CONTENT_W * 0.4])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Paragraph(f"<right>{date_str}</right>", S["right"]))
    story.append(HRFlowable(width=CONTENT_W, thickness=1.5,
                             color=NPCI_PURPLE, spaceAfter=8, spaceBefore=4))


# ── NPCI Footer callback ──────────────────────────────────
class _NPCIFooter:
    """Canvas callback that draws the NPCI address footer on every page."""
    ADDRESS = ("1001A, The Capital, B Wing, 10th Floor, Bandra Kurla Complex, "
               "Bandra (East) Mumbai – 400 051  |  Tel No: 022 4000 9100  |  "
               "Website: www.npci.org.in  |  CIN: U74899MH2008NPL180097")

    def __init__(self, doc_title="NPCI Document"):
        self.doc_title = doc_title

    def __call__(self, canv, doc):
        canv.saveState()
        canv.setFont("Helvetica", 7)
        canv.setFillColor(NPCI_GRAY)
        # Footer line
        canv.setStrokeColor(NPCI_BORDER)
        canv.setLineWidth(0.5)
        canv.line(MARGIN_L, MARGIN_B - 4 * mm, PAGE_W - MARGIN_R, MARGIN_B - 4 * mm)
        canv.drawCentredString(PAGE_W / 2, MARGIN_B - 8 * mm, self.ADDRESS)
        # Page number
        canv.drawRightString(PAGE_W - MARGIN_R, MARGIN_B - 8 * mm,
                             f"Page {doc.page}")
        canv.restoreState()


def _build_pdf(story, out_path, title="NPCI Document"):
    """Build a PDF from a story list. Returns bytes if out_path is None."""
    buf = io.BytesIO()
    footer_cb = _NPCIFooter(title)
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B + 10 * mm,
        title=title, author="NPCI – ChangeIQ",
    )
    doc.build(story, onFirstPage=footer_cb, onLaterPages=footer_cb)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════
# 1. CIRCULAR PDF
# ═══════════════════════════════════════════════════════════
def generate_circular_pdf(circular_text: str, feature_name: str,
                           cr_id: str = "", version: str = "1.0") -> bytes:
    S = _styles()
    story = []
    today = datetime.now().strftime("%B %d, %Y")
    year = datetime.now().year
    oc_num = cr_id or f"NPCI/UPI/OC/{year}/001"
    ref_no = f"NPCI/UPI/OC No. {oc_num}/{year}-{str(year+1)[2:]}"

    _npci_header(story, ref_no, today, S)
    story.append(Spacer(1, 4 * mm))

    # "To," block
    story.append(Paragraph("<b>To,</b>", S["body_left"]))
    story.append(Paragraph("All Members of Unified Payment Interface (UPI)", S["body_left"]))
    story.append(Spacer(1, 5 * mm))

    # Subject
    story.append(Paragraph(f"<u><b>Subject: {feature_name}</b></u>", S["subject"]))
    story.append(Spacer(1, 3 * mm))

    # Body — render each line of the circular text
    if circular_text:
        for para in circular_text.split("\n"):
            para = para.strip()
            if not para:
                story.append(Spacer(1, 3 * mm))
                continue
            # Section headings (numbered like "1. BACKGROUND")
            if len(para) > 2 and para[0].isdigit() and para[1] in ".)" and para[2:].strip().isupper():
                story.append(Paragraph(f"<b>{para}</b>", S["bold"]))
            elif para.startswith("Yours faithfully") or para.startswith("SD/-") or para.startswith("For and on behalf"):
                story.append(Spacer(1, 5 * mm))
                story.append(Paragraph(para, S["body_left"]))
            else:
                story.append(Paragraph(para, S["body"]))
    else:
        story.append(Paragraph("Circular content not available.", S["body"]))

    story.append(Spacer(1, 5 * mm))
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                             color=NPCI_BORDER, spaceAfter=6))

    return _build_pdf(story, None, f"NPCI Circular – {feature_name}")


# ═══════════════════════════════════════════════════════════
# 2. PRODUCT NOTE PDF
# ═══════════════════════════════════════════════════════════
def generate_product_note_pdf(product_note_text: str, feature_name: str,
                               cr_id: str = "", version: str = "1.0") -> bytes:
    S = _styles()
    story = []
    today = datetime.now().strftime("%B %d, %Y")

    # Cover header with NPCI logo centred
    if _LOGO_EXISTS:
        try:
            logo = RLImage(_LOGO_PATH, width=4.5 * cm, height=2.0 * cm)
            logo.hAlign = "CENTER"
            story.append(logo)
        except Exception:
            pass
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width=CONTENT_W, thickness=2,
                             color=NPCI_PURPLE, spaceAfter=4))
    story.append(Paragraph("NATIONAL PAYMENTS CORPORATION OF INDIA", S["center_bold"]))
    story.append(Paragraph("Unified Payments Interface", S["center"]))
    story.append(HRFlowable(width=CONTENT_W, thickness=1,
                             color=NPCI_PURPLE, spaceAfter=8))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("<b>PRODUCT NOTE</b>", S["h1"]))
    story.append(Spacer(1, 2 * mm))

    meta_data = [
        ["Feature:", feature_name],
        ["CR ID:", cr_id or "—"],
        ["Version:", version],
        ["Date:", today],
        ["Classification:", "Internal – UPI Product Team"],
    ]
    meta_table = Table(meta_data, colWidths=[3.5 * cm, CONTENT_W - 3.5 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 14),
        ("TEXTCOLOR", (0, 0), (0, -1), NPCI_PURPLE),
        ("TEXTCOLOR", (1, 0), (1, -1), NPCI_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                             color=NPCI_BORDER, spaceBefore=8, spaceAfter=8))

    # Body text
    if product_note_text:
        for para in product_note_text.split("\n"):
            para = para.strip()
            if not para:
                story.append(Spacer(1, 3 * mm))
                continue
            # Section headings
            if para and para[0].isdigit() and "." in para[:3]:
                rest = para.split(".", 1)[-1].strip()
                if rest.isupper() or rest.istitle():
                    story.append(Spacer(1, 3 * mm))
                    story.append(Paragraph(f"<b>{para}</b>", S["h2"]))
                    continue
            if para.startswith("-") or para.startswith("•"):
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{para}", S["body_left"]))
            else:
                story.append(Paragraph(para, S["body"]))
    else:
        story.append(Paragraph("Product note content not available.", S["body"]))

    return _build_pdf(story, None, f"Product Note – {feature_name}")


# ═══════════════════════════════════════════════════════════
# 3. TECHNICAL SPECIFICATIONS PDF
# ═══════════════════════════════════════════════════════════
def generate_tech_specs_pdf(tech_specs: dict, feature_name: str,
                             cr_id: str = "", version: str = "1.0") -> bytes:
    S = _styles()
    story = []
    today = datetime.now().strftime("%B %d, %Y")
    ref_no = f"NPCI/UPI/TECH/{cr_id or 'DRAFT'}"

    _npci_header(story, ref_no, today, S)
    story.append(Paragraph("<b>TECHNICAL SPECIFICATIONS</b>", S["h1"]))
    story.append(Paragraph(f"Feature: {feature_name}   |   Version: {version}   |   CR: {cr_id or '—'}",
                            S["small"]))
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                             color=NPCI_BORDER, spaceBefore=4, spaceAfter=8))

    if not tech_specs:
        story.append(Paragraph("No technical specifications available.", S["body"]))
        return _build_pdf(story, None, f"Tech Specs – {feature_name}")

    # Summary row
    api_name = tech_specs.get("api_name", "—")
    base_url = tech_specs.get("base_url", "—")
    api_ver  = tech_specs.get("version", version)
    sum_data = [["API Name", "Base URL", "API Version"],
                [api_name, base_url, api_ver]]
    _styled_table(story, sum_data, [4*cm, CONTENT_W - 7*cm, 3*cm], header=True)
    story.append(Spacer(1, 4 * mm))

    # Flow description
    flow = tech_specs.get("flow_description", "")
    if flow:
        story.append(Paragraph("<b>Transaction Flow</b>", S["h2"]))
        for line in flow.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), S["body_left"]))
        story.append(Spacer(1, 4 * mm))

    # Endpoints
    endpoints = tech_specs.get("endpoints", [])
    if endpoints:
        story.append(Paragraph(f"<b>API Endpoints ({len(endpoints)})</b>", S["h2"]))
        for ep in endpoints:
            method = ep.get("method", "POST")
            path   = ep.get("path", "—")
            desc   = ep.get("description", "")
            story.append(KeepTogether([
                Paragraph(f'<font color="#006400"><b>{method}</b></font>  '
                          f'<font face="Courier">{path}</font>', S["bold"]),
                Paragraph(desc, S["small"]),
                Spacer(1, 2 * mm),
            ]))
            # Request/Response tables side by side
            req_json  = json.dumps(ep.get("request", {}), indent=2)
            resp_json = json.dumps(ep.get("response", {}), indent=2)
            req_cell  = [Paragraph("<b>Request</b>", S["bold"]),
                         Preformatted(req_json[:600], S["code"])]
            resp_cell = [Paragraph("<b>Response</b>", S["bold"]),
                         Preformatted(resp_json[:600], S["code"])]
            ep_table  = Table([[req_cell, resp_cell]],
                               colWidths=[CONTENT_W / 2 - 3, CONTENT_W / 2 - 3])
            ep_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("BOX", (0, 0), (0, 0), 0.3, NPCI_BORDER),
                ("BOX", (1, 0), (1, 0), 0.3, NPCI_BORDER),
            ]))
            story.append(ep_table)

            # Error codes
            errs = ep.get("error_codes", [])
            if errs:
                err_data = [["Code", "HTTP", "Message"]]
                for e in errs:
                    err_data.append([e.get("code",""), str(e.get("http_status","")), e.get("message","")])
                _styled_table(story, err_data,
                               [2.5*cm, 1.8*cm, CONTENT_W - 4.3*cm], header=True)
            story.append(Spacer(1, 5 * mm))

    # Field definitions
    fields = tech_specs.get("field_definitions", [])
    if fields:
        story.append(Paragraph(f"<b>Field Definitions ({len(fields)})</b>", S["h2"]))
        fd_data = [["Field", "Type", "Mandatory", "Validation", "Description"]]
        for f in fields:
            fd_data.append([
                f.get("field", ""),
                f.get("type", ""),
                "✓ Yes" if f.get("mandatory") else "No",
                f.get("validation", "—"),
                f.get("description", ""),
            ])
        _styled_table(story, fd_data,
                       [3*cm, 3*cm, 1.8*cm, 4*cm, CONTENT_W - 11.8*cm], header=True)

    return _build_pdf(story, None, f"Technical Specifications – {feature_name}")


# ═══════════════════════════════════════════════════════════
# 4. TEST CASES PDF
# ═══════════════════════════════════════════════════════════
def generate_test_cases_pdf(test_cases: list, feature_name: str,
                             cr_id: str = "", version: str = "1.0") -> bytes:
    S = _styles()
    story = []
    today = datetime.now().strftime("%B %d, %Y")
    ref_no = f"NPCI/UPI/TEST/{cr_id or 'DRAFT'}"

    _npci_header(story, ref_no, today, S)
    story.append(Paragraph("<b>CERTIFICATION TEST CASES</b>", S["h1"]))
    story.append(Paragraph(f"Feature: {feature_name}   |   Version: {version}   |   CR: {cr_id or '—'}   |   Total: {len(test_cases)}",
                            S["small"]))
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                             color=NPCI_BORDER, spaceBefore=4, spaceAfter=8))

    # Summary stats
    pos  = sum(1 for t in test_cases if t.get("category") == "Positive")
    neg  = sum(1 for t in test_cases if t.get("category") == "Negative")
    edge = sum(1 for t in test_cases if t.get("category") == "Edge")
    sum_data = [["Category", "Count"],
                ["✓ Positive", str(pos)],
                ["✗ Negative", str(neg)],
                ["◈ Edge Cases", str(edge)],
                ["TOTAL", str(len(test_cases))]]
    _styled_table(story, sum_data, [5*cm, 3*cm], header=True)
    story.append(Spacer(1, 6 * mm))

    cat_colours = {"Positive": GREEN_OK, "Negative": RED_ERR, "Edge": colors.HexColor("#B8860B")}

    for tc in test_cases:
        tc_id    = tc.get("tc_id", "TC-?")
        category = tc.get("category", "Edge")
        title    = tc.get("title", "")
        precond  = tc.get("preconditions", "—")
        inp      = json.dumps(tc.get("input", {}), indent=2)
        exp      = json.dumps(tc.get("expected_output", {}), indent=2)
        val_pts  = tc.get("validation_points", [])

        colour = cat_colours.get(category, NPCI_DARK)
        header_cell = [
            Table([[
                Paragraph(f"<b>{tc_id}</b>", ParagraphStyle("tcid", fontName="Helvetica-Bold",
                           fontSize=10, textColor=colors.white)),
                Paragraph(f"<b>{category}</b>", ParagraphStyle("tcat", fontName="Helvetica-Bold",
                           fontSize=9, textColor=colors.white, alignment=TA_RIGHT)),
            ]], colWidths=[CONTENT_W * 0.5, CONTENT_W * 0.5])
        ]
        tc_header = Table([header_cell], colWidths=[CONTENT_W])
        tc_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colour),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        detail_data = [
            [Paragraph("<b>Title</b>", S["bold"]), Paragraph(title, S["body_left"])],
            [Paragraph("<b>Preconditions</b>", S["bold"]), Paragraph(precond, S["body_left"])],
            [Paragraph("<b>Input</b>", S["bold"]), Preformatted(inp[:400], S["code"])],
            [Paragraph("<b>Expected Output</b>", S["bold"]), Preformatted(exp[:300], S["code"])],
        ]
        if val_pts:
            vp_text = "\n".join(f"• {v}" for v in val_pts)
            detail_data.append([
                Paragraph("<b>Validations</b>", S["bold"]),
                Preformatted(vp_text, S["code"])
            ])

        detail_table = Table(detail_data, colWidths=[3.5*cm, CONTENT_W - 3.5*cm])
        detail_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, NPCI_LIGHT]),
            ("BOX", (0, 0), (-1, -1), 0.5, NPCI_BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, NPCI_BORDER),
        ]))

        story.append(KeepTogether([tc_header, detail_table, Spacer(1, 5 * mm)]))

    return _build_pdf(story, None, f"Test Cases – {feature_name}")


# ═══════════════════════════════════════════════════════════
# 5. XSD PDF
# ═══════════════════════════════════════════════════════════
def generate_xsd_pdf(xsd_text: str, feature_name: str,
                     cr_id: str = "", version: str = "1.0") -> bytes:
    S = _styles()
    story = []
    today = datetime.now().strftime("%B %d, %Y")
    ref_no = f"NPCI/UPI/XSD/{cr_id or 'DRAFT'}"

    _npci_header(story, ref_no, today, S)
    story.append(Paragraph("<b>XSD SCHEMA DEFINITION</b>", S["h1"]))
    story.append(Paragraph(f"Feature: {feature_name}   |   Version: {version}   |   CR: {cr_id or '—'}",
                            S["small"]))
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                             color=NPCI_BORDER, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("The following XML Schema Definition (XSD) defines the message structure "
                            "for the UPI API integration.", S["body"]))
    story.append(Spacer(1, 4 * mm))

    if xsd_text:
        # Split into chunks to avoid overflow
        chunk_size = 80  # chars per line
        xsd_lines = xsd_text.split("\n")
        chunk = []
        for line in xsd_lines:
            chunk.append(line)
            if len(chunk) >= 40:
                story.append(Preformatted("\n".join(chunk), S["code"]))
                story.append(Spacer(1, 2 * mm))
                chunk = []
        if chunk:
            story.append(Preformatted("\n".join(chunk), S["code"]))
    else:
        story.append(Paragraph("XSD content not available.", S["body"]))

    return _build_pdf(story, None, f"XSD Schema – {feature_name}")


# ═══════════════════════════════════════════════════════════
# 6. SAMPLE PAYLOADS PDF
# ═══════════════════════════════════════════════════════════
def generate_payloads_pdf(payloads: dict, feature_name: str,
                           cr_id: str = "", version: str = "1.0") -> bytes:
    S = _styles()
    story = []
    today = datetime.now().strftime("%B %d, %Y")
    ref_no = f"NPCI/UPI/PAYLOAD/{cr_id or 'DRAFT'}"

    _npci_header(story, ref_no, today, S)
    story.append(Paragraph("<b>SAMPLE REQUEST / RESPONSE PAYLOADS</b>", S["h1"]))
    story.append(Paragraph(f"Feature: {feature_name}   |   Version: {version}   |   CR: {cr_id or '—'}",
                            S["small"]))
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5,
                             color=NPCI_BORDER, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("The following payloads are normative samples for integration and "
                            "certification testing.", S["body"]))
    story.append(Spacer(1, 4 * mm))

    section_labels = {
        "success_request":  ("✅ Success – Request",  GREEN_OK),
        "success_response": ("✅ Success – Response", GREEN_OK),
        "error_request":    ("❌ Error – Request",    RED_ERR),
        "error_response":   ("❌ Error – Response",   RED_ERR),
    }

    for key, (label, colour) in section_labels.items():
        data = payloads.get(key, {})
        json_str = json.dumps(data, indent=2)
        lbl_style = ParagraphStyle("paylbl", fontName="Helvetica-Bold",
                                    fontSize=10, textColor=colour, spaceAfter=4)
        story.append(Paragraph(label, lbl_style))
        story.append(Preformatted(json_str[:1200], S["code"]))
        story.append(Spacer(1, 5 * mm))

    return _build_pdf(story, None, f"Sample Payloads – {feature_name}")


# ═══════════════════════════════════════════════════════════
# Helper: styled table
# ═══════════════════════════════════════════════════════════
def _styled_table(story, data, col_widths, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 13),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, NPCI_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, NPCI_BORDER),
        ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, NPCI_LIGHT]),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), NPCI_PURPLE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(style))
    story.append(t)
    story.append(Spacer(1, 2 * mm))
