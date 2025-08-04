"""
Website scraping module for extracting text and images.

This module handles the scraping of business websites to collect
text content and images for further analysis.
"""

import requests
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from config.settings import settings


@dataclass
class ScrapingOptions:
    """Configuration options for business scraping."""
    max_pages: int = 10
    include_images: bool = True
    timeout_per_page: int = 30
    page_types: List[str] = None
    
    def __post_init__(self):
        if self.page_types is None:
            self.page_types = ["about", "services", "contact", "home", "other"]


@dataclass
class PageData:
    """Data structure for individual page scraping results."""
    url: str
    page_type: str
    text_content: str
    text_length: int
    images: List[Dict]
    scraped_at: datetime
    scrape_success: bool
    error_message: Optional[str] = None


@dataclass
class BusinessData:
    """Unified data structure for complete business scraping results."""
    business_url: str
    scraped_at: datetime
    scraping_metadata: Dict
    pages: List[PageData]
    business_intelligence: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "business_url": self.business_url,
            "scraped_at": self.scraped_at.isoformat(),
            "scraping_metadata": self.scraping_metadata,
            "pages": [
                {
                    "url": page.url,
                    "page_type": page.page_type,
                    "text_content": page.text_content,
                    "text_length": page.text_length,
                    "images": page.images,
                    "scraped_at": page.scraped_at.isoformat(),
                    "scrape_success": page.scrape_success,
                    "error_message": page.error_message
                }
                for page in self.pages
            ],
            "business_intelligence": self.business_intelligence
        }


