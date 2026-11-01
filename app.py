
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import date, timedelta
import plotly.express as px

BASE = Path(__file__).parent
DB = BASE / "bookloop.db"
CSV = BASE / "data" / "sample_books.csv"

st.set_page_config(
    page_title="BookLoop | Smart Library",
    page_icon="📚",
    layout="wide"
)


 
# ---------- DESIGN ----------

# ---------- DESIGN ----------
st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #dcecff 0%, transparent 40%),
        radial-gradient(ellipse at 90% 15%, #d9f5ed 0%, transparent 35%),
        #f5f7fb;
    color: #111827 !important;
}

/* ===== GLOBAL TEXT ===== */
[data-testid="stMain"] {
    color: #111827 !important;
}

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] h5 {
    color: #111827 !important;
    font-weight: 750 !important;
}

[data-testid="stMain"] .stMarkdown,
[data-testid="stMain"] .stMarkdown p,
[data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {
    color: #374151 !important;
}

/* ===== HERO BANNER ===== */
.hero {
    position: relative;
    overflow: hidden;
    padding: 38px 34px;
    border-radius: 24px;
    background: linear-gradient(120deg, #101a32, #183e52 65%, #176b73);
    border: 1px solid #34576b;
    box-shadow: 0 15px 40px rgba(15, 35, 60, 0.15);
    margin-bottom: 24px;
}

.hero h1 {
    color: #ffffff !important;
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -1.2px;
    margin: 0;
}

.hero p {
    color: #d9e8f2 !important;
    font-size: 17px;
    margin-top: 12px;
}

/* ===== KPI CARDS ===== */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.96) !important;
    border: 1px solid #dce4ef !important;
    border-bottom: 4px solid #177e89 !important;
    border-radius: 18px !important;
    padding: 22px 20px !important;
    box-shadow: 0 8px 26px rgba(20, 40, 75, 0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* Metric labels */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetric"] label {
    color: #4b5563 !important;
    font-size: 14px !important;
    font-weight: 650 !important;
}

/* Metric numbers */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"] {
    color: #111827 !important;
    font-weight: 800 !important;
}

/* ===== SECTION HEADINGS ===== */
[data-testid="stMain"] h2 {
    color: #111827 !important;
    font-size: 25px !important;
    letter-spacing: -0.5px;
}

[data-testid="stMain"] h3 {
    color: #17233e !important;
}

/* ===== TABLES ===== */
[data-testid="stDataFrame"] {
    border: 1px solid #dce4ef;
    border-radius: 14px;
    overflow: hidden;
}

/* ===== BUTTONS ===== */
.stButton button,
.stFormSubmitButton button {
    border-radius: 11px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease;
}

.stButton button[kind="primary"],
.stFormSubmitButton button[kind="primary"] {
    background: #176b73 !important;
    color: #ffffff !important;
    border: 1px solid #176b73 !important;
}

.stButton button[kind="primary"]:hover,
.stFormSubmitButton button[kind="primary"]:hover {
    background: #10535b !important;
    border-color: #10535b !important;
}

/* ===== INPUTS ===== */
[data-testid="stMain"] input,
[data-testid="stMain"] textarea {
    color: #111827 !important;
    background-color: #ffffff !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: #101a32 !important;
}

[data-testid="stSidebar"] * {
    color: #f3f6fc !important;
}

[data-testid="stSidebar"] [aria-current="page"] {
    background-color: #1d4052 !important;
    border-radius: 10px;
}

/* ===== ALERTS ===== */
[data-testid="stAlert"] p {
    font-weight: 500;
}

/* ===== RESPONSIVE SPACING ===== */
@media (max-width: 768px) {
    .hero {
        padding: 24px 20px;
        border-radius: 18px;
    }

    .hero h1 {
        font-size: 29px;
    }
}

