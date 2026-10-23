

"use strict";


/* ==========================================================================
   1. MOVIE DATA
   Every movie is an object with the same properties:
     id       - short unique code; also used in links, e.g. booking.html?movie=neon-orbit
     genres   - the FIRST genre is the main genre, any others are secondary
     rating   - according to Australian classification: G, PG, M or MA15+
     audience - age groups the film is made for (Child, Teen, Adult)
     viewing  - viewing occasions it suits (Family, Date Night, Friends, Solo)
     price    - full adult ticket price in Australian dollars
     sessions - daily session times in 24-hour "HH:MM" format
   The same information is written in the HTML of movies.html for visitors.
   ========================================================================== */
const MOVIES = [
    {
        id: "skyline-pursuit",
        title: "Skyline Pursuit",
        genres: ["Action", "Thriller"],
        rating: "M",
        runtime: 128,
        price: 22.00,
        audience: ["Teen", "Adult"],
        viewing: ["Friends", "Solo"],
        sessions: ["10:30", "13:45", "19:00", "21:30"],
        image: "images/movie1.jpg"
    },
    {
        id: "lantern-keepers",
        title: "The Lantern Keepers",
        genres: ["Animation", "Adventure"],
        rating: "G",
        runtime: 98,
        price: 16.00,
        audience: ["Child", "Teen", "Adult"],
        viewing: ["Family"],
        sessions: ["09:30", "11:45", "14:00", "16:15"],
        image: "images/movie2.jpg"
    },
    {
        id: "plus-one-problems",
        title: "Plus One Problems",
        genres: ["Comedy", "Romance"],
        rating: "M",
        runtime: 112,
        price: 19.50,
        audience: ["Teen", "Adult"],
        viewing: ["Date Night", "Friends"],
        sessions: ["12:15", "17:30", "20:15"],
        image: "images/movie3.jpg"
    },
    {
        id: "quiet-harbour",
        title: "Quiet Harbour",
        genres: ["Drama"],
        rating: "M",
        runtime: 121,
        price: 19.50,
        audience: ["Adult"],
        viewing: ["Solo", "Date Night"],
        sessions: ["11:00", "15:30", "18:45"],
        image: "images/movie4.jpg"
    },
    {
        id: "neon-orbit",
        title: "Neon Orbit",
        genres: ["Sci-Fi", "Action"],
        rating: "M",
        runtime: 135,
        price: 24.00,
        audience: ["Teen", "Adult"],
        viewing: ["Friends", "Solo"],
        sessions: ["13:00", "16:30", "20:00"],
        image: "images/movie5.jpg"
    },
    {
        id: "hollow-lane",
        title: "Midnight at Hollow Lane",
        genres: ["Horror", "Mystery"],
        rating: "MA15+",
        runtime: 104,
        price: 19.50,
        audience: ["Adult"],
        viewing: ["Friends", "Date Night"],
        sessions: ["18:30", "21:00", "23:15"],
        image: "images/movie6.jpg"
    },
    {
        id: "grandpa-goes-viral",
        title: "Grandpa Goes Viral",
        genres: ["Comedy", "Family"],
        rating: "PG",
        runtime: 95,
        price: 17.00,
        audience: ["Child", "Teen", "Adult"],
        viewing: ["Family", "Friends"],
        sessions: ["10:00", "12:30", "15:00", "17:45"],
        image: "images/movie7.jpg"
    },
    {
        id: "paper-hearts",
        title: "Paper Hearts in Paris",
        genres: ["Romance", "Drama"],
        rating: "PG",
        runtime: 109,
        price: 18.00,
        audience: ["Teen", "Adult"],
        viewing: ["Date Night", "Solo"],
        sessions: ["11:30", "16:00", "19:15"],
        image: "images/movie8.jpg"
    },
    {
        id: "robo-pup-rescue",
        title: "Robo Pup Rescue",
        genres: ["Animation", "Action"],
        rating: "PG",
        runtime: 92,
        price: 16.00,
        audience: ["Child", "Teen"],
        viewing: ["Family", "Friends"],
        sessions: ["09:45", "12:00", "14:30", "16:45"],
        image: "images/movie9.jpg"
    }
];

/* Ticket types: the movie's adult price is multiplied by "rate" */
const TICKET_TYPES = {
    adult: { label: "Adult", rate: 1 },
    student: { label: "Student", rate: 0.8 },   /* 20% off */
    child: { label: "Child", rate: 0.6 }        /* 40% off */
};

/* Accepted credit cards and how many digits each card number must have */
const CARD_TYPES = {
    visa: { label: "Visa", digits: 16 },
    mastercard: { label: "Mastercard", digits: 16 },
    amex: { label: "American Express", digits: 15 }
};

const MAX_TICKETS = 10;                         
const WATCHLIST_KEY = "cinesparkWatchlist";     

/* Reusable regular expressions for validation */
const EMAIL_PATTERN = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
const DIGITS_ONLY = /^\d+$/;


