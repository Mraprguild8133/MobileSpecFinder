"""
Web scraper for mobile phone information from 91mobiles.com and gsmarena.com
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import Dict, List, Optional, Tuple
import trafilatura

logger = logging.getLogger(__name__)

class MobileScraper:
    """Scraper class for mobile phone data"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting to avoid being blocked"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.config.REQUEST_DELAY:
            time.sleep(self.config.REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> Optional[str]:
        """Make a rate-limited HTTP request"""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=self.config.TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def search_91mobiles(self, query: str) -> List[Dict]:
        """Search for mobile phones on 91mobiles.com"""
        # Try multiple URL formats as the site structure may have changed
        search_urls = [
            f"https://www.91mobiles.com/search?stext={query.replace(' ', '+')}",
            f"https://www.91mobiles.com/hub/mobiles/{query.replace(' ', '-').lower()}",
            f"https://www.91mobiles.com/search?search_text={query.replace(' ', '%20')}",
            f"https://www.91mobiles.com/search/{query.replace(' ', '-').lower()}"
        ]
        
        html_content = None
        successful_url = None
        
        for search_url in search_urls:
            html_content = self._make_request(search_url)
            if html_content and "404" not in html_content:
                successful_url = search_url
                break
                
        if not html_content:
            logger.warning(f"All 91mobiles URLs failed for query: {query}")
            return []
            
        logger.info(f"91mobiles search successful with URL: {successful_url}")
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Try multiple selectors as the HTML structure may have changed
        product_cards = (
            soup.find_all('div', class_='listingbox') or
            soup.find_all('div', class_='product-item') or
            soup.find_all('div', class_='mobile-item') or
            soup.find_all('article', class_='product') or
            soup.find_all('div', {'data-testid': 'product-card'}) or
            soup.find_all('div', class_='card') or
            soup.find_all('li', class_='product')
        )
        
        for card in product_cards[:self.config.MAX_RESULTS_PER_PAGE]:
            try:
                product = self._parse_91mobiles_product(card)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error parsing 91mobiles product: {e}")
                continue
        
        return products
    
    def _parse_91mobiles_product(self, card) -> Optional[Dict]:
        """Parse individual product from 91mobiles"""
        try:
            # Extract product name with multiple selectors
            name_elem = (
                card.find('h3') or
                card.find('a', class_='title') or
                card.find('h2') or
                card.find('h4') or
                card.find('a', class_='product-title') or
                card.find('[data-testid="product-name"]') or
                card.find('div', class_='name') or
                card.find('span', class_='title')
            )
            
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            
            # Extract product URL
            link_elem = card.find('a')
            product_url = link_elem.get('href') if link_elem else None
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.91mobiles.com{product_url}"
            
            # Extract image URL with multiple attributes
            img_elem = card.find('img')
            image_url = None
            if img_elem:
                image_url = (
                    img_elem.get('src') or
                    img_elem.get('data-src') or
                    img_elem.get('data-lazy') or
                    img_elem.get('data-original')
                )
            
            # Extract price with multiple selectors
            price_elem = (
                card.find('span', class_='price') or
                card.find('div', class_='price') or
                card.find('span', class_='cost') or
                card.find('[data-testid="price"]') or
                card.find('div', class_='price-current') or
                card.find('p', class_='price')
            )
            price = price_elem.get_text(strip=True) if price_elem else "Price not available"
            
            # Extract comprehensive specs
            specs = []
            spec_elems = (
                card.find_all('li') or 
                card.find_all('span', class_='spec') or
                card.find_all('div', class_='feature') or
                card.find_all('p', class_='specification')
            )
            for spec in spec_elems[:8]:  # Get more detailed specs
                spec_text = spec.get_text(strip=True)
                if spec_text and len(spec_text) > 3:
                    specs.append(spec_text)
                    
            # Get detailed product info if URL available
            detailed_info = {}
            if product_url:
                detailed_info = self._get_91mobiles_details(product_url)
            
            product_data = {
                'name': name,
                'price': price,
                'image_url': image_url,
                'product_url': product_url,
                'specs': specs,
                'source': '91mobiles'
            }
            
            # Add detailed information if available
            if detailed_info:
                product_data.update(detailed_info)
                
            return product_data
        
        except Exception as e:
            logger.error(f"Error parsing 91mobiles product card: {e}")
            return None
    
    def search_gsmarena(self, query: str) -> List[Dict]:
        """Search for mobile phones on gsmarena.com"""
        search_url = f"https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={query.replace(' ', '+')}"
        
        html_content = self._make_request(search_url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Find product listings
        product_cards = soup.find_all('div', class_='makers') or soup.find_all('li')
        
        for card in product_cards[:self.config.MAX_RESULTS_PER_PAGE]:
            try:
                product = self._parse_gsmarena_product(card)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error parsing GSMArena product: {e}")
                continue
        
        return products
    
    def _parse_gsmarena_product(self, card) -> Optional[Dict]:
        """Parse individual product from GSMArena"""
        try:
            # Extract product link and name
            link_elem = card.find('a')
            if not link_elem:
                return None
            
            name = link_elem.get('title') or link_elem.get_text(strip=True)
            if not name:
                return None
            
            product_url = link_elem.get('href')
            if product_url and not product_url.startswith('http'):
                product_url = f"https://www.gsmarena.com/{product_url}"
            
            # Extract image
            img_elem = card.find('img')
            image_url = img_elem.get('src') if img_elem else None
            if image_url and not image_url.startswith('http'):
                image_url = f"https://www.gsmarena.com/{image_url}"
            
            # Get detailed specs if product URL is available
            specs = []
            if product_url:
                detailed_specs = self._get_gsmarena_details(product_url)
                specs = detailed_specs.get('specs', [])
            
            return {
                'name': name,
                'price': "Check GSMArena for pricing",
                'image_url': image_url,
                'product_url': product_url,
                'specs': specs,
                'source': 'GSMArena'
            }
        
        except Exception as e:
            logger.error(f"Error parsing GSMArena product card: {e}")
            return None
    
    def _get_gsmarena_details(self, product_url: str) -> Dict:
        """Get detailed specifications from GSMArena product page"""
        try:
            html_content = self._make_request(product_url)
            if not html_content:
                return {}
            
            # Use trafilatura for better text extraction
            text_content = trafilatura.extract(html_content)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            specs = []
            
            # Find specification table
            spec_tables = soup.find_all('table')
            for table in spec_tables:
                if hasattr(table, 'find_all'):
                    rows = table.find_all('tr')
                    for row in rows[:10]:  # Limit to prevent too much data
                        if hasattr(row, 'find_all'):
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                spec_name = cells[0].get_text(strip=True)
                                spec_value = cells[1].get_text(strip=True)
                                if spec_name and spec_value:
                                    specs.append(f"{spec_name}: {spec_value}")
            
            return {
                'specs': specs[:12],  # More comprehensive specs
                'detailed_specs': self._extract_detailed_specs(soup),
                'features': self._extract_features(soup),
                'summary': self._extract_summary(soup)
            }
            
        except Exception as e:
            logger.error(f"Error getting GSMArena details: {e}")
            return {}
    
    def _get_91mobiles_details(self, product_url: str) -> Dict:
        """Get detailed product information from 91mobiles product page"""
        try:
            html_content = self._make_request(product_url)
            if not html_content:
                return {}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            return {
                'detailed_specs': self._extract_detailed_specs(soup),
                'features': self._extract_features(soup),
                'summary': self._extract_summary(soup)
            }
        except Exception as e:
            logger.error(f"Error getting 91mobiles details: {e}")
            return {}
    
    def _extract_detailed_specs(self, soup) -> List[str]:
        """Extract detailed specifications from product page"""
        specs = []
        try:
            # Try multiple spec table selectors
            spec_sections = (
                soup.find_all('div', class_='spec-table') or
                soup.find_all('table', class_='specifications') or
                soup.find_all('div', class_='phone-feature') or
                soup.find_all('ul', class_='spec-list')
            )
            
            for section in spec_sections:
                if hasattr(section, 'find_all'):
                    rows = section.find_all(['tr', 'li', 'div'])
                    for row in rows[:15]:  # Comprehensive specs
                        text = row.get_text(strip=True)
                        if text and len(text) > 10 and ':' in text:
                            specs.append(text)
        except Exception as e:
            logger.error(f"Error extracting detailed specs: {e}")
        
        return specs[:12]
    
    def _extract_features(self, soup) -> List[str]:
        """Extract key features from product page"""
        features = []
        try:
            feature_sections = (
                soup.find_all('div', class_='features') or
                soup.find_all('ul', class_='key-features') or
                soup.find_all('div', class_='highlights')
            )
            
            for section in feature_sections:
                if hasattr(section, 'find_all'):
                    items = section.find_all(['li', 'p', 'div'])
                    for item in items[:8]:
                        text = item.get_text(strip=True)
                        if text and len(text) > 5:
                            features.append(text)
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
        
        return features[:6]
    
    def _extract_summary(self, soup) -> str:
        """Extract product summary/description"""
        try:
            summary_elems = (
                soup.find('div', class_='summary') or
                soup.find('p', class_='description') or
                soup.find('div', class_='overview') or
                soup.find('meta', attrs={'name': 'description'})
            )
            
            if summary_elems:
                if hasattr(summary_elems, 'get'):
                    return summary_elems.get('content', '')[:200]
                else:
                    return summary_elems.get_text(strip=True)[:200]
        except Exception as e:
            logger.error(f"Error extracting summary: {e}")
        
        return ""
    
    def search_mobiles(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search mobiles from both sources and combine results"""
        all_products = []
        
        # Search 91mobiles
        try:
            mobiles_91_results = self.search_91mobiles(query)
            all_products.extend(mobiles_91_results)
            logger.info(f"Found {len(mobiles_91_results)} results from 91mobiles")
        except Exception as e:
            logger.error(f"Error searching 91mobiles: {e}")
        
        # Search GSMArena
        try:
            gsmarena_results = self.search_gsmarena(query)
            all_products.extend(gsmarena_results)
            logger.info(f"Found {len(gsmarena_results)} results from GSMArena")
        except Exception as e:
            logger.error(f"Error searching GSMArena: {e}")
        
        # Apply filters if provided
        if filters:
            all_products = self._apply_filters(all_products, filters)
        
        # Remove duplicates and limit results
        seen_names = set()
        unique_products = []
        for product in all_products:
            if product['name'] not in seen_names:
                seen_names.add(product['name'])
                unique_products.append(product)
                if len(unique_products) >= self.config.MAX_TOTAL_RESULTS:
                    break
        
        return unique_products
    
    def _apply_filters(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply search filters to products"""
        filtered_products = []
        
        for product in products:
            # Brand filter
            if filters.get('brand'):
                brand_matches = any(
                    brand.lower() in product['name'].lower() 
                    for brand in filters['brand']
                )
                if not brand_matches:
                    continue
            
            # Price filter (basic implementation)
            if filters.get('price_range'):
                # This is a simplified price filter
                # In a real implementation, you'd need to parse price strings properly
                price_text = product.get('price', '').lower()
                if 'not available' in price_text or 'check' in price_text:
                    # Include products without clear pricing
                    pass
            
            filtered_products.append(product)
        
        return filtered_products
