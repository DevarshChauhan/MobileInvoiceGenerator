"""
Module for generating invoices for the mobile shop.
Handles tax calculations and invoice item management.
"""
import datetime
from utils import calculate_gst, format_currency, generate_invoice_number, generate_hsn_code

class InvoiceItem:
    """Represents a single item in an invoice."""
    def __init__(self, brand, model, storage, color, price, hsn_code, quantity=1):
        self.brand = brand
        self.model = model
        self.storage = storage
        self.color = color
        self.price = price  # Price per unit (before tax)
        self.quantity = quantity
        self.hsn_code = hsn_code or generate_hsn_code()
        
        # Calculate taxes
        self.sgst_rate = 9  # 9% SGST
        self.cgst_rate = 9  # 9% CGST
        
        self.amount = self.price * self.quantity
        self.sgst, self.cgst, self.total = calculate_gst(self.amount, self.sgst_rate + self.cgst_rate)
    
    def get_description(self):
        """Return a detailed description of the item."""
        return f"{self.brand} {self.model} ({self.storage}, {self.color})"
    
    def to_dict(self):
        """Convert the invoice item to a dictionary for easy access."""
        return {
            "brand": self.brand,
            "model": self.model,
            "storage": self.storage,
            "color": self.color,
            "description": self.get_description(),
            "hsn_code": self.hsn_code,
            "price": self.price,
            "quantity": self.quantity,
            "amount": self.amount,
            "sgst_rate": self.sgst_rate,
            "cgst_rate": self.cgst_rate,
            "sgst": self.sgst,
            "cgst": self.cgst,
            "total": self.total
        }

class Invoice:
    """Represents a complete invoice with customer details and items."""
    def __init__(self, customer_name, customer_address, customer_phone, customer_email=None, customer_gstin=None):
        self.invoice_number = generate_invoice_number()
        self.date = datetime.datetime.now()
        
        # Customer details
        self.customer_name = customer_name
        self.customer_address = customer_address
        self.customer_phone = customer_phone
        self.customer_email = customer_email
        self.customer_gstin = customer_gstin
        
        # Seller details (can be customized)
        self.seller_name = "MobileTech Retail Solutions"
        self.seller_address = "123, Tech Park, Main Street, Bangalore - 560001, Karnataka"
        self.seller_phone = "9876543210"
        self.seller_email = "info@mobiletech.com"
        self.seller_gstin = "29AABCT1332L1ZB"  # Sample GSTIN
        
        # Items and calculations
        self.items = []
        self.sub_total = 0
        self.total_sgst = 0
        self.total_cgst = 0
        self.grand_total = 0
    
    def add_item(self, invoice_item):
        """Add an item to the invoice and update totals."""
        self.items.append(invoice_item)
        
        # Update totals
        self.sub_total += invoice_item.amount
        self.total_sgst += invoice_item.sgst
        self.total_cgst += invoice_item.cgst
        self.grand_total += invoice_item.total
    
    def to_dict(self):
        """Convert the invoice to a dictionary for easy access."""
        return {
            "invoice_number": self.invoice_number,
            "date": self.date.strftime("%d-%m-%Y"),
            "time": self.date.strftime("%H:%M:%S"),
            
            "customer_name": self.customer_name,
            "customer_address": self.customer_address,
            "customer_phone": self.customer_phone,
            "customer_email": self.customer_email,
            "customer_gstin": self.customer_gstin,
            
            "seller_name": self.seller_name,
            "seller_address": self.seller_address,
            "seller_phone": self.seller_phone,
            "seller_email": self.seller_email,
            "seller_gstin": self.seller_gstin,
            
            "items": [item.to_dict() for item in self.items],
            
            "sub_total": self.sub_total,
            "total_sgst": self.total_sgst,
            "total_cgst": self.total_cgst,
            "grand_total": self.grand_total,
            
            # Formatted currency values
            "sub_total_formatted": format_currency(self.sub_total),
            "total_sgst_formatted": format_currency(self.total_sgst),
            "total_cgst_formatted": format_currency(self.total_cgst),
            "grand_total_formatted": format_currency(self.grand_total),
            "grand_total_words": number_to_words(int(self.grand_total))
        }


def number_to_words(number):
    """Convert a number to words for the invoice."""
    units = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve',
             'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    
    def convert_less_than_thousand(number):
        if number < 20:
            return units[number]
        elif number < 100:
            return tens[number // 10] + (' ' + units[number % 10] if number % 10 != 0 else '')
        else:
            return units[number // 100] + ' Hundred' + (' and ' + convert_less_than_thousand(number % 100) if number % 100 != 0 else '')
    
    if number == 0:
        return 'Zero'
    
    result = ''
    
    # Handle crores (tens of millions)
    if number >= 10000000:
        result += convert_less_than_thousand(number // 10000000) + ' Crore '
        number %= 10000000
    
    # Handle lakhs (hundreds of thousands)
    if number >= 100000:
        result += convert_less_than_thousand(number // 100000) + ' Lakh '
        number %= 100000
    
    # Handle thousands
    if number >= 1000:
        result += convert_less_than_thousand(number // 1000) + ' Thousand '
        number %= 1000
    
    # Handle remaining part
    if number > 0:
        result += convert_less_than_thousand(number)
    
    return result.strip() + ' Rupees Only'
