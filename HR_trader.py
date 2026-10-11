"""
HR Traders - Pure Python PDF Generator
No external libraries required.
Supports: Warning, Payment Shortage, Complaint, Register
"""

from datetime import datetime
import os

# ============================================================
# COMPANY SETTINGS (edit these)
# ============================================================
COMPANY_NAME = "HR TRADERS"
COMPANY_TAGLINE = "Machine Sales • Service • Repair"
COMPANY_ADDRESS = "Your Address Here, City, Pakistan"
COMPANY_PHONE = "+92-XXX-XXXXXXX"
COMPANY_EMAIL = "info@hrtraders.com"


# ============================================================
# PURE PYTHON PDF BUILDER
# ============================================================
class SimplePDF:
    def __init__(self, filename):
        self.filename = filename
        self.pages = []
        self.current_page = []
        self.y = 800          # start from top
        self.page_width = 595
        self.page_height = 842
        self.margin = 50

    def _add_text(self, text, x, y, size=11, bold=False):
        font = "Helvetica-Bold" if bold else "Helvetica"
        safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        self.current_page.append(f"BT /F1 {size} Tf {x} {y} Td ({safe}) Tj ET")

    def add_line(self, text, size=11, bold=False, center=False, color=None):
        if self.y < 60:
            self.new_page()
        x = self.margin
        if center:
            # approximate centering
            x = (self.page_width - len(text) * size * 0.5) / 2
            if x < self.margin:
                x = self.margin
        self._add_text(text, x, self.y, size, bold)
        self.y -= size + 6

    def add_space(self, points=12):
        self.y -= points

    def add_key_value(self, key, value):
        if not value:
            return
        if self.y < 60:
            self.new_page()
        self._add_text(f"{key}:", self.margin, self.y, 10, bold=True)
        self._add_text(str(value), self.margin + 140, self.y, 10)
        self.y -= 16

    def add_separator(self):
        if self.y < 60:
            self.new_page()
        self.current_page.append(f"0.5 w {self.margin} {self.y} m {self.page_width - self.margin} {self.y} l S")
        self.y -= 14

    def new_page(self):
        self.pages.append(self.current_page)
        self.current_page = []
        self.y = 800

    def save(self):
        if self.current_page:
            self.pages.append(self.current_page)

        objects = []
        # 1: Catalog
        objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

        # 2: Pages
        kids = " ".join(f"{i + 3} 0 R" for i in range(len(self.pages)))
        objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>\nendobj\n")

        # Font
        objects.append("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
        objects.append("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")

        content_ids = []
        for i, page_content in enumerate(self.pages):
            page_id = 5 + i * 2
            content_id = page_id + 1
            content_ids.append(content_id)

            # Page object
            objects.append(
                f"{page_id} 0 obj\n"
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.page_width} {self.page_height}] "
                f"/Contents {content_id} 0 R /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> >>\n"
                f"endobj\n"
            )

            stream = "\n".join(page_content)
            objects.append(
                f"{content_id} 0 obj\n"
                f"<< /Length {len(stream)} >>\n"
                f"stream\n{stream}\nendstream\n"
                f"endobj\n"
            )

        # Build PDF
        pdf = ["%PDF-1.4\n"]
        offsets = [0]
        for obj in objects:
            offsets.append(sum(len(o) for o in pdf))
            pdf.append(obj)

        xref_pos = sum(len(o) for o in pdf)
        pdf.append(f"xref\n0 {len(offsets)}\n")
        pdf.append("0000000000 65535 f \n")
        for off in offsets[1:]:
            pdf.append(f"{off:010d} 00000 n \n")

        pdf.append(
            f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        )

        with open(self.filename, "wb") as f:
            f.write("".join(pdf).encode("latin-1"))
        print(f"✅ PDF created → {self.filename}")