/* ==========================================================================
   2. GENERAL HELPER FUNCTIONS
   ========================================================================== */

/* Returns the movie object with the given id, or null if there is none */
function findMovieById(id) {
    const movie = MOVIES.find(function (item) {
        return item.id === id;
    });
    return movie || null;
}


function formatPrice(amount) {
    return "$" + amount.toFixed(2);
}


function roundMoney(amount) {
    return Math.round(amount * 100) / 100;
}

/* 128 -> "2h 8m" */
function formatRuntime(minutes) {
    return Math.floor(minutes / 60) + "h " + (minutes % 60) + "m";
}

/* "19:00" -> "7:00 pm" */
function formatTime(time24) {
    const parts = time24.split(":");
    let hours = parseInt(parts[0], 10);
    const suffix = hours >= 12 ? "pm" : "am";
    hours = hours % 12;
    if (hours === 0) {
        hours = 12;
    }
    return hours + ":" + parts[1] + " " + suffix;
}

/* "MA15+" -> "rating rating-ma" (CSS classes for the coloured badge) */
function ratingClass(rating) {
    return "rating rating-" + rating.replace("15+", "").toLowerCase();
}

/* Adds a leading zero: 7 -> "07" */
function pad(number) {
    return String(number).padStart(2, "0");
}

/* Today's date in the same "YYYY-MM-DD" format used by <input type="date"> */
function getTodayString() {
    const now = new Date();
    return now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate());
}

/* Current time as "HH:MM" (24-hour) */
function getNowTimeString() {
    const now = new Date();
    return pad(now.getHours()) + ":" + pad(now.getMinutes());
}

/* Trimmed value of a form field ("" if the field does not exist) */
function getFieldValue(id) {
    const field = document.getElementById(id);
    return field ? field.value.trim() : "";
}

/* Value of the checked radio button in a group ("" if none is checked) */
function getCheckedValue(name) {
    const checked = document.querySelector('input[name="' + name + '"]:checked');
    return checked ? checked.value : "";
}

/* ["a", "b", "c"] -> "a, b and c" (used to build friendly error messages) */
function joinWithAnd(items) {
    if (items.length <= 1) {
        return items.join("");
    }
    return items.slice(0, -1).join(", ") + " and " + items[items.length - 1];
}

/* Shows a short message at the bottom of the screen (watchlist feedback) */
let toastTimer = null;
function showToast(message) {
    const toast = document.getElementById("toast");
    if (!toast) {
        return;
    }
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
        toast.classList.remove("is-visible");
    }, 2500);
}


/* ==========================================================================
   3. NAVIGATION - mobile menu button

   ========================================================================== */
function initNavigation() {
    const toggle = document.getElementById("navToggle");
    const nav = document.getElementById("mainNav");
    if (!toggle || !nav) {
        return;
    }

    toggle.addEventListener("click", function () {
        nav.classList.toggle("is-open");
    });
}


/* ==========================================================================
   4. WATCHLIST / FAVOURITES - BONUS TASK

   ========================================================================== */


function getWatchlist() {
    try {
        const saved = sessionStorage.getItem(WATCHLIST_KEY);
        const list = saved ? JSON.parse(saved) : [];
        return Array.isArray(list) ? list : [];
    } catch (error) {
        return [];
    }
}

function saveWatchlist(list) {
    try {
        sessionStorage.setItem(WATCHLIST_KEY, JSON.stringify(list));
    } catch (error) {
        /* Storage is unavailable (e.g. disabled by the browser) - nothing else to do */
    }
    updateWatchlistCount();
}

function isInWatchlist(movieId) {
    return getWatchlist().includes(movieId);
}

function addToWatchlist(movieId) {
    const list = getWatchlist();
    if (!list.includes(movieId)) {
        list.push(movieId);
        saveWatchlist(list);
    }
}

function removeFromWatchlist(movieId) {
    const list = getWatchlist().filter(function (id) {
        return id !== movieId;
    });
    saveWatchlist(list);
}

/* Updates the small number badge next to "Watchlist" in the navigation */
function updateWatchlistCount() {
    const badge = document.getElementById("watchlistCount");
    if (badge) {
        badge.textContent = getWatchlist().length;
    }
}

/* Changes a watchlist button's text and style to match the saved state */
function setWatchlistButtonState(button, saved) {
    button.textContent = saved ? "♥ In Watchlist" : "♡ Add to Watchlist";
    button.classList.toggle("is-saved", saved);
}

/* movies.html - every "Add to Watchlist" button adds or removes its movie */
function initWatchlistButtons() {
    const buttons = document.querySelectorAll(".watchlist-btn");

    buttons.forEach(function (button) {
        const movieId = button.dataset.movieId;
        setWatchlistButtonState(button, isInWatchlist(movieId));

        button.addEventListener("click", function () {
            const movie = findMovieById(movieId);
            if (isInWatchlist(movieId)) {
                removeFromWatchlist(movieId);
                setWatchlistButtonState(button, false);
                showToast(movie.title + " was removed from your watchlist.");
            } else {
                addToWatchlist(movieId);
                setWatchlistButtonState(button, true);
                showToast(movie.title + " was added to your watchlist.");
            }
        });
    });
}


