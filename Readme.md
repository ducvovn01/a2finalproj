# COS10005 Web Development - Assignment 2 (Semester 2, 2026)

## CineSpark - Movie Discovery and Ticket Booking Platform

**Student name:** Quang Phu Duc Vo
**Student ID:** 105739480

**Mercury link:** http://mercury.swin.edu.au/cos10005/s105739480/assignment2/index.html
**GitHub repo: [github.com/ducvovn01/a2finalproj.git](https://github.com/ducvovn01/a2finalproj.git)**

---

## 1. Website Structure

```
assignment2/
|-- index.html        Home page: purpose and values, target users, services,
|                     how it works, "now showing" preview, call to action.
|-- movies.html       Movie listing: 9 movies, each with title, genre, age
|                     rating, running time, 50-100 word description, poster,
|                     ticket price, daily sessions, "Book Now" and
|                     "Add to Watchlist" buttons.
|-- recommend.html    Recommendation form (genre, age group, viewing
|                     preference) and JavaScript-generated results.
|-- register.html     Registration form with JavaScript validation.
|-- booking.html      Booking form with movie pre-fill, live booking cost,
|                     conditional payment fields and JavaScript validation.
|-- watchlist.html    BONUS: watchlist / favourites page.
|-- css/style.css     The only stylesheet (linked to every page).
|-- js/script.js      All JavaScript (linked to every page).
|-- images/           logo.png, favicon.png, hero.jpg, movie1.jpg - movie9.jpg
`-- Readme.md         This file.
```

Every page shares the same `<header>` with the logo and the main `<nav>`, uses `<main>`, `<section>`, `<article>`, `<aside>` and `<footer>` elements, and highlights the current page in the navigation (`class="active"`). On phones the navigation collapses behind a "Menu" button.

### Responsive design (mobile-first CSS)

- **Mobile** (<= 767px): single column, collapsible menu
- **Tablet** (768-1023px): two-column card grids, menu in one row
- **Desktop** (>= 1024px): full multi-column layouts, side panels

Both forms use `method="post"` and send their data to `http://mercury.swin.edu.au/it000000/cos10005/regtest.php` once they are valid.

---

## 2. How the Selected Movie Is Carried Over to the Booking Page

**Approach:** URL query string (read with `URLSearchParams`).

Every "Book" link includes the movie's id and the page it came from, e.g.:

```
booking.html?movie=neon-orbit&from=movies       (Movies page)
booking.html?movie=neon-orbit&from=recommend    (Recommendations page)
booking.html?movie=neon-orbit&from=watchlist    (Watchlist page)
```

When `booking.html` loads, `prefillMovieFromUrl()` in `script.js`:

1. reads the `movie` and `from` values with `URLSearchParams`,
2. checks that the id belongs to a real movie in the `MOVIES` array (unknown ids are ignored),
3. selects that movie in the Movie dropdown and shows a short message saying which page it came from.

The user can still change the movie at any time. Visiting `booking.html` directly simply leaves the dropdown on "-- Select a movie --".

**Why this approach:** it needs no storage, works the same from every page, the choice is visible in the address bar (easy to test, bookmark or share), and the pre-fill only happens when the user actually clicks a Book link.

---

## 3. JavaScript Validation Logic (Plain English)

### General approach (`script.js`, section 6)

- Each form has a "rules" object: one small function per field that returns an error message, or an empty string when the field is fine.
- On submit, every rule is run. Each error is shown in red directly under its field, the field gets a red border, a summary box at the top says how many errors there are, and keyboard focus moves to the first problem.
- If there is at least one error, `event.preventDefault()` stops the form from being submitted.
- After the first attempt, the form is re-checked every time the user types or changes something, so each message disappears as soon as the problem is fixed.
- The forms use the `novalidate` attribute so the browser's own pop-up messages do not replace these clearer JavaScript messages.

### Registration form (`register.html`)

- Every field must be completed.
- **Username:** at least 5 characters; only letters, numbers and underscores.
- **Email:** must look like `name@domain.ext`.
- **Phone:** digits only, 8 to 15 digits.
- **Password:** at least 10 characters with an uppercase letter, a lowercase letter, a number and a special character. The message lists exactly which requirements are still missing, and a checklist under the password box ticks each requirement live while typing.
- **Confirm password:** must match the password exactly.
- **Gender** must be selected, at least one preferred genre must be ticked and a country/region must be chosen.

### Booking form (`booking.html`)

- Full name, email, phone, movie, screening date, session time, number of tickets, payment method and billing email are required.
- Full name must not contain numbers. Email and billing email must be valid.
- **Phone:** digits only, at least 10 digits (maximum 15).
- **Screening date** cannot be before today (the date picker's minimum is also set to today). If the date is today, sessions that have already started are disabled, and a session in the past is rejected.
- **Number of tickets** must be a whole number greater than 0 (maximum 10).
- Child tickets cannot be booked for MA15+ movies.
- **Voucher payment:** only the voucher code box is shown, and it must be 12 digits. No card fields are shown or checked.
- **Online payment:** card fields are shown. Card type, name on card, card number and expiry (MM/YY, not expired) are required. The card number must contain digits only: 16 digits for Visa/Mastercard, 15 for Amex. This is a format check only - no real payment is processed.

### Dynamic booking behaviour

- Choosing a movie shows its poster and details, loads its session times and updates the price.
- Ticket price = movie's adult price x ticket type rate (Adult 100%, Student 80%, Child 60%); Total = ticket price x tickets. Both values update instantly and are sent with the form.
- Payment fields appear/disappear with the chosen payment method. Hidden fields are also disabled so they are not submitted.
- Ticking "Same as email address" copies the email into the billing email (and keeps it in sync); unticking makes the field editable again.

### Recommendation logic (`recommend.html`, `script.js` section 5)

1. **Age filter:** Child -> G/PG only; Teen -> G/PG/M; Adult -> all ratings.
2. **Family filter:** "Family" viewing allows only G and PG movies.
3. **Scoring:** main genre match +5, secondary genre match +3, suits the viewing occasion +3, made for the age group +2 (maximum 10).
4. The top 3 movies are shown with a match percentage and the reasons they were chosen. If no movie of the chosen genre is suitable, a message explains why (e.g. the only Horror movie is MA15+, so it is not shown to teens) and the closest matches are shown instead.

Each result has a "Book this movie" link that pre-fills the booking page.

### Bonus - Watchlist (`watchlist.html`, `script.js` section 4)

- The watchlist is an array of movie ids saved in `sessionStorage` as JSON.
- "Add to Watchlist" on the Movies page adds/removes a movie; the number badge in the navigation updates on every page.
- `watchlist.html` reads the array, shows each saved movie with "Book Now" and "Remove" buttons, and has a "Clear watchlist" button.
- `sessionStorage` was chosen because the list must last while the user moves between pages during the browsing session, and is cleared automatically when the tab is closed.

---

## 4. Test Data (Fake - No Real Payment Is Processed)

| Payment method | Value                            |
| -------------- | -------------------------------- |
| Voucher code   | `123456789012`                 |
| Visa           | `4111111111111111`             |
| Mastercard     | `5555555555554444`             |
| Amex           | `378282246310005`              |
| Expiry         | Any future month, e.g. `12/29` |

---

## 5. Known Issues and Limitations

- **Front-end only:** no database. Registrations and bookings are only sent to the `regtest.php` test page; no account or booking is actually stored.
- **Card checks** are format checks only (digits and length); vouchers are not checked against real codes.
- **Watchlist** uses `sessionStorage`, so it belongs to one browser tab and is emptied when that tab/browser is closed (as the bonus task describes).
- **Duplicated movie data:** details are written in `movies.html` and also stored in the `MOVIES` array in `script.js` (used for prices, sessions and recommendations), so a change to a movie must be made in both places.
- **JavaScript required:** recommendations, prices, session times and the watchlist need JavaScript; a message is displayed if JavaScript is disabled.
- The "date must not be in the past" check uses the clock of the user's device.

---

## 6. References

- CineSpark and all nine movies (titles, stories, characters) are fictional and were written for this assignment.
- All images (logo, favicon, home page illustration and posters) are original artwork, drawn with a Python (Pillow) script made for this project. No third-party images are used.
- Icons on the home and registration pages are standard Unicode emoji characters displayed by the visitor's own system font.
- **Age ratings** follow the Australian classification categories:
  Australian Classification Board, "What do the ratings mean?",
  https://www.classification.gov.au/classification-ratings/what-do-ratings-mean
- **URLSearchParams** (reading the query string):
  MDN Web Docs, https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams
- **sessionStorage** (watchlist):
  MDN Web Docs, https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage
- **Fake test card numbers** are the publicly documented test numbers from Stripe, "Testing", https://docs.stripe.com/testing
