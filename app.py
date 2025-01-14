from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json
import asyncio
import logging
import streamlit as st
import sys

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Ustawienie innej pętli na Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def extract_sportfuel_products(url):
    # Initialize browser config
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True
    )
    
    # Initialize crawler config with JSON CSS extraction strategy
    crawler_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Sportfuel Product Search Results",
                "baseSelector": "div.product-info.row",
                "fields": [
                    {
                        "name": "title",
                        "selector": "h2.product-name a",
                        "type": "text"
                    },
                    {
                        "name": "url",
                        "selector": "h2.product-name a",
                        "type": "attribute",
                        "attribute": "href"
                    },
                    {
                        "name": "producer_image",
                        "selector": "div.producer-logo img",
                        "type": "attribute",
                        "attribute": "src"
                     },
                    {
                        "name": "producer_name",
                        "selector": "div.producer-logo a",
                        "type": "attribute",
                        "attribute": "title"
                     },
                    {
                        "name": "description",
                        "selector": "span.listing-description",
                        "type": "text"
                    },

                ]
            }
        )
    )
    
    logging.debug(f"Pobieranie danych z: {url}")
    
    try:
        # Use context manager for proper resource handling
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # Extract the data
            result = await crawler.arun(url=url, config=crawler_config)
            
            logging.debug(f"Wynik pobierania: {result}")
            
            if result and result.extracted_content:
                # Parse the JSON string into a list of products
                products = json.loads(result.extracted_content)
                return products
            else:
                logging.error("Nie udało się pobrać lub przetworzyć danych.")
                st.error("Nie udało się pobrać danych z podanego adresu URL.")
                return None
    except Exception as e:
         logging.error(f"Wystąpił błąd podczas pobierania danych: {e}")
         st.error(f"Wystąpił błąd podczas pobierania danych: {e}")
         return None


async def main():
    st.title("Sportfuel Product Scraper")
    
    url = st.text_input("Wprowadź adres URL strony z produktami", "https://sportfuel.pl/48-weglowodany-pl")
    
    if st.button("Pobierz dane"):
        if url:
            with st.spinner("Pobieranie danych..."):
              products = await extract_sportfuel_products(url)
            if products:
              for product in products:
                  st.subheader(product.get('title'))
                  st.write(f"**URL:** {product.get('url')}")
                  if product.get('producer_image'):
                     st.image(product.get('producer_image'), width=100)
                  st.write(f"**Producer Name:** {product.get('producer_name')}")
                  st.write(f"**Description:** {product.get('description')}")
                  st.markdown("---")

if __name__ == "__main__":
    asyncio.run(main())