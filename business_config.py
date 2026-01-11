# amilie Business Configuration
# Edit this file to update your pricing and FAQ

BUSINESS_INFO = {
    "name": "amilie",
    "tagline": "Professional digital designs & VTuber models",
    "services": "logos, banners, VTuber models, and digital designs",
}

PRICING = {
    "logo": {
        "price": "$50-100",
        "description": "Custom logo design",
    },
    "banner": {
        "price": "$50-100",
        "description": "Custom banner design",
    },
    "vtuber_model_2d": {
        "price": "$200-500",
        "description": "2D VTuber model",
    },
    "vtuber_model_3d": {
        "price": "$200-500",
        "description": "3D VTuber model",
    },
    "other": {
        "price": "$200-600",
        "description": "Other digital services",
    },
}

FAQ = {
    "delivery_time": "4-5 business days",
    "revisions": "4 revisions included",
    "payment_methods": "PayPal, Stripe, and other methods",
    "rush_orders": "Rush orders are not available at the moment",
    "refund_policy": "Please contact us to discuss refund options",
}

# Build pricing text for AI context
def get_pricing_text():
    text = "PRICING:\n"
    for service, info in PRICING.items():
        text += f"- {service.replace('_', ' ').title()}: {info['price']}\n"
    return text

def get_faq_text():
    text = "FAQ:\n"
    text += f"- Delivery time: {FAQ['delivery_time']}\n"
    text += f"- Revisions: {FAQ['revisions']}\n"
    text += f"- Payment methods: {FAQ['payment_methods']}\n"
    text += f"- Rush orders: {FAQ['rush_orders']}\n"
    return text

def get_full_context():
    return f"""
Business: {BUSINESS_INFO['name']}
Services: {BUSINESS_INFO['services']}

{get_pricing_text()}
{get_faq_text()}
"""