function createWatchlistItemHTML(movie) {
    return `
        <article class="watch-item">
            <img src="${movie.image}" alt="Poster for ${movie.title}" width="400" height="600">
            <div>
                <h3>${movie.title}</h3>
                <p><span class="${ratingClass(movie.rating)}">${movie.rating}</span>
                    ${movie.genres.join(", ")} &middot; ${formatRuntime(movie.runtime)}</p>
                <p>Adult ticket: ${formatPrice(movie.price)}</p>
                <div class="watch-item-actions">
                    <a class="btn btn-primary btn-small" href="booking.html?movie=${movie.id}&amp;from=watchlist">Book Now</a>
                    <button type="button" class="btn btn-outline btn-small remove-btn" data-movie-id="${movie.id}">Remove</button>
                </div>
            </div>
        </article>`;
}

/* watchlist.html - draws the list (or the empty message) from sessionStorage */
function renderWatchlist() {
    const container = document.getElementById("watchlistItems");
    const emptyState = document.getElementById("watchlistEmpty");
    const clearButton = document.getElementById("clearWatchlist");
    const summary = document.getElementById("watchlistSummary");

    /* Convert saved ids into movie objects (ignoring any unknown ids) */
    const movies = getWatchlist().map(findMovieById).filter(function (movie) {
        return movie !== null;
    });

    container.innerHTML = movies.map(createWatchlistItemHTML).join("");
    emptyState.hidden = movies.length > 0;
    clearButton.hidden = movies.length === 0;
    summary.textContent = movies.length === 1
        ? "You have 1 movie saved."
        : "You have " + movies.length + " movies saved.";
}

function initWatchlistPage() {
    const container = document.getElementById("watchlistItems");
    if (!container) {
        return;
    }

    renderWatchlist();

    /* One click listener on the container handles every "Remove" button,
       including buttons created later (this is called event delegation). */
    container.addEventListener("click", function (event) {
        const button = event.target.closest(".remove-btn");
        if (!button) {
            return;
        }
        const movie = findMovieById(button.dataset.movieId);
        removeFromWatchlist(button.dataset.movieId);
        renderWatchlist();
        showToast(movie.title + " was removed from your watchlist.");
    });

    document.getElementById("clearWatchlist").addEventListener("click", function () {
        if (window.confirm("Remove all movies from your watchlist?")) {
            saveWatchlist([]);
            renderWatchlist();
            showToast("Your watchlist has been cleared.");
        }
    });
}


/* ==========================================================================
   5. RECOMMENDATION ENGINE (recommend.html)
   
   ========================================================================== */
const RATINGS_BY_AGE = {
    Child: ["G", "PG"],
    Teen: ["G", "PG", "M"],
    Adult: ["G", "PG", "M", "MA15+"]
};

const POINTS = {
    mainGenre: 5,
    otherGenre: 3,
    viewing: 3,
    audience: 2
};

const MAX_POINTS = POINTS.mainGenre + POINTS.viewing + POINTS.audience;   /* equals to 10 */

const AGE_LABELS = {
    Child: "children (under 13)",
    Teen: "teens (13-17)",
    Adult: "adults (18+)"
};

const VIEWING_REASONS = {
    "Family": "A great pick for a family outing",
    "Date Night": "Perfect for a date night",
    "Friends": "Fun to watch with a group of friends",
    "Solo": "Rewarding to watch on your own"
};

/* Rules 1 and 2: which classifications are allowed for these preferences */
function getAllowedRatings(ageGroup, viewing) {
    let allowed = RATINGS_BY_AGE[ageGroup];
    if (viewing === "Family") {
        allowed = allowed.filter(function (rating) {
            return rating === "G" || rating === "PG";
        });
    }
    return allowed;
}

/* Rule 3: score one movie and remember why it scored */
function scoreMovie(movie, prefs) {
    let genrePoints = 0;
    let score = 0;
    const reasons = [];

    if (movie.genres[0] === prefs.genre) {
        genrePoints = POINTS.mainGenre;
        reasons.push(prefs.genre + " is its main genre - just what you asked for");
    } else if (movie.genres.includes(prefs.genre)) {
        genrePoints = POINTS.otherGenre;
        reasons.push("Includes plenty of " + prefs.genre + " moments");
    }
    score += genrePoints;

    if (movie.viewing.includes(prefs.viewing)) {
        score += POINTS.viewing;
        reasons.push(VIEWING_REASONS[prefs.viewing]);
    }

    if (movie.audience.includes(prefs.age)) {
        score += POINTS.audience;
        reasons.push("Made with " + AGE_LABELS[prefs.age] + " in mind");
    }

    reasons.push("Rated " + movie.rating + " - suitable for your age group");

    return { movie: movie, score: score, genrePoints: genrePoints, reasons: reasons };
}


