"""
This module provides the mobile phone database for the invoice generator application.
It contains comprehensive data about various mobile phone models from different brands.
"""

# Mobile phone database with details for various brands and models
MOBILE_DATABASE = {
    "Samsung": [
        {
            "model": "Galaxy S23 Ultra",
            "storage": "256GB",
            "color": "Phantom Black",
            "price": 124999.00,
            "hsn_code": "85171290",
            "description": "6.8\" QHD+ Dynamic AMOLED, Snapdragon 8 Gen 2, 12GB RAM, 200MP camera",
            "stock": 15
        },
        {
            "model": "Galaxy S23",
            "storage": "128GB",
            "color": "Green",
            "price": 74999.00,
            "hsn_code": "85171290",
            "description": "6.1\" FHD+ Dynamic AMOLED, Snapdragon 8 Gen 2, 8GB RAM, 50MP camera",
            "stock": 25
        },
        {
            "model": "Galaxy Z Fold 5",
            "storage": "512GB",
            "color": "Cream",
            "price": 164999.00,
            "hsn_code": "85171290",
            "description": "7.6\" Main + 6.2\" Cover AMOLED, Snapdragon 8 Gen 2, 12GB RAM",
            "stock": 8
        },
        {
            "model": "Galaxy A54",
            "storage": "128GB",
            "color": "Awesome Violet",
            "price": 38999.00,
            "hsn_code": "85171290",
            "description": "6.4\" FHD+ Super AMOLED, Exynos 1380, 8GB RAM, 50MP camera",
            "stock": 30
        },
        {
            "model": "Galaxy M34",
            "storage": "128GB",
            "color": "Midnight Blue",
            "price": 18999.00,
            "hsn_code": "85171290",
            "description": "6.5\" FHD+ Super AMOLED, Exynos 1280, 6GB RAM, 50MP camera",
            "stock": 45
        }
    ],
    "Apple": [
        {
            "model": "iPhone 15 Pro Max",
            "storage": "256GB",
            "color": "Natural Titanium",
            "price": 159900.00,
            "hsn_code": "85171290",
            "description": "6.7\" Super Retina XDR, A17 Pro, 8GB RAM, 48MP camera",
            "stock": 10
        },
        {
            "model": "iPhone 15",
            "storage": "128GB",
            "color": "Blue",
            "price": 79900.00,
            "hsn_code": "85171290",
            "description": "6.1\" Super Retina XDR, A16 Bionic, 6GB RAM, 48MP camera",
            "stock": 20
        },
        {
            "model": "iPhone 14",
            "storage": "128GB",
            "color": "Midnight",
            "price": 69900.00,
            "hsn_code": "85171290",
            "description": "6.1\" Super Retina XDR, A15 Bionic, 6GB RAM, 12MP camera",
            "stock": 25
        },
        {
            "model": "iPhone 13",
            "storage": "128GB",
            "color": "Starlight",
            "price": 59900.00,
            "hsn_code": "85171290",
            "description": "6.1\" Super Retina XDR, A15 Bionic, 4GB RAM, 12MP camera",
            "stock": 15
        },
        {
            "model": "iPhone SE (2022)",
            "storage": "64GB",
            "color": "Red",
            "price": 49900.00,
            "hsn_code": "85171290",
            "description": "4.7\" Retina HD, A15 Bionic, 4GB RAM, 12MP camera",
            "stock": 30
        }
    ],
    "Oppo": [
        {
            "model": "Find X6 Pro",
            "storage": "256GB",
            "color": "Black",
            "price": 69990.00,
            "hsn_code": "85171290",
            "description": "6.82\" LTPO AMOLED, Snapdragon 8 Gen 2, 12GB RAM, 50MP camera",
            "stock": 12
        },
        {
            "model": "Reno 10 Pro+",
            "storage": "256GB",
            "color": "Glossy Purple",
            "price": 54999.00,
            "hsn_code": "85171290",
            "description": "6.7\" AMOLED, Snapdragon 8+ Gen 1, 12GB RAM, 50MP camera",
            "stock": 18
        },
        {
            "model": "F23",
            "storage": "128GB",
            "color": "Cool Black",
            "price": 24999.00,
            "hsn_code": "85171290",
            "description": "6.72\" LCD, Snapdragon 695, 8GB RAM, 64MP camera",
            "stock": 25
        },
        {
            "model": "A78",
            "storage": "128GB",
            "color": "Aqua Green",
            "price": 18999.00,
            "hsn_code": "85171290",
            "description": "6.67\" LCD, MediaTek Helio G85, 8GB RAM, 50MP camera",
            "stock": 32
        }
    ],
    "Vivo": [
        {
            "model": "X90 Pro",
            "storage": "256GB",
            "color": "Legend Black",
            "price": 84999.00,
            "hsn_code": "85171290",
            "description": "6.78\" AMOLED, MediaTek Dimensity 9200, 12GB RAM, 50MP camera",
            "stock": 10
        },
        {
            "model": "V29 Pro",
            "storage": "256GB",
            "color": "Himalayan Blue",
            "price": 39999.00,
            "hsn_code": "85171290",
            "description": "6.78\" AMOLED, MediaTek Dimensity 8200, 8GB RAM, 50MP camera",
            "stock": 20
        },
        {
            "model": "T2",
            "storage": "128GB",
            "color": "Nitro Blue",
            "price": 18999.00,
            "hsn_code": "85171290",
            "description": "6.38\" AMOLED, Snapdragon 695, 6GB RAM, 64MP camera",
            "stock": 25
        },
        {
            "model": "Y36",
            "storage": "128GB",
            "color": "Meteor Black",
            "price": 14999.00,
            "hsn_code": "85171290",
            "description": "6.64\" LCD, Snapdragon 680, 4GB RAM, 50MP camera",
            "stock": 35
        }
    ],
    "Redmi": [
        {
            "model": "Note 13 Pro+",
            "storage": "256GB",
            "color": "Fusion White",
            "price": 29999.00,
            "hsn_code": "85171290",
            "description": "6.67\" AMOLED, MediaTek Dimensity 1080, 8GB RAM, 200MP camera",
            "stock": 22
        },
        {
            "model": "Note 13",
            "storage": "128GB",
            "color": "Coral Purple",
            "price": 17999.00,
            "hsn_code": "85171290",
            "description": "6.67\" AMOLED, Snapdragon 685, 6GB RAM, 108MP camera",
            "stock": 30
        },
        {
            "model": "12",
            "storage": "128GB",
            "color": "Moonstone Silver",
            "price": 24999.00,
            "hsn_code": "85171290",
            "description": "6.28\" AMOLED, Snapdragon 8 Gen 1, 8GB RAM, 50MP camera",
            "stock": 15
        },
        {
            "model": "A2+",
            "storage": "64GB",
            "color": "Sea Green",
            "price": 8999.00,
            "hsn_code": "85171290",
            "description": "6.52\" HD+ LCD, MediaTek Helio G36, 4GB RAM, 8MP camera",
            "stock": 40
        }
    ],
    "Realme": [
        {
            "model": "GT 5",
            "storage": "256GB",
            "color": "Parrot Blue",
            "price": 59999.00,
            "hsn_code": "85171290",
            "description": "6.78\" AMOLED, Snapdragon 8 Gen 2, 16GB RAM, 50MP camera",
            "stock": 10
        },
        {
            "model": "11 Pro+",
            "storage": "256GB",
            "color": "Sunrise Beige",
            "price": 27999.00,
            "hsn_code": "85171290",
            "description": "6.7\" AMOLED, MediaTek Dimensity 7050, 8GB RAM, 50MP camera",
            "stock": 18
        },
        {
            "model": "Narzo 60",
            "storage": "128GB",
            "color": "Mars Orange",
            "price": 17999.00,
            "hsn_code": "85171290",
            "description": "6.43\" AMOLED, MediaTek Dimensity 6020, 6GB RAM, 64MP camera",
            "stock": 25
        },
        {
            "model": "C53",
            "storage": "128GB",
            "color": "Champion Gold",
            "price": 10999.00,
            "hsn_code": "85171290",
            "description": "6.74\" LCD, Unisoc T612, 4GB RAM, 50MP camera",
            "stock": 35
        }
    ]
}

