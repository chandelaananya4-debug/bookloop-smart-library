
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
st.markdown("""
<style>
.stApp {
    background: linear-gradient(130deg,#f4f7ff,#f0faf7);
}
[data-testid="stSidebar"] {
    background: #101c35;
}
[data-testid="stSidebar"] * {
    color: #f4f7ff;
}
.hero {
    padding: 26px;
    border-radius: 22px;
    background: linear-gradient(115deg,#14264b,#24677a);
    color: white;
    margin-bottom: 20px;
}
.hero h1 {font-size: 38px;margin:0;}
.hero p {color:#dbeafe;margin-top:8px;}
div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e4eaf3;
    box-shadow: 0 5px 15px #13294b0a;
}
.stButton button[kind="primary"] {
    background: #176b73;
}

# ---------- DESIGN ----------
st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #f4f7ff 0%, #edf7f5 100%);
    color: #17233e;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #101c35;
}
[data-testid="stSidebar"] * {
    color: #f4f7ff;
}

/* Main content text */
[data-testid="stMain"] {
    color: #17233e;
}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {
    color: #14264b !important;
}
[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] .stMarkdown {
    color: #334155;
}

/* Hero banner */
.hero {
    padding: 30px;
    border-radius: 22px;
    background: linear-gradient(115deg, #14264b, #24677a);
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px #14264b16;
}
.hero h1 {
    color: #ffffff !important;
    font-size: 38px;
    font-weight: 750;
    margin: 0;
}
.hero p {
    color: #dceaf3 !important;
    margin-top: 8px;
    font-size: 17px;
}

/* KPI metric cards */
[data-testid="stMetric"] {
    background: #ffffff !important;
    padding: 20px !important;
    border-radius: 18px !important;
    border: 1px solid #dce5f1 !important;
    box-shadow: 0 8px 25px #14264b0b;
}
[data-testid="stMetric"] label,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #64748b !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #14264b !important;
    font-weight: 750 !important;
}

/* Containers and tables */
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #dce5f1;
    border-radius: 16px;
}
[data-testid="stDataFrame"] {
    border: 1px solid #dce5f1;
    border-radius: 12px;
    overflow: hidden;
}

/* Buttons */
.stButton button[kind="primary"],
.stFormSubmitButton button[kind="primary"] {
    background: #176b73;
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 650;
}
.stButton button[kind="primary"]:hover,
.stFormSubmitButton button[kind="primary"]:hover {
    background: #12545b;
    color: white;
}

/* Inputs */
[data-testid="stMain"] input,
[data-testid="stMain"] textarea {
    color: #17233e !important;
}

/* Chart and general spacing */
[data-testid="stMain"] h2 {
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

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

    term = st.text_input(
        "🔎 Search",
        placeholder="Search title, author, ISBN..."
    )

    categories = ["All"] + (
        sorted(books["category"].dropna().unique().tolist())
        if not books.empty else []
    )
    category = st.selectbox("Filter Category", categories)

    result = books.copy()

    if term:
        mask = result[
            ["title", "author", "category", "isbn"]
        ].fillna("").astype(str).apply(
            lambda col: col.str.contains(
                term, case=False, regex=False
            )
        ).any(axis=1)
        result = result[mask]

    if category != "All":
        result = result[result["category"] == category]

    st.caption(f"{len(result)} matching book(s)")

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
