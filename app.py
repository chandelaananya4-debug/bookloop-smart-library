import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path
from datetime import date, timedelta

st.set_page_config(
    page_title="BookLoop | Smart Library",
    page_icon="📚",
    layout="wide"
)

DB = Path(__file__).parent / "bookloop.db"

# ---------------- CUSTOM UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f3f6ff,#edf9f5);
    color:#111827;
}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {
    color:#111827 !important;
    font-weight:800 !important;
}
[data-testid="stMain"] p,
[data-testid="stMain"] label {
    color:#263449;
}
[data-testid="stSidebar"] {
    background:#101a32;
}
[data-testid="stSidebar"] * {
    color:white;
}
.hero {
    padding:36px;
    border-radius:25px;
    background:linear-gradient(120deg,#14264b,#176b73);
    margin-bottom:25px;
    box-shadow:0 12px 30px #14264b18;
}
.hero h1 {
    color:white !important;
    font-size:42px;
    margin:0;
}
.hero p {
    color:#e1edf7 !important;
    font-size:18px;
}
[data-testid="stMetric"] {
    background:white;
    padding:20px;
    border:1px solid #dce5ef;
    border-bottom:4px solid #167c80;
    border-radius:17px;
    box-shadow:0 8px 22px #172b4d0a;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] * {
    color:#111827 !important;
}
.stButton button {
    border-radius:12px;
    font-weight:650;
}
[data-testid="stMain"] input {
    color:#111827 !important;
    background:white !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DATABASE ----------------
def connect():
    return sqlite3.connect(DB, check_same_thread=False)


def initialize():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            isbn TEXT DEFAULT '',
            total INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS loans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            borrower TEXT,
            borrowed_on TEXT,
            due_date TEXT,
            returned_on TEXT DEFAULT '',
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
        """)

        count = con.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        if count == 0:
            sample_books = [
                ("Atomic Habits","James Clear","Self-help","9780735211292",3),
                ("The Alchemist","Paulo Coelho","Fiction","9780062315007",2),
                ("Clean Code","Robert C. Martin","Technology","9780132350884",2),
                ("Deep Work","Cal Newport","Productivity","9781455586691",2),
                ("The Psychology of Money","Morgan Housel","Finance","9780857197689",2),
                ("The Hobbit","J. R. R. Tolkien","Fantasy","9780547928227",2),
                ("Pride and Prejudice","Jane Austen","Classic","9780141439518",2),
                ("1984","George Orwell","Dystopian","9780451524935",2),
                ("Cosmos","Carl Sagan","Science","9780345539434",2),
                ("Python Crash Course","Eric Matthes","Technology","9781718502703",3),
                ("The Midnight Library","Matt Haig","Fiction","9780525559474",2),
                ("The Hunger Games","Suzanne Collins","Young Adult","9780439023481",2),
                ("The Martian","Andy Weir","Science Fiction","9780553418026",2),
                ("Wings of Fire","A. P. J. Abdul Kalam","Biography","9788173711466",2),
                ("The Lean Startup","Eric Ries","Business","9780307887894",2),
                ("The Design of Everyday Things","Don Norman","Design","9780465050659",1),
                ("And Then There Were None","Agatha Christie","Mystery","9780062073488",2),
                ("Thinking, Fast and Slow","Daniel Kahneman","Psychology","9780374533557",2),
                ("Sapiens","Yuval Noah Harari","History","9780062316097",2),
                ("Dune","Frank Herbert","Science Fiction","9780441172719",2),
                ("Rich Dad Poor Dad","Robert Kiyosaki","Finance","9781612680194",2),
                ("The Great Gatsby","F. Scott Fitzgerald","Classic","9780743273565",2),
            ]

            con.executemany("""
                INSERT INTO books
                (title,author,category,isbn,total,available)
                VALUES(?,?,?,?,?,?)
            """, [
                (t,a,c,i,n,n) for t,a,c,i,n in sample_books
            ])


def get_books():
    with connect() as con:
        return pd.read_sql_query(
            "SELECT * FROM books ORDER BY title", con
        )


def get_loans(active=False):
    query = """
        SELECT loans.id, loans.book_id, books.title,
        loans.borrower, loans.borrowed_on,
        loans.due_date, loans.returned_on
        FROM loans JOIN books ON books.id=loans.book_id
    """
    if active:
        query += " WHERE COALESCE(loans.returned_on,'')=''"
    query += " ORDER BY loans.id DESC"

    with connect() as con:
        return pd.read_sql_query(query, con)


def hero(title, subtitle, label="BOOKLOOP / SMART LIBRARY"):
    st.markdown(f"""
    <div class="hero">
        <div style="color:#91e2d2;font-size:12px;
        letter-spacing:2px;font-weight:bold">{label}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


initialize()
books = get_books()
loans = get_loans()
active_loans = get_loans(active=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("# 📚 BookLoop")
    st.caption("SMART LIBRARY COMPANION")
    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Book Discovery",
            "Borrow / Return",
            "Library Management",
            "Reading Activity"
        ]
    )
    st.divider()
    st.caption("DISCOVER • BORROW • READ")


# ---------------- CATEGORY SUGGESTIONS ----------------
suggestions = {
    "Fiction": [
        "The Alchemist", "The Midnight Library",
        "The Kite Runner"
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
        "The Psychology of Money", "Rich Dad Poor Dad",
        "The Intelligent Investor"
    ],
    "Self-help": [
        "Atomic Habits", "Mindset", "The Power of Habit"
    ],
    "Productivity": [
        "Deep Work", "Essentialism", "Atomic Habits"
    ],
    "Classic": [
        "Pride and Prejudice", "1984", "The Great Gatsby"
    ],
    "Biography": [
        "Wings of Fire", "Steve Jobs", "Elon Musk"
    ],
    "Design": [
        "The Design of Everyday Things",
        "Don't Make Me Think", "Sprint"
    ],
    "Mystery": [
        "And Then There Were None",
        "The Hound of the Baskervilles",
        "Murder on the Orient Express"
    ],
    "Science Fiction": [
        "The Martian", "Dune", "Project Hail Mary"
    ],
    "Psychology": [
        "Thinking, Fast and Slow", "Mindset", "Quiet"
    ],
    "Business": [
        "The Lean Startup", "Zero to One", "Start with Why"
    ],
    "History": [
        "Sapiens", "India After Gandhi",
        "The Discovery of India"
    ],
    "Dystopian": [
        "1984", "The Hunger Games", "Fahrenheit 451"
    ],
    "Young Adult": [
        "The Hunger Games", "Harry Potter",
        "The Fault in Our Stars"
    ]
}


# ---------------- OVERVIEW ----------------
if page == "Overview":
    hero(
        "Your library, in one loop.",
        "Discover books. Track circulation. Keep reading."
    )

    a, b, c, d = st.columns(4)
    a.metric("Book Titles", len(books))
    b.metric("Total Copies", int(books["total"].sum()))
    c.metric("Available Copies", int(books["available"].sum()))
    d.metric("Active Loans", len(active_loans))

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("📊 Collection Analytics")

        if not books.empty:
            grouped = books.groupby(
                "category", as_index=False
            )["total"].sum()

            fig = px.bar(
                grouped,
                x="category",
                y="total",
                color="category",
                template="plotly_white",
                labels={"total": "Copies", "category": "Category"}
            )
            fig.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#263449"
            )
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("📖 Recent Loans")

        if active_loans.empty:
            st.success("No active loans right now.")
        else:
            for _, loan in active_loans.head(5).iterrows():
                with st.container(border=True):
                    st.markdown(f"**{loan['title']}**")
                    st.caption(
                        f"{loan['borrower']} • Due {loan['due_date']}"
                    )

    st.info("Use the sidebar to explore BookLoop features.")


