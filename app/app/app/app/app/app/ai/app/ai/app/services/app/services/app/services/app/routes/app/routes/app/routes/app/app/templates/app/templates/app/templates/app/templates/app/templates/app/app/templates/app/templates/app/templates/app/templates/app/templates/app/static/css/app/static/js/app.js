async function api(url, options = {}) {

    const response = await fetch(
        url,
        options
    );

    const data =
        await response
            .json()
            .catch(() => ({
                detail:
                    "Unexpected server response."
            }));

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Request failed."
        );
    }

    return data;
}


async function logout() {

    await api(
        "/logout",
        {
            method: "POST"
        }
    );

    window.location.href = "/";
}


function money(
    value,
    currency = "INR"
) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: currency,
            maximumFractionDigits: 0
        }
    ).format(value);
}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        function (character) {

            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[character];

        }
    );
}


function renderResult(
    target,
    payload
) {

    const result =
        payload.result;


    const allocations =
        result.budget_allocations
            .map(
                allocation => `
                <div class="alloc">

                    <span>
                        ${escapeHtml(
                            allocation.category
                        )}
                        —
                        ${allocation.percentage}%
                    </span>

                    <b>
                        ${money(
                            allocation.amount,
                            result.currency
                        )}
                    </b>

                </div>
                `
            )
            .join("");


    const recommendations =
        result.recommendations
            .map(
                item => `
                <div class="recommendation">

                    <span class="tag">
                        ${escapeHtml(
                            item.platform
                        )}
                    </span>

                    <h3>
                        ${escapeHtml(
                            item.name
                        )}
                    </h3>

                    <p>
                        ${escapeHtml(
                            item.rationale
                        )}
                    </p>

                    <div class="price">
                        ${money(
                            item.estimated_price,
                            item.currency
                        )}
                    </div>

                    <a
                        href="${escapeHtml(
                            item.search_url
                        )}"
                        target="_blank"
                        rel="noopener"
                    >
                        Search platform →
                    </a>

                </div>
                `
            )
            .join("");


    const tips =
        result.tips
            .map(
                tip =>
                    `<li>
                        ${escapeHtml(tip)}
                    </li>`
            )
            .join("");


    target.innerHTML = `

        <h2>
            ${escapeHtml(
                result.title
            )}
        </h2>

        <p>
            ${escapeHtml(
                result.summary
            )}
        </p>


        <h3>
            Budget allocation
        </h3>

        ${allocations}


        <h3>
            Recommendations
        </h3>

        ${recommendations}


        <h3>
            Tips
        </h3>

        <ul>
            ${tips}
        </ul>


        <p class="muted">
            ${escapeHtml(
                result.disclaimer
            )}
        </p>
    `;
}


function addRoom() {

    const container =
        document.querySelector(
            "#rooms"
        );

    const roomNumber =
        container.children.length + 1;


    const room =
        document.createElement(
            "div"
        );

    room.className =
        "card room";


    room.innerHTML = `

        <label>

            Room ${roomNumber}

            <input
                name="room_name"
                required
                value="${
                    roomNumber === 1
                        ? "Living Room"
                        : "Bedroom"
                }"
            >

        </label>


        <div class="items">
        </div>


        <button
            type="button"
            class="button ghost small"
        >
            + item
        </button>
    `;


    container.appendChild(
        room
    );


    room.querySelector(
        "button"
    ).onclick = function () {

        addItem(this);

    };


    addItem(
        room.querySelector(
            "button"
        )
    );
}


function addItem(button) {

    const items =
        button.parentElement
            .querySelector(
                ".items"
            );


    const row =
        document.createElement(
            "div"
        );


    row.className =
        "item-row";


    row.style.cssText =
        `
        display:grid;
        grid-template-columns:
            1fr 90px;
        gap:8px;
        margin:8px 0;
        `;


    row.innerHTML = `

        <input
            name="item_name"
            placeholder="Item"
            required
        >

        <input
            name="item_qty"
            type="number"
            min="1"
            value="1"
        >
    `;


    items.appendChild(
        row
    );
}


