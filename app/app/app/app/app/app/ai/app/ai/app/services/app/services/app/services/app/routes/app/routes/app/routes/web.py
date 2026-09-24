from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from app.auth import (
    get_current_user
)

from app.database import (
    get_db
)


templates = Jinja2Templates(
    directory="app/templates"
)


router = APIRouter()


def get_optional_user(request):

    try:

        return get_current_user(
            request
        )

    except Exception:

        return None


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user":
                get_optional_user(request)
        }
    )


@router.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(
    request: Request
):

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user":
                get_optional_user(request)
        }
    )


@router.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(
    request: Request
):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "user":
                get_optional_user(request)
        }
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(
    request: Request
):

    user = get_current_user(
        request
    )

    with get_db() as db:

        rows = db.execute(
            """
            SELECT
                id,
                planner_type,
                created_at
            FROM recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 8
            """,
            (user.id,)
        ).fetchall()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "items": rows
        }
    )


@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse
)
def planner(
    request: Request,
    planner: str
):

    user = get_current_user(
        request
    )

    if planner not in {
        "home",
        "party",
        "jewelry"
    }:

        return RedirectResponse(
            "/"
        )

    return templates.TemplateResponse(
        f"{planner}_planner.html",
        {
            "request": request,
            "user": user
        }
    )


@router.get(
    "/history",
    response_class=HTMLResponse
)
def history(
    request: Request
):

    user = get_current_user(
        request
    )

    with get_db() as db:

        rows = db.execute(
            """
            SELECT
                id,
                planner_type,
                created_at,
                result_json
            FROM recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user.id,)
        ).fetchall()

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "user": user,
            "items": rows
        }
    )


@router.get(
    "/testimonials",
    response_class=HTMLResponse
)
def testimonials(
    request: Request
):

    return templates.TemplateResponse(
        "testimonials.html",
        {
            "request": request,
            "user":
                get_optional_user(request)
        }
    )