# ---------------- BOOK DISCOVERY ----------------
elif page == "Book Discovery":
    hero(
        "Find your next read.",
        "Explore the collection with smart search.",
        "BOOKLOOP / DISCOVERY"
    )

    search = st.text_input(
        "🔎 Search books",
        placeholder="Search title, author, category or ISBN..."
    )

    catalog_categories = sorted(
        books["category"].fillna("Other").astype(str).unique()
    )

    categories = ["All"] + catalog_categories

    st.markdown("### ✦ Explore by category")
    st.caption("Choose a category to see relevant book suggestions.")

    # Keep the selected category across reruns
    if "selected_book_category" not in st.session_state:
        st.session_state.selected_book_category = "All"

    if st.session_state.selected_book_category not in categories:
        st.session_state.selected_book_category = "All"

    # Category buttons
    for start in range(0, len(categories), 4):
        group = categories[start:start+4]
        cols = st.columns(4)

        for i, category in enumerate(group):
            with cols[i]:
                is_selected = (
                    st.session_state.selected_book_category == category
                )
                if st.button(
                    ("✦ " if is_selected else "○ ") + category,
                    key=f"cat_{start}_{i}_{category}",
                    type="primary" if is_selected else "secondary",
                    use_container_width=True
                ):
                    st.session_state.selected_book_category = category
                    st.rerun()

    selected_category = st.session_state.selected_book_category

    filtered = books.copy()

    if selected_category != "All":
        filtered = filtered[
            filtered["category"].fillna("").astype(str) == selected_category
        ]

    if search.strip():
        mask = filtered[
            ["title", "author", "category", "isbn"]
        ].fillna("").astype(str).apply(
            lambda col: col.str.contains(
                search.strip(), case=False, regex=False
            )
        ).any(axis=1)

        filtered = filtered[mask]

    # Suggestions
    if selected_category != "All":
        st.markdown(f"### ✨ Recommended reads · {selected_category}")

        suggested_titles = suggestions.get(selected_category, [])
        matched = []

        for title in suggested_titles:
            match = books[
                books["title"].fillna("").str.contains(
                    title, case=False, regex=False
                )
            ]
            if not match.empty:
                matched.append(match.iloc[0])

        if matched:
            cols = st.columns(min(3, len(matched)))

            for i, book in enumerate(matched[:3]):
                with cols[i]:
                    with st.container(border=True):
                        st.markdown("📘")
                        st.markdown(f"**{book['title']}**")
                        st.caption(f"by {book['author']}")

                        if book["available"] > 0:
                            st.success("Available")
                        else:
                            st.warning("Currently borrowed")
        else:
            st.info(
                "No matching suggestion is currently in your catalog. "
                "Add more books to expand your recommendations."
            )

    else:
        st.markdown("### 🌟 Popular reading lanes")
        lane_cols = st.columns(3)
        featured = [
            ("💻", "Technology", "Coding and innovation"),
            ("🚀", "Science Fiction", "Explore future worlds"),
            ("🌱", "Self-help", "Habits and personal growth"),
            ("🔍", "Mystery", "Solve the unexpected"),
            ("📖", "Classic", "Timeless stories"),
            ("💰", "Finance", "Money and smart decisions")
        ]

        for i, (emoji, cat, desc) in enumerate(featured):
            with lane_cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### {emoji} {cat}")
                    st.caption(desc)
                    if st.button(
                        f"Explore {cat}",
                        key=f"feature_{cat}",
                        use_container_width=True
                    ):
                        if cat in categories:
                            st.session_state.selected_book_category = cat
                        else:
                            st.session_state.selected_book_category = "All"
                        st.rerun()

    st.divider()
    st.subheader("📚 Discover books")
    st.caption(f"{len(filtered)} matching title(s)")

    if filtered.empty:
        st.info("No books found. Try another search or category.")
    else:
        for _, book in filtered.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.markdown(f"**📕 {book['title']}**")
                c1.caption(f"by {book['author']}")
                c2.markdown(f"**{book['category']}**")
                c2.caption(f"ISBN: {book['isbn'] or '—'}")
                c3.metric(
                    "Available",
                    f"{int(book['available'])}/{int(book['total'])}"
                )


