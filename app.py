import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from io import BytesIO

# ====================== COMPANY SETTINGS ======================
COMPANY_NAME = "HR TRADERS"
COMPANY_TAGLINE = "Machine Sales • Service • Repair"
COMPANY_ADDRESS = "Your Address Here, City, Pakistan"
COMPANY_PHONE = "+92-XXX-XXXXXXX"
COMPANY_EMAIL = "info@hrtraders.com"

PRIMARY = HexColor("#1a365d")
ACCENT = HexColor("#c53030")
LIGHT = HexColor("#edf2f7")

# ====================== STYLES ======================
def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CompanyTitle', fontName='Helvetica-Bold', fontSize=20,
                              textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=2))
    styles.add(ParagraphStyle(name='Tagline', fontName='Helvetica', fontSize=9,
                              textColor=HexColor("#4a5568"), alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle(name='DocTitle', fontName='Helvetica-Bold', fontSize=15,
                              textColor=PRIMARY, alignment=TA_CENTER, spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle(name='SectionHead', fontName='Helvetica-Bold', fontSize=11,
                              textColor=PRIMARY, spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle(name='BodyText2', fontName='Helvetica', fontSize=10,
                              leading=14, alignment=TA_JUSTIFY, spaceAfter=6))
    styles.add(ParagraphStyle(name='Label', fontName='Helvetica-Bold', fontSize=9,
                              textColor=HexColor("#2d3748")))
    styles.add(ParagraphStyle(name='Value', fontName='Helvetica', fontSize=10))
    styles.add(ParagraphStyle(name='Footer', fontName='Helvetica', fontSize=8,
                              textColor=HexColor("#718096"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='WarningText', fontName='Helvetica-Bold', fontSize=11,
                              textColor=ACCENT, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8))
    return styles

# ====================== PDF HELPERS ======================
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, h - 10*mm, w, 10*mm, fill=1, stroke=0)
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(0.8)
    canvas.line(15*mm, 14*mm, w - 15*mm, 14*mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(HexColor("#718096"))
    canvas.drawCentredString(w/2, 7*mm, f"{COMPANY_NAME}  |  {COMPANY_PHONE}  |  {COMPANY_EMAIL}")
    canvas.drawRightString(w - 15*mm, 7*mm, f"Page {doc.page}")
    canvas.restoreState()

def make_header(styles):
    elems = [
        Paragraph(COMPANY_NAME, styles['CompanyTitle']),
        Paragraph(COMPANY_TAGLINE, styles['Tagline']),
        Paragraph(f"{COMPANY_ADDRESS}<br/>{COMPANY_PHONE} | {COMPANY_EMAIL}", styles['Footer']),
        Spacer(1, 3),
        HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=6)
    ]
    return elems

def info_table(data, styles):
    rows = []
    for k, v in data.items():
        if v:
            rows.append([
                Paragraph(f"<b>{k}</b>", styles['Label']),
                Paragraph(str(v), styles['Value'])
            ])
    if not rows:
        return []
    t = Table(rows, colWidths=[2.1*inch, 4.6*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, PRIMARY),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, HexColor("#cbd5e0")),
    ]))
    return [t]

def signature_block(styles):
    elems = [Spacer(1, 22)]
    sig = Table([[
        Paragraph("<b>Customer Signature</b><br/><br/><br/>________________________", styles['Value']),
        Paragraph("<b>Authorized Signature<br/>(HR Traders)</b><br/><br/><br/>________________________", styles['Value'])
    ]], colWidths=[3.5*inch, 3.5*inch])
    sig.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elems.append(sig)
    return elems

def build_pdf(story) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=18*mm, bottomMargin=20*mm)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer.getvalue()