function getRecommendations(prefs) {
    const allowedRatings = getAllowedRatings(prefs.age, prefs.viewing);

    /* Rule 1 + 2: keep only suitable movies */
    const suitable = MOVIES.filter(function (movie) {
        return allowedRatings.includes(movie.rating);
    });

    /* Rule 3: score them */
    const scored = suitable.map(function (movie) {
        return scoreMovie(movie, prefs);
    });

    /* Rule 4: sort by score, then by genre points when scores are equal */
    scored.sort(function (a, b) {
        return (b.score - a.score) || (b.genrePoints - a.genrePoints);
    });

    /* Movies of the chosen genre that were removed by the age/family filter */
    const filteredOut = MOVIES.filter(function (movie) {
        return movie.genres.includes(prefs.genre) && !allowedRatings.includes(movie.rating);
    });

    return {
        allowedRatings: allowedRatings,
        results: scored.slice(0, 3),
        hasGenreMatch: scored.some(function (item) {
            return item.genrePoints > 0;
        }),
        filteredOut: filteredOut
    };
}

/* Builds the HTML for one recommended movie card */
function createResultCardHTML(result, index) {
    const movie = result.movie;
    const percent = Math.round((result.score / MAX_POINTS) * 100);
    const reasonsHTML = result.reasons.map(function (reason) {
        return "<li>" + reason + "</li>";
    }).join("");

    return `
        <article class="result-card${index === 0 ? " top-pick" : ""}">
            <img src="${movie.image}" alt="Poster for ${movie.title}" width="400" height="600">
            <div>
                <p class="result-rank">${index === 0 ? "★ Top pick" : "Match #" + (index + 1)}</p>
                <h3>${movie.title}</h3>
                <p class="result-meta"><span class="${ratingClass(movie.rating)}">${movie.rating}</span>
                    ${movie.genres.join(" / ")} &middot; ${formatRuntime(movie.runtime)} &middot; ${formatPrice(movie.price)}</p>
                <div class="match">
                    <span class="match-label">${percent}% match</span>
                    <span class="match-bar"><span style="width: ${percent}%"></span></span>
                </div>
                <ul class="reasons">${reasonsHTML}</ul>
                <div class="result-actions">
                    <a class="btn btn-primary btn-small" href="booking.html?movie=${movie.id}&amp;from=recommend">Book this movie</a>
                    <a class="btn btn-outline btn-small" href="movies.html#${movie.id}">View details</a>
                </div>
            </div>
        </article>`;
}

/* Shows the recommendations (or a helpful message) on the page */
function renderRecommendations(prefs, outcome) {
    const resultsBox = document.getElementById("recommendResults");
    const placeholder = document.getElementById("resultsPlaceholder");

    let html = `<p class="results-summary">For <strong>${prefs.genre}</strong> fans, watching as
        <strong>${AGE_LABELS[prefs.age]}</strong> on a <strong>${prefs.viewing}</strong> outing,
        we only considered movies rated <strong>${outcome.allowedRatings.join(", ")}</strong>.</p>`;

    if (!outcome.hasGenreMatch) {
        let reason = "We don't have a suitable " + prefs.genre + " movie showing right now";
        if (outcome.filteredOut.length > 0) {
            const titles = outcome.filteredOut.map(function (movie) {
                return movie.title + " (" + movie.rating + ")";
            });
            reason = "Our " + prefs.genre + " movies - " + joinWithAnd(titles) +
                " - are not suitable for " + (prefs.viewing === "Family" ? "a family outing" : AGE_LABELS[prefs.age]);
        }
        html += `<p class="notice">${reason}, so here are the closest matches based on your other preferences.</p>`;
    }

    html += outcome.results.map(createResultCardHTML).join("");

    resultsBox.innerHTML = html;
    resultsBox.hidden = false;
    placeholder.hidden = true;

    /* On phones and tablets the results are below the form, so scroll to them */
    if (window.innerWidth < 1024) {
        document.getElementById("resultsHeading").scrollIntoView({ behavior: "smooth" });
    }
}

function initRecommendForm() {
    const form = document.getElementById("recommendForm");
    if (!form) {
        return;
    }

    /* Each rule returns an error message, or "" when the answer is fine */
    const rules = {
        genre: function () {
            return getCheckedValue("genre") ? "" : "Please choose a preferred genre.";
        },
        ageGroup: function () {
            return getCheckedValue("ageGroup") ? "" : "Please choose an age group.";
        },
        viewing: function () {
            return getCheckedValue("viewing") ? "" : "Please choose a viewing preference.";
        }
    };

    let hasSubmitted = false;

    function showRecommendations() {
        const prefs = {
            genre: getCheckedValue("genre"),
            age: getCheckedValue("ageGroup"),
            viewing: getCheckedValue("viewing")
        };
        renderRecommendations(prefs, getRecommendations(prefs));
    }

    form.addEventListener("submit", function (event) {
        /* Results are shown on this page, so the form is never sent to a server */
        event.preventDefault();
        hasSubmitted = true;
        const invalidFields = validateFields(rules);
        if (invalidFields.length > 0) {
            focusField(invalidFields[0]);
            return;
        }
        showRecommendations();
    });

    /* After the first search, changing any answer updates the results instantly */
    form.addEventListener("change", function () {
        if (hasSubmitted && validateFields(rules).length === 0) {
            showRecommendations();
        }
    });

    form.addEventListener("reset", function () {
        hasSubmitted = false;
        clearAllErrors(rules);
        document.getElementById("recommendResults").hidden = true;
        document.getElementById("resultsPlaceholder").hidden = false;
    });
}