document.addEventListener(
    "DOMContentLoaded",
    function () {


        const registerForm =
            document.querySelector(
                "#register-form"
            );


        if (registerForm) {

            registerForm.addEventListener(
                "submit",
                async function (event) {

                    event.preventDefault();

                    try {

                        await api(
                            "/register",
                            {
                                method: "POST",
                                body:
                                    new FormData(
                                        registerForm
                                    )
                            }
                        );

                        window.location.href =
                            "/dashboard";

                    } catch (error) {

                        registerForm
                            .querySelector(
                                ".error"
                            )
                            .textContent =
                            error.message;
                    }
                }
            );
        }


        const loginForm =
            document.querySelector(
                "#login-form"
            );


        if (loginForm) {

            loginForm.addEventListener(
                "submit",
                async function (event) {

                    event.preventDefault();

                    try {

                        await api(
                            "/login",
                            {
                                method: "POST",
                                body:
                                    new FormData(
                                        loginForm
                                    )
                            }
                        );

                        window.location.href =
                            "/dashboard";

                    } catch (error) {

                        loginForm
                            .querySelector(
                                ".error"
                            )
                            .textContent =
                            error.message;
                    }
                }
            );
        }


        const homeForm =
            document.querySelector(
                "#home-form"
            );


        if (homeForm) {

            addRoom();


            homeForm.addEventListener(
                "submit",
                async function (event) {

                    event.preventDefault();


                    const rooms =
                        [
                            ...document.querySelectorAll(
                                ".room"
                            )
                        ].map(
                            room => ({

                                name:
                                    room
                                        .querySelector(
                                            '[name="room_name"]'
                                        )
                                        .value,

                                items:
                                    [
                                        ...room.querySelectorAll(
                                            ".item-row"
                                        )
                                    ].map(
                                        item => ({

                                            name:
                                                item
                                                    .querySelector(
                                                        '[name="item_name"]'
                                                    )
                                                    .value,

                                            quantity:
                                                Number(
                                                    item
                                                        .querySelector(
                                                            '[name="item_qty"]'
                                                        )
                                                        .value
                                                )
                                        })
                                    )
                            })
                        );


                    const body = {

                        budget:
                            Number(
                                homeForm.budget.value
                            ),

                        currency:
                            "INR",

                        style:
                            homeForm.style.value,

                        preferences:
                            homeForm.preferences.value,

                        rooms:
                            rooms
                    };


                    try {

                        const response =
                            await api(
                                "/generate-home",
                                {
                                    method: "POST",

                                    headers: {
                                        "Content-Type":
                                            "application/json"
                                    },

                                    body:
                                        JSON.stringify(
                                            body
                                        )
                                }
                            );


                        renderResult(
                            document.querySelector(
                                "#results"
                            ),
                            response
                        );

                    } catch (error) {

                        homeForm
                            .querySelector(
                                ".error"
                            )
                            .textContent =
                            error.message;
                    }
                }
            );
        }


        const partyForm =
            document.querySelector(
                "#party-form"
            );


        if (partyForm) {

            partyForm.addEventListener(
                "submit",
                async function (event) {

                    event.preventDefault();


                    const body = {

                        budget:
                            Number(
                                partyForm.budget.value
                            ),

                        currency:
                            "INR",

                        guests:
                            Number(
                                partyForm.guests.value
                            ),

                        event_type:
                            partyForm.event_type.value,

                        venue:
                            partyForm.venue.value,

                        preferences:
                            partyForm.preferences.value
                    };


                    try {

                        const response =
                            await api(
                                "/generate-party",
                                {
                                    method: "POST",

                                    headers: {
                                        "Content-Type":
                                            "application/json"
                                    },

                                    body:
                                        JSON.stringify(
                                            body
                                        )
                                }
                            );


                        renderResult(
                            document.querySelector(
                                "#results"
                            ),
                            response
                        );

                    } catch (error) {

                        partyForm
                            .querySelector(
                                ".error"
                            )
                            .textContent =
                            error.message;
                    }
                }
            );
        }


        const jewelryForm =
            document.querySelector(
                "#jewelry-form"
            );


        if (jewelryForm) {

            jewelryForm.addEventListener(
                "submit",
                async function (event) {

                    event.preventDefault();


                    try {

                        const response =
                            await api(
                                "/generate-jewelry",
                                {
                                    method: "POST",
                                    body:
                                        new FormData(
                                            jewelryForm
                                        )
                                }
                            );


                        renderResult(
                            document.querySelector(
                                "#results"
                            ),
                            response
                        );

                    } catch (error) {

                        jewelryForm
                            .querySelector(
                                ".error"
                            )
                            .textContent =
                            error.message;
                    }
                }
            );
        }

    }
);
