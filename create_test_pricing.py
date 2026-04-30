from src.services.pricing_service import pricing_service

def setup():
    parsed_data = {
        'prices': [
            ("2024-01-01", 10.0),
            ("2024-01-05", 15.5)
        ]
    }
    pricing_service.save_pricing_data("123", "V123", "", parsed_data, save_daily=True, save_offers=False)

setup()
