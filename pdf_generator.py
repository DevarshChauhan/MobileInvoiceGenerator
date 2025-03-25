"""
Module for generating PDF invoices.
Uses ReportLab to create professionally formatted PDF documents.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
from datetime import datetime

def create_invoice_pdf(invoice_data):
    """
    Create a PDF invoice from the provided invoice data.
    
    Parameters:
    - invoice_data: Dictionary containing all invoice information
    
    Returns:
    - BytesIO object containing the PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=1*cm, 
        leftMargin=1*cm, 
        topMargin=1*cm, 
        bottomMargin=1*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
    ))
    styles.add(ParagraphStyle(
        name='InvoiceSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,  # Center
    ))
    styles.add(ParagraphStyle(
        name='InvoiceInfo',
        parent=styles['Normal'],
        fontSize=9,
    ))
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,  # Center
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=9,
    ))
    styles.add(ParagraphStyle(
        name='Total',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        alignment=2,  # Right aligned
    ))
    
    # Build the document
    elements = []
    
    # Title
    elements.append(Paragraph("TAX INVOICE", styles['InvoiceTitle']))
    elements.append(Spacer(1, 5*mm))
    
    # Invoice information
    invoice_info = [
        ['Invoice No.:', invoice_data['invoice_number'], 'Date:', invoice_data['date']],
        ['Time:', invoice_data['time'], '', '']
    ]
    
    invoice_info_table = Table(invoice_info, colWidths=[2.5*cm, 4*cm, 2*cm, 2.5*cm])
    invoice_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(invoice_info_table)
    elements.append(Spacer(1, 5*mm))
    
    # Seller and customer information
    seller_customer_data = [
        ['Seller:', 'Buyer:'],
        [
            f"{invoice_data['seller_name']}\n{invoice_data['seller_address']}\nPhone: {invoice_data['seller_phone']}\nEmail: {invoice_data['seller_email']}\nGSTIN: {invoice_data['seller_gstin']}",
            f"{invoice_data['customer_name']}\n{invoice_data['customer_address']}\nPhone: {invoice_data['customer_phone']}" +
            (f"\nEmail: {invoice_data['customer_email']}" if invoice_data.get('customer_email') else "") +
            (f"\nGSTIN: {invoice_data['customer_gstin']}" if invoice_data.get('customer_gstin') else "")
        ]
    ]
    
    seller_customer_table = Table(seller_customer_data, colWidths=[8.5*cm, 8.5*cm])
    seller_customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (1, -1), 'TOP'),
        ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
    ]))
    elements.append(seller_customer_table)
    elements.append(Spacer(1, 5*mm))
    
    # Invoice items
    table_data = [
        ['#', 'Description', 'HSN/SAC', 'Qty', 'Rate', 'Amount', 'SGST 9%', 'CGST 9%', 'Total']
    ]
    
    for i, item in enumerate(invoice_data['items']):
        table_data.append([
            i+1,
            Paragraph(item['description'], styles['TableCell']),
            item['hsn_code'],
            item['quantity'],
            f"₹{item['price']:,.2f}",
            f"₹{item['amount']:,.2f}",
            f"₹{item['sgst']:,.2f}",
            f"₹{item['cgst']:,.2f}",
            f"₹{item['total']:,.2f}"
        ])
    
    # Add total row
    table_data.append([
        '',
        'Total:',
        '',
        sum(item['quantity'] for item in invoice_data['items']),
        '',
        invoice_data['sub_total_formatted'],
        invoice_data['total_sgst_formatted'],
        invoice_data['total_cgst_formatted'],
        invoice_data['grand_total_formatted']
    ])
    
    col_widths = [0.7*cm, 6*cm, 1.8*cm, 0.8*cm, 1.8*cm, 2*cm, 1.8*cm, 1.8*cm, 2*cm]
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Alignment for specific columns
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Quantity
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Rate
        ('ALIGN', (5, 1), (8, -1), 'RIGHT'),   # Amount, SGST, CGST, Total
        
        # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    elements.append(items_table)
    
    # Amount in words
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(f"Amount in words: {invoice_data['grand_total_words']}", styles['TableCell']))
    
    # Terms and conditions
    elements.append(Spacer(1, 8*mm))
    elements.append(Paragraph("Terms and Conditions:", styles['TableHeader']))
    elements.append(Paragraph("1. Goods once sold will not be taken back or exchanged.", styles['TableCell']))
    elements.append(Paragraph("2. Warranty as per manufacturer's terms and conditions only.", styles['TableCell']))
    elements.append(Paragraph("3. All disputes are subject to local jurisdiction only.", styles['TableCell']))
    
    # Signature
    elements.append(Spacer(1, 1.5*cm))
    sig_table = Table([
        ['For ' + invoice_data['seller_name'], 'Received the above goods in good condition'],
        ['Authorized Signatory', 'Customer Signature']
    ], colWidths=[8.5*cm, 8.5*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (1, 1), 'CENTER'),
        ('FONTNAME', (0, 1), (1, 1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (1, -1), 'BOTTOM'),
    ]))
    elements.append(sig_table)
    
    # Build the PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

def get_pdf_download_link(pdf_buffer, filename="invoice.pdf"):
    """
    Generate a download link for the PDF.
    
    Parameters:
    - pdf_buffer: BytesIO buffer containing the PDF data
    - filename: Name for the downloaded file
    
    Returns:
    - HTML download link
    """
    pdf_data = pdf_buffer.getvalue()
    b64_pdf = base64.b64encode(pdf_data).decode()
    href = f'data:application/pdf;base64,{b64_pdf}'
    
    return href
