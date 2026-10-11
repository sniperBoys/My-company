"""
HR Traders - Document Generator
Creates professional PDFs for:
  - Warning Letter
  - Payment Shortage Notice
  - Complaint Form
  - Machine Register / Job Card
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# ============================================================
# COMPANY DETAILS  (edit these if needed)
# ============================================================
COMPANY_NAME = "HR TRADERS"
COMPANY_TAGLINE = "Machine Sales • Service • Repair"
COMPANY_ADDRESS = "Your Address Here, City, Pakistan"
COMPANY_PHONE = "+92-XXX-XXXXXXX"
COMPANY_EMAIL = "info@hrtraders.com"
COMPANY_NTN = "NTN: XXXXXXX-X"          # optional

# Colors
PRIMARY = HexColor("#1a365d")      # Dark blue
ACCENT  = HexColor("#c53030")      # Red (for warnings)
LIGHT   = HexColor("#edf2f7")      # Light gray
GREEN   = HexColor("#276749")      # Green for success notes

# ============================================================
# STYLES
# ============================================================
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CompanyTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='Tagline',
        fontName='Helvetica',
        fontSize=9,
        textColor=HexColor("#4a5568"),
        alignment=TA_CENTER,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='SectionHead',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Label',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=HexColor("#2d3748")
    ))
    styles.add(ParagraphStyle(
        name='Value',
        fontName='Helvetica',
        fontSize=10
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=HexColor("#718096"),
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='WarningText',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=ACCENT,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=8
    ))
    return styles

# ============================================================
# HELPER – Header & Footer
# ============================================================
def add_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4

    # Top colored bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, height - 12*mm, width, 12*mm, fill=1, stroke=0)

    # Footer line
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(1)
    canvas.line(15*mm, 15*mm, width - 15*mm, 15*mm)

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(HexColor("#718096"))
    canvas.drawCentredString(width/2, 8*mm,
        f"{COMPANY_NAME}  |  {COMPANY_PHONE}  |  {COMPANY_EMAIL}")
    canvas.drawRightString(width - 15*mm, 8*mm, f"Page {doc.page}")

    canvas.restoreState()

# ============================================================
# DATA COLLECTION
# ============================================================
def ask(prompt, required=True, default=""):
    while True:
        val = input(f"{prompt}: ").strip()
        if val:
            return val
        if not required:
            return default
        print("  → This field is required.")

def collect_common_data():
    print("\n--- Customer & Machine Details ---")
    data = {
        "customer_name" : ask("Customer Name"),
        "customer_phone": ask("Customer Phone"),
        "customer_address": ask("Customer Address (optional)", required=False),
        "machine_name"  : ask("Machine Name / Model"),
        "machine_serial": ask("Machine Serial No. (optional)", required=False),
        "date"          : ask("Date (DD-MM-YYYY)", default=datetime.now().strftime("%d-%m-%Y")),
        "ref_no"        : ask("Reference / Job No. (optional)", required=False,
                              default=f"HR-{datetime.now().strftime('%Y%m%d-%H%M')}"),
    }
    return data

def collect_warning_data():
    data = collect_common_data()
    print("\n--- Warning Specific ---")
    data["issue"] = ask("Describe the issue / reason for warning")
    data["previous_warnings"] = ask("Number of previous warnings (0 if none)", default="0")
    data["deadline"] = ask("Deadline to resolve (DD-MM-YYYY)", required=False)
    data["remarks"] = ask("Additional remarks (optional)", required=False)
    return data

def collect_payment_data():
    data = collect_common_data()
    print("\n--- Payment Shortage Details ---")
    data["machine_cost"]   = ask("Total Machine Cost (Rs.)")
    data["amount_paid"]    = ask("Amount Already Paid (Rs.)")
    data["amount_due"]     = ask("Outstanding / Shortage Amount (Rs.)")
    data["due_date"]       = ask("Payment Due Date (DD-MM-YYYY)")
    data["payment_method"] = ask("Preferred Payment Method (Cash/Bank/JazzCash etc.)", required=False)
    data["bank_details"]   = ask("Bank Account / Payment details (optional)", required=False)
    data["remarks"]        = ask("Additional remarks (optional)", required=False)
    return data

def collect_complaint_data():
    data = collect_common_data()
    print("\n--- Complaint Details ---")
    data["complaint_date"] = ask("Date of Complaint", default=datetime.now().strftime("%d-%m-%Y"))
    data["problem"]        = ask("Describe the problem / complaint in detail")
    data["when_started"]   = ask("When did the problem start?", required=False)
    data["warranty"]       = ask("Under Warranty? (Yes/No)", default="No")
    data["priority"]       = ask("Priority (Low/Medium/High/Urgent)", default="Medium")
    data["remarks"]        = ask("Additional remarks (optional)", required=False)
    return data

def collect_register_data():
    data = collect_common_data()
    print("\n--- Job / Register Details ---")
    data["received_date"]  = ask("Date Machine Received", default=datetime.now().strftime("%d-%m-%Y"))
    data["problem"]        = ask("Problem reported by customer")
    data["estimated_cost"] = ask("Estimated Repair Cost (Rs.)", required=False)
    data["parts_needed"]   = ask("Parts required (optional)", required=False)
    data["technician"]     = ask("Assigned Technician (optional)", required=False)
    data["status"]         = ask("Current Status (Received/In Progress/Completed)", default="Received")
    data["remarks"]        = ask("Additional remarks (optional)", required=False)
    return data

# ============================================================
# PDF BUILDERS
# ============================================================
def make_header(styles):
    elements = []
    elements.append(Paragraph(COMPANY_NAME, styles['CompanyTitle']))
    elements.append(Paragraph(COMPANY_TAGLINE, styles['Tagline']))
    elements.append(Paragraph(f"{COMPANY_ADDRESS}<br/>{COMPANY_PHONE} | {COMPANY_EMAIL}", styles['Footer']))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=6))
    return elements

def info_table(data_dict, styles):
    """Create a clean 2-column key-value table"""
    rows = []
    for key, value in data_dict.items():
        if value:
            rows.append([
                Paragraph(f"<b>{key}</b>", styles['Label']),
                Paragraph(str(value), styles['Value'])
            ])
    if not rows:
        return []

    t = Table(rows, colWidths=[2.2*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, PRIMARY),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, HexColor("#cbd5e0")),
    ]))
    return [t]

def signature_block(styles):
    elements = []
    elements.append(Spacer(1, 25))
    sig = Table([
        [Paragraph("<b>Customer Signature</b><br/><br/><br/>________________________", styles['Value']),
         Paragraph("<b>Authorized Signature<br/>(HR Traders)</b><br/><br/><br/>________________________", styles['Value'])]
    ], colWidths=[3.5*inch, 3.5*inch])
    sig.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig)
    return elements

# ---------- WARNING LETTER ----------
def build_warning_pdf(data, filename):
    styles = get_styles()
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=22*mm
    )
    story = make_header(styles)

    story.append(Paragraph("⚠  WARNING NOTICE", styles['DocTitle']))
    story.append(Paragraph(f"<b>Ref No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("CUSTOMER & MACHINE INFORMATION", styles['SectionHead']))
    story.extend(info_table({
        "Customer Name": data['customer_name'],
        "Phone": data['customer_phone'],
        "Address": data.get('customer_address', ''),
        "Machine": data['machine_name'],
        "Serial No.": data.get('machine_serial', ''),
    }, styles))

    story.append(Paragraph("REASON FOR WARNING", styles['SectionHead']))
    story.append(Paragraph(data['issue'], styles['BodyText2']))

    if data.get('previous_warnings') and data['previous_warnings'] != "0":
        story.append(Paragraph(
            f"<b>Previous Warnings Issued:</b> {data['previous_warnings']}", styles['BodyText2']))

    story.append(Paragraph(
        "This is an official warning. Please resolve the above issue within the given time to avoid further action.",
        styles['WarningText']))

    if data.get('deadline'):
        story.append(Paragraph(f"<b>Deadline to Resolve:</b> {data['deadline']}", styles['BodyText2']))

    if data.get('remarks'):
        story.append(Paragraph("ADDITIONAL REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))

    story.extend(signature_block(styles))
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print(f"\n✅ Warning PDF created → {filename}")

# ---------- PAYMENT SHORTAGE ----------
def build_payment_pdf(data, filename):
    styles = get_styles()
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=22*mm
    )
    story = make_header(styles)

    story.append(Paragraph("PAYMENT SHORTAGE NOTICE", styles['DocTitle']))
    story.append(Paragraph(f"<b>Ref No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("CUSTOMER & MACHINE INFORMATION", styles['SectionHead']))
    story.extend(info_table({
        "Customer Name": data['customer_name'],
        "Phone": data['customer_phone'],
        "Address": data.get('customer_address', ''),
        "Machine": data['machine_name'],
        "Serial No.": data.get('machine_serial', ''),
    }, styles))

    story.append(Paragraph("PAYMENT DETAILS", styles['SectionHead']))
    story.extend(info_table({
        "Total Machine Cost": f"Rs. {data['machine_cost']}",
        "Amount Paid": f"Rs. {data['amount_paid']}",
        "Outstanding Amount": f"Rs. {data['amount_due']}",
        "Payment Due Date": data['due_date'],
        "Preferred Method": data.get('payment_method', ''),
        "Bank / Payment Details": data.get('bank_details', ''),
    }, styles))

    story.append(Paragraph(
        "You are kindly requested to clear the outstanding amount on or before the due date to avoid any inconvenience or further action.",
        styles['BodyText2']))

    if data.get('remarks'):
        story.append(Paragraph("ADDITIONAL REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))

    story.extend(signature_block(styles))
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print(f"\n✅ Payment Shortage PDF created → {filename}")

# ---------- COMPLAINT FORM ----------
def build_complaint_pdf(data, filename):
    styles = get_styles()
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=22*mm
    )
    story = make_header(styles)

    story.append(Paragraph("CUSTOMER COMPLAINT FORM", styles['DocTitle']))
    story.append(Paragraph(f"<b>Ref No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("CUSTOMER & MACHINE INFORMATION", styles['SectionHead']))
    story.extend(info_table({
        "Customer Name": data['customer_name'],
        "Phone": data['customer_phone'],
        "Address": data.get('customer_address', ''),
        "Machine": data['machine_name'],
        "Serial No.": data.get('machine_serial', ''),
    }, styles))

    story.append(Paragraph("COMPLAINT DETAILS", styles['SectionHead']))
    story.extend(info_table({
        "Complaint Date": data['complaint_date'],
        "Priority": data['priority'],
        "Under Warranty": data['warranty'],
        "When Problem Started": data.get('when_started', ''),
    }, styles))

    story.append(Paragraph("PROBLEM DESCRIPTION", styles['SectionHead']))
    story.append(Paragraph(data['problem'], styles['BodyText2']))

    if data.get('remarks'):
        story.append(Paragraph("ADDITIONAL REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>We have received your complaint and will take necessary action at the earliest.</i>",
        styles['BodyText2']))

    story.extend(signature_block(styles))
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print(f"\n✅ Complaint PDF created → {filename}")

# ---------- REGISTER / JOB CARD ----------
def build_register_pdf(data, filename):
    styles = get_styles()
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=22*mm
    )
    story = make_header(styles)

    story.append(Paragraph("MACHINE REGISTER / JOB CARD", styles['DocTitle']))
    story.append(Paragraph(f"<b>Job No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("CUSTOMER & MACHINE INFORMATION", styles['SectionHead']))
    story.extend(info_table({
        "Customer Name": data['customer_name'],
        "Phone": data['customer_phone'],
        "Address": data.get('customer_address', ''),
        "Machine": data['machine_name'],
        "Serial No.": data.get('machine_serial', ''),
    }, styles))

    story.append(Paragraph("JOB DETAILS", styles['SectionHead']))
    story.extend(info_table({
        "Date Received": data['received_date'],
        "Current Status": data['status'],
        "Assigned Technician": data.get('technician', ''),
        "Estimated Cost": f"Rs. {data['estimated_cost']}" if data.get('estimated_cost') else '',
        "Parts Required": data.get('parts_needed', ''),
    }, styles))

    story.append(Paragraph("PROBLEM REPORTED", styles['SectionHead']))
    story.append(Paragraph(data['problem'], styles['BodyText2']))

    if data.get('remarks'):
        story.append(Paragraph("ADDITIONAL REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))

    # Work done section (blank for filling later)
    story.append(Paragraph("WORK DONE / PARTS USED (Office Use)", styles['SectionHead']))
    blank = Table([
        [Paragraph("Description of Work / Parts", styles['Label']),
         Paragraph("Qty", styles['Label']),
         Paragraph("Amount (Rs.)", styles['Label'])],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ], colWidths=[4.2*inch, 1*inch, 1.5*inch])
    blank.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, PRIMARY),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, HexColor("#cbd5e0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(blank)

    story.extend(signature_block(styles))
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print(f"\n✅ Register / Job Card PDF created → {filename}")

# ============================================================
# MAIN MENU
# ============================================================
def main():
    print("=" * 55)
    print(f"   {COMPANY_NAME}  –  Document Generator")
    print("=" * 55)
    print("""
Select Document Type:
  1. Warning Letter
  2. Payment Shortage Notice
  3. Customer Complaint Form
  4. Machine Register / Job Card
  0. Exit
""")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "0":
        print("Goodbye!")
        return

    builders = {
        "1": ("Warning", collect_warning_data, build_warning_pdf),
        "2": ("Payment_Shortage", collect_payment_data, build_payment_pdf),
        "3": ("Complaint", collect_complaint_data, build_complaint_pdf),
        "4": ("Register", collect_register_data, build_register_pdf),
    }

    if choice not in builders:
        print("Invalid choice. Please run again.")
        return

    doc_type, collector, builder = builders[choice]
    data = collector()

    # Create output folder
    os.makedirs("HR_Traders_PDFs", exist_ok=True)
    safe_name = data['customer_name'].replace(" ", "_")[:20]
    filename = f"HR_Traders_PDFs/{doc_type}_{safe_name}_{data['ref_no']}.pdf"

    builder(data, filename)
    print(f"\nFile saved in folder: HR_Traders_PDFs/")
    print("You can open the PDF now.")

if __name__ == "__main__":
    main()
