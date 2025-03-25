"""
Mobile Shop Invoice Generator
A Streamlit application for generating GST/CGST compliant invoices for mobile phone sales.
"""
import streamlit as st
import pandas as pd
import datetime
import os
import base64
from mobile_data import (
    get_all_brands, get_models_by_brand, 
    search_phones, get_phone_details, 
    update_stock
)
from invoice_generator import Invoice, InvoiceItem
from pdf_generator import create_invoice_pdf, get_pdf_download_link
from utils import (
    validate_phone_number, validate_gstin, 
    validate_email, format_currency,
    state_code_from_gstin, get_state_name
)

# Set page configuration
st.set_page_config(
    page_title="Mobile Shop Invoice Generator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f'<style>{f.read()}</style>'
        st.markdown(css, unsafe_allow_html=True)

load_css('' 'style.css')

# Helper function for showing brand logos as colored badge
def get_brand_logo_html(brand, width=120):
    brand_colors = {
        'samsung': '#1428a0',
        'apple': '#000000',
        'oppo': '#025e3b',
        'vivo': '#415fff',
        'redmi': '#ff6700',
        'realme': '#ffc803'
    }
    
    brand_lower = brand.lower()
    color = brand_colors.get(brand_lower, '#0066ff')
    text_color = '#ffffff' if brand_lower != 'realme' else '#000000'
    
    return f'<div style="background-color: {color}; color: {text_color}; width: {width}px; height: 40px; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-weight: bold;">{brand.upper()}</div>'

# Custom function for buttons with specific styling
def styled_button(label, key, button_type="primary", on_click=None):
    col = st.container()
    with col:
        st.markdown(f'<div class="{button_type}-button">', unsafe_allow_html=True)
        clicked = st.button(label, key=key, on_click=on_click)
        st.markdown('</div>', unsafe_allow_html=True)
    return clicked

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'invoice' not in st.session_state:
    st.session_state.invoice = None
if 'invoice_pdf' not in st.session_state:
    st.session_state.invoice_pdf = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Logo and title
st.markdown('<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 4])
with col1:
    st.image("assets/logo.svg", width=120)
with col2:
    st.markdown('<h1 class="main-title">Mobile Shop Invoice Generator</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-title">Generate GST-compliant invoices for mobile phone sales</h3>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for search and navigation
with st.sidebar:
    st.markdown('<div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 15px;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #0066ff; margin-bottom: 10px;">📱 Product Search</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    search_tab, browse_tab = st.tabs(["🔎 Search", "📋 Browse"])
    
    with search_tab:
        st.markdown('<div class="section-container" style="background-color: white;">', unsafe_allow_html=True)
        search_query = st.text_input("Search by brand, model, or specifications:", placeholder="iPhone, Samsung Galaxy, etc...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if search_query:
            st.session_state.search_results = search_phones(search_query)
            
            if st.session_state.search_results:
                st.markdown(f'<div class="badge badge-success">Found {len(st.session_state.search_results)} results</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge badge-warning">No results found</div>', unsafe_allow_html=True)
    
    with browse_tab:
        st.markdown('<div class="section-container" style="background-color: white;">', unsafe_allow_html=True)
        # Brand selector with logos
        st.markdown("<p>Select a brand:</p>", unsafe_allow_html=True)
        all_brands = get_all_brands()
        
        # Display brand logos as a gallery
        brand_cols = st.columns(2)
        for i, brand in enumerate(all_brands):
            with brand_cols[i % 2]:
                st.markdown(f'<div style="text-align: center; margin-bottom: 10px; cursor: pointer;" '
                           f'onclick="document.querySelector(\'[data-testid=stSelectbox] select\').value=\'{brand}\'; '
                           f'document.querySelector(\'[data-testid=stSelectbox] select\').dispatchEvent(new Event(\'change\'));">'
                           f'{get_brand_logo_html(brand, width=80)}</div>', unsafe_allow_html=True)
        
        # Hidden actual selector
        selected_brand = st.selectbox("Select Brand:", all_brands, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if selected_brand:
            models = get_models_by_brand(selected_brand)
            st.session_state.search_results = [
                {**model, "brand": selected_brand} for model in models
            ]
            st.markdown(f'<div class="badge badge-primary">{len(models)} {selected_brand} models available</div>', unsafe_allow_html=True)
    
    # Cart summary in sidebar
    st.markdown('<div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 20px 0 15px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #0066ff; margin-bottom: 10px;">🛒 Cart Summary</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        total_amount = sum(item['quantity'] * item['price'] for item in st.session_state.cart)
        
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-label">Items</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(st.session_state.cart)}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-label">Total</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{format_currency(total_amount)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="danger-button" style="margin-top: 10px;">', unsafe_allow_html=True)
        if st.button("Clear Cart 🗑️"):
            st.session_state.cart = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-container" style="text-align: center; padding: 20px;">', unsafe_allow_html=True)
        st.markdown('🛒', unsafe_allow_html=True)
        st.markdown('<p style="color: #666;">Your cart is empty</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown('<div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 20px 0 15px 0;">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #0066ff; margin-bottom: 10px;">📃 Navigation</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="primary-button">', unsafe_allow_html=True)
        if st.button("📱 Products"):
            st.session_state.page = "products"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
        if st.button("🛍️ Checkout"):
            st.session_state.page = "checkout"
            if not st.session_state.cart:
                st.warning("Add items to cart first!")
            else:
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Main content
if 'page' not in st.session_state:
    st.session_state.page = "products"

if st.session_state.page == "products":
    st.markdown('<h2 style="color: #0066ff; margin-bottom: 20px;">📱 Available Products</h2>', unsafe_allow_html=True)
    
    # Display search results or browse results
    if st.session_state.search_results:
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.search_results)
        
        # Display sorting options
        st.markdown('<div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
        sort_col1, sort_col2 = st.columns([3, 1])
        with sort_col1:
            st.markdown('<span style="color: #666; font-size: 0.9rem;">Sort products by:</span>', unsafe_allow_html=True)
        with sort_col2:
            sort_option = st.selectbox(
                "Sort by", 
                ["Price: Low to High", "Price: High to Low", "Brand", "Model", "Storage"],
                label_visibility="collapsed"
            )
        
        # Sort the results based on selection
        if sort_option == "Price: Low to High":
            st.session_state.search_results = sorted(st.session_state.search_results, key=lambda x: x['price'])
        elif sort_option == "Price: High to Low":
            st.session_state.search_results = sorted(st.session_state.search_results, key=lambda x: x['price'], reverse=True)
        elif sort_option == "Brand":
            st.session_state.search_results = sorted(st.session_state.search_results, key=lambda x: x['brand'])
        elif sort_option == "Model":
            st.session_state.search_results = sorted(st.session_state.search_results, key=lambda x: x['model'])
        elif sort_option == "Storage":
            st.session_state.search_results = sorted(st.session_state.search_results, key=lambda x: x['storage'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create a grid layout for products
        cols_per_row = 2
        rows = [st.columns(cols_per_row) for _ in range((len(st.session_state.search_results) + cols_per_row - 1) // cols_per_row)]
        
        # For each result, show in a card-like format
        for i, row in enumerate(st.session_state.search_results):
            col_idx = i % cols_per_row
            row_idx = i // cols_per_row
            
            with rows[row_idx][col_idx]:
                # Card container
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # Header with brand logo and model
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                    f'<div style="flex: 0 0 80px; text-align: center;">{get_brand_logo_html(row["brand"], width=60)}</div>'
                    f'<div style="flex-grow: 1;"><h3 style="margin: 0; color: #333;">{row["model"]}</h3>'
                    f'<div style="font-size: 0.8rem; color: #666;">HSN: {row["hsn_code"]}</div></div>'
                    f'</div>', 
                    unsafe_allow_html=True
                )
                
                # Product details
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(
                        f'<div class="badge badge-primary">{row["storage"]}</div> '
                        f'<div class="badge badge-success">{row["color"]}</div>',
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(
                        f'<div style="text-align: right; font-size: 1.2rem; font-weight: bold; color: #0066ff;">'
                        f'{format_currency(row["price"])}</div>',
                        unsafe_allow_html=True
                    )
                
                # Description
                st.markdown(
                    f'<div style="margin: 10px 0; font-size: 0.9rem; color: #444;">{row["description"]}</div>',
                    unsafe_allow_html=True
                )
                
                # Stock information
                stock_color = "#4CAF50" if row["stock"] > 5 else "#ff9800" if row["stock"] > 0 else "#f44336"
                st.markdown(
                    f'<div style="font-size: 0.8rem; margin-bottom: 10px;">'
                    f'<span style="color: {stock_color}; font-weight: bold;">● </span>'
                    f'<span style="color: #666;">Stock: {row["stock"]} units</span></div>',
                    unsafe_allow_html=True
                )
                
                # Add to cart section
                quantity_col, button_col = st.columns([1, 2])
                
                with quantity_col:
                    quantity = st.number_input(
                        "Qty", 
                        min_value=1, 
                        max_value=row['stock'], 
                        value=1,
                        key=f"qty_{i}"
                    )
                
                with button_col:
                    st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
                    add_button = st.button("Add to Cart 🛒", key=f"add_{i}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if add_button:
                        # Create a new item for the cart
                        cart_item = {
                            'brand': row['brand'],
                            'model': row['model'],
                            'storage': row['storage'],
                            'color': row['color'],
                            'price': row['price'],
                            'hsn_code': row['hsn_code'],
                            'quantity': quantity,
                            'description': row['description']
                        }
                        
                        # Check if this item is already in cart
                        existing_item = None
                        for j, item in enumerate(st.session_state.cart):
                            if (item['brand'] == cart_item['brand'] and
                                item['model'] == cart_item['model'] and
                                item['storage'] == cart_item['storage'] and
                                item['color'] == cart_item['color']):
                                existing_item = j
                                break
                        
                        if existing_item is not None:
                            # Update existing item
                            st.session_state.cart[existing_item]['quantity'] += quantity
                        else:
                            # Add new item
                            st.session_state.cart.append(cart_item)
                        
                        st.success(f"Added {quantity} {row['brand']} {row['model']} to cart!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Empty state with brand logos
        st.markdown('<div style="text-align: center; padding: 40px; background-color: #f9f9f9; border-radius: 10px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 48px; color: #ccc; margin-bottom: 20px;">🔍</div>', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #666; margin: 20px 0;">Search for products or select a brand to browse</h3>', unsafe_allow_html=True)
        
        # Display all brand logos
        brand_cols = st.columns(3)
        for i, brand in enumerate(get_all_brands()):
            with brand_cols[i % 3]:
                st.markdown(f'<div style="text-align: center; margin: 10px;">{get_brand_logo_html(brand, width=80)}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "checkout":
    st.markdown('<h2 style="color: #0066ff; margin-bottom: 20px;">🛒 Checkout</h2>', unsafe_allow_html=True)
    
    # Display cart items
    if st.session_state.cart:
        # Step indicator
        st.markdown(
            '<div style="display: flex; margin-bottom: 30px; background-color: #f8f9fa; padding: 15px; border-radius: 10px;">'
            '<div style="flex: 1; text-align: center; position: relative;">'
            '<div style="background-color: #0066ff; color: white; width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 5px;">1</div>'
            '<div style="font-size: 0.9rem; font-weight: bold; color: #0066ff;">Cart</div>'
            '<div style="height: 3px; background-color: #0066ff; position: absolute; top: 15px; right: 0; width: 50%;"></div>'
            '</div>'
            '<div style="flex: 1; text-align: center; position: relative;">'
            '<div style="background-color: #0066ff; color: white; width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 5px;">2</div>'
            '<div style="font-size: 0.9rem; font-weight: bold; color: #0066ff;">Information</div>'
            '<div style="height: 3px; background-color: #0066ff; position: absolute; top: 15px; left: 0; width: 50%;"></div>'
            '<div style="height: 3px; background-color: #ddd; position: absolute; top: 15px; right: 0; width: 50%;"></div>'
            '</div>'
            '<div style="flex: 1; text-align: center; position: relative;">'
            '<div style="background-color: #ddd; color: #666; width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 5px;">3</div>'
            '<div style="font-size: 0.9rem; color: #666;">Invoice</div>'
            '<div style="height: 3px; background-color: #ddd; position: absolute; top: 15px; left: 0; width: 50%;"></div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Cart items display
        st.markdown('<div class="section-container" style="background-color: white; margin-bottom: 30px;">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-bottom: 15px;">Items in Your Cart</h3>', unsafe_allow_html=True)
        
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df['Amount'] = cart_df['price'] * cart_df['quantity']
        
        # Custom cart display with item cards instead of table
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(
                    f'<div style="display: flex; align-items: center;">'
                    f'<div style="flex: 0 0 60px; text-align: center;">{get_brand_logo_html(item["brand"], width=50)}</div>'
                    f'<div style="flex-grow: 1;">'
                    f'<div style="font-weight: bold;">{item["brand"]} {item["model"]}</div>'
                    f'<div style="font-size: 0.8rem; color: #666;">{item["storage"]} | {item["color"]}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    f'<div style="text-align: center;">'
                    f'<div style="font-size: 0.8rem; color: #666;">Price × Quantity</div>'
                    f'<div>{format_currency(item["price"])} × {item["quantity"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col3:
                amount = item["price"] * item["quantity"]
                st.markdown(
                    f'<div style="text-align: right; font-weight: bold;">'
                    f'{format_currency(amount)}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            if i < len(st.session_state.cart) - 1:
                st.markdown('<hr style="margin: 10px 0; border-color: #f0f0f0;">', unsafe_allow_html=True)
        
        # Total calculation
        subtotal = cart_df['Amount'].sum()
        gst_rate = 18
        sgst_rate = cgst_rate = gst_rate / 2
        sgst_amount = cgst_amount = (subtotal * sgst_rate) / 100
        total = subtotal + (sgst_amount + cgst_amount)
        
        st.markdown('<div style="margin-top: 20px; border-top: 1px solid #ddd; padding-top: 15px;">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 2])
        
        with col2:
            st.markdown(
                f'<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">'
                f'<span style="color: #666;">Subtotal:</span>'
                f'<span>{format_currency(subtotal)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                f'<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">'
                f'<span style="color: #666;">SGST ({int(sgst_rate)}%):</span>'
                f'<span>{format_currency(sgst_amount)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                f'<div style="display: flex; justify-content: space-between; margin-bottom: 5px;">'
                f'<span style="color: #666;">CGST ({int(cgst_rate)}%):</span>'
                f'<span>{format_currency(cgst_amount)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                f'<div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 1.1rem; margin-top: 10px; padding-top: 10px; border-top: 1px dashed #ddd;">'
                f'<span>Total:</span>'
                f'<span style="color: #0066ff;">{format_currency(total)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Customer Information Form
        st.markdown('<div class="section-container" style="background-color: white;">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-bottom: 20px;">Customer Information</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 15px;">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 1rem; margin-bottom: 15px;">Personal Details</h4>', unsafe_allow_html=True)
            customer_name = st.text_input("Full Name*", key="name", placeholder="Enter customer's full name")
            customer_phone = st.text_input("Phone Number*", key="phone", placeholder="10-digit mobile number")
            customer_email = st.text_input("Email Address", key="email", placeholder="email@example.com (optional)")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 15px;">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 1rem; margin-bottom: 15px;">Billing Details</h4>', unsafe_allow_html=True)
            customer_address = st.text_area("Full Address*", key="address", placeholder="Enter complete address with pincode")
            customer_gstin = st.text_input("GSTIN", key="gstin", placeholder="15-character GSTIN (if applicable)")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit order button
        st.markdown('<div style="text-align: center; margin-top: 30px;">', unsafe_allow_html=True)
        st.markdown('<div class="primary-button" style="display: inline-block; width: 250px;">', unsafe_allow_html=True)
        generate_button = st.button("Generate Invoice 📄")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if generate_button:
            # Validate form
            errors = []
            
            if not customer_name:
                errors.append("Customer name is required")
            
            if not customer_phone or not validate_phone_number(customer_phone):
                errors.append("Valid phone number is required (10 digits)")
            
            if not customer_address:
                errors.append("Customer address is required")
            
            if customer_email and not validate_email(customer_email):
                errors.append("Please provide a valid email address")
            
            if customer_gstin and not validate_gstin(customer_gstin):
                errors.append("Please provide a valid GSTIN (15 characters)")
            
            if errors:
                st.markdown('<div style="background-color: #ffebee; padding: 15px; border-radius: 10px; margin-top: 20px;">', unsafe_allow_html=True)
                st.markdown('<h4 style="color: #f44336; margin-bottom: 10px;">Please fix the following errors:</h4>', unsafe_allow_html=True)
                for error in errors:
                    st.markdown(f'<div style="color: #f44336; margin-bottom: 5px;">• {error}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Create invoice with progress indicator
                progress_placeholder = st.empty()
                progress_placeholder.markdown(
                    '<div style="background-color: #e7f6e7; padding: 15px; border-radius: 10px; text-align: center;">'
                    '<div class="loading-animation" style="font-size: 1.1rem; color: #4CAF50; margin-bottom: 10px;">Processing invoice...</div>'
                    '<div style="font-size: 0.9rem; color: #666;">This may take a few moments</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
                
                # Create invoice
                invoice = Invoice(
                    customer_name=customer_name,
                    customer_address=customer_address,
                    customer_phone=customer_phone,
                    customer_email=customer_email,
                    customer_gstin=customer_gstin
                )
                
                # Add items to invoice
                for item in st.session_state.cart:
                    invoice_item = InvoiceItem(
                        brand=item['brand'],
                        model=item['model'],
                        storage=item['storage'],
                        color=item['color'],
                        price=item['price'],
                        hsn_code=item['hsn_code'],
                        quantity=item['quantity']
                    )
                    invoice.add_item(invoice_item)
                    
                    # Update stock
                    update_stock(
                        item['brand'], 
                        item['model'], 
                        item['storage'], 
                        item['color'], 
                        item['quantity']
                    )
                
                # Store invoice in session state
                st.session_state.invoice = invoice.to_dict()
                
                # Generate PDF
                pdf_buffer = create_invoice_pdf(st.session_state.invoice)
                st.session_state.invoice_pdf = pdf_buffer
                
                # Change page to invoice view
                st.session_state.page = "invoice"
                st.rerun()
    else:
        # Empty cart display
        st.markdown(
            '<div style="text-align: center; padding: 50px; background-color: #f9f9f9; border-radius: 10px;">'
            '<div style="font-size: 64px; color: #ccc; margin-bottom: 20px;">🛒</div>'
            '<h3 style="color: #666; margin-bottom: 30px;">Your cart is empty</h3>'
            '<div class="primary-button" style="width: 200px; margin: 0 auto;">'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        if st.button("Browse Products 📱"):
            st.session_state.page = "products"
            st.rerun()

elif st.session_state.page == "invoice":
    if st.session_state.invoice:
        st.markdown('<h2 style="color: #0066ff; margin-bottom: 20px;">📄 Invoice Generated</h2>', unsafe_allow_html=True)
        
        # Step indicator
        st.markdown(
            '<div style="display: flex; margin-bottom: 30px; background-color: #f8f9fa; padding: 15px; border-radius: 10px;">'
            '<div style="flex: 1; text-align: center; position: relative;">'
            '<div style="background-color: #0066ff; color: white; width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 5px;">1</div>'
            '<div style="font-size: 0.9rem; font-weight: bold; color: #0066ff;">Cart</div>'
            '<div style="height: 3px; background-color: #0066ff; position: absolute; top: 15px; right: 0; width: 50%;"></div>'
            '</div>'
            '<div style="flex: 1; text-align: center; position: relative;">'
            '<div style="background-color: #0066ff; color: white; width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 5px;">2</div>'
            '<div style="font-size: 0.9rem; font-weight: bold; color: #0066ff;">Information</div>'
            '<div style="height: 3px; background-color: #0066ff; position: absolute; top: 15px; left: 0; width: 50%;"></div>'
            '<div style="height: 3px; background-color: #0066ff; position: absolute; top: 15px; right: 0; width: 50%;"></div>'
            '</div>'
            '<div style="flex: 1; text-align: center; position: relative;">'
            '<div style="background-color: #0066ff; color: white; width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-bottom: 5px;">3</div>'
            '<div style="font-size: 0.9rem; font-weight: bold; color: #0066ff;">Invoice</div>'
            '<div style="height: 3px; background-color: #0066ff; position: absolute; top: 15px; left: 0; width: 50%;"></div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        invoice_data = st.session_state.invoice
        
        # Success message
        st.markdown(
            '<div style="background-color: #e7f6e7; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">'
            '<div style="color: #4CAF50; font-size: 24px; margin-bottom: 10px;">✓</div>'
            '<div style="font-size: 1.2rem; font-weight: bold; color: #4CAF50; margin-bottom: 5px;">Invoice Generated Successfully</div>'
            f'<div style="font-size: 0.9rem; color: #666;">Invoice #{invoice_data["invoice_number"]}</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Invoice container
        st.markdown('<div class="section-container" style="background-color: white; padding: 25px; border: 1px solid #ddd;">', unsafe_allow_html=True)
        
        # Invoice header
        st.markdown(
            '<div style="display: flex; justify-content: space-between; margin-bottom: 20px;">'
            '<div>'
            '<h1 style="color: #333; margin: 0; font-size: 24px;">TAX INVOICE</h1>'
            f'<div style="color: #666; font-size: 0.9rem; margin-top: 5px;">Invoice #{invoice_data["invoice_number"]}</div>'
            '</div>'
            '<div style="text-align: right;">'
            f'<div style="font-size: 0.9rem; color: #666;">Date: {invoice_data["date"]}</div>'
            f'<div style="font-size: 0.9rem; color: #666;">Time: {invoice_data["time"]}</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Seller and customer information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                '<div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; height: 100%;">'
                '<h3 style="font-size: 1rem; margin-bottom: 10px; color: #333;">Seller Information</h3>'
                f'<div style="font-weight: bold; margin-bottom: 5px;">{invoice_data["seller_name"]}</div>'
                f'<div style="font-size: 0.9rem; margin-bottom: 5px; color: #666;">GSTIN: {invoice_data["seller_gstin"]}</div>'
                f'<div style="font-size: 0.9rem; white-space: pre-line; color: #666;">{invoice_data["seller_address"]}</div>'
                '</div>',
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                '<div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; height: 100%;">'
                '<h3 style="font-size: 1rem; margin-bottom: 10px; color: #333;">Customer Information</h3>'
                f'<div style="font-weight: bold; margin-bottom: 5px;">{invoice_data["customer_name"]}</div>'
                f'<div style="font-size: 0.9rem; margin-bottom: 5px; color: #666;">Phone: {invoice_data["customer_phone"]}</div>'
                + (f'<div style="font-size: 0.9rem; margin-bottom: 5px; color: #666;">Email: {invoice_data["customer_email"]}</div>' if invoice_data.get("customer_email") else '') +
                f'<div style="font-size: 0.9rem; white-space: pre-line; color: #666;">{invoice_data["customer_address"]}</div>'
                + (f'<div style="font-size: 0.9rem; margin-top: 5px; color: #666;">GSTIN: {invoice_data["customer_gstin"]}</div>' if invoice_data.get("customer_gstin") else '') +
                '</div>',
                unsafe_allow_html=True
            )
        
        # Items table
        st.markdown('<h3 style="font-size: 1.1rem; margin: 20px 0 15px 0; color: #333;">Purchased Items</h3>', unsafe_allow_html=True)
        
        # Custom styled table header
        st.markdown(
            '<div style="display: flex; background-color: #f3f4f6; padding: 10px; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; font-weight: bold; font-size: 0.9rem;">'
            '<div style="flex: 3;">Description</div>'
            '<div style="flex: 1; text-align: center;">HSN</div>'
            '<div style="flex: 1; text-align: center;">Qty</div>'
            '<div style="flex: 1; text-align: right;">Rate</div>'
            '<div style="flex: 1; text-align: right;">Amount</div>'
            '<div style="flex: 1; text-align: right;">SGST (9%)</div>'
            '<div style="flex: 1; text-align: right;">CGST (9%)</div>'
            '<div style="flex: 1; text-align: right;">Total</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Table rows
        for i, item in enumerate(invoice_data['items']):
            bg_color = '#ffffff' if i % 2 == 0 else '#f9f9f9'
            st.markdown(
                f'<div style="display: flex; padding: 10px; border-bottom: 1px solid #eee; font-size: 0.9rem; background-color: {bg_color};">'
                f'<div style="flex: 3;">{item["description"]}</div>'
                f'<div style="flex: 1; text-align: center;">{item["hsn_code"]}</div>'
                f'<div style="flex: 1; text-align: center;">{item["quantity"]}</div>'
                f'<div style="flex: 1; text-align: right;">{format_currency(item["price"])}</div>'
                f'<div style="flex: 1; text-align: right;">{format_currency(item["amount"])}</div>'
                f'<div style="flex: 1; text-align: right;">{format_currency(item["sgst"])}</div>'
                f'<div style="flex: 1; text-align: right;">{format_currency(item["cgst"])}</div>'
                f'<div style="flex: 1; text-align: right;">{format_currency(item["total"])}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        # Totals section
        st.markdown(
            '<div style="display: flex; margin-top: 20px;">'
            '<div style="flex: 6;"></div>'
            '<div style="flex: 4;">'
            '<div style="border: 1px solid #ddd; border-radius: 5px; overflow: hidden;">'
            
            '<div style="display: flex; padding: 10px; border-bottom: 1px solid #eee; font-size: 0.9rem;">'
            '<div style="flex: 1; color: #666;">Subtotal:</div>'
            f'<div style="flex: 1; text-align: right;">{invoice_data["sub_total_formatted"]}</div>'
            '</div>'
            
            '<div style="display: flex; padding: 10px; border-bottom: 1px solid #eee; font-size: 0.9rem;">'
            '<div style="flex: 1; color: #666;">SGST (9%):</div>'
            f'<div style="flex: 1; text-align: right;">{invoice_data["total_sgst_formatted"]}</div>'
            '</div>'
            
            '<div style="display: flex; padding: 10px; border-bottom: 1px solid #eee; font-size: 0.9rem;">'
            '<div style="flex: 1; color: #666;">CGST (9%):</div>'
            f'<div style="flex: 1; text-align: right;">{invoice_data["total_cgst_formatted"]}</div>'
            '</div>'
            
            '<div style="display: flex; padding: 12px; background-color: #f9f9f9; font-weight: bold; font-size: 1rem;">'
            '<div style="flex: 1;">Grand Total:</div>'
            f'<div style="flex: 1; text-align: right; color: #0066ff;">{invoice_data["grand_total_formatted"]}</div>'
            '</div>'
            
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Amount in words
        st.markdown(
            '<div style="margin-top: 15px; font-size: 0.9rem; font-style: italic; color: #666;">'
            f'Amount in Words: {invoice_data["grand_total_words"]}'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Terms and conditions
        st.markdown(
            '<div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee;">'
            '<h3 style="font-size: 1rem; margin-bottom: 10px; color: #333;">Terms & Conditions</h3>'
            '<ul style="font-size: 0.85rem; color: #666; margin: 0; padding-left: 20px;">'
            '<li>Goods once sold will not be taken back or exchanged.</li>'
            '<li>All disputes are subject to local jurisdiction only.</li>'
            '<li>Warranty as per manufacturer\'s terms and conditions only.</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # Invoice footer
        st.markdown(
            '<div style="margin-top: 30px; display: flex; justify-content: space-between;">'
            '<div style="font-size: 0.85rem; color: #666;">'
            'Thank you for your business!'
            '</div>'
            '<div style="font-size: 0.85rem; color: #666; text-align: right;">'
            f'For {invoice_data["seller_name"]}<br>'
            '<div style="margin-top: 20px;">Authorized Signatory</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Actions section
        st.markdown('<div style="display: flex; justify-content: center; margin-top: 30px; gap: 20px;">', unsafe_allow_html=True)
        
        # PDF download
        if st.session_state.invoice_pdf:
            pdf_href = get_pdf_download_link(
                st.session_state.invoice_pdf,
                f"Invoice_{invoice_data['invoice_number']}.pdf"
            )
            
            st.markdown(
                f'<a href="{pdf_href}" download="Invoice_{invoice_data["invoice_number"]}.pdf" '
                f'style="display: inline-flex; align-items: center; padding: 12px 25px; color: white; background-color: #0066ff; '
                f'text-decoration: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'
                f'Download PDF</a>', 
                unsafe_allow_html=True
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="primary-button" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("Create New Invoice 📄"):
                # Reset session state
                st.session_state.cart = []
                st.session_state.invoice = None
                st.session_state.invoice_pdf = None
                st.session_state.page = "products"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="light-button" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("Print Invoice 🖨️"):
                st.markdown(
                    '<script>window.print();</script>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align: center; padding: 50px; background-color: #f9f9f9; border-radius: 10px; margin-top: 30px;">'
            '<div style="color: #f44336; font-size: 50px; margin-bottom: 20px;">!</div>'
            '<h3 style="color: #666; margin-bottom: 20px;">No invoice data found</h3>'
            '<div class="primary-button" style="width: 200px; margin: 0 auto;">'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        if st.button("Return to Products 📱"):
            st.session_state.page = "products"
            st.rerun()

# Footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown(
    '<div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0;">'
    '<div>'
    '<div style="font-weight: bold; margin-bottom: 5px;">Mobile Shop Invoice Generator</div>'
    '<div style="font-size: 0.8rem; color: #666;">GST/CGST compliant invoice solution</div>'
    '</div>'
    '<div style="text-align: center;">'
    '<div style="margin-bottom: 5px;">Quick Links</div>'
    '<div style="font-size: 0.8rem;">'
    '<a href="#" style="color: #0066ff; text-decoration: none; margin: 0 10px;">Home</a>'
    '<a href="#" style="color: #0066ff; text-decoration: none; margin: 0 10px;">Browse</a>'
    '<a href="#" style="color: #0066ff; text-decoration: none; margin: 0 10px;">Help</a>'
    '</div>'
    '</div>'
    '<div style="text-align: right;">'
    '<div style="font-size: 0.8rem; color: #666;">© 2023 Mobile Shop Invoice Generator</div>'
    '<div style="font-size: 0.8rem; color: #666;">All Rights Reserved</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)
