"""
PDF Itinerary Generator Module
Generates a polished, professional PDF document from an ItineraryData object
using ReportLab Platypus with custom styles, tables, and page numbering.
"""

import io
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas

from .itinerary_generator import ItineraryData


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw 'Page X of Y' footers
    and standard running headers on subsequent pages.
    """
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

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6B7280"))

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 36, 25, footer_text)
        self.drawString(36, 25, "AI-Powered Travel Planner Mini-Project | Final Year Academic Demonstration")

        # Thin footer rule
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.75)
        self.line(36, 35, letter[0] - 36, 35)

        self.restoreState()


def create_itinerary_pdf(itinerary: ItineraryData) -> bytes:
    """
    Builds a professional PDF document from ItineraryData.
    Returns the binary PDF content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    # Custom palette
    primary_color = colors.HexColor("#1E3A8A")   # Deep Indigo/Navy
    secondary_color = colors.HexColor("#0D9488") # Teal
    dark_gray = colors.HexColor("#1F2937")       # Charcoal
    light_bg = colors.HexColor("#F3F4F6")        # Light gray background
    accent_green = colors.HexColor("#15803D")    # Emerald Green
    accent_red = colors.HexColor("#B91C1C")      # Crimson

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=0,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
        alignment=0,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6,
    )

    day_header_style = ParagraphStyle(
        "DayHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.white,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_gray,
    )

    body_bold = ParagraphStyle(
        "BodyBoldCustom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=dark_gray,
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=dark_gray,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=dark_gray,
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6B7280"),
    )

    elements = []

    # -------------------------------------------------------------------------
    # Header Banner
    # -------------------------------------------------------------------------
    elements.append(Paragraph("AI-POWERED TRAVEL PLANNER", title_style))
    elements.append(Paragraph("Personalized Day-Wise Itinerary & Expense Estimation Report", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=secondary_color, spaceAfter=12))

    # -------------------------------------------------------------------------
    # Key Trip Metadata Table
    # -------------------------------------------------------------------------
    diff = itinerary.budget_difference_inr
    status_color = accent_green if diff >= 0 else accent_red
    diff_label = f"+INR {diff:,.0f} (Savings)" if diff >= 0 else f"-INR {abs(diff):,.0f} (Deficit)"

    meta_data = [
        [
            Paragraph("<b>Destination:</b>", table_cell),
            Paragraph(f"<b>{itinerary.destination}</b>", table_cell),
            Paragraph("<b>Starting From:</b>", table_cell),
            Paragraph(itinerary.starting_city, table_cell),
        ],
        [
            Paragraph("<b>Duration:</b>", table_cell),
            Paragraph(f"{itinerary.duration_days} Days", table_cell),
            Paragraph("<b>Travelers:</b>", table_cell),
            Paragraph(str(itinerary.travelers_count), table_cell),
        ],
        [
            Paragraph("<b>Travel Style:</b>", table_cell),
            Paragraph(itinerary.travel_style, table_cell),
            Paragraph("<b>Budget Status:</b>", table_cell),
            Paragraph(f"<font color='{status_color.hexval()}'><b>{itinerary.budget_status}</b></font>", table_cell),
        ],
        [
            Paragraph("<b>Allocated Budget:</b>", table_cell),
            Paragraph(f"INR {itinerary.user_budget_inr:,.0f}", table_cell),
            Paragraph("<b>Estimated Total:</b>", table_cell),
            Paragraph(f"<b>INR {itinerary.total_estimated_cost_inr:,.0f}</b>", table_cell_bold),
        ],
    ]

    meta_table = Table(meta_data, colWidths=[1.3 * inch, 2.2 * inch, 1.3 * inch, 2.2 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Trip Overview
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Trip Summary", h1_style))
    elements.append(Paragraph(itinerary.trip_overview, body_style))
    elements.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Cost Breakdown Table
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Total Expense Breakdown (All Days)", h1_style))
    cost_data = [
        [
            Paragraph("<b>Category</b>", table_cell_bold),
            Paragraph("<b>Estimated Expense (INR)</b>", table_cell_bold),
            Paragraph("<b>Share (%)</b>", table_cell_bold),
        ],
        [
            Paragraph("Accommodation (Hotels/Stays)", table_cell),
            Paragraph(f"INR {itinerary.total_accommodation_cost_inr:,.0f}", table_cell),
            Paragraph(f"{(itinerary.total_accommodation_cost_inr / max(1, itinerary.total_estimated_cost_inr))*100:.1f}%", table_cell),
        ],
        [
            Paragraph("Food & Dining", table_cell),
            Paragraph(f"INR {itinerary.total_food_cost_inr:,.0f}", table_cell),
            Paragraph(f"{(itinerary.total_food_cost_inr / max(1, itinerary.total_estimated_cost_inr))*100:.1f}%", table_cell),
        ],
        [
            Paragraph("Local Transportation", table_cell),
            Paragraph(f"INR {itinerary.total_transport_cost_inr:,.0f}", table_cell),
            Paragraph(f"{(itinerary.total_transport_cost_inr / max(1, itinerary.total_estimated_cost_inr))*100:.1f}%", table_cell),
        ],
        [
            Paragraph("Activities, Entry Fees & Guides", table_cell),
            Paragraph(f"INR {itinerary.total_activities_cost_inr:,.0f}", table_cell),
            Paragraph(f"{(itinerary.total_activities_cost_inr / max(1, itinerary.total_estimated_cost_inr))*100:.1f}%", table_cell),
        ],
        [
            Paragraph("<b>GRAND TOTAL ESTIMATED COST</b>", table_cell_bold),
            Paragraph(f"<b>INR {itinerary.total_estimated_cost_inr:,.0f}</b>", table_cell_bold),
            Paragraph("<b>100.0%</b>", table_cell_bold),
        ],
    ]

    cost_table = Table(cost_data, colWidths=[3.2 * inch, 2.3 * inch, 1.5 * inch])
    cost_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FEF3C7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 6))

    # Budget Explanation
    elements.append(Paragraph(f"<b>Budget Analysis:</b> {itinerary.budget_breakdown_explanation}", body_style))
    elements.append(Spacer(1, 12))

    # -------------------------------------------------------------------------
    # Day-By-Day Itinerary
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Day-by-Day Schedule", h1_style))

    for day in itinerary.days:
        day_block = []

        # Day Header Bar
        header_text = f"Day {day.day_number}: {day.day_title}"
        day_banner_data = [[Paragraph(header_text, day_header_style)]]
        day_banner = Table(day_banner_data, colWidths=[7.0 * inch])
        day_banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), primary_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        day_block.append(day_banner)
        day_block.append(Spacer(1, 4))

        # Schedule details
        schedule_data = [
            [Paragraph("<b>Morning:</b>", body_bold), Paragraph(day.morning_activities, body_style)],
            [Paragraph("<b>Afternoon:</b>", body_bold), Paragraph(day.afternoon_activities, body_style)],
            [Paragraph("<b>Evening:</b>", body_bold), Paragraph(day.evening_activities, body_style)],
        ]
        schedule_table = Table(schedule_data, colWidths=[1.0 * inch, 6.0 * inch])
        schedule_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ]))
        day_block.append(schedule_table)
        day_block.append(Spacer(1, 4))

        # Attractions if present
        if day.suggested_attractions:
            attr_rows = [[
                Paragraph("<b>Attraction / Activity</b>", table_cell_bold),
                Paragraph("<b>Highlights</b>", table_cell_bold),
                Paragraph("<b>Est. Fee (INR)</b>", table_cell_bold)
            ]]
            for attr in day.suggested_attractions:
                fee_txt = f"INR {attr.entry_fee_inr:,.0f}" if attr.entry_fee_inr > 0 else "Free"
                attr_rows.append([
                    Paragraph(attr.name, table_cell),
                    Paragraph(attr.description, table_cell),
                    Paragraph(fee_txt, table_cell),
                ])
            attr_table = Table(attr_rows, colWidths=[2.2 * inch, 3.6 * inch, 1.2 * inch])
            attr_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ]))
            day_block.append(attr_table)
            day_block.append(Spacer(1, 4))

        # Daily Cost Bar
        day_cost_str = (
            f"<b>Day {day.day_number} Estimated Expense:</b> "
            f"Transport: INR {day.transportation_cost_inr:,.0f} | "
            f"Food: INR {day.food_cost_inr:,.0f} | "
            f"Stay: INR {day.accommodation_cost_inr:,.0f} | "
            f"Activities: INR {day.activity_cost_inr:,.0f} | "
            f"<b>Total: INR {day.total_daily_cost_inr:,.0f}</b>"
        )
        day_cost_table = Table([[Paragraph(day_cost_str, table_cell)]], colWidths=[7.0 * inch])
        day_cost_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        day_block.append(day_cost_table)
        day_block.append(Spacer(1, 10))

        # Keep each day grouped together when possible
        elements.append(KeepTogether(day_block))

    # -------------------------------------------------------------------------
    # Practical Tips Section
    # -------------------------------------------------------------------------
    if itinerary.practical_travel_tips:
        elements.append(Paragraph("Practical Travel Tips", h1_style))
        for i, tip in enumerate(itinerary.practical_travel_tips, start=1):
            elements.append(Paragraph(f"• <b>Tip {i}:</b> {tip}", body_style))
            elements.append(Spacer(1, 2))
        elements.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Disclaimer Box
    # -------------------------------------------------------------------------
    disclaimer_block = [
        Paragraph("<b>Important Notice & Disclaimer:</b>", body_bold),
        Paragraph(itinerary.disclaimer, disclaimer_style),
    ]
    disclaimer_table = Table([[disclaimer_block]], colWidths=[7.0 * inch])
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FCD34D")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(Spacer(1, 6))
    elements.append(disclaimer_table)

    # Build the document
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
