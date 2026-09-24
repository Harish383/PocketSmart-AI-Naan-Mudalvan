import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import RecommendationResponse

from app.services.platform_links import (
    platform_search
)


class GeminiRecommendationService:

    def __init__(self):

        if settings.GEMINI_API_KEY:

            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        else:

            self.client = None

    def build_prompt(
        self,
        planner: str,
        data: dict[str, Any]
    ) -> str:

        return f"""
You are PocketSmart AI.

You are a budget planning and recommendation assistant.

Planner type:
{planner}

User request:

{json.dumps(
    data,
    ensure_ascii=False,
    indent=2
)}

Your job is to generate practical,
budget-conscious recommendations.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "planner_type": "{planner}",

    "title": "Short title",

    "summary": "Practical summary",

    "budget": 50000,

    "currency": "INR",

    "budget_allocations": [
        {{
            "category": "Furniture",
            "amount": 20000,
            "percentage": 40,
            "rationale": "Reason"
        }}
    ],

    "recommendations": [
        {{
            "name": "Product or service",
            "category": "Furniture",
            "estimated_price": 5000,
            "currency": "INR",
            "platform": "Amazon",
            "rationale": "Why this fits",
            "search_url": "https://www.amazon.in/",
            "quantity": 1
        }}
    ],

    "tips": [
        "Helpful tip"
    ]
}}

Rules:

1. Keep recommendations within the supplied budget.

2. Do not claim live inventory.

3. Do not invent ratings.

4. Do not invent reviews.

5. Do not invent product IDs.

6. Prices are estimates.

7. Use these platforms when appropriate:

Amazon
Flipkart
IKEA
Swiggy
Zomato
OYO

8. Use platform search URLs.

9. For jewelry, use outfit information only
for style coordination.

10. Do not identify people in uploaded images.

11. Keep recommendations practical.

12. Return concise results.
"""

    def generate(
        self,
        planner: str,
        data: dict[str, Any],
        image_bytes: bytes | None = None,
        image_mime: str | None = None
    ) -> RecommendationResponse:

        if not self.client:

            return fallback_recommendation(
                planner,
                data
            )

        prompt = self.build_prompt(
            planner,
            data
        )

        contents = [prompt]

        if image_bytes:

            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image_mime or "image/jpeg"
                )
            )

        try:

            response = (
                self.client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.4,
                        response_mime_type="application/json"
                    )
                )
            )

            raw = response.text or ""

            parsed = json.loads(raw)

            return RecommendationResponse.model_validate(
                parsed
            )

        except Exception:

            return fallback_recommendation(
                planner,
                data
            )


def fallback_recommendation(
    planner: str,
    data: dict[str, Any]
) -> RecommendationResponse:

    budget = float(
        data["budget"]
    )

    currency = data.get(
        "currency",
        "INR"
    )

    if planner == "home":

        items = [
            (
                "LED ceiling light",
                "lighting",
                budget * 0.08,
                "IKEA"
            ),
            (
                "Side table",
                "furniture",
                budget * 0.12,
                "Amazon"
            ),
            (
                "Wall decor set",
                "decor",
                budget * 0.08,
                "Amazon"
            ),
            (
                "Storage cabinet",
                "furniture",
                budget * 0.20,
                "IKEA"
            )
        ]

        allocations = [
            (
                "Furniture",
                budget * 0.45,
                45,
                "Prioritize durable pieces."
            ),
            (
                "Lighting",
                budget * 0.20,
                20,
                "Use layered lighting."
            ),
            (
                "Decor",
                budget * 0.20,
                20,
                "Use statement pieces."
            ),
            (
                "Contingency",
                budget * 0.15,
                15,
                "Keep a reserve."
            )
        ]

        title = "Budget-friendly home setup"

        summary = (
            "A balanced starter plan prioritizing "
            "essential furniture, lighting and decor."
        )

    elif planner == "party":

        items = [
            (
                "Catering package",
                "food",
                budget * 0.38,
                "Swiggy"
            ),
            (
                "Venue or accommodation",
                "venue",
                budget * 0.25,
                "OYO"
            ),
            (
                "Decoration kit",
                "decoration",
                budget * 0.12,
                "Amazon"
            ),
            (
                "Tableware and supplies",
                "supplies",
                budget * 0.08,
                "Amazon"
            )
        ]

        allocations = [
            (
                "Food",
                budget * 0.40,
                40,
                "Food is a major variable cost."
            ),
            (
                "Venue",
                budget * 0.25,
                25,
                "Reserve a predictable amount."
            ),
            (
                "Decoration",
                budget * 0.15,
                15,
                "Keep decor simple."
            ),
            (
                "Entertainment and buffer",
                budget * 0.20,
                20,
                "Use for extras and emergencies."
            )
        ]

        event_type = data.get(
            "event_type",
            "event"
        )

        title = (
            f"{event_type.title()} budget plan"
        )

        summary = (
            f"A practical event plan for "
            f"{data.get('guests', 0)} guests."
        )

    else:

        items = [
            (
                "Minimal necklace",
                "necklace",
                budget * 0.30,
                "Flipkart"
            ),
            (
                "Matching earrings",
                "earrings",
                budget * 0.20,
                "Amazon"
            ),
            (
                "Bracelet",
                "bracelet",
                budget * 0.18,
                "Flipkart"
            ),
            (
                "Statement earrings",
                "earrings",
                budget * 0.22,
                "Amazon"
            )
        ]

        allocations = [
            (
                "Necklace",
                budget * 0.35,
                35,
                "Use one anchor piece."
            ),
            (
                "Earrings",
                budget * 0.25,
                25,
                "Match scale to the outfit."
            ),
            (
                "Bracelet",
                budget * 0.15,
                15,
                "Use as a subtle accent."
            ),
            (
                "Buffer",
                budget * 0.25,
                25,
                "Keep flexibility."
            )
        ]

        occasion = data.get(
            "occasion",
            "occasion"
        )

        title = (
            f"{occasion.title()} jewelry shortlist"
        )

        summary = (
            "A coordinated jewelry shortlist "
            "based on occasion, style and budget."
        )

    recommendations = []

    for (
        name,
        category,
        price,
        platform
    ) in items:

        recommendations.append(
            {
                "name": name,

                "category": category,

                "estimated_price": round(
                    max(price, 100),
                    2
                ),

                "currency": currency,

                "platform": platform,

                "rationale": (
                    "Fallback recommendation "
                    "used when Gemini is unavailable."
                ),

                "search_url": platform_search(
                    platform,
                    name
                ),

                "quantity": 1
            }
        )

    return RecommendationResponse(
        planner_type=planner,

        title=title,

        summary=summary,

        budget=budget,

        currency=currency,

        budget_allocations=[
            {
                "category": category,
                "amount": round(amount, 2),
                "percentage": percentage,
                "rationale": rationale
            }
            for (
                category,
                amount,
                percentage,
                rationale
            ) in allocations
        ],

        recommendations=recommendations,

        tips=[
            "Compare final prices before purchasing.",

            "Keep a contingency for delivery and taxes.",

            "Platform links are search shortcuts, "
            "not live inventory."
        ]
    )
