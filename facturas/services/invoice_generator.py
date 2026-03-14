"""
Generador de facturas PDF conforme a RD 1619/2012 (AEAT).
Requiere: reportlab
"""
import io
import base64
from datetime import date
from typing import List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT


# ── Colores corporativos ───────────────────────────────────────────────────────
COLOR_HEADER  = colors.HexColor("#1a3a5c")
COLOR_ACCENT  = colors.HexColor("#2563eb")
COLOR_LIGHT   = colors.HexColor("#f1f5f9")
COLOR_BORDER  = colors.HexColor("#e2e8f0")
COLOR_TEXT    = colors.HexColor("#1e293b")
COLOR_MUTED   = colors.HexColor("#64748b")


def _eur(amount: float) -> str:
    return f"{amount:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_invoice_pdf(data: dict) -> dict:
    """
    Genera una factura PDF y devuelve {pdf_base64, invoice_number, totals}.
    data dict keys: invoice, issuer, client, lines, taxes, options
    """
    inv     = data.get("invoice", {})
    issuer  = data.get("issuer", {})
    client  = data.get("client", {})
    lines   = data.get("lines", [])
    taxes   = data.get("taxes", {})
    options = data.get("options", {})

    series = inv.get("series", "A")
    number = inv.get("number", 1)
    invoice_number = f"{series}-{str(number).zfill(4)}"
    invoice_date   = inv.get("date", str(date.today()))
    due_date       = inv.get("due_date", "")
    currency       = inv.get("currency", "EUR")

    irpf_rate = taxes.get("irpf_rate", 0)
    notes     = options.get("notes", "")
    watermark = options.get("watermark", False)

    # ── Calcular totales ───────────────────────────────────────────────────────
    computed_lines = []
    subtotal_base  = 0.0
    iva_breakdown  = {}  # rate -> amount

    for line in lines:
        qty        = float(line.get("quantity", 1))
        unit_price = float(line.get("unit_price", 0))
        iva_rate   = float(line.get("iva_rate", 21))
        discount   = float(line.get("discount", 0))
        desc       = line.get("description", "")

        base = round(qty * unit_price * (1 - discount / 100), 2)
        iva_amount = round(base * iva_rate / 100, 2)

        subtotal_base += base
        iva_breakdown[iva_rate] = round(iva_breakdown.get(iva_rate, 0) + iva_amount, 2)

        computed_lines.append({
            "description": desc,
            "quantity": qty,
            "unit_price": unit_price,
            "discount": discount,
            "iva_rate": iva_rate,
            "base": base,
            "iva_amount": iva_amount,
        })

    subtotal_base  = round(subtotal_base, 2)
    total_iva      = round(sum(iva_breakdown.values()), 2)
    irpf_amount    = round(subtotal_base * irpf_rate / 100, 2)
    total_invoice  = round(subtotal_base + total_iva - irpf_amount, 2)

    # ── Construir PDF ──────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle("normal", fontName="Helvetica", fontSize=9, textColor=COLOR_TEXT, leading=13)
    style_small  = ParagraphStyle("small",  fontName="Helvetica", fontSize=8, textColor=COLOR_MUTED, leading=11)
    style_bold   = ParagraphStyle("bold",   fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_TEXT)
    style_title  = ParagraphStyle("title",  fontName="Helvetica-Bold", fontSize=22, textColor=COLOR_HEADER)
    style_right  = ParagraphStyle("right",  fontName="Helvetica", fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT)
    style_right_bold = ParagraphStyle("right_bold", fontName="Helvetica-Bold", fontSize=10, textColor=COLOR_TEXT, alignment=TA_RIGHT)
    style_center = ParagraphStyle("center", fontName="Helvetica", fontSize=8, textColor=COLOR_MUTED, alignment=TA_CENTER)

    story = []

    # ── Cabecera: emisor + título FACTURA ──────────────────────────────────────
    issuer_text = f"<b>{issuer.get('name', '')}</b><br/>"
    if issuer.get("nif"):     issuer_text += f"NIF: {issuer['nif']}<br/>"
    if issuer.get("address"): issuer_text += f"{issuer['address']}<br/>"
    if issuer.get("city") or issuer.get("postal_code"):
        issuer_text += f"{issuer.get('postal_code','')} {issuer.get('city','')} {issuer.get('province','')}<br/>".strip()
    if issuer.get("email"):   issuer_text += f"{issuer['email']}"

    header_data = [
        [
            Paragraph(issuer_text, style_normal),
            Paragraph("FACTURA", style_title),
        ]
    ]
    header_table = Table(header_data, colWidths=[100*mm, 80*mm])
    header_table.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("ALIGN",       (1, 0), (1, 0),   "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_ACCENT, spaceAfter=6))

    # ── Datos factura + datos cliente ──────────────────────────────────────────
    invoice_info = (
        f"<b>Nº Factura:</b> {invoice_number}<br/>"
        f"<b>Fecha emisión:</b> {invoice_date}<br/>"
        + (f"<b>Vencimiento:</b> {due_date}<br/>" if due_date else "")
        + f"<b>Moneda:</b> {currency}"
    )

    client_text = f"<b>CLIENTE</b><br/>"
    client_text += f"<b>{client.get('name', '')}</b><br/>"
    if client.get("nif"):     client_text += f"NIF/CIF: {client['nif']}<br/>"
    if client.get("address"): client_text += f"{client['address']}<br/>"
    if client.get("city"):    client_text += f"{client.get('postal_code','')} {client.get('city','')}"

    info_data = [
        [
            Paragraph(invoice_info, style_normal),
            Paragraph(client_text, style_normal),
        ]
    ]
    info_table = Table(info_data, colWidths=[90*mm, 90*mm])
    info_table.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("BACKGROUND",    (0,0), (0,0),   COLOR_LIGHT),
        ("BACKGROUND",    (1,0), (1,0),   COLOR_LIGHT),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ("BOX",           (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    story.append(Spacer(1, 4*mm))
    story.append(info_table)
    story.append(Spacer(1, 6*mm))

    # ── Líneas de factura ──────────────────────────────────────────────────────
    lines_header = ["Descripción", "Cant.", "Precio unit.", "Dto.%", "IVA%", "Base imp."]
    lines_rows = [lines_header]

    for l in computed_lines:
        lines_rows.append([
            Paragraph(l["description"], style_normal),
            f"{l['quantity']:g}",
            _eur(l["unit_price"]),
            f"{l['discount']:g}%" if l["discount"] else "—",
            f"{l['iva_rate']:g}%",
            _eur(l["base"]),
        ])

    col_widths = [74*mm, 15*mm, 24*mm, 14*mm, 14*mm, 23*mm]
    lines_table = Table(lines_rows, colWidths=col_widths, repeatRows=1)
    lines_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),   COLOR_HEADER),
        ("TEXTCOLOR",     (0,0), (-1,0),   colors.white),
        ("FONTNAME",      (0,0), (-1,0),   "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1),  8),
        ("ALIGN",         (1,0), (-1,-1),  "RIGHT"),
        ("ALIGN",         (0,0), (0,-1),   "LEFT"),
        ("VALIGN",        (0,0), (-1,-1),  "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
        ("GRID",          (0,0), (-1,-1),  0.3, COLOR_BORDER),
        ("LEFTPADDING",   (0,0), (-1,-1),  5),
        ("RIGHTPADDING",  (0,0), (-1,-1),  5),
        ("TOPPADDING",    (0,0), (-1,-1),  4),
        ("BOTTOMPADDING", (0,0), (-1,-1),  4),
    ]))
    story.append(lines_table)
    story.append(Spacer(1, 4*mm))

    # ── Totales ────────────────────────────────────────────────────────────────
    totals_rows = []
    totals_rows.append(["Base imponible:", _eur(subtotal_base)])

    for rate, amount in sorted(iva_breakdown.items()):
        totals_rows.append([f"IVA {rate:g}%:", _eur(amount)])

    if irpf_rate:
        totals_rows.append([f"Retención IRPF {irpf_rate}%:", f"- {_eur(irpf_amount)}"])

    totals_rows.append(["TOTAL A PAGAR:", _eur(total_invoice)])

    totals_table = Table(totals_rows, colWidths=[45*mm, 30*mm])
    totals_style = [
        ("FONTSIZE",      (0,0), (-1,-1),  9),
        ("ALIGN",         (1,0), (1,-1),   "RIGHT"),
        ("ALIGN",         (0,0), (0,-1),   "RIGHT"),
        ("LEFTPADDING",   (0,0), (-1,-1),  5),
        ("RIGHTPADDING",  (0,0), (-1,-1),  5),
        ("TOPPADDING",    (0,0), (-1,-1),  3),
        ("BOTTOMPADDING", (0,0), (-1,-1),  3),
        ("LINEABOVE",     (0,-1), (-1,-1), 1.5, COLOR_ACCENT),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,-1), (-1,-1), 10),
        ("BACKGROUND",    (0,-1), (-1,-1), COLOR_LIGHT),
    ]
    totals_table.setStyle(TableStyle(totals_style))

    # Alinear totales a la derecha
    totals_container = Table([[None, totals_table]], colWidths=[110*mm, 75*mm])
    totals_container.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(totals_container)

    # ── Notas / desglose IVA (obligatorio AEAT) ────────────────────────────────
    if notes or watermark:
        story.append(Spacer(1, 6*mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 3*mm))

    if notes:
        story.append(Paragraph(f"<b>Notas:</b> {notes}", style_small))

    if watermark:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("★ DEMO — Generado con Spanish Invoice PDF Generator API", style_center))

    # ── Footer legal ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.3, color=COLOR_BORDER))
    story.append(Spacer(1, 2*mm))
    footer_text = (
        "Factura emitida conforme al Real Decreto 1619/2012, de 30 de noviembre, "
        "por el que se aprueba el Reglamento por el que se regulan las obligaciones de facturación."
    )
    story.append(Paragraph(footer_text, style_center))

    doc.build(story)
    pdf_bytes = buf.getvalue()

    return {
        "success": True,
        "invoice_number": invoice_number,
        "date": invoice_date,
        "subtotal": subtotal_base,
        "iva_breakdown": {f"iva_{int(k)}": v for k, v in iva_breakdown.items()},
        "iva_total": total_iva,
        "irpf_rate": irpf_rate,
        "irpf_amount": irpf_amount,
        "total": total_invoice,
        "pdf_base64": base64.b64encode(pdf_bytes).decode(),
        "pdf_size_kb": round(len(pdf_bytes) / 1024, 1),
    }