/* ==========================================================================
   6. FORM VALIDATION HELPERS (shared by the registration and booking forms)

   ========================================================================== */

/* Displays an error message under a field and marks the field as invalid */
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorBox = document.getElementById(fieldId + "Error");
    if (errorBox) {
        errorBox.textContent = message;
    }
    if (field) {
        field.classList.add("is-invalid");
    }
}

/* Removes the error message and invalid styling from a field */
function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorBox = document.getElementById(fieldId + "Error");
    if (errorBox) {
        errorBox.textContent = "";
    }
    if (field) {
        field.classList.remove("is-invalid");
    }
}

function clearAllErrors(rules) {
    Object.keys(rules).forEach(clearFieldError);
}

/* Runs every rule, shows/clears messages and returns the ids of invalid fields */
function validateFields(rules) {
    const invalidFields = [];
    Object.keys(rules).forEach(function (fieldId) {
        const message = rules[fieldId]();
        if (message) {
            showFieldError(fieldId, message);
            invalidFields.push(fieldId);
        } else {
            clearFieldError(fieldId);
        }
    });
    return invalidFields;
}

/* Shows how many errors are left in the box at the top of the form */
function updateErrorSummary(summaryId, invalidFields) {
    const summary = document.getElementById(summaryId);
    if (!summary) {
        return;
    }
    if (invalidFields.length === 0) {
        summary.hidden = true;
        summary.textContent = "";
        return;
    }
    const count = invalidFields.length;
    const text = "Please fix the " + count + (count === 1 ? " error" : " errors") +
        " highlighted below before submitting the form.";
    if (summary.textContent !== text) {
        summary.textContent = text;
    }
    summary.hidden = false;
}


function focusField(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) {
        return;
    }
    const target = field.matches("fieldset") ? field.querySelector("input") : field;
    if (target) {
        target.focus();
    }
}

/* Connects a rules object to a form:
     - on submit, every rule is checked; if any fail the submission is blocked
     - after the first attempt the form is re-checked as the user types,
       so each error disappears as soon as it is fixed                       */
function setupFormValidation(form, rules, summaryId) {
    let hasTriedToSubmit = false;

    form.addEventListener("submit", function (event) {
        hasTriedToSubmit = true;
        const invalidFields = validateFields(rules);
        updateErrorSummary(summaryId, invalidFields);
        if (invalidFields.length > 0) {
            event.preventDefault();          /* block submission until all errors are fixed */
            focusField(invalidFields[0]);
        }
    });

    function recheck() {
        if (hasTriedToSubmit) {
            updateErrorSummary(summaryId, validateFields(rules));
        }
    }
    form.addEventListener("input", recheck);
    form.addEventListener("change", recheck);

    form.addEventListener("reset", function () {
        hasTriedToSubmit = false;
        clearAllErrors(rules);
        updateErrorSummary(summaryId, []);
    });
}

/* Shared email check used by both forms */
function checkEmail(value, label) {
    if (value === "") {
        return "Please enter your " + label + ".";
    }
    if (!EMAIL_PATTERN.test(value)) {
        return "Please enter a valid " + label + " (for example name@example.com).";
    }
    return "";
}


/* ==========================================================================
   7. REGISTRATION FORM (register.html)
   ========================================================================== */

/* Password requirements - used for both the live checklist and validation */
const PASSWORD_RULES = [
    { id: "length", text: "at least 10 characters", test: function (pw) { return pw.length >= 10; } },
    { id: "upper", text: "an uppercase letter", test: function (pw) { return /[A-Z]/.test(pw); } },
    { id: "lower", text: "a lowercase letter", test: function (pw) { return /[a-z]/.test(pw); } },
    { id: "number", text: "a number", test: function (pw) { return /[0-9]/.test(pw); } },
    { id: "special", text: "a special character (e.g. ! @ # $)", test: function (pw) { return /[^A-Za-z0-9]/.test(pw); } }
];

/* Returns the descriptions of the password rules that are NOT yet met */
function getMissingPasswordRules(password) {
    return PASSWORD_RULES.filter(function (rule) {
        return !rule.test(password);
    }).map(function (rule) {
        return rule.text;
    });
}

