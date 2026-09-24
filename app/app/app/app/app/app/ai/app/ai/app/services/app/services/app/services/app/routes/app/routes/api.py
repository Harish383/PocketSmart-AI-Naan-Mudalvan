import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile
)

from fastapi.responses import JSONResponse

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password
)

from app.config import settings

from app.database import get_db

from app.models import User

from app.schemas import (
    HomeRequest,
    PartyRequest,
    JewelryRequest
)

from app.services.recommendation_service import (
    service
)


router = APIRouter()


def set_auth_cookie(
    response,
    token: str
):

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
            * 60
        )
    )


@router.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):

    name = name.strip()

    email = email.strip().lower()

    if len(name) < 2:

        raise HTTPException(
            status_code=400,
            detail="Name must contain at least 2 characters."
        )

    if len(password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters."
        )

    with get_db() as db:

        existing = db.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Email is already registered."
            )

        cursor = db.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hash_password(password)
            )
        )

        user_id = cursor.lastrowid

    response = JSONResponse(
        {
            "message": "Registration successful.",
            "user_id": user_id
        }
    )

    set_auth_cookie(
        response,
        create_access_token(user_id)
    )

    return response


@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...)
):

    email = email.strip().lower()

    with get_db() as db:

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if (
        not user
        or not verify_password(
            password,
            user["password_hash"]
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    response = JSONResponse(
        {
            "message": "Login successful."
        }
    )

    set_auth_cookie(
        response,
        create_access_token(
            user["id"]
        )
    )

    return response


@router.post("/logout")
def logout():

    response = JSONResponse(
        {
            "message": "Logged out successfully."
        }
    )

    response.delete_cookie(
        "access_token"
    )

    return response


@router.post("/token")
def token(
    email: str = Form(...),
    password: str = Form(...)
):

    email = email.strip().lower()

    with get_db() as db:

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if (
        not user
        or not verify_password(
            password,
            user["password_hash"]
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials."
        )

    return {
        "access_token":
            create_access_token(user["id"]),

        "token_type":
            "bearer"
    }


@router.post("/generate-home")
def generate_home(
    payload: HomeRequest,
    user: User = Depends(
        get_current_user
    )
):

    recommendation_id, result = (
        service.create(
            user_id=user.id,
            planner="home",
            payload=payload.model_dump()
        )
    )

    return {
        "recommendation_id":
            recommendation_id,

        "result":
            result.model_dump()
    }


@router.post("/generate-party")
def generate_party(
    payload: PartyRequest,
    user: User = Depends(
        get_current_user
    )
):

    recommendation_id, result = (
        service.create(
            user_id=user.id,
            planner="party",
            payload=payload.model_dump()
        )
    )

    return {
        "recommendation_id":
            recommendation_id,

        "result":
            result.model_dump()
    }


@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    currency: str = Form("INR"),
    occasion: str = Form(...),
    style: str = Form("elegant"),
    outfit_description: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user: User = Depends(
        get_current_user
    )
):

    payload = JewelryRequest(
        budget=budget,
        currency=currency,
        occasion=occasion,
        style=style,
        outfit_description=outfit_description
    ).model_dump()

    image_bytes = None
    image_mime = None

    if outfit_image:

        image_bytes = (
            await outfit_image.read()
        )

        if len(image_bytes) > settings.MAX_IMAGE_BYTES:

            raise HTTPException(
                status_code=413,
                detail="Image must be 5 MB or smaller."
            )

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if (
            outfit_image.content_type
            not in allowed_types
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPEG, PNG and WebP "
                    "images are supported."
                )
            )

        image_mime = (
            outfit_image.content_type
        )

    recommendation_id, result = (
        service.create(
            user_id=user.id,
            planner="jewelry",
            payload=payload,
            image_bytes=image_bytes,
            image_mime=image_mime
        )
    )

    return {
        "recommendation_id":
            recommendation_id,

        "result":
            result.model_dump()
    }


@router.get(
    "/recommendations-details/{recommendation_id}"
)
def recommendation_details(
    recommendation_id: int,
    user: User = Depends(
        get_current_user
    )
):

    with get_db() as db:

        row = db.execute(
            """
            SELECT
                id,
                planner_type,
                result_json,
                created_at
            FROM recommendations
            WHERE
                id = ?
                AND user_id = ?
            """,
            (
                recommendation_id,
                user.id
            )
        ).fetchone()

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found."
        )

    return {
        "id": row["id"],

        "planner_type":
            row["planner_type"],

        "result":
            json.loads(
                row["result_json"]
            ),

        "created_at":
            row["created_at"]
    }


@router.get("/session-info")
def session_info(
    user: User = Depends(
        get_current_user
    )
):

    return {
        "authenticated": True,

        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.get("/session-data")
def session_data(
    user: User = Depends(
        get_current_user
    )
):

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },

        "recent_recommendations":
            service.history(
                user.id,
                10
            )
    }


@router.get("/history-data")
def history_data(
    user: User = Depends(
        get_current_user
    )
):

    return {
        "items":
            service.history(
                user.id
            )
    }


@router.get("/startup")
def startup():

    return {
        "status": "ready",

        "gemini_configured":
            bool(
                settings.GEMINI_API_KEY
            ),

        "model":
            settings.GEMINI_MODEL
    }


@router.get("/health")
def health():

    return {
        "status": "ok"
    }
