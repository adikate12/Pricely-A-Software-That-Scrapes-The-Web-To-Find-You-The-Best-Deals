        def is_mobile_phone(product):
            # Check if product is a mobile phone (not an accessory)
            name = product.get('Product Name', '').lower()
            return ('mobile' in name or 'phone' in name) and not any(acc in name for acc in ['case', 'cover', 'charger', 'cable', 'headphone', 'earphone'])
        
        # Load products from different sources
        amazon_products = load_json_file('../Amazon/amazon_products.json')
        croma_products = load_json_file('../Croma/croma_mobiles_2.json')
        flipkart_products = load_json_file('../Home/flipkart_mobiles_2.json')
        
        print(f"Loaded Amazon products: {len(amazon_products)}")
        print(f"Loaded Croma products: {len(croma_products)}")
        print(f"Loaded Flipkart products: {len(flipkart_products)}")
        
        # Process and combine products 