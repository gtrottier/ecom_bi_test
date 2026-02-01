import random

from langchain_core.tools import tool

from app.schema import ToolResult


@tool
def scrape_product_data(product_name: str, brand: str) -> ToolResult:
    """
    Simule un scraping des données du produit
    Pour une vrai fonction on aurait soit des appels API/requetes HTTP
    soit un vrai "scraping" avec des librairies comme BeautifulSoup etc.
    """

    platforms = ["amazon", "bestbuy", "ebay", "walmart"]
    data = []
    market_price = random.randint(100, 350)
    try:
        for platform in platforms:
            data.append(
                {
                    "platform": platform,
                    "price": market_price + random.randint(-50, 50),
                    "availability": random.choice(
                        ["In Stock", "Low Stock", "Out of Stock"]
                    ),
                    "url": f"https://www.{platform.lower()}.com/{brand}/{product_name.replace(' ', '-').lower()}",
                }
            )

    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": str(e) if e else "Unknown error",
            "retryable": False,
        }
    return {"status": "ok", "data": data}