</style>
""", unsafe_allow_html=True)


# ---------- DATABASE ----------
def db():
    return sqlite3.connect(DB)

def setup():
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT UNIQUE,
            total INTEGER NOT NULL,
            available INTEGER NOT NULL
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS loans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            borrower TEXT NOT NULL,
            borrowed TEXT NOT NULL,
            due TEXT NOT NULL,
            returned TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
        """)
        count = con.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        if count == 0 and CSV.exists():
            df = pd.read_csv(CSV).fillna("")
            for _, r in df.iterrows():
                n = max(1, int(r["copies"]))
                con.execute("""
                INSERT OR IGNORE INTO books
                (title,author,category,isbn,total,available)
                VALUES(?,?,?,?,?,?)
                """, (
                    r["title"], r["author"], r["category"],
                    str(r["isbn"]) or None, n, n
                ))

setup()

def read_books():
    with db() as con:
        return pd.read_sql_query("SELECT * FROM books", con)

def read_loans():
    with db() as con:
        return pd.read_sql_query("""
        SELECT loans.*, books.title, books.author
        FROM loans JOIN books ON books.id=loans.book_id
        ORDER BY loans.id DESC
        """, con)

def header(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1>'
        f'<p>{subtitle}</p></div>',
        unsafe_allow_html=True
    )

# ---------- NAVIGATION ----------
st.sidebar.title("📚 BookLoop")
st.sidebar.caption("SMART LIBRARY COMPANION")
page = st.sidebar.radio(
    "NAVIGATION",
    ["Overview", "Book Discovery", "Borrow / Return",
     "Library Management", "Reading Activity"]
)
st.sidebar.divider()
st.sidebar.caption("College project prototype")

books = read_books()
loans = read_loans()

active = loans[loans["returned"].isna()] if not loans.empty else loans