/* Ticks each item of the checklist under the password box as the user types */
function updatePasswordChecklist() {
    const password = document.getElementById("password").value;
    PASSWORD_RULES.forEach(function (rule) {
        const item = document.querySelector('#passwordRules [data-rule="' + rule.id + '"]');
        if (item) {
            item.classList.toggle("met", rule.test(password));
        }
    });
}

function initRegisterForm() {
    const form = document.getElementById("registerForm");
    if (!form) {
        return;
    }

    const rules = {
        username: function () {
            const value = getFieldValue("username");
            if (value === "") {
                return "Please enter a username.";
            }
            if (value.length < 5) {
                return "Username must be at least 5 characters long (you entered " + value.length + ").";
            }
            if (!/^[A-Za-z0-9_]+$/.test(value)) {
                return "Username can only contain letters, numbers and underscores (_) - no spaces or symbols.";
            }
            return "";
        },
        email: function () {
            return checkEmail(getFieldValue("email"), "email address");
        },
        phone: function () {
            const value = getFieldValue("phone");
            if (value === "") {
                return "Please enter your phone number.";
            }
            if (!DIGITS_ONLY.test(value)) {
                return "Phone number must contain digits only (no spaces, dashes or + sign).";
            }
            if (value.length < 8 || value.length > 15) {
                return "Phone number must be between 8 and 15 digits long (you entered " + value.length + ").";
            }
            return "";
        },
        password: function () {
            const value = document.getElementById("password").value;   /* not trimmed: spaces count */
            if (value === "") {
                return "Please enter a password.";
            }
            const missing = getMissingPasswordRules(value);
            if (missing.length > 0) {
                return "Password must contain " + joinWithAnd(missing) + ".";
            }
            return "";
        },
        confirmPassword: function () {
            const value = document.getElementById("confirmPassword").value;
            if (value === "") {
                return "Please confirm your password.";
            }
            if (value !== document.getElementById("password").value) {
                return "Passwords do not match. Please type the same password again.";
            }
            return "";
        },
        gender: function () {
            return getCheckedValue("gender") ? "" : "Please select your gender.";
        },
        genres: function () {
            const checked = document.querySelectorAll('input[name="genres[]"]:checked');
            return checked.length > 0 ? "" : "Please choose at least one preferred movie genre.";
        },
        country: function () {
            return getFieldValue("country") ? "" : "Please select your country or region.";
        }
    };

    setupFormValidation(form, rules, "registerErrors");

    document.getElementById("password").addEventListener("input", updatePasswordChecklist);
    form.addEventListener("reset", function () {
        /* The reset event fires before the fields are cleared, so wait a moment */
        setTimeout(updatePasswordChecklist, 0);
    });
}


/* ==========================================================================
   8. BOOKING FORM (booking.html)
   ========================================================================== */


function prefillMovieFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const movie = findMovieById(params.get("movie"));
    if (!movie) {
        return;      /* no (or unknown) movie in the URL - user chooses from the dropdown */
    }

    document.getElementById("movie").value = movie.id;

    const sources = {
        movies: "the Movies page",
        recommend: "your recommendations",
        watchlist: "your watchlist"
    };
    const source = sources[params.get("from")] || "the previous page";
    const notice = document.getElementById("prefillNotice");
    notice.innerHTML = "<strong>" + movie.title + "</strong> has been selected for you from " +
        source + ". You can change the movie at any time using the Movie dropdown.";
    notice.hidden = false;
}


function updateMoviePreview() {
    const preview = document.getElementById("moviePreview");
    const movie = findMovieById(getFieldValue("movie"));
    if (!movie) {
        preview.hidden = true;
        preview.innerHTML = "";
        return;
    }
    preview.innerHTML = `
        <img src="${movie.image}" alt="" width="400" height="600">
        <div>
            <p class="preview-title">${movie.title}</p>
            <p class="preview-meta"><span class="${ratingClass(movie.rating)}">${movie.rating}</span>
                ${movie.genres.join(", ")} &middot; ${formatRuntime(movie.runtime)}</p>
            <p class="preview-meta">Adult ticket ${formatPrice(movie.price)}</p>
        </div>`;
    preview.hidden = false;
}


function updateSessionTimes() {
    const select = document.getElementById("sessionTime");
    const movie = findMovieById(getFieldValue("movie"));
    const previousChoice = select.value;

    select.innerHTML = "";
    if (!movie) {
        select.add(new Option("Select a movie first", ""));
        select.disabled = true;
        return;
    }

    select.disabled = false;
    select.add(new Option("Choose a session time", ""));

    /* If the screening is today, sessions that have already started can't be booked */
    const isToday = getFieldValue("screeningDate") === getTodayString();
    const nowTime = getNowTimeString();

    movie.sessions.forEach(function (time) {
        const option = new Option(formatTime(time), time);
        if (isToday && time <= nowTime) {
            option.disabled = true;
            option.textContent += " (already started)";
        }
        select.add(option);
    });

    /* Keep the user's earlier choice if the new movie also has that session */
    const kept = Array.from(select.options).find(function (option) {
        return option.value === previousChoice && !option.disabled;
    });
    if (kept) {
        select.value = previousChoice;
    }
}


