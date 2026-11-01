
# 📚 BookLoop — Smart Library Companion

BookLoop is a college project that makes library management easier through a clean, interactive web application.

## Features

- Book search by title, author, category, and ISBN
- Category filters
- Book availability tracking
- Borrow and return workflow
- Due-date tracking
- Library catalog management
- Dashboard analytics
- Reading activity history
- CSV report exports

## Tech Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

## Installation

1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Create a virtual environment (recommended).

### Windows

    py -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py

## Project Structure

    bookloop-smart-library/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    └── data/
        └── sample_books.csv

## Sample Data

The initial collection is imported from data/sample_books.csv when the database is first created.

## Team Responsibilities

Member 1: Book discovery, catalog, and sample dataset.

Member 2: Database, borrowing, returns, and loan validation.

Member 3: UI, dashboard analytics, integration, and testing.

All members should review and test the integrated project.

## Deployment

You can deploy using Streamlit Community Cloud:

https://share.streamlit.io/

Select your GitHub repository, branch main, and main file app.py.

## Limitations

This is a classroom prototype.

- No authentication or role-based access.
- Borrower activity is visible to visitors.
- Use fictional borrower data for demos.
- SQLite data on hosted filesystems may not persist reliably.
- The project needs a persistent database, access controls,
  and backups before real-world multi-user use.
