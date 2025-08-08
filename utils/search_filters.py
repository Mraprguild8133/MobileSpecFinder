"""
Search filtering utilities
"""
import re
from typing import Dict, List, Optional

class SearchFilters:
    """Class to handle search filtering logic"""
    
    def __init__(self, config):
        self.config = config
    
    def apply_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply search filters to a list of products"""
        if not filters:
            return products
        
        filtered_products = []
        
        for product in products:
            if self._product_matches_filters(product, filters):
                filtered_products.append(product)
        
        return filtered_products
    
    def _product_matches_filters(self, product: Dict, filters: Dict) -> bool:
        """Check if a product matches the applied filters"""
        
        # Brand filter
        if filters.get('brand'):
            brand_match = self._check_brand_filter(product, filters['brand'])
            if not brand_match:
                return False
        
        # Price filter
        if filters.get('price_range'):
            price_match = self._check_price_filter(product, filters['price_range'])
            if not price_match:
                return False
        
        return True
    
    def _check_brand_filter(self, product: Dict, selected_brands: List[str]) -> bool:
        """Check if product matches brand filter"""
        product_name = product.get('name', '').lower()
        
        for brand in selected_brands:
            if brand.lower() in product_name:
                return True
        
        return False
    
    def _check_price_filter(self, product: Dict, price_range: str) -> bool:
        """Check if product matches price filter"""
        price_text = product.get('price', '').lower()
        
        # If price is not available or from GSMArena, include it
        if not price_text or 'not available' in price_text or 'check' in price_text:
            return True
        
        # Extract numeric price value
        price_value = self._extract_price_value(price_text)
        if price_value is None:
            return True  # Include if we can't determine price
        
        # Check against price range
        if price_range in self.config.PRICE_RANGES:
            min_price, max_price = self.config.PRICE_RANGES[price_range]
            return min_price <= price_value <= max_price
        
        return True
    
    def _extract_price_value(self, price_text: str) -> Optional[int]:
        """Extract numeric price value from price text"""
        try:
            # Remove common currency symbols and text
            cleaned_price = re.sub(r'[^\d,]', '', price_text)
            cleaned_price = cleaned_price.replace(',', '')
            
            if cleaned_price:
                return int(cleaned_price)
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def get_filter_summary(self, filters: Dict) -> str:
        """Get a human-readable summary of active filters"""
        if not filters:
            return "No filters applied"
        
        summary_parts = []
        
        if filters.get('brand'):
            brands = ', '.join(filters['brand'])
            summary_parts.append(f"Brands: {brands}")
        
        if filters.get('price_range'):
            range_names = {
                'budget': 'Budget (₹0-15K)',
                'mid': 'Mid-range (₹15K-35K)',
                'premium': 'Premium (₹35K-80K)',
                'flagship': 'Flagship (₹80K+)'
            }
            price_range = filters['price_range']
            summary_parts.append(f"Price: {range_names.get(price_range, price_range)}")
        
        return ' | '.join(summary_parts)
    
    def validate_filters(self, filters: Dict) -> Dict:
        """Validate and clean filter values"""
        validated_filters = {}
        
        # Validate brand filter
        if filters.get('brand'):
            valid_brands = []
            for brand in filters['brand']:
                if isinstance(brand, str) and brand.strip():
                    # Check if brand is in supported list (case-insensitive)
                    for supported_brand in self.config.SUPPORTED_BRANDS:
                        if brand.lower() == supported_brand.lower():
                            valid_brands.append(supported_brand)
                            break
                    else:
                        # Add even if not in supported list
                        valid_brands.append(brand.strip().title())
            
            if valid_brands:
                validated_filters['brand'] = valid_brands
        
        # Validate price range filter
        if filters.get('price_range'):
            price_range = filters['price_range']
            if price_range in self.config.PRICE_RANGES:
                validated_filters['price_range'] = price_range
        
        return validated_filters
