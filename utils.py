"""
Utility functions for the mobile invoice generator application.
"""
import datetime
import random
import string

def generate_invoice_number():
    """Generate a unique invoice number based on date and random chars."""
    date_prefix = datetime.datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"INV-{date_prefix}-{random_suffix}"

def calculate_gst(price, rate=18):
    """
    Calculate GST amount based on price and rate.
    
    Parameters:
    - price: Base price before tax
    - rate: GST rate in percentage (default is 18%)
    
    Returns a tuple containing (SGST, CGST, total)
    """
    # GST in India is split equally between SGST (State) and CGST (Central)
    gst_amount = (price * rate) / 100
    sgst = gst_amount / 2
    cgst = gst_amount / 2
    total = price + gst_amount
    
    return (sgst, cgst, total)

def format_currency(amount):
    """Format amount as Indian Rupees."""
    return f"₹{amount:,.2f}"

def generate_hsn_code():
    """Generate a sample HSN code for mobile phones if not provided."""
    return "85171290"  # Default HSN code for mobile phones

def validate_phone_number(phone):
    """Validate if the phone number is in correct Indian format."""
    if phone and phone.isdigit() and len(phone) == 10:
        return True
    return False

def validate_gstin(gstin):
    """
    Validate if the GSTIN (Goods and Services Tax Identification Number) is in correct format.
    
    Basic validation for 15-character GSTIN
    """
    if gstin and len(gstin) == 15 and gstin[:2].isdigit() and gstin[2:12].isalnum():
        return True
    return False

def validate_email(email):
    """Basic email validation."""
    if email and '@' in email and '.' in email.split('@')[1]:
        return True
    return False

def state_code_from_gstin(gstin):
    """Extract state code from GSTIN."""
    if gstin and len(gstin) >= 2:
        return gstin[:2]
    return "00"  # Default state code

def get_state_name(state_code):
    """Get state name from state code."""
    state_codes = {
        "01": "Jammu & Kashmir",
        "02": "Himachal Pradesh",
        "03": "Punjab",
        "04": "Chandigarh",
        "05": "Uttarakhand",
        "06": "Haryana",
        "07": "Delhi",
        "08": "Rajasthan",
        "09": "Uttar Pradesh",
        "10": "Bihar",
        "11": "Sikkim",
        "12": "Arunachal Pradesh",
        "13": "Nagaland",
        "14": "Manipur",
        "15": "Mizoram",
        "16": "Tripura",
        "17": "Meghalaya",
        "18": "Assam",
        "19": "West Bengal",
        "20": "Jharkhand",
        "21": "Odisha",
        "22": "Chhattisgarh",
        "23": "Madhya Pradesh",
        "24": "Gujarat",
        "25": "Daman & Diu",
        "26": "Dadra & Nagar Haveli",
        "27": "Maharashtra",
        "28": "Andhra Pradesh (Before bifurcation)",
        "29": "Karnataka",
        "30": "Goa",
        "31": "Lakshadweep",
        "32": "Kerala",
        "33": "Tamil Nadu",
        "34": "Puducherry",
        "35": "Andaman & Nicobar Islands",
        "36": "Telangana",
        "37": "Andhra Pradesh (After bifurcation)",
        "38": "Ladakh",
        "97": "Other Territory",
        "99": "Centre Jurisdiction"
    }
    return state_codes.get(state_code, "Unknown State")
