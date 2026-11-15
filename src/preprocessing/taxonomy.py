"""
AutoSense - Locked Automotive Aspect Taxonomy
Defines the canonical 8 aspect categories, subcategories, and aspect mapping lexicon
for Aspect-Based Sentiment Analysis (ABSA).
"""

AUTOMOTIVE_TAXONOMY = {
    "Performance": {
        "subcategories": ["Engine", "Acceleration", "Braking", "Handling", "Transmission"],
        "keywords": [
            "engine", "acceleration", "braking", "handling", "transmission", "torque",
            "gearbox", "clutch", "horsepower", "pickup", "speed", "drive", "drivetrain",
            "overtaking", "steering", "stability", "brakes", "gear shift", "power", "turbo"
        ]
    },
    "Economy": {
        "subcategories": ["Mileage", "Fuel Consumption", "Running Cost"],
        "keywords": [
            "mileage", "fuel consumption", "running cost", "fuel economy", "efficiency",
            "kmpl", "fuel average", "petrol cost", "diesel cost", "battery range",
            "charging cost", "ev range", "consumption", "fuel tank", "cost per km"
        ]
    },
    "Comfort": {
        "subcategories": ["Seats", "Legroom", "Suspension", "Cabin Space"],
        "keywords": [
            "seats", "legroom", "suspension", "cabin space", "headroom", "knee room",
            "seating", "cushioning", "ride quality", "bumps", "smooth ride", "plush",
            "lumbar support", "boot space", "noise insulation", "nvh", "quiet cabin"
        ]
    },
    "Technology": {
        "subcategories": ["Infotainment", "Navigation", "Bluetooth", "Connectivity"],
        "keywords": [
            "infotainment", "navigation", "bluetooth", "connectivity", "touchscreen",
            "android auto", "apple carplay", "sound system", "speakers", "gps",
            "usb", "wireless charger", "cluster", "digital display", "voice commands"
        ]
    },
    "Safety": {
        "subcategories": ["Airbags", "ABS", "ADAS", "Safety Rating"],
        "keywords": [
            "airbags", "abs", "adas", "safety rating", "ncap", "crash test", "esp",
            "traction control", "hill assist", "seatbelt", "emergency braking",
            "blind spot", "lane assist", "build quality", "sheet metal"
        ]
    },
    "Design": {
        "subcategories": ["Interior", "Exterior", "Paint", "Styling"],
        "keywords": [
            "interior", "exterior", "paint", "styling", "looks", "dashboard",
            "finish", "alloys", "grille", "headlights", "led drl", "body line",
            "curves", "aesthetic", "fit and finish", "plastics", "upholstery"
        ]
    },
    "Ownership": {
        "subcategories": ["Service", "Maintenance", "Reliability", "Spare Parts"],
        "keywords": [
            "service", "maintenance", "reliability", "spare parts", "service center",
            "dealership", "warranty", "after sales", "breakdown", "servicing",
            "parts availability", "mechanic", "durability", "trouble free"
        ]
    },
    "Value": {
        "subcategories": ["Price", "Features", "Resale Value"],
        "keywords": [
            "price", "features", "resale value", "value for money", "vfm", "pricing",
            "expensive", "affordable", "on road price", "segment features",
            "worth it", "costly", "depreciation", "budget"
        ]
    }
}

ASPECT_SENTIMENT_TRIGGERS = {
    "positive": [
        "good", "great", "excellent", "superb", "smooth", "responsive", "comfortable",
        "reliable", "premium", "spacious", "impressive", "best", "love", "satisfactory",
        "quick", "solid", "economical", "punchy", "refined", "top notch", "fantastic"
    ],
    "negative": [
        "poor", "bad", "terrible", "noisy", "sluggish", "lag", "stiff", "uncomfortable",
        "disappointing", "expensive", "costly", "complaint", "vibration", "defect",
        "faulty", "cheap", "rough", "rattle", "delayed", "horrible", "worst", "leak"
    ]
}

def get_taxonomy_summary():
    """Returns structured metadata of the locked 8 aspect categories."""
    summary = []
    for cat, data in AUTOMOTIVE_TAXONOMY.items():
        summary.append({
            "category": cat,
            "subcategories": data["subcategories"],
            "keyword_count": len(data["keywords"]),
            "sample_keywords": data["keywords"][:4]
        })
    return summary