# ====================== DOCUMENT CREATORS ======================
def create_warning(data):
    styles = get_styles()
    story = make_header(styles)
    story.append(Paragraph("⚠  WARNING NOTICE", styles['DocTitle']))
    story.append(Paragraph(f"<b>Ref No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 6))
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
        story.append(Paragraph(f"<b>Previous Warnings:</b> {data['previous_warnings']}", styles['BodyText2']))
    story.append(Paragraph("This is an official warning. Please resolve the issue within the given time.", styles['WarningText']))
    if data.get('deadline'):
        story.append(Paragraph(f"<b>Deadline:</b> {data['deadline']}", styles['BodyText2']))
    if data.get('remarks'):
        story.append(Paragraph("REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))
    story.extend(signature_block(styles))
    return build_pdf(story)

def create_payment(data):
    styles = get_styles()
    story = make_header(styles)
    story.append(Paragraph("PAYMENT SHORTAGE NOTICE", styles['DocTitle']))
    story.append(Paragraph(f"<b>Ref No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 6))
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
        "Due Date": data['due_date'],
        "Payment Method": data.get('payment_method', ''),
        "Bank Details": data.get('bank_details', ''),
    }, styles))
    story.append(Paragraph("Kindly clear the outstanding amount on or before the due date.", styles['BodyText2']))
    if data.get('remarks'):
        story.append(Paragraph("REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))
    story.extend(signature_block(styles))
    return build_pdf(story)

def create_complaint(data):
    styles = get_styles()
    story = make_header(styles)
    story.append(Paragraph("CUSTOMER COMPLAINT FORM", styles['DocTitle']))
    story.append(Paragraph(f"<b>Ref No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 6))
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
        "Complaint Date": data.get('complaint_date', data['date']),
        "Priority": data.get('priority', 'Medium'),
        "Under Warranty": data.get('warranty', 'No'),
        "When Started": data.get('when_started', ''),
    }, styles))
    story.append(Paragraph("PROBLEM DESCRIPTION", styles['SectionHead']))
    story.append(Paragraph(data['problem'], styles['BodyText2']))
    if data.get('remarks'):
        story.append(Paragraph("REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<i>We have received your complaint and will take necessary action soon.</i>", styles['BodyText2']))
    story.extend(signature_block(styles))
    return build_pdf(story)

def create_register(data):
    styles = get_styles()
    story = make_header(styles)
    story.append(Paragraph("MACHINE REGISTER / JOB CARD", styles['DocTitle']))
    story.append(Paragraph(f"<b>Job No:</b> {data['ref_no']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {data['date']}", styles['Value']))
    story.append(Spacer(1, 6))
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
        "Date Received": data.get('received_date', data['date']),
        "Status": data.get('status', 'Received'),
        "Technician": data.get('technician', ''),
        "Estimated Cost": f"Rs. {data['estimated_cost']}" if data.get('estimated_cost') else '',
        "Parts Needed": data.get('parts_needed', ''),
    }, styles))
    story.append(Paragraph("PROBLEM REPORTED", styles['SectionHead']))
    story.append(Paragraph(data['problem'], styles['BodyText2']))
    if data.get('remarks'):
        story.append(Paragraph("REMARKS", styles['SectionHead']))
        story.append(Paragraph(data['remarks'], styles['BodyText2']))
    story.append(Paragraph("WORK DONE / PARTS USED (Office Use)", styles['SectionHead']))
    blank = Table([
        [Paragraph("Description of Work / Parts", styles['Label']),
         Paragraph("Qty", styles['Label']),
         Paragraph("Amount (Rs.)", styles['Label'])],
        ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""],
    ], colWidths=[4.2*inch, 1*inch, 1.5*inch])
    blank.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, PRIMARY),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, HexColor("#cbd5e0")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(blank)
    story.extend(signature_block(styles))
    return build_pdf(story)

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="HR Traders Documents", page_icon="📄", layout="centered")

st.title("HR TRADERS")
st.caption("Document Generator – Warning • Payment • Complaint • Register")

doc_type = st.selectbox(
    "Select Document Type",
    ["Warning Letter", "Payment Shortage Notice", "Customer Complaint Form", "Machine Register / Job Card"]
)

st.subheader("Customer & Machine Details")
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("Customer Name *")
    customer_phone = st.text_input("Customer Phone *")
    customer_address = st.text_input("Customer Address")
with col2:
    machine_name = st.text_input("Machine Name / Model *")
    machine_serial = st.text_input("Machine Serial No.")
    date = st.text_input("Date (DD-MM-YYYY)", value=datetime.now().strftime("%d-%m-%Y"))

ref_no = st.text_input("Reference / Job No.", value=f"HR-{datetime.now().strftime('%Y%m%d-%H%M')}")

pdf_bytes = None
filename = "document.pdf"