# ---------------- BORROW / RETURN ----------------
elif page == "Borrow / Return":
    hero(
        "Keep books moving.",
        "Borrow with care. Return on time.",
        "BOOKLOOP / CIRCULATION"
    )

    borrow_tab, return_tab = st.tabs(
        ["📥 Borrow a book", "📤 Return a book"]
    )

    with borrow_tab:
        available = books[books["available"] > 0]

        if available.empty:
            st.info("No copies are currently available.")
        else:
            with st.form("borrow_form", clear_on_submit=True):
                borrower = st.text_input("Borrower name")
                book_id = st.selectbox(
                    "Choose a book",
                    available["id"].tolist(),
                    format_func=lambda x: available.loc[
                        available["id"] == x, "title"
                    ].iloc[0]
                )
                duration = st.selectbox("Loan duration", [7, 14, 21], index=1)
                submit = st.form_submit_button(
                    "Confirm borrow", type="primary"
                )

            if submit:
                if not borrower.strip():
                    st.error("Please enter borrower name.")
                else:
                    today = date.today()
                    due = today + timedelta(days=duration)

                    with connect() as con:
                        current = con.execute(
                            "SELECT available FROM books WHERE id=?",
                            (book_id,)
                        ).fetchone()

                        if current and current[0] > 0:
                            con.execute("""
                                INSERT INTO loans
                                (book_id,borrower,borrowed_on,due_date,returned_on)
                                VALUES(?,?,?,?, '')
                            """, (
                                book_id, borrower.strip(),
                                today.isoformat(), due.isoformat()
                            ))
                            con.execute("""
                                UPDATE books
                                SET available=available-1 WHERE id=?
                            """, (book_id,))

                            st.success(f"Borrow successful! Return by {due}.")
                            st.rerun()
                        else:
                            st.error("Book unavailable. Please refresh.")

    with return_tab:
        current = get_loans(active=True)

        if current.empty:
            st.info("No active loans.")
        else:
            def loan_label(loan_id):
                row = current[current["id"] == loan_id].iloc[0]
                return f"{row['title']} — {row['borrower']} (due {row['due_date']})"

            with st.form("return_form"):
                selected_loan = st.selectbox(
                    "Select loan",
                    current["id"].tolist(),
                    format_func=loan_label
                )
                return_btn = st.form_submit_button(
                    "Mark as returned", type="primary"
                )

            if return_btn:
                chosen = current[
                    current["id"] == selected_loan
                ].iloc[0]

                with connect() as con:
                    con.execute("""
                        UPDATE loans SET returned_on=?
                        WHERE id=? AND COALESCE(returned_on,'')=''
                    """, (date.today().isoformat(), selected_loan))

                    con.execute("""
                        UPDATE books
                        SET available=MIN(available+1,total)
                        WHERE id=?
                    """, (int(chosen["book_id"]),))

                st.success("Book return recorded.")
                st.rerun()


