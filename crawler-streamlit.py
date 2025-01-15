import asyncio
import json
import sys
import streamlit as st
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# Ustawienie innej pętli na Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Konfiguracja schematu
schema = {
    "name": "Dane o produkcie",
    "baseSelector": "article",
    "fields": [
        {
            "name": "product_name",
            "selector": "h2[itemprop='name'] > a",
            "type": "text",
        },
        {
            "name": "product_link",
            "selector": "a[itemprop='url']",
            "type": "attribute",
            "attribute": "href"
        },
        {
            "name": "product_img",
            "selector": "img[itemprop='image']",
            "type": "attribute",
            "attribute": "src"
        },
        {
            "name": "product_price",
            "selector": "span[itemprop='price']",
            "type": "attribute",
            "attribute": "content"
        },
        {
            "name": "product_currency",
            "selector": "span[itemprop='priceCurrency']",
            "type": "attribute",
            "attribute": "content"
        },
        {
            "name": "product_description",
            "selector": ".listing-description",
            "type": "text",
        }
    ]
}

# Konfiguracja crawlera
config = CrawlerRunConfig(
    # Content filtering
    exclude_domains=["adsite.com"],
    excluded_tags=[
        "form",          # Formularze (wyszukiwanie, logowanie, itp.)
        "header",        # Nagłówek strony
        "footer",        # Stopka strony
        "nav",           # Nawigacja
        "aside",         # Boczne panele
        "script",        # Skrypty JavaScript
        "style",         # Style CSS
        "noscript",      # Treść dla wyłączonego JavaScriptu
        "iframe",        # Osadzone strony
        "ins",           # Reklamy (Google AdSense)
        "amp-ad",        # Reklamy AMP
        "link",          # Linki zewnętrzne do stylów itp.
        "meta",          # Metadane
        "svg",           # Obrazki wektorowe
        "input",         # Pola wejściowe formularzy
        "select",        # Rozwijane menu
        "textarea",      # Pola tekstowe formularzy
        "button",        # Przyciski interakcji
        "label",         # Etykiety formularzy
        "legend",        # Legendy pól formularza
        "fieldset",      # Grupowanie pól formularza
        "option"         # Opcje w rozwijanych menu
    ],
    css_selector="article",
    exclude_social_media_links=True,
    exclude_external_images=False,
    exclude_external_links=True,
    cache_mode=CacheMode.BYPASS,
    extraction_strategy=JsonCssExtractionStrategy(schema)
)

async def run_crawler(url):
    """Uruchamia crawlera i zwraca wyniki."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        return result

def get_missing_fields(item):
    """Zwraca listę brakujących pól dla produktu."""
    required_fields = ["product_name", "product_description", "product_price", "product_img", "product_link"]
    return [field for field in required_fields if not item.get(field)]

async def main():
    st.title("CRAWLER-ek")

    url = st.text_input("Podaj URL strony do przeszukania:", "https://sportfuel.pl/nowosci")
    if st.button("Uruchom Crawlera"):
        with st.spinner("Pobieranie i przetwarzanie danych..."):
            result = await run_crawler(url)
            if result.success:
                st.success("Crawling zakończony pomyślnie!")
                st.write("**Status:** ", result.success)
                st.write("**Długość Wyczyszczonego HTML:** ", len(result.cleaned_html))
                st.write("**Długość Surowego HTML:** ", len(result.html))
                st.write("**Długość Extractowana:** ", len(result.extracted_content))

                if result.extracted_content:
                  try:
                      extracted_data = json.loads(result.extracted_content)
                      num_products = len(extracted_data)  # Liczba znalezionych produktów
                      st.write(f"**Liczba znalezionych produktów:** {num_products}")
                      st.subheader("Wyodrębnione dane:")
                      
                      for item in extracted_data:
                          st.markdown("---")  # Dodaj linię oddzielającą produkty
                          col1, col2 = st.columns([1, 2])  # Ustaw 2 kolumny

                          with col1:
                              if item.get("product_img"):
                                  st.image(item["product_img"], width=200)
                              else:
                                  st.write("Brak Zdjęcia")

                          with col2:
                              name = item.get("product_name", "Brak Nazwy")
                              st.subheader(name)

                              description = item.get("product_description", "Brak Opisu")
                              st.write(description)

                              price = item.get("product_price")
                              currency = item.get("product_currency", "")
                              if price:
                                  st.write(f"**Cena:** {price} {currency}")
                              else:
                                  st.write("**Cena:** Brak Danych")
                              
                              link = item.get("product_link")
                              if link:
                                st.markdown(f"[Link do produktu]({link})")
                              else:
                                st.write("**Link:** Brak Danych")


                          missing_fields = get_missing_fields(item)
                          if missing_fields:
                              st.warning(f"Brakujące pola: {', '.join(missing_fields)}")

                          with st.expander("Pokaż JSON"):
                              st.json(item)

                  except json.JSONDecodeError:
                    st.error("Błąd: Nie można sparsować wyodrębnionych danych jako JSON.")
                    st.text(result.extracted_content)
                
                else:
                    st.warning("Brak wyodrębnionych danych.")
            else:
                st.error(f"Crawling nie powiódł się. Błąd: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())