# ---------- OVERVIEW ----------
if page == "Overview":
    header(
        "Your library, in one loop.",
        "Discover books. Track circulation. Keep reading."
    )

    total_titles = len(books)
    total_copies = int(books["total"].sum()) if not books.empty else 0
    available = int(books["available"].sum()) if not books.empty else 0
    borrowed = len(active)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Book Titles", total_titles)
    c2.metric("Total Copies", total_copies)
    c3.metric("Available Copies", available)
    c4.metric("Active Loans", borrowed)

    st.write("")
    left, right = st.columns([1.1, 0.9])

    with left:
        st.subheader("📊 Collection Analytics")
        if not books.empty:
            chart = books.groupby(
                "category", as_index=False
            )["total"].sum()
            fig = px.bar(
                chart, x="category", y="total",
                color="category",
                template="plotly_white",
                title="Copies by Category"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("📖 Recent Loans")
        if active.empty:
            st.success("No active loans right now.")
        else:
            st.dataframe(
                active[["borrower", "title", "borrowed", "due"]],
                use_container_width=True,
                hide_index=True
            )

    st.info("Use the sidebar to explore BookLoop features.")

# ---------- BOOK DISCOVERY ----------
elif page == "Book Discovery":
    header(
        "Find your next read.",
        "Explore the collection with smart search."
    )

    term =
    # ---------- SMART DISCOVERY ----------
    # Search input
    term = st.text_input(
        "🔎 Search your next read",
        placeholder="Search title, author, ISBN...",
        key="book_search"
    )

    # Curated category suggestions
    category_suggestions = {
        "Fiction": [
            "The Alchemist", "The Kite Runner",
            "The Midnight Library"
        ],
        "Technology": [
            "Clean Code", "Python Crash Course",
            "The Pragmatic Programmer"
        ],
        "Science": [
            "Cosmos", "A Brief History of Time", "Sapiens"
        ],
        "Fantasy": [
            "The Hobbit", "The Lord of the Rings",
            "Harry Potter"
        ],
        "Finance": [
            "The Psychology of Money",
            "Rich Dad Poor Dad", "The Intelligent Investor"
        ],
        "Self-help": [
            "Atomic Habits", "The Power of Habit", "Deep Work"
        ],
    }

    # Categories to display
    preferred_categories = [
        "All", "Fiction", "Technology", "Science",
        "Fantasy", "Finance", "Self-help"
    ]

    # Keep categories that exist in the current dataset
    existing_categories = (
        books["category"].dropna().unique().tolist()
        if not books.empty else []
    )

    category_options = ["All"] + [
        c for c in preferred_categories[1:]
        if c in existing_categories
    ]

    # Also allow other dataset categories
    category_options += [
        c for c in sorted(existing_categories)
        if c not in category_options
    ]

    # Selected category
    if "selected_book_category" not in st.session_state:
        st.session_state.selected_book_category = "All"

    st.markdown("### ✦ Explore by category")
    st.caption("Choose your reading mood to discover something new.")

    # Category chips
    chip_cols = st.columns(min(len(category_options), 4))

    for i, cat in enumerate(category_options):
        with chip_cols[i % len(chip_cols)]:
            if st.button(
                ("✦ " if cat == st.session_state.selected_book_category
                 else "○ ") + cat,
                key=f"category_chip_{i}",
                use_container_width=True,
                type=(
                    "primary"
                    if cat == st.session_state.selected_book_category
                    else "secondary"
                )
            ):
                st.session_state.selected_book_category = cat
                st.rerun()

    category = st.session_state.selected_book_category

    # Suggestions based on selected category
    if category != "All":
        st.markdown("### ✨ Suggested for you")
        st.caption(f"Popular picks in {category}")

        suggestions = category_suggestions.get(category, [])

        # Only suggest titles that actually exist in the catalog
        available_titles = (
            books["title"].fillna("").astype(str).tolist()
            if not books.empty else []
        )

        matched_suggestions = [
            title for title in suggestions
            if any(title.lower() in t.lower() for t in available_titles)
        ]

        if matched_suggestions:
            suggestion_cols = st.columns(
                min(3, len(matched_suggestions))
            )

            for i, title in enumerate(matched_suggestions[:3]):
                with suggestion_cols[i]:
                    with st.container(border=True):
                        st.markdown("📘")
                        st.markdown(f"**{title}**")
                        if st.button(
                            "Search this book",
                            key=f"suggest_{category}_{i}",
                            use_container_width=True
                        ):
                            st.session_state.book_search = title
                            st.rerun()
        else:
            st.info(
                "No curated suggestions yet for this category. "
                "Try browsing the books below."
            )

    # Filter catalog
    result = books.copy()

    if category != "All":
        result = result[result["category"] == category]

    if term:
        mask = result[
            ["title", "author", "category", "isbn"]
        ].fillna("").astype(str).apply(
            lambda col: col.str.contains(
                term, case=False, regex=False
            )
        ).any(axis=1)

        result = result[mask]

    st.markdown("---")
    st.markdown("### 📚 Discover books")
    st.caption(f"{len(result)} matching book(s)")

    if result.empty:
        st.info("No books found. Try another category or search.")
    else:
        for _, b in result.iterrows():
            with st.container(border=True):
                a, m, c = st.columns([3, 2, 1])

                a.subheader("📕 " + b["title"])
                a.caption("by " + b["author"])

                m.write("**" + b["category"] + "**")
                m.caption("ISBN: " + str(b["isbn"] or "N/A"))

                c.metric(
                    "Available",
                    f"{b['available']}/{b['total']}"
                )

       
            

# ---------- BORROW / RETURN ----------
elif page == "Borrow / Return":
    header(
        "Circulation Desk.",
        "Borrow a title or record a return."
    )

    tab1, tab2 = st.tabs(["📥 Borrow", "📤 Return"])

    with tab1:
        available_books = books[books["available"] > 0]

        if available_books.empty:
            st.info("No books currently available.")
        else:
            with st.form("borrow_form"):
                choices = {
                    f"{r.title} — {r.author} (ID {r.id})": int(r.id)
                    for r in available_books.itertuples()
                }
                selected = st.selectbox("Select Book", list(choices))
                borrower = st.text_input("Borrower demo name / ID")
                days = st.selectbox("Loan Duration", [7, 14, 21], index=1)
                submit = st.form_submit_button(
                    "Confirm Borrow", type="primary"
                )

            if submit:
                if not borrower.strip():
                    st.error("Please enter a borrower name or demo ID.")
                else:
                    book_id = choices[selected]
                    today = date.today()
                    with db() as con:
                        current = con.execute(
                            "SELECT available FROM books WHERE id=?",
                            (book_id,)
                        ).fetchone()

                        if current and current[0] > 0:
                            con.execute("""
                            INSERT INTO loans
                            (book_id,borrower,borrowed,due)
                            VALUES(?,?,?,?)
                            """, (
                                book_id, borrower.strip(),
                                today.isoformat(),
                                (today + timedelta(days=days)).isoformat()
                            ))
                            con.execute("""
                            UPDATE books
                            SET available=available-1 WHERE id=?
                            """, (book_id,))
                            st.success("Book borrowed successfully!")
                            st.rerun()
                        else:
                            st.error("Copy unavailable. Refresh and retry.")

    with tab2:
        open_loans = active.copy()

        if open_loans.empty:
            st.info("No active loans.")
        else:
            with st.form("return_form"):
                choices = {
                    f"Loan #{r.id} | {r.title} | {r.borrower} | Due {r.due}":
                    int(r.id)
                    for r in open_loans.itertuples()
                }
                selected = st.selectbox("Select Loan", list(choices))
                submit_return = st.form_submit_button(
                    "Record Return", type="primary"
                )

            if submit_return:
                loan_id = choices[selected]
                with db() as con:
                    book_id = con.execute(
                        "SELECT book_id FROM loans WHERE id=? AND returned IS NULL",
                        (loan_id,)
                    ).fetchone()

                    if book_id:
                        con.execute(
                            "UPDATE loans SET returned=? WHERE id=?",
                            (date.today().isoformat(), loan_id)
                        )
                        con.execute("""
                        UPDATE books
                        SET available=MIN(total,available+1)
                        WHERE id=?
                        """, (book_id[0],))
                        st.success("Return recorded.")
                        st.rerun()
                    else:
                        st.warning("This loan was already returned.")

# ---------- LIBRARY MANAGEMENT ----------
elif page == "Library Management":
    header(
        "Manage the collection.",
        "Add titles and maintain your catalog."
    )

    with st.expander("➕ Add New Book", expanded=True):
        with st.form("add_book"):
            col1, col2 = st.columns(2)
            title = col1.text_input("Book Title *")
            author = col2.text_input("Author *")
            category = col1.text_input("Category *", value="General")
            isbn = col2.text_input("ISBN (optional)")
            copies = st.number_input(
                "Number of Copies", min_value=1, max_value=500, value=1
            )
            submit = st.form_submit_button("Add Book", type="primary")

        if submit:
            if not title.strip() or not author.strip() or not category.strip():
                st.error("Fill in all required fields.")
            else:
                try:
                    with db() as con:
                        con.execute("""
                        INSERT INTO books
                        (title,author,category,isbn,total,available)
                        VALUES(?,?,?,?,?,?)
                        """, (
                            title.strip(), author.strip(), category.strip(),
                            isbn.strip() or None, int(copies), int(copies)
                        ))
                    st.success("Book added!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("ISBN already exists. Check or leave it blank.")

    st.subheader("📚 Current Catalog")
    if books.empty:
        st.info("Catalog is empty.")
    else:
        st.dataframe(
            books[["id", "title", "author", "category",
                   "isbn", "total", "available"]],
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "⬇️ Export Catalog CSV",
            books.to_csv(index=False).encode("utf-8"),
            "bookloop_catalog.csv",
            "text/csv"
        )

# ---------- READING ACTIVITY ----------
else:
    header(
        "Your reading trail.",
        "Review loan activity and export reports."
    )

    if loans.empty:
        st.info("No reading activity yet. Borrow a book to begin.")
    else:
        history = loans.copy()
        history["status"] = history["returned"].fillna("Active")
        history["overdue"] = (
            history["returned"].isna()
            & (pd.to_datetime(history["due"]).dt.date < date.today())
        )
        st.metric("Total Loan Records", len(history))
        st.dataframe(
            history[[
                "borrower", "title", "author", "borrowed",
                "due", "returned", "status", "overdue"
            ]],
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "⬇️ Export Reading Activity",
            history.to_csv(index=False).encode("utf-8"),
            "bookloop_activity.csv",
            "text/csv"
        )

st.sidebar.divider()
st.sidebar.caption("BookLoop • Student project")
