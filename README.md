![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)
![Railway](https://img.shields.io/badge/Database-Railway-purple)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

# Food Waste Management System

A full-stack data analytics web application that connects food providers (restaurants, supermarkets, grocery stores, catering services) with receivers (NGOs, shelters, charities, individuals) to reduce food wastage. Built with MySQL for data storage and analysis, and Streamlit for an interactive web interface with real-time CRUD operations and 15 analytical SQL queries.

---

## Live Demo

[https://food-waste-management-cv6o4yv7xdmmqbntsxxif2.streamlit.app](https://food-waste-management-cv6o4yv7xdmmqbntsxxif2.streamlit.app)

---

## Dataset

| Table | Rows | Description |
|---|---|---|
| providers_data.csv | 1,000 | Food donors - restaurants, supermarkets, grocery stores, catering services |
| receivers_data.csv | 1,000 | Food recipients - NGOs, charities, shelters, individuals |
| food_listings_data.csv | 1,000 | Available food items with quantity, expiry date, food type and meal type |
| claims_data.csv | 1,000 | Claim records linking receivers to food listings with status tracking |

> CSV files are included in the `Data/` folder for reference. The live database is hosted on Railway.

---

## Key Findings

- **25,794 total food units** available across 1,000 listings from 4 provider types
- **33.90% claim completion rate** - one in three claims is successfully fulfilled, highlighting a significant execution gap
- **33.60% cancellation rate** - nearly equal to completions, indicating receivers are claiming but not following through
- **Charity receivers** lead with the highest completion rate at **35.82%**, followed by Shelters (34.35%), NGOs (33.82%) and Individuals (31.30%)
- **Restaurants** contribute the highest total food quantity (6,923 units) despite Supermarkets having the most listings (267)
- **Monday** is the busiest and most successful claim day - 160 claims with a 39.38% completion rate
- **Friday** is the weakest day - only 123 claims and the lowest completion rate at 29.27%
- **~171 food listings have zero claims**, representing the highest food waste risk in the dataset
- **Vegetarian food** receives the most claims (350 total), ahead of Non-Vegetarian (331) and Vegan (319)
- **Breakfast** is the most claimed meal type (278 claims) while Dinner achieves the best completion rate (37.07%)
- **Rice and Bread** are the most frequently listed food items, each appearing 12-15 times across different types and meal categories
- Providers with only 1 listing tend to attract 3-4 claims each, suggesting smaller donors attract disproportionate interest

---

## Tech Stack

- **Database** - MySQL 8.0 (hosted on Railway)
- **Backend / Analysis** - Python, pandas, SQLAlchemy
- **Frontend** - Streamlit, Plotly
- **Version Control** - Git, GitHub

---

## Project Structure

```
food-waste-management/
├── app.py                          - Streamlit web application (7 pages, 15 queries, CRUD)
├── requirements.txt                - Python dependencies for Streamlit Cloud
├── .gitignore                      - Excludes secrets and sensitive files
├── Data/
│   ├── providers_data.csv          - Provider dataset (1,000 rows)
│   ├── receivers_data.csv          - Receiver dataset (1,000 rows)
│   ├── food_listings_data.csv      - Food listings dataset (1,000 rows)
│   └── claims_data.csv             - Claims dataset (1,000 rows)
├── SQL/
│   ├── phase1_workbench.sql        - Database schema creation and data loading
│   ├── phase2_cleaning.sql         - Data cleaning and computed column setup
│   └── phase3_queries.sql          - 15 SQL analysis queries
└── .streamlit/
    └── secrets.toml                - NOT committed (local and Streamlit Cloud only)
```

---

## Run Locally

**1 - Clone the repository:**
```bash
git clone https://github.com/Atharva270803/Food-Waste-Management.git
cd Food-Waste-Management
```

**2 - Install dependencies:**
```bash
pip install -r requirements.txt
```

**3 - Add database credentials:**

Create a file at `.streamlit/secrets.toml`:
```toml
[mysql]
host     = "thomas.proxy.rlwy.net"
port     = 21342
user     = "root"
password = "your_password_here"
database = "railway"
```

**4 - Run the app:**
```bash
streamlit run app.py
```

App opens at `http://localhost:8501`