def get_all_brands():
    """Return a list of all available brands."""
    return list(MOBILE_DATABASE.keys())

def get_models_by_brand(brand):
    """Return all models for a specific brand."""
    return MOBILE_DATABASE.get(brand, [])

def search_phones(query):
    """Search phones by brand, model, or description."""
    results = []
    query = query.lower()
    
    for brand, models in MOBILE_DATABASE.items():
        for phone in models:
            if (query in brand.lower() or 
                query in phone["model"].lower() or 
                query in phone["description"].lower() or
                query in phone["color"].lower()):
                # Add brand to the phone dict for easier display
                phone_with_brand = phone.copy()
                phone_with_brand["brand"] = brand
                results.append(phone_with_brand)
    
    return results

def get_phone_details(brand, model, storage, color):
    """Get detailed information for a specific phone model."""
    for phone in MOBILE_DATABASE.get(brand, []):
        if (phone["model"] == model and 
            phone["storage"] == storage and 
            phone["color"] == color):
            return phone
    return None

def update_stock(brand, model, storage, color, quantity=1):
    """Update stock after selling phones."""
    for phone in MOBILE_DATABASE.get(brand, []):
        if (phone["model"] == model and 
            phone["storage"] == storage and 
            phone["color"] == color):
            if phone["stock"] >= quantity:
                phone["stock"] -= quantity
                return True
            else:
                return False
    return False