class WebsiteScraper:
    """Scraper for extracting content from business websites."""
    
    def __init__(self):
        """Initialize the website scraper."""
        self.session = requests.Session()
        self.user_agent = 'BusinessIntelligenceBot/1.0 (+https://github.com/chenxunchi/biz-intel-llm)'
        self.session.headers.update({
            'User-Agent': self.user_agent
        })
        self.timeout = settings.max_scrape_timeout
        self.robots_cache = {}  # Cache robots.txt files
    
    def scrape_text(self, url: str) -> str:
        """Extract text content from a website.
        
        Args:
            url: The website URL to scrape
            
        Returns:
            Extracted text content
        """
        try:
            # Normalize URL first
            normalized_url = self._normalize_url(url)
            
            if not self._validate_url(normalized_url):
                raise ValueError(f"Invalid URL: {url}")
            
            # Try to find a working URL variation
            working_url = self._try_url_variations(normalized_url)
            
            if not self._can_fetch(working_url):
                raise ValueError(f"Robots.txt disallows scraping: {working_url}")
            
            response = self.session.get(working_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text from main content areas
            text_content = []
            
            # Try to find main content areas first
            main_content = soup.find_all(['main', 'article', 'section']) or [soup]
            
            for content in main_content:
                # Get text from headings and paragraphs
                for element in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span']):
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out very short text
                        text_content.append(text)
            
            # Clean and join text
            clean_text = self._clean_text(' '.join(text_content))
            return clean_text
            
        except requests.RequestException as e:
            raise Exception(f"Error scraping text from {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error scraping {url}: {str(e)}")
    
    def scrape_images(self, url: str) -> List[Dict[str, str]]:
        """Extract images from a website.
        
        Args:
            url: The website URL to scrape
            
        Returns:
            List of dictionaries containing image information
        """
        try:
            # Normalize URL first
            normalized_url = self._normalize_url(url)
            
            if not self._validate_url(normalized_url):
                raise ValueError(f"Invalid URL: {url}")
            
            # Try to find a working URL variation
            working_url = self._try_url_variations(normalized_url)
            
            if not self._can_fetch(working_url):
                raise ValueError(f"Robots.txt disallows scraping: {working_url}")
            
            response = self.session.get(working_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            images = []
            
            # Find all img tags
            img_tags = soup.find_all('img')
            
            for img in img_tags[:settings.max_images_per_site]:
                src = img.get('src')
                alt = img.get('alt', '')
                
                if src:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, src)
                    
                    # Filter out very small images and common non-content images
                    if self._is_valid_image(img, alt):
                        images.append({
                            'url': absolute_url,
                            'alt_text': alt,
                            'title': img.get('title', ''),
                            'width': img.get('width', ''),
                            'height': img.get('height', '')
                        })
            
            return images
            
        except requests.RequestException as e:
            raise Exception(f"Error scraping images from {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error scraping images from {url}: {str(e)}")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize and fix common URL formatting issues.
        
        Args:
            url: Raw URL input from user
            
        Returns:
            Properly formatted URL
        """
        if not url:
            raise ValueError("URL cannot be empty")
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            # Try HTTPS first (more common and secure)
            url = 'https://' + url
        
        # Add www if domain looks incomplete
        parsed = urlparse(url)
        if parsed.netloc and '.' in parsed.netloc:
            # Check if it's a bare domain without subdomain
            parts = parsed.netloc.split('.')
            if len(parts) == 2 and not parsed.netloc.startswith('www.'):
                # For domains like "abc.com", try "www.abc.com"
                url = f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}"
                if parsed.query:
                    url += f"?{parsed.query}"
                if parsed.fragment:
                    url += f"#{parsed.fragment}"
        
        return url
    
    def _validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
    def _try_url_variations(self, base_url: str) -> str:
        """Try different URL variations to find a working one.
        
        Args:
            base_url: Base URL to try variations of
            
        Returns:
            Working URL or original if none work
        """
        variations = [
            base_url,  # Try original first
        ]
        
        # If it's a www URL, try without www
        if base_url.startswith('https://www.'):
            variations.append(base_url.replace('https://www.', 'https://'))
        elif base_url.startswith('http://www.'):
            variations.append(base_url.replace('http://www.', 'http://'))
        
        # If it's non-www, try with www
        if '://www.' not in base_url:
            parsed = urlparse(base_url)
            www_url = f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}"
            variations.append(www_url)
        
        # Try HTTP if HTTPS was used
        if base_url.startswith('https://'):
            variations.append(base_url.replace('https://', 'http://'))
        
        # Test each variation
        for variation in variations:
            try:
                response = self.session.head(variation, timeout=5, allow_redirects=True)
                if response.status_code < 400:
                    return variation
            except:
                continue
                
        # Return original if none work
        return base_url
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common unwanted patterns
        text = re.sub(r'^\s*\|.*?\|\s*$', '', text, flags=re.MULTILINE)  # Table separators
        text = re.sub(r'Cookie.*?Accept', '', text, flags=re.IGNORECASE)  # Cookie notices
        
        # Limit length to avoid overly long content
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        return text
    
    def _is_valid_image(self, img_tag, alt_text: str) -> bool:
        """Check if image is likely to be content-relevant.
        
        Args:
            img_tag: BeautifulSoup img tag
            alt_text: Image alt text
            
        Returns:
            True if image appears to be content-relevant
        """
        # Skip common non-content images
        src = img_tag.get('src', '').lower()
        alt_lower = alt_text.lower()
        
        skip_patterns = [
            'logo', 'icon', 'favicon', 'pixel', 'tracker', 'button',
            'arrow', 'bullet', 'spacer', '1x1', 'transparent'
        ]
        
        for pattern in skip_patterns:
            if pattern in src or pattern in alt_lower:
                return False
        
        # Check minimum size if available
        width = img_tag.get('width')
        height = img_tag.get('height')
        
        if width and height:
            try:
                w, h = int(width), int(height)
                if w < 50 or h < 50:  # Skip very small images
                    return False
            except ValueError:
                pass
        
        return True
    
    def _can_fetch(self, url: str) -> bool:
        """Check if robots.txt allows fetching the URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if fetching is allowed, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Check cache first
            if base_url not in self.robots_cache:
                self._load_robots_txt(base_url)
            
            rp = self.robots_cache.get(base_url)
            if rp is None:
                # If we can't load robots.txt, allow by default
                return True
            
            return rp.can_fetch(self.user_agent, url)
            
        except Exception:
            # If any error occurs, allow by default (be permissive)
            return True
    
    def _load_robots_txt(self, base_url: str) -> None:
        """Load and cache robots.txt for a domain.
        
        Args:
            base_url: Base URL of the domain
        """
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            
            # Try to read robots.txt with a shorter timeout
            try:
                response = self.session.get(robots_url, timeout=5)
                if response.status_code == 200:
                    # Parse the robots.txt content
                    rp.set_url(robots_url)
                    rp.read()
                    self.robots_cache[base_url] = rp
                else:
                    # No robots.txt or error - allow by default
                    self.robots_cache[base_url] = None
            except requests.RequestException:
                # Network error - allow by default
                self.robots_cache[base_url] = None
                
        except Exception:
            # Any error - allow by default
            self.robots_cache[base_url] = None
    
    def discover_pages(self, base_url: str, max_pages: int = 10) -> List[str]:
        """Discover important pages from a business website.
        
        Args:
            base_url: The base URL of the website (e.g., https://example.com)
            max_pages: Maximum number of pages to discover
            
        Returns:
            List of discovered page URLs prioritized by business relevance
        """
        try:
            # Normalize URL first
            normalized_url = self._normalize_url(base_url)
            
            if not self._validate_url(normalized_url):
                raise ValueError(f"Invalid base URL: {base_url}")
            
            # Try to find a working URL variation
            working_url = self._try_url_variations(normalized_url)
            
            discovered_urls = set()
            
            # 1. Always include the homepage
            discovered_urls.add(working_url.rstrip('/'))
            
            # 2. Try sitemap discovery first (most comprehensive)
            sitemap_urls = self._discover_from_sitemap(working_url)
            discovered_urls.update(sitemap_urls)
            
            # 3. If we don't have enough pages, discover from internal links
            if len(discovered_urls) < max_pages:
                link_urls = self._discover_from_links(working_url, max_pages - len(discovered_urls))
                discovered_urls.update(link_urls)
            
            # 4. Prioritize pages by business relevance
            prioritized_urls = self._prioritize_business_pages(list(discovered_urls))
            
            return prioritized_urls[:max_pages]
            
        except Exception as e:
            # Fallback to normalized URL if discovery fails
            try:
                normalized_url = self._normalize_url(base_url)
                working_url = self._try_url_variations(normalized_url)
                return [working_url.rstrip('/')]
            except:
                return [base_url.rstrip('/')]
    
    def _discover_from_sitemap(self, base_url: str) -> Set[str]:
        """Discover pages from sitemap.xml.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Set of URLs found in sitemap
        """
        discovered_urls = set()
        
        try:
            # Common sitemap locations
            sitemap_urls = [
                urljoin(base_url, '/sitemap.xml'),
                urljoin(base_url, '/sitemap_index.xml'),
                urljoin(base_url, '/sitemap/sitemap.xml')
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    if not self._can_fetch(sitemap_url):
                        continue
                        
                    response = self.session.get(sitemap_url, timeout=self.timeout)
                    if response.status_code == 200:
                        urls = self._parse_sitemap(response.content)
                        discovered_urls.update(urls)
                        break  # Found a working sitemap
                        
                except requests.RequestException:
                    continue  # Try next sitemap location
                    
        except Exception:
            pass  # Sitemap discovery failed, continue with other methods
            
        return discovered_urls
    
    def _parse_sitemap(self, sitemap_content: bytes) -> Set[str]:
        """Parse sitemap XML content to extract URLs.
        
        Args:
            sitemap_content: Raw sitemap XML content
            
        Returns:
            Set of URLs found in sitemap
        """
        urls = set()
        
        try:
            root = ET.fromstring(sitemap_content)
            
            # Handle sitemap index files
            if 'sitemapindex' in root.tag:
                for sitemap in root:
                    loc_elem = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None and loc_elem.text:
                        # Recursively parse individual sitemaps
                        try:
                            response = self.session.get(loc_elem.text, timeout=self.timeout)
                            if response.status_code == 200:
                                sub_urls = self._parse_sitemap(response.content)
                                urls.update(sub_urls)
                        except:
                            continue
            
            # Handle regular sitemap files
            else:
                for url in root:
                    loc_elem = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None and loc_elem.text:
                        urls.add(loc_elem.text)
                        
        except ET.ParseError:
            pass  # Invalid XML, skip
        except Exception:
            pass  # Other parsing error, skip
            
        return urls
    
    def _discover_from_links(self, base_url: str, max_links: int) -> Set[str]:
        """Discover pages by following internal links from homepage.
        
        Args:
            base_url: Base URL to start discovery from
            max_links: Maximum number of links to discover
            
        Returns:
            Set of internal URLs found
        """
        discovered_urls = set()
        
        try:
            if not self._can_fetch(base_url):
                return discovered_urls
                
            response = self.session.get(base_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            base_domain = urlparse(base_url).netloc
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                parsed_url = urlparse(absolute_url)
                
                # Only include internal links from same domain
                if (parsed_url.netloc == base_domain and 
                    self._is_valid_business_page(absolute_url, link.get_text(strip=True))):
                    discovered_urls.add(absolute_url)
                    
                    if len(discovered_urls) >= max_links:
                        break
                        
        except Exception:
            pass  # Link discovery failed
            
        return discovered_urls
    
    def _is_valid_business_page(self, url: str, link_text: str) -> bool:
        """Check if a URL represents a valid business page.
        
        Args:
            url: URL to check
            link_text: Text content of the link
            
        Returns:
            True if appears to be a business-relevant page
        """
        url_lower = url.lower()
        text_lower = link_text.lower()
        
        # Skip common non-business pages
        skip_patterns = [
            'login', 'register', 'cart', 'checkout', 'admin', 'wp-admin',
            'blog', 'news', 'feed', 'rss', 'xml', 'json', 'pdf',
            'privacy', 'terms', 'cookie', 'legal', 'disclaimer',
            'contact-form', 'thank-you', 'confirmation',
            '#', 'javascript:', 'mailto:', 'tel:', 'download'
        ]
        
        for pattern in skip_patterns:
            if pattern in url_lower or pattern in text_lower:
                return False
        
        # Skip very long URLs (likely dynamic/filtered content)
        if len(url) > 200:
            return False
            
        return True
    
    def _prioritize_business_pages(self, urls: List[str]) -> List[str]:
        """Prioritize URLs by business relevance.
        
        Args:
            urls: List of URLs to prioritize
            
        Returns:
            URLs sorted by business importance
        """
        def get_priority_score(url: str) -> int:
            """Calculate priority score for a URL (higher = more important)."""
            url_lower = url.lower()
            score = 0
            
            # High priority business pages
            high_priority_keywords = [
                'about', 'services', 'products', 'solutions', 'offering',
                'company', 'team', 'portfolio', 'work', 'case-studies',
                'industries', 'clients', 'testimonials'
            ]
            
            # Medium priority pages
            medium_priority_keywords = [
                'home', 'index', 'main', 'contact', 'location',
                'careers', 'jobs', 'press', 'media'
            ]
            
            # Check for high priority keywords
            for keyword in high_priority_keywords:
                if keyword in url_lower:
                    score += 10
                    
            # Check for medium priority keywords
            for keyword in medium_priority_keywords:
                if keyword in url_lower:
                    score += 5
            
            # Prefer shorter URLs (usually more important pages)
            if len(url) < 50:
                score += 3
            elif len(url) < 100:
                score += 1
                
            # Prefer URLs with fewer path segments
            path_segments = len([p for p in urlparse(url).path.split('/') if p])
            if path_segments <= 1:
                score += 5
            elif path_segments <= 2:
                score += 2
                
            return score
        
        # Sort by priority score (descending)
        return sorted(urls, key=get_priority_score, reverse=True)
    
    def scrape_business(self, base_url: str, options: ScrapingOptions = None) -> BusinessData:
        """Comprehensive business website analysis with unified output.
        
        Args:
            base_url: The base URL of the business website
            options: Scraping configuration options
            
        Returns:
            BusinessData: Unified structure with all scraped information
        """
        options = options or ScrapingOptions()
        start_time = datetime.now()
        
        try:
            # Step 1: Page Discovery (existing method)
            discovered_urls = self.discover_pages(base_url, options.max_pages)
            
            # Step 2: Process Each Page
            pages = []
            for url in discovered_urls:
                page_data = self._scrape_single_page(url, options)
                pages.append(page_data)
            
            # Step 3: Compute Business Intelligence
            business_intel = self._compute_business_intelligence(pages)
            
            # Step 4: Generate Metadata
            metadata = self._generate_scraping_metadata(pages, start_time)
            
            # Step 5: Package Results
            return BusinessData(
                business_url=base_url,
                scraped_at=start_time,
                scraping_metadata=metadata,
                pages=pages,
                business_intelligence=business_intel
            )
            
        except Exception as e:
            # Fallback for complete failure
            return BusinessData(
                business_url=base_url,
                scraped_at=start_time,
                scraping_metadata={
                    "total_pages_attempted": 0,
                    "successful_pages": 0,
                    "failed_pages": 0,
                    "success_rate": 0.0,
                    "total_scrape_time": (datetime.now() - start_time).total_seconds(),
                    "errors": [str(e)]
                },
                pages=[],
                business_intelligence={}
            )
    
    def _scrape_single_page(self, url: str, options: ScrapingOptions) -> PageData:
        """Scrape content from a single page with error handling.
        
        Args:
            url: Page URL to scrape
            options: Scraping options
            
        Returns:
            PageData: Results for the single page
        """
        scrape_start = datetime.now()
        
        try:
            # Classify page type
            page_type = self._classify_page_type(url)
            
            # Skip if page type not requested
            if page_type not in options.page_types:
                return PageData(
                    url=url,
                    page_type=page_type,
                    text_content="",
                    text_length=0,
                    images=[],
                    scraped_at=scrape_start,
                    scrape_success=True,
                    error_message="Page type skipped per options"
                )
            
            # Scrape content using existing methods
            text_content = ""
            images = []
            
            try:
                text_content = self.scrape_text(url)
            except Exception as e:
                # Continue with image scraping even if text fails
                pass
            
            if options.include_images:
                try:
                    images = self.scrape_images(url)
                except Exception as e:
                    # Continue even if image scraping fails
                    pass
            
            return PageData(
                url=url,
                page_type=page_type,
                text_content=text_content,
                text_length=len(text_content),
                images=images,
                scraped_at=scrape_start,
                scrape_success=True
            )
            
        except Exception as e:
            return PageData(
                url=url,
                page_type="unknown",
                text_content="",
                text_length=0,
                images=[],
                scraped_at=scrape_start,
                scrape_success=False,
                error_message=str(e)
            )
    
    def _classify_page_type(self, url: str) -> str:
        """Classify page type based on URL patterns.
        
        Args:
            url: URL to classify
            
        Returns:
            Page type classification
        """
        url_lower = url.lower()
        
        page_type_patterns = {
            "about": ["about", "company", "team", "history", "who-we-are", "our-story"],
            "services": ["services", "products", "solutions", "offerings", "what-we-do"],
            "contact": ["contact", "location", "address", "phone", "reach-us", "get-in-touch"],
            "home": ["", "/", "home", "index", "main", "landing"],
        }
        
        for page_type, patterns in page_type_patterns.items():
            if any(pattern in url_lower for pattern in patterns):
                return page_type
        
        return "other"
    
    def _compute_business_intelligence(self, pages: List[PageData]) -> Dict:
        """Compute business intelligence metrics from scraped pages.
        
        Args:
            pages: List of scraped page data
            
        Returns:
            Business intelligence dictionary
        """
        successful_pages = [p for p in pages if p.scrape_success]
        failed_pages = [p for p in pages if not p.scrape_success]
        
        # Basic metrics
        total_pages = len(pages)
        success_count = len(successful_pages)
        success_rate = success_count / total_pages if total_pages > 0 else 0
        
        # Content metrics
        total_text = sum(p.text_length for p in successful_pages)
        total_images = sum(len(p.images) for p in successful_pages)
        avg_text_per_page = total_text / success_count if success_count > 0 else 0
        avg_images_per_page = total_images / success_count if success_count > 0 else 0
        
        # Page type analysis
        page_types_found = list(set(p.page_type for p in successful_pages))
        key_pages_present = self._check_key_pages(successful_pages)
        
        # Content quality assessment
        quality_score = self._calculate_content_quality_score(successful_pages)
        
        return {
            "scraping_metrics": {
                "total_pages_found": total_pages,
                "successful_pages": success_count,
                "failed_pages": len(failed_pages),
                "success_rate": round(success_rate, 3)
            },
            "content_metrics": {
                "total_text_length": total_text,
                "total_images": total_images,
                "avg_text_per_page": round(avg_text_per_page, 0),
                "avg_images_per_page": round(avg_images_per_page, 1)
            },
            "page_analysis": {
                "page_types_found": page_types_found,
                "key_pages_present": key_pages_present,
                "content_quality_score": round(quality_score, 2)
            },
            "errors": [p.error_message for p in failed_pages if p.error_message]
        }
    
    def _check_key_pages(self, pages: List[PageData]) -> Dict[str, bool]:
        """Check which key business pages are present.
        
        Args:
            pages: List of successful page data
            
        Returns:
            Dictionary of key page presence flags
        """
        page_types = {p.page_type for p in pages}
        
        return {
            "has_about": "about" in page_types,
            "has_services": "services" in page_types,
            "has_contact": "contact" in page_types,
            "has_home": "home" in page_types
        }
    
    def _calculate_content_quality_score(self, pages: List[PageData]) -> float:
        """Calculate content quality score based on various factors.
        
        Args:
            pages: List of successful page data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not pages:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        # Factor 1: Text content richness (0-0.4)
        avg_text_length = sum(p.text_length for p in pages) / len(pages)
        if avg_text_length > 5000:
            score += 0.4
        elif avg_text_length > 2000:
            score += 0.3
        elif avg_text_length > 500:
            score += 0.2
        elif avg_text_length > 100:
            score += 0.1
        max_score += 0.4
        
        # Factor 2: Image presence (0-0.2)
        avg_images = sum(len(p.images) for p in pages) / len(pages)
        if avg_images > 5:
            score += 0.2
        elif avg_images > 2:
            score += 0.15
        elif avg_images > 0:
            score += 0.1
        max_score += 0.2
        
        # Factor 3: Key pages completeness (0-0.3)
        key_pages = self._check_key_pages(pages)
        key_pages_count = sum(key_pages.values())
        score += (key_pages_count / 4) * 0.3
        max_score += 0.3
        
        # Factor 4: Success rate (0-0.1)
        success_rate = len([p for p in pages if p.scrape_success]) / len(pages)
        score += success_rate * 0.1
        max_score += 0.1
        
        return min(score / max_score, 1.0) if max_score > 0 else 0.0
    
    def _generate_scraping_metadata(self, pages: List[PageData], start_time: datetime) -> Dict:
        """Generate metadata about the scraping process.
        
        Args:
            pages: List of page data
            start_time: When scraping started
            
        Returns:
            Metadata dictionary
        """
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        successful_pages = [p for p in pages if p.scrape_success]
        failed_pages = [p for p in pages if not p.scrape_success]
        
        return {
            "scraping_session": {
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "total_duration_seconds": round(total_time, 2)
            },
            "page_processing": {
                "total_pages_attempted": len(pages),
                "successful_pages": len(successful_pages),
                "failed_pages": len(failed_pages),
                "success_rate": round(len(successful_pages) / len(pages), 3) if pages else 0.0
            },
            "errors": [p.error_message for p in failed_pages if p.error_message],
            "performance": {
                "avg_time_per_page": round(total_time / len(pages), 2) if pages else 0.0,
                "pages_per_minute": round((len(pages) / total_time) * 60, 1) if total_time > 0 else 0.0
            }
        }