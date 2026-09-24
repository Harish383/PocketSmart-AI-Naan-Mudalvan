from urllib.parse import quote_plus


def platform_search(
    platform: str,
    query: str
) -> str:

    encoded = quote_plus(
        query
    )

    urls = {

        "Amazon":
            f"https://www.amazon.in/s?k={encoded}",

        "Flipkart":
            f"https://www.flipkart.com/search?q={encoded}",

        "IKEA":
            f"https://www.ikea.com/in/en/search/?q={encoded}",

        "Swiggy":
            f"https://www.swiggy.com/search?query={encoded}",

        "Zomato":
            f"https://www.zomato.com/search?query={encoded}",

        "OYO":
            f"https://www.oyorooms.com/search?location={encoded}"
    }

    return urls.get(
        platform,
        f"https://www.google.com/search?q={encoded}"
    )


def choose_platform(
    category: str,
    planner: str
) -> str:

    category = category.lower()

    if planner == "home":

        if category in {
            "furniture",
            "decor",
            "lighting"
        }:
            return "IKEA"

        return "Amazon"

    if planner == "party":

        if category in {
            "food",
            "catering"
        }:
            return "Swiggy"

        if category == "venue":
            return "OYO"

        return "Amazon"

    return "Flipkart"
