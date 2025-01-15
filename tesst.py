import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def main():
    config = CrawlerRunConfig(
        css_selector=".product-name", 
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://sportfuel.pl/36-przed-wysilkiem-pl", 
            config=config
        )
        print("Partial HTML length:", result.cleaned_html)

if __name__ == "__main__":
    asyncio.run(main())