# ============================================================
# DOCUMENT CREATORS
# ============================================================
def create_header(pdf):
    pdf.add_line(COMPANY_NAME, size=18, bold=True, center=True)
    pdf.add_line(COMPANY_TAGLINE, size=9, center=True)
    pdf.add_line(f"{COMPANY_ADDRESS}  |  {COMPANY_PHONE}  |  {COMPANY_EMAIL}", size=8, center=True)
    pdf.add_space(6)
    pdf.add_separator()


def create_warning(data, filename):
    pdf = SimplePDF(filename)
    create_header(pdf)

    pdf.add_line("WARNING NOTICE", size=16, bold=True, center=True)
    pdf.add_space(4)
    pdf.add_line(f"Ref No: {data['ref_no']}          Date: {data['date']}", size=10)
    pdf.add_space(8)

    pdf.add_line("CUSTOMER & MACHINE INFORMATION", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Customer Name", data["customer_name"])
    pdf.add_key_value("Phone", data["customer_phone"])
    pdf.add_key_value("Address", data.get("customer_address", ""))
    pdf.add_key_value("Machine", data["machine_name"])
    pdf.add_key_value("Serial No.", data.get("machine_serial", ""))
    pdf.add_space(6)

    pdf.add_line("REASON FOR WARNING", size=11, bold=True)
    pdf.add_separator()
    pdf.add_line(data["issue"], size=10)
    pdf.add_space(4)

    if data.get("previous_warnings") and data["previous_warnings"] != "0":
        pdf.add_key_value("Previous Warnings", data["previous_warnings"])

    pdf.add_space(6)
    pdf.add_line("This is an official warning. Please resolve the issue within the given time.", size=10, bold=True)

    if data.get("deadline"):
        pdf.add_key_value("Deadline to Resolve", data["deadline"])

    if data.get("remarks"):
        pdf.add_space(4)
        pdf.add_line("ADDITIONAL REMARKS", size=11, bold=True)
        pdf.add_line(data["remarks"], size=10)

    pdf.add_space(30)
    pdf.add_line("Customer Signature                    Authorized Signature (HR Traders)", size=10)
    pdf.add_space(20)
    pdf.add_line("________________________              ________________________", size=10)

    pdf.save()


def create_payment(data, filename):
    pdf = SimplePDF(filename)
    create_header(pdf)

    pdf.add_line("PAYMENT SHORTAGE NOTICE", size=16, bold=True, center=True)
    pdf.add_space(4)
    pdf.add_line(f"Ref No: {data['ref_no']}          Date: {data['date']}", size=10)
    pdf.add_space(8)

    pdf.add_line("CUSTOMER & MACHINE INFORMATION", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Customer Name", data["customer_name"])
    pdf.add_key_value("Phone", data["customer_phone"])
    pdf.add_key_value("Address", data.get("customer_address", ""))
    pdf.add_key_value("Machine", data["machine_name"])
    pdf.add_key_value("Serial No.", data.get("machine_serial", ""))
    pdf.add_space(6)

    pdf.add_line("PAYMENT DETAILS", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Total Machine Cost", f"Rs. {data['machine_cost']}")
    pdf.add_key_value("Amount Paid", f"Rs. {data['amount_paid']}")
    pdf.add_key_value("Outstanding Amount", f"Rs. {data['amount_due']}")
    pdf.add_key_value("Due Date", data["due_date"])
    pdf.add_key_value("Payment Method", data.get("payment_method", ""))
    pdf.add_key_value("Bank Details", data.get("bank_details", ""))
    pdf.add_space(8)

    pdf.add_line("Please clear the outstanding amount on or before the due date.", size=10, bold=True)

    if data.get("remarks"):
        pdf.add_space(4)
        pdf.add_line("ADDITIONAL REMARKS", size=11, bold=True)
        pdf.add_line(data["remarks"], size=10)

    pdf.add_space(30)
    pdf.add_line("Customer Signature                    Authorized Signature (HR Traders)", size=10)
    pdf.add_space(20)
    pdf.add_line("________________________              ________________________", size=10)

    pdf.save()


def create_complaint(data, filename):
    pdf = SimplePDF(filename)
    create_header(pdf)

    pdf.add_line("CUSTOMER COMPLAINT FORM", size=16, bold=True, center=True)
    pdf.add_space(4)
    pdf.add_line(f"Ref No: {data['ref_no']}          Date: {data['date']}", size=10)
    pdf.add_space(8)

    pdf.add_line("CUSTOMER & MACHINE INFORMATION", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Customer Name", data["customer_name"])
    pdf.add_key_value("Phone", data["customer_phone"])
    pdf.add_key_value("Address", data.get("customer_address", ""))
    pdf.add_key_value("Machine", data["machine_name"])
    pdf.add_key_value("Serial No.", data.get("machine_serial", ""))
    pdf.add_space(6)

    pdf.add_line("COMPLAINT DETAILS", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Complaint Date", data.get("complaint_date", data["date"]))
    pdf.add_key_value("Priority", data.get("priority", "Medium"))
    pdf.add_key_value("Under Warranty", data.get("warranty", "No"))
    pdf.add_key_value("When Started", data.get("when_started", ""))
    pdf.add_space(6)

    pdf.add_line("PROBLEM DESCRIPTION", size=11, bold=True)
    pdf.add_separator()
    pdf.add_line(data["problem"], size=10)

    if data.get("remarks"):
        pdf.add_space(4)
        pdf.add_line("ADDITIONAL REMARKS", size=11, bold=True)
        pdf.add_line(data["remarks"], size=10)

    pdf.add_space(10)
    pdf.add_line("We have received your complaint and will take necessary action soon.", size=10)

    pdf.add_space(30)
    pdf.add_line("Customer Signature                    Authorized Signature (HR Traders)", size=10)
    pdf.add_space(20)
    pdf.add_line("________________________              ________________________", size=10)

    pdf.save()


def create_register(data, filename):
    pdf = SimplePDF(filename)
    create_header(pdf)

    pdf.add_line("MACHINE REGISTER / JOB CARD", size=16, bold=True, center=True)
    pdf.add_space(4)
    pdf.add_line(f"Job No: {data['ref_no']}          Date: {data['date']}", size=10)
    pdf.add_space(8)

    pdf.add_line("CUSTOMER & MACHINE INFORMATION", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Customer Name", data["customer_name"])
    pdf.add_key_value("Phone", data["customer_phone"])
    pdf.add_key_value("Address", data.get("customer_address", ""))
    pdf.add_key_value("Machine", data["machine_name"])
    pdf.add_key_value("Serial No.", data.get("machine_serial", ""))
    pdf.add_space(6)

    pdf.add_line("JOB DETAILS", size=11, bold=True)
    pdf.add_separator()
    pdf.add_key_value("Date Received", data.get("received_date", data["date"]))
    pdf.add_key_value("Status", data.get("status", "Received"))
    pdf.add_key_value("Technician", data.get("technician", ""))
    pdf.add_key_value("Estimated Cost", f"Rs. {data['estimated_cost']}" if data.get("estimated_cost") else "")
    pdf.add_key_value("Parts Needed", data.get("parts_needed", ""))
    pdf.add_space(6)

    pdf.add_line("PROBLEM REPORTED", size=11, bold=True)
    pdf.add_separator()
    pdf.add_line(data["problem"], size=10)

    if data.get("remarks"):
        pdf.add_space(4)
        pdf.add_line("ADDITIONAL REMARKS", size=11, bold=True)
        pdf.add_line(data["remarks"], size=10)

    pdf.add_space(10)
    pdf.add_line("WORK DONE / PARTS USED (Office Use)", size=11, bold=True)
    pdf.add_separator()
    pdf.add_line("Description                              Qty          Amount (Rs.)", size=9, bold=True)
    pdf.add_line("_______________________________________________________________", size=9)
    pdf.add_line("_______________________________________________________________", size=9)
    pdf.add_line("_______________________________________________________________", size=9)
    pdf.add_line("_______________________________________________________________", size=9)

    pdf.add_space(25)
    pdf.add_line("Customer Signature                    Authorized Signature (HR Traders)", size=10)
    pdf.add_space(20)
    pdf.add_line("________________________              ________________________", size=10)

    pdf.save()


# ============================================================
# DATA COLLECTION
# ============================================================
def ask(prompt, required=True, default=""):
    while True:
        val = input(f"  {prompt}: ").strip()
        if val:
            return val
        if not required:
            return default
        print("    → Required field")


def collect_common():
    print("\n--- Customer & Machine ---")
    return {
        "customer_name": ask("Customer Name"),
        "customer_phone": ask("Customer Phone"),
        "customer_address": ask("Address (optional)", required=False),
        "machine_name": ask("Machine Name / Model"),
        "machine_serial": ask("Serial No. (optional)", required=False),
        "date": ask("Date (DD-MM-YYYY)", default=datetime.now().strftime("%d-%m-%Y")),
        "ref_no": ask("Ref / Job No. (optional)", required=False,
                      default=f"HR-{datetime.now().strftime('%Y%m%d-%H%M')}"),
    }


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 50)
    print(f"   {COMPANY_NAME}  –  Document Generator")
    print("   (Pure Python – No Libraries Needed)")
    print("=" * 50)
    print("""
  1. Warning Letter
  2. Payment Shortage Notice
  3. Customer Complaint Form
  4. Machine Register / Job Card
  0. Exit
""")
    choice = input("Select (1-4): ").strip()

    if choice == "0":
        return

    os.makedirs("HR_PDFs", exist_ok=True)

    if choice == "1":
        data = collect_common()
        print("\n--- Warning Details ---")
        data["issue"] = ask("Reason for Warning")
        data["previous_warnings"] = ask("Previous Warnings (0 if none)", default="0")
        data["deadline"] = ask("Deadline (optional)", required=False)
        data["remarks"] = ask("Remarks (optional)", required=False)
        fname = f"HR_PDFs/Warning_{data['customer_name'].replace(' ', '_')}.pdf"
        create_warning(data, fname)

    elif choice == "2":
        data = collect_common()
        print("\n--- Payment Details ---")
        data["machine_cost"] = ask("Total Machine Cost (Rs.)")
        data["amount_paid"] = ask("Amount Paid (Rs.)")
        data["amount_due"] = ask("Outstanding Amount (Rs.)")
        data["due_date"] = ask("Due Date (DD-MM-YYYY)")
        data["payment_method"] = ask("Payment Method (optional)", required=False)
        data["bank_details"] = ask("Bank Details (optional)", required=False)
        data["remarks"] = ask("Remarks (optional)", required=False)
        fname = f"HR_PDFs/Payment_{data['customer_name'].replace(' ', '_')}.pdf"
        create_payment(data, fname)

    elif choice == "3":
        data = collect_common()
        print("\n--- Complaint Details ---")
        data["problem"] = ask("Problem Description")
        data["complaint_date"] = ask("Complaint Date", default=data["date"])
        data["when_started"] = ask("When problem started (optional)", required=False)
        data["warranty"] = ask("Under Warranty? (Yes/No)", default="No")
        data["priority"] = ask("Priority (Low/Medium/High)", default="Medium")
        data["remarks"] = ask("Remarks (optional)", required=False)
        fname = f"HR_PDFs/Complaint_{data['customer_name'].replace(' ', '_')}.pdf"
        create_complaint(data, fname)

    elif choice == "4":
        data = collect_common()
        print("\n--- Job / Register Details ---")
        data["problem"] = ask("Problem Reported")
        data["received_date"] = ask("Date Received", default=data["date"])
        data["estimated_cost"] = ask("Estimated Cost (optional)", required=False)
        data["parts_needed"] = ask("Parts Needed (optional)", required=False)
        data["technician"] = ask("Technician (optional)", required=False)
        data["status"] = ask("Status", default="Received")
        data["remarks"] = ask("Remarks (optional)", required=False)
        fname = f"HR_PDFs/Register_{data['customer_name'].replace(' ', '_')}.pdf"
        create_register(data, fname)

    else:
        print("Invalid choice.")

    print("\nDone. Check the HR_PDFs folder.")


if __name__ == "__main__":
    main()