function updateBookingCost() {
    const movie = findMovieById(getFieldValue("movie"));
    const ticketType = TICKET_TYPES[getFieldValue("ticketType")] || TICKET_TYPES.adult;
    const quantity = parseInt(getFieldValue("numTickets"), 10);
    const priceField = document.getElementById("ticketPrice");
    const totalField = document.getElementById("totalCost");
    const breakdown = document.getElementById("costBreakdown");

    if (!movie) {
        priceField.value = formatPrice(0);
        totalField.value = formatPrice(0);
        breakdown.textContent = "Select a movie to see its ticket price.";
        return;
    }

    const ticketPrice = roundMoney(movie.price * ticketType.rate);
    const validQuantity = quantity > 0 ? quantity : 0;     /* NaN or negatives count as 0 */
    const total = roundMoney(ticketPrice * validQuantity);

    priceField.value = formatPrice(ticketPrice);
    totalField.value = formatPrice(total);
    breakdown.textContent = validQuantity + " × " + ticketType.label + " ticket" +
        (validQuantity === 1 ? "" : "s") + " for " + movie.title + " at " +
        formatPrice(ticketPrice) + " each";
}


function setSectionVisible(sectionId, visible) {
    const section = document.getElementById(sectionId);
    section.hidden = !visible;
    /* Disabled fields are skipped by the browser when the form is submitted */
    section.querySelectorAll("input, select").forEach(function (field) {
        field.disabled = !visible;
    });
}

function togglePaymentFields() {
    const method = getCheckedValue("paymentMethod");
    setSectionVisible("voucherFields", method === "voucher");
    setSectionVisible("cardFields", method === "online");
}


function updateCardNumberLength() {
    const card = CARD_TYPES[getFieldValue("cardType")];
    const input = document.getElementById("cardNumber");
    const hint = document.getElementById("cardNumberHint");
    if (card) {
        input.maxLength = card.digits;
        hint.textContent = card.label + " card numbers have exactly " + card.digits + " digits (digits only).";
    } else {
        input.maxLength = 16;
        hint.textContent = "Visa and Mastercard: 16 digits. American Express: 15 digits.";
    }
}


function syncBillingEmail() {
    const checkbox = document.getElementById("sameAsEmail");
    const billingEmail = document.getElementById("billingEmail");
    if (checkbox.checked) {
        billingEmail.value = getFieldValue("email");
        billingEmail.readOnly = true;
    } else {
        billingEmail.readOnly = false;
    }
}


function refreshBookingForm() {
    updateMoviePreview();
    updateSessionTimes();
    updateBookingCost();
    togglePaymentFields();
    updateCardNumberLength();
    syncBillingEmail();
}


