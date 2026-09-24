from typing import Literal

from pydantic import BaseModel, Field


class RoomItem(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

    quantity: int = Field(
        default=1,
        ge=1,
        le=100
    )


class Room(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

    items: list[RoomItem] = Field(
        default_factory=list
    )


class HomeRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    currency: str = "INR"

    style: str = Field(
        default="modern",
        max_length=80
    )

    rooms: list[Room] = Field(
        min_length=1,
        max_length=20
    )

    preferences: str = Field(
        default="",
        max_length=1000
    )


class PartyRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    currency: str = "INR"

    guests: int = Field(
        gt=0,
        le=10_000
    )

    event_type: str = Field(
        min_length=2,
        max_length=80
    )

    venue: str = Field(
        default="",
        max_length=200
    )

    preferences: str = Field(
        default="",
        max_length=1000
    )


class JewelryRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    currency: str = "INR"

    occasion: str = Field(
        min_length=2,
        max_length=100
    )

    style: str = Field(
        default="elegant",
        max_length=100
    )

    outfit_description: str = Field(
        default="",
        max_length=1000
    )


class ProductRecommendation(BaseModel):
    name: str

    category: str

    estimated_price: float = Field(
        ge=0
    )

    currency: str = "INR"

    platform: str

    rationale: str

    search_url: str

    quantity: int = Field(
        default=1,
        ge=1
    )


class BudgetAllocation(BaseModel):
    category: str

    amount: float = Field(
        ge=0
    )

    percentage: float = Field(
        ge=0,
        le=100
    )

    rationale: str


class RecommendationResponse(BaseModel):
    planner_type: Literal[
        "home",
        "party",
        "jewelry"
    ]

    title: str

    summary: str

    budget: float

    currency: str

    budget_allocations: list[
        BudgetAllocation
    ] = []

    recommendations: list[
        ProductRecommendation
    ] = []

    tips: list[str] = []

    disclaimer: str = (
        "Prices and availability are estimates. "
        "Verify final price and availability "
        "on the linked platform before purchasing."
    )