def calculate_totals(data: dict) -> dict:
    """Calcula totales sin generar PDF."""
    lines  = data.get("lines", [])
    taxes  = data.get("taxes", {})
    irpf_rate = taxes.get("irpf_rate", 0)

    subtotal = 0.0
    iva_breakdown = {}

    for line in lines:
        qty        = float(line.get("quantity", 1))
        unit_price = float(line.get("unit_price", 0))
        iva_rate   = float(line.get("iva_rate", 21))
        discount   = float(line.get("discount", 0))

        base       = round(qty * unit_price * (1 - discount / 100), 2)
        iva_amount = round(base * iva_rate / 100, 2)

        subtotal += base
        iva_breakdown[iva_rate] = round(iva_breakdown.get(iva_rate, 0) + iva_amount, 2)

    subtotal      = round(subtotal, 2)
    total_iva     = round(sum(iva_breakdown.values()), 2)
    irpf_amount   = round(subtotal * irpf_rate / 100, 2)
    total_invoice = round(subtotal + total_iva - irpf_amount, 2)

    return {
        "subtotal": subtotal,
        "iva_breakdown": {f"iva_{int(k)}": v for k, v in iva_breakdown.items()},
        "iva_total": total_iva,
        "irpf_rate": irpf_rate,
        "irpf_amount": irpf_amount,
        "total": total_invoice,
    }