# ---------------- LIBRARY MANAGEMENT ----------------
elif page == "Library Management":
    hero(
        "Manage your collection.",
        "Keep the catalog accurate and ready to explore.",
        "BOOKLOOP / CATALOG"
    )

    st.subheader("➕ Add a book")

    # Use a dropdown for categories, with an option for custom category.
    standard_categories = [
        "Fiction", "Technology", "Science", "Fantasy", "Finance",
        "Self-help", "Productivity", "Classic", "Biography", "Design",
        "Mystery", "Science Fiction", "Psychology", "Business",
        "History", "Dystopian", "Young Adult", "Other", "Custom"
    ]

    with st.form("add_book_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        title = c1.text_input("Book title")
        author = c2.text_input("Author")

        c3, c4, c5 = st.columns([2, 2, 1])
        category_choice = c3.selectbox(
            "Category", standard_categories
        )
        custom_category = ""
        if category_choice == "Custom":
            custom_category = st.text_input("Enter custom category")

        isbn = c4.text_input("ISBN (optional)")
        copies = c5.number_input(
            "Copies", min_value=1, max_value=500, value=1
        )

        add = st.form_submit_button(
            "Add to catalog", type="primary"
        )

    if add:
        final_category = (
            custom_category.strip()
            if category_choice == "Custom"
            else category_choice
        )

        if not title.strip() or not author.strip():
            st.error("Title and author are required.")
        elif not final_category:
            st.error("Please enter a category.")
        else:
            with connect() as con:
                con.execute("""
                    INSERT INTO books
                    (title,author,category,isbn,total,available)
                    VALUES(?,?,?,?,?,?)
                """, (
                    title.strip(), author.strip(),
                    final_category, isbn.strip(),
                    int(copies), int(copies)
                ))

            st.success("Book added successfully.")
            st.rerun()

    st.divider()
    st.subheader("📚 Current catalog")

    current_books = get_books()

    if current_books.empty:
        st.info("No books yet.")
    else:
        st.dataframe(
            current_books[
                ["title","author","category","isbn","total","available"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Export catalog CSV",
            current_books.to_csv(index=False).encode("utf-8"),
            file_name="bookloop_catalog.csv",
            mime="text/csv"
        )


# ---------------- READING ACTIVITY ----------------
elif page == "Reading Activity":
    hero(
        "Your reading activity.",
        "A clear view of circulation history.",
        "BOOKLOOP / ACTIVITY"
    )

    history = get_loans()

    if history.empty:
        st.info("No borrowing activity yet.")
    else:
        history["Status"] = history["returned_on"].fillna("").apply(
            lambda x: "Returned" if str(x).strip() else "Active"
        )

        today = date.today().isoformat()

        history["Due status"] = history.apply(
            lambda row: (
                "Returned" if row["Status"] == "Returned"
                else (
                    "Overdue"
                    if str(row["due_date"]) and row["due_date"] < today
                    else "On time"
                )
            ),
            axis=1
        )

        st.dataframe(
            history[
                ["title","borrower","borrowed_on","due_date",
                 "returned_on","Status","Due status"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Export reading activity",
            history.to_csv(index=False).encode("utf-8"),
            file_name="bookloop_reading_activity.csv",
            mime="text/csv"
        )

st.caption(
    "BookLoop • College project prototype. "
    "Use demo borrower information. Authentication and persistent "
    "storage are recommended before real multi-user deployment."
)