if doc_type == "Warning Letter":
    st.subheader("Warning Details")
    issue = st.text_area("Reason for Warning *")
    previous_warnings = st.text_input("Previous Warnings", value="0")
    deadline = st.text_input("Deadline (DD-MM-YYYY)")
    remarks = st.text_area("Remarks")

    if st.button("Generate Warning PDF", type="primary"):
        if customer_name and customer_phone and machine_name and issue:
            data = {
                "customer_name": customer_name, "customer_phone": customer_phone,
                "customer_address": customer_address, "machine_name": machine_name,
                "machine_serial": machine_serial, "date": date, "ref_no": ref_no,
                "issue": issue, "previous_warnings": previous_warnings,
                "deadline": deadline, "remarks": remarks
            }
            pdf_bytes = create_warning(data)
            filename = f"Warning_{customer_name.replace(' ', '_')}.pdf"
        else:
            st.error("Please fill all required fields (*)")

elif doc_type == "Payment Shortage Notice":
    st.subheader("Payment Details")
    machine_cost = st.text_input("Total Machine Cost (Rs.) *")
    amount_paid = st.text_input("Amount Paid (Rs.) *")
    amount_due = st.text_input("Outstanding Amount (Rs.) *")
    due_date = st.text_input("Due Date (DD-MM-YYYY) *")
    payment_method = st.text_input("Payment Method")
    bank_details = st.text_input("Bank / Payment Details")
    remarks = st.text_area("Remarks")

    if st.button("Generate Payment PDF", type="primary"):
        if all([customer_name, customer_phone, machine_name, machine_cost, amount_paid, amount_due, due_date]):
            data = {
                "customer_name": customer_name, "customer_phone": customer_phone,
                "customer_address": customer_address, "machine_name": machine_name,
                "machine_serial": machine_serial, "date": date, "ref_no": ref_no,
                "machine_cost": machine_cost, "amount_paid": amount_paid,
                "amount_due": amount_due, "due_date": due_date,
                "payment_method": payment_method, "bank_details": bank_details,
                "remarks": remarks
            }
            pdf_bytes = create_payment(data)
            filename = f"Payment_{customer_name.replace(' ', '_')}.pdf"
        else:
            st.error("Please fill all required fields (*)")

elif doc_type == "Customer Complaint Form":
    st.subheader("Complaint Details")
    problem = st.text_area("Problem Description *")
    complaint_date = st.text_input("Complaint Date", value=date)
    when_started = st.text_input("When did the problem start?")
    warranty = st.selectbox("Under Warranty?", ["No", "Yes"])
    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
    remarks = st.text_area("Remarks")

    if st.button("Generate Complaint PDF", type="primary"):
        if customer_name and customer_phone and machine_name and problem:
            data = {
                "customer_name": customer_name, "customer_phone": customer_phone,
                "customer_address": customer_address, "machine_name": machine_name,
                "machine_serial": machine_serial, "date": date, "ref_no": ref_no,
                "problem": problem, "complaint_date": complaint_date,
                "when_started": when_started, "warranty": warranty,
                "priority": priority, "remarks": remarks
            }
            pdf_bytes = create_complaint(data)
            filename = f"Complaint_{customer_name.replace(' ', '_')}.pdf"
        else:
            st.error("Please fill all required fields (*)")

else:  # Register
    st.subheader("Job Card Details")
    problem = st.text_area("Problem Reported *")
    received_date = st.text_input("Date Received", value=date)
    estimated_cost = st.text_input("Estimated Repair Cost (Rs.)")
    parts_needed = st.text_input("Parts Needed")
    technician = st.text_input("Assigned Technician")
    status = st.selectbox("Status", ["Received", "In Progress", "Completed", "Delivered"])
    remarks = st.text_area("Remarks")

    if st.button("Generate Job Card PDF", type="primary"):
        if customer_name and customer_phone and machine_name and problem:
            data = {
                "customer_name": customer_name, "customer_phone": customer_phone,
                "customer_address": customer_address, "machine_name": machine_name,
                "machine_serial": machine_serial, "date": date, "ref_no": ref_no,
                "problem": problem, "received_date": received_date,
                "estimated_cost": estimated_cost, "parts_needed": parts_needed,
                "technician": technician, "status": status, "remarks": remarks
            }
            pdf_bytes = create_register(data)
            filename = f"Register_{customer_name.replace(' ', '_')}.pdf"
        else:
            st.error("Please fill all required fields (*)")

# Download button
if pdf_bytes:
    st.success("✅ PDF generated successfully!")
    st.download_button(
        label="📥 Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf"
    )