function getBookingRules() {
    return {
        fullName: function () {
            const value = getFieldValue("fullName");
            if (value === "") {
                return "Please enter your full name.";
            }
            if (value.length < 2) {
                return "Full name must be at least 2 characters long.";
            }
            if (/\d/.test(value)) {
                return "Full name should not contain numbers.";
            }
            return "";
        },
        email: function () {
            return checkEmail(getFieldValue("email"), "email address");
        },
        phone: function () {
            const value = getFieldValue("phone");
            if (value === "") {
                return "Please enter your phone number.";
            }
            if (!DIGITS_ONLY.test(value)) {
                return "Phone number must contain digits only (no spaces, dashes or + sign).";
            }
            if (value.length < 10) {
                return "Phone number must contain at least 10 digits (you entered " + value.length + ").";
            }
            if (value.length > 15) {
                return "Phone number cannot be longer than 15 digits.";
            }
            return "";
        },
        movie: function () {
            return getFieldValue("movie") ? "" : "Please select a movie.";
        },
        screeningDate: function () {
            const date = getFieldValue("screeningDate");
            if (date === "") {
                return "Please choose a screening date.";
            }
            /* Dates in "YYYY-MM-DD" format can be compared as text */
            if (date < getTodayString()) {
                return "The screening date cannot be in the past.";
            }
            return "";
        },
        sessionTime: function () {
            const time = getFieldValue("sessionTime");
            if (!getFieldValue("movie")) {
                return "Select a movie first to see its session times.";
            }
            if (time === "") {
                return "Please choose a session time.";
            }
            const date = getFieldValue("screeningDate");
            if (date !== "" && new Date(date + "T" + time) < new Date()) {
                return "This session has already started. Please choose a later time or another date.";
            }
            return "";
        },
        numTickets: function () {
            const raw = getFieldValue("numTickets");
            if (raw === "") {
                return "Please enter the number of tickets.";
            }
            const quantity = Number(raw);
            if (!Number.isInteger(quantity)) {
                return "Number of tickets must be a whole number.";
            }
            if (quantity <= 0) {
                return "Number of tickets must be greater than 0.";
            }
            if (quantity > MAX_TICKETS) {
                return "You can book a maximum of " + MAX_TICKETS + " tickets in one booking.";
            }
            return "";
        },
        ticketType: function () {
            const type = getFieldValue("ticketType");
            const movie = findMovieById(getFieldValue("movie"));
            if (type === "") {
                return "Please choose a ticket type.";
            }
            if (type === "child" && movie && movie.rating === "MA15+") {
                return "Child tickets are not available for MA15+ movies. Please choose Adult or Student.";
            }
            return "";
        },
        paymentMethod: function () {
            return getCheckedValue("paymentMethod") ? "" : "Please choose a payment method.";
        },
        /* Voucher code - only checked when "Voucher" is the payment method */
        voucherCode: function () {
            if (getCheckedValue("paymentMethod") !== "voucher") {
                return "";
            }
            const value = getFieldValue("voucherCode");
            if (value === "") {
                return "Please enter your 12-digit voucher code.";
            }
            if (!/^\d{12}$/.test(value)) {
                return "Voucher code must be exactly 12 digits.";
            }
            return "";
        },
        /* Card fields - only checked when "Online payment" is the payment method */
        cardType: function () {
            if (getCheckedValue("paymentMethod") !== "online") {
                return "";
            }
            return getFieldValue("cardType") ? "" : "Please select your card type.";
        },
        cardName: function () {
            if (getCheckedValue("paymentMethod") !== "online") {
                return "";
            }
            const value = getFieldValue("cardName");
            if (value === "") {
                return "Please enter the name shown on the card.";
            }
            if (!/^[A-Za-z][A-Za-z '.-]*$/.test(value)) {
                return "Name on card can only contain letters, spaces, hyphens and apostrophes.";
            }
            return "";
        },
        cardNumber: function () {
            if (getCheckedValue("paymentMethod") !== "online") {
                return "";
            }
            const value = getFieldValue("cardNumber");
            const card = CARD_TYPES[getFieldValue("cardType")];
            if (value === "") {
                return "Please enter your card number.";
            }
            if (!DIGITS_ONLY.test(value)) {
                return "Card number must contain digits only (no spaces or dashes).";
            }
            if (card && value.length !== card.digits) {
                return card.label + " card numbers must be exactly " + card.digits +
                    " digits (you entered " + value.length + ").";
            }
            return "";
        },
        cardExpiry: function () {
            if (getCheckedValue("paymentMethod") !== "online") {
                return "";
            }
            const value = getFieldValue("cardExpiry");
            if (value === "") {
                return "Please enter the card expiry date.";
            }
            if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(value)) {
                return "Expiry date must be in MM/YY format, e.g. 08/28.";
            }
            const month = parseInt(value.slice(0, 2), 10);
            const year = 2000 + parseInt(value.slice(3), 10);
            /* A card is valid until the end of its expiry month */
            if (new Date(year, month, 1) <= new Date()) {
                return "This card has expired.";
            }
            return "";
        },
        billingEmail: function () {
            return checkEmail(getFieldValue("billingEmail"), "billing email address");
        }
    };
}

function initBookingForm() {
    const form = document.getElementById("bookingForm");
    if (!form) {
        return;
    }

    /* Screening dates can't be in the past - also limit the date picker */
    document.getElementById("screeningDate").min = getTodayString();

    prefillMovieFromUrl();

    /* Dynamic behaviour: each control updates the parts of the page it affects */
    document.getElementById("movie").addEventListener("change", function () {
        updateMoviePreview();
        updateSessionTimes();
        updateBookingCost();
    });
    document.getElementById("screeningDate").addEventListener("change", updateSessionTimes);
    document.getElementById("ticketType").addEventListener("change", updateBookingCost);
    document.getElementById("numTickets").addEventListener("input", updateBookingCost);
    document.getElementById("cardType").addEventListener("change", updateCardNumberLength);
    document.getElementById("sameAsEmail").addEventListener("change", syncBillingEmail);
    document.getElementById("email").addEventListener("input", syncBillingEmail);
    document.querySelectorAll('input[name="paymentMethod"]').forEach(function (radio) {
        radio.addEventListener("change", togglePaymentFields);
    });

    form.addEventListener("reset", function () {
        document.getElementById("prefillNotice").hidden = true;
        /* The reset event fires before the fields are cleared, so wait a moment */
        setTimeout(refreshBookingForm, 0);
    });

    setupFormValidation(form, getBookingRules(), "bookingErrors");

    refreshBookingForm();
}


/* ==========================================================================
   9. PAGE START-UP

   ========================================================================== */
document.addEventListener("DOMContentLoaded", function () {
    /* Tells the CSS that JavaScript is running (enables the mobile menu button) */
    document.documentElement.classList.add("js");

    initNavigation();
    updateWatchlistCount();
    initWatchlistButtons();
    initWatchlistPage();
    initRecommendForm();
    initRegisterForm();
    initBookingForm();
});
