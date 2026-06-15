import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Food Wastage Management", page_icon="🥗", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { background-color: #f0f4f8; }
    .block-container { padding-top: 1rem; }
    h1 { color: #1a5276; }
    h2 { color: #1a5276; }
    h3 { color: #2e86c1; }
    div[data-testid="metric-container"] { background-color: #1a5276; border-radius: 10px; padding: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
    div[data-testid="metric-container"] label { color: #aed6f1 !important; font-size: 14px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; font-weight: bold !important; }
    .stButton > button { background-color: #2ecc71; color: white; border-radius: 8px; border: none; padding: 8px 20px; }
    .stButton > button:hover { background-color: #27ae60; }
    .danger-box { background: #fadbd8; padding: 10px; border-radius: 8px; border-left: 4px solid #e74c3c; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

EXPIRY_CASE = "CASE WHEN DATEDIFF(Expiry_Date,'2025-03-01')<=5 THEN 'Critical' WHEN DATEDIFF(Expiry_Date,'2025-03-01')<=10 THEN 'Urgent' WHEN DATEDIFF(Expiry_Date,'2025-03-01')<=20 THEN 'Normal' ELSE 'Fresh' END"
EXPIRY_DAYS = "DATEDIFF(Expiry_Date,'2025-03-01')"

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

def run_query(sql, params=None):
    conn = get_connection()
    return pd.read_sql(sql, conn, params=params)

def run_write(sql, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    return cur.rowcount

def in_clause(lst):
    return "(" + ",".join(["%s"] * len(lst)) + ")"

ALL_FOOD_TYPES = ["Vegetarian", "Vegan", "Non-Vegetarian"]
ALL_MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snacks"]
ALL_STATUSES   = ["Pending", "Completed", "Cancelled"]

st.sidebar.image("https://img.icons8.com/color/96/salad.png", width=80)
st.sidebar.title("🥗 Food Wastage\nManagement")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["📊 Dashboard","🍱 Food Listings","🏢 Providers","🤝 Receivers","📋 Claims","📈 Analytics (15 Queries)","➕ CRUD Operations"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Filters (global)**")
food_type_filter = st.sidebar.multiselect("Food Type", ALL_FOOD_TYPES, default=ALL_FOOD_TYPES)
meal_type_filter = st.sidebar.multiselect("Meal Type", ALL_MEAL_TYPES, default=ALL_MEAL_TYPES)
status_filter    = st.sidebar.multiselect("Claim Status", ALL_STATUSES, default=ALL_STATUSES)
if not food_type_filter: food_type_filter = ALL_FOOD_TYPES
if not meal_type_filter: meal_type_filter = ALL_MEAL_TYPES
if not status_filter:    status_filter    = ALL_STATUSES

# ── DASHBOARD ────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 Food Wastage Management — Dashboard")
    st.markdown("Overview of food donations, claims, and distribution activity.")
    st.markdown("---")
    col1,col2,col3,col4,col5 = st.columns(5)
    col1.metric("🍱 Food Listings",    f"{run_query('SELECT COUNT(*) AS c FROM food_listings')['c'][0]:,}")
    col2.metric("📦 Total Quantity",   f"{run_query('SELECT SUM(Quantity) AS c FROM food_listings')['c'][0]:,} units")
    col3.metric("📋 Total Claims",     f"{run_query('SELECT COUNT(*) AS c FROM claims')['c'][0]:,}")
    col4.metric("✅ Completed Claims", f"{run_query("SELECT COUNT(*) AS c FROM claims WHERE Status='Completed'")['c'][0]:,}")
    col5.metric("⚠️ Unclaimed Food",  f"{run_query('SELECT COUNT(*) AS c FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID WHERE c.Claim_ID IS NULL')['c'][0]:,}")
    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Claim Status Distribution")
        df = run_query("SELECT Status, COUNT(*) AS count FROM claims GROUP BY Status")
        fig = px.pie(df, values='count', names='Status', color_discrete_map={'Completed':'#2ecc71','Pending':'#f39c12','Cancelled':'#e74c3c'}, hole=0.4)
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Food Quantity by Provider Type")
        df = run_query("SELECT Provider_Type, SUM(Quantity) AS total_quantity FROM food_listings GROUP BY Provider_Type ORDER BY total_quantity DESC")
        fig = px.bar(df, x='Provider_Type', y='total_quantity', color='total_quantity', color_continuous_scale='Greens', labels={'total_quantity':'Total Quantity','Provider_Type':'Provider Type'})
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Food Type Distribution")
        df = run_query("SELECT Food_Type, COUNT(*) AS count FROM food_listings GROUP BY Food_Type")
        fig = px.pie(df, values='count', names='Food_Type', color_discrete_map={'Vegetarian':'#27ae60','Vegan':'#3498db','Non-Vegetarian':'#e74c3c'}, hole=0.4)
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Claims by Day of Week")
        df = run_query("SELECT DAYNAME(Timestamp) AS Claim_Day, COUNT(*) AS claims FROM claims GROUP BY Claim_Day ORDER BY claims DESC")
        fig = px.bar(df, x='Claim_Day', y='claims', color='claims', color_continuous_scale='Blues', labels={'claims':'Total Claims','Claim_Day':'Day'})
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Expiry Status of Food Listings")
    df = run_query(f"SELECT {EXPIRY_CASE} AS Expiry_Status, COUNT(*) AS count, SUM(Quantity) AS total_qty FROM food_listings GROUP BY Expiry_Status")
    fig = px.bar(df, x='Expiry_Status', y='total_qty', color='Expiry_Status', color_discrete_map={'Critical':'#e74c3c','Urgent':'#e67e22','Normal':'#f1c40f','Fresh':'#2ecc71'}, labels={'total_qty':'Total Quantity','Expiry_Status':'Expiry Status'})
    fig.update_layout(margin=dict(t=0,b=20,l=0,r=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ── FOOD LISTINGS ────────────────────────────────────────────
elif page == "🍱 Food Listings":
    st.title("🍱 Food Listings")
    col1,col2,col3 = st.columns(3)
    with col1: search = st.text_input("Search food name","")
    with col2:
        loc_options = run_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")['Location'].tolist()
        loc = st.selectbox("Filter by Location", ["All"]+loc_options)
    with col3: exp_status = st.selectbox("Expiry Status", ["All","Fresh","Normal","Urgent","Critical"])
    sql = f"SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, f.Food_Type, f.Meal_Type, f.Location, f.Provider_Type, {EXPIRY_DAYS} AS Days_Until_Expiry, {EXPIRY_CASE} AS Expiry_Status, p.Name AS Provider_Name FROM food_listings f JOIN providers p ON f.Provider_ID=p.Provider_ID WHERE f.Food_Type IN {in_clause(food_type_filter)} AND f.Meal_Type IN {in_clause(meal_type_filter)}"
    params = food_type_filter + meal_type_filter
    if search: sql += " AND f.Food_Name LIKE %s"; params.append(f"%{search}%")
    if loc != "All": sql += " AND f.Location=%s"; params.append(loc)
    if exp_status != "All": sql += f" AND {EXPIRY_CASE}=%s"; params.append(exp_status)
    sql += " ORDER BY f.Expiry_Date ASC LIMIT 500"
    df = run_query(sql, params)
    st.markdown(f"**{len(df)} listings found**")
    st.dataframe(df, use_container_width=True, height=500)

# ── PROVIDERS ────────────────────────────────────────────────
elif page == "🏢 Providers":
    st.title("🏢 Providers")
    col1,col2 = st.columns(2)
    with col1: search = st.text_input("Search provider name","")
    with col2: ptype = st.selectbox("Provider Type", ["All","Restaurant","Supermarket","Grocery Store","Catering Service"])
    sql = "SELECT p.Provider_ID, p.Name, p.Type, p.City, p.Contact, COUNT(f.Food_ID) AS total_listings, SUM(f.Quantity) AS total_quantity FROM providers p LEFT JOIN food_listings f ON p.Provider_ID=f.Provider_ID WHERE 1=1"
    params = []
    if search: sql += " AND p.Name LIKE %s"; params.append(f"%{search}%")
    if ptype != "All": sql += " AND p.Type=%s"; params.append(ptype)
    sql += " GROUP BY p.Provider_ID, p.Name, p.Type, p.City, p.Contact ORDER BY total_quantity DESC"
    df = run_query(sql, params if params else None)
    st.markdown(f"**{len(df)} providers found**")
    st.dataframe(df, use_container_width=True, height=500)

# ── RECEIVERS ────────────────────────────────────────────────
elif page == "🤝 Receivers":
    st.title("🤝 Receivers")
    col1,col2 = st.columns(2)
    with col1: search = st.text_input("Search receiver name","")
    with col2: rtype = st.selectbox("Receiver Type", ["All","NGO","Charity","Shelter","Individual"])
    sql = "SELECT r.Receiver_ID, r.Name, r.Type, r.City, r.Contact, COUNT(c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed FROM receivers r LEFT JOIN claims c ON r.Receiver_ID=c.Receiver_ID WHERE 1=1"
    params = []
    if search: sql += " AND r.Name LIKE %s"; params.append(f"%{search}%")
    if rtype != "All": sql += " AND r.Type=%s"; params.append(rtype)
    sql += " GROUP BY r.Receiver_ID, r.Name, r.Type, r.City, r.Contact ORDER BY total_claims DESC"
    df = run_query(sql, params if params else None)
    st.markdown(f"**{len(df)} receivers found**")
    st.dataframe(df, use_container_width=True, height=500)

# ── CLAIMS ───────────────────────────────────────────────────
elif page == "📋 Claims":
    st.title("📋 Claims")
    sql = f"SELECT c.Claim_ID, c.Status, c.Timestamp, DAYNAME(c.Timestamp) AS Claim_Day, f.Food_Name, f.Food_Type, f.Meal_Type, f.Quantity, r.Name AS Receiver_Name, r.Type AS Receiver_Type, p.Name AS Provider_Name FROM claims c JOIN food_listings f ON c.Food_ID=f.Food_ID JOIN receivers r ON c.Receiver_ID=r.Receiver_ID JOIN providers p ON f.Provider_ID=p.Provider_ID WHERE c.Status IN {in_clause(status_filter)} ORDER BY c.Timestamp DESC LIMIT 500"
    df = run_query(sql, status_filter)
    st.markdown(f"**{len(df)} claims found**")
    st.dataframe(df, use_container_width=True, height=500)

# ── ANALYTICS ────────────────────────────────────────────────
elif page == "📈 Analytics (15 Queries)":
    st.title("📈 Analytics — 15 SQL Queries")
    query_choice = st.selectbox("Select Query", [
        "Q1 — Food listings by provider type",
        "Q2 — Top 10 most donated food items",
        "Q3 — Food availability by type and meal",
        "Q4 — Claim status distribution",
        "Q5 — Completion rate by receiver type",
        "Q6 — Top 10 most active providers",
        "Q7 — Top 10 most active receivers",
        "Q8 — Unclaimed food listings",
        "Q9 — Claimed vs available by food type",
        "Q10 — Daily claim activity trend",
        "Q11 — Expiry urgency vs claim status",
        "Q12 — Provider performance scorecard",
        "Q13 — Food distribution by location",
        "Q14 — Meal type demand analysis",
        "Q15 — Food waste risk report",
    ])
    queries = {
        "Q1 — Food listings by provider type": "SELECT Provider_Type, COUNT(*) AS total_listings, SUM(Quantity) AS total_quantity, ROUND(AVG(Quantity),2) AS avg_quantity, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM food_listings),2) AS pct_of_total FROM food_listings GROUP BY Provider_Type ORDER BY total_quantity DESC",
        "Q2 — Top 10 most donated food items": "SELECT Food_Name, COUNT(*) AS times_listed, SUM(Quantity) AS total_quantity, Food_Type, Meal_Type FROM food_listings GROUP BY Food_Name, Food_Type, Meal_Type ORDER BY total_quantity DESC LIMIT 10",
        "Q3 — Food availability by type and meal": "SELECT Food_Type, Meal_Type, COUNT(*) AS listings, SUM(Quantity) AS total_quantity, ROUND(AVG(Quantity),2) AS avg_quantity FROM food_listings GROUP BY Food_Type, Meal_Type ORDER BY Food_Type, Meal_Type",
        "Q4 — Claim status distribution": "SELECT Status, COUNT(*) AS total_claims, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),2) AS percentage FROM claims GROUP BY Status ORDER BY total_claims DESC",
        "Q5 — Completion rate by receiver type": "SELECT r.Type AS receiver_type, COUNT(c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed, SUM(CASE WHEN c.Status='Cancelled' THEN 1 ELSE 0 END) AS cancelled, SUM(CASE WHEN c.Status='Pending' THEN 1 ELSE 0 END) AS pending, ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)*100.0/COUNT(c.Claim_ID),2) AS completion_rate_pct FROM claims c JOIN receivers r ON c.Receiver_ID=r.Receiver_ID GROUP BY r.Type ORDER BY completion_rate_pct DESC",
        "Q6 — Top 10 most active providers": "SELECT p.Name AS provider_name, p.Type, p.City, COUNT(f.Food_ID) AS total_listings, SUM(f.Quantity) AS total_quantity_donated FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID, p.Name, p.Type, p.City ORDER BY total_quantity_donated DESC LIMIT 10",
        "Q7 — Top 10 most active receivers": "SELECT r.Name AS receiver_name, r.Type, r.City, COUNT(c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed, ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)*100.0/COUNT(c.Claim_ID),2) AS success_rate_pct FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Receiver_ID, r.Name, r.Type, r.City ORDER BY total_claims DESC LIMIT 10",
        "Q8 — Unclaimed food listings": f"SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, {EXPIRY_DAYS} AS Days_Until_Expiry, f.Food_Type, f.Meal_Type, p.Name AS provider_name, p.City FROM food_listings f JOIN providers p ON f.Provider_ID=p.Provider_ID LEFT JOIN claims c ON f.Food_ID=c.Food_ID WHERE c.Claim_ID IS NULL ORDER BY Days_Until_Expiry ASC LIMIT 20",
        "Q9 — Claimed vs available by food type": "SELECT f.Food_Type, SUM(f.Quantity) AS total_available, COUNT(DISTINCT f.Food_ID) AS total_listings, COUNT(DISTINCT c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed_claims, ROUND(COUNT(DISTINCT c.Claim_ID)*100.0/COUNT(DISTINCT f.Food_ID),2) AS claims_per_listing FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_Type ORDER BY total_available DESC",
        "Q10 — Daily claim activity trend": "SELECT DAYNAME(Timestamp) AS Claim_Day, COUNT(*) AS total_claims, SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END) AS completed, SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END) AS cancelled, SUM(CASE WHEN Status='Pending' THEN 1 ELSE 0 END) AS pending, ROUND(SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS completion_rate_pct FROM claims GROUP BY Claim_Day ORDER BY total_claims DESC",
        "Q11 — Expiry urgency vs claim status": f"SELECT {EXPIRY_CASE} AS Expiry_Status, COUNT(DISTINCT f.Food_ID) AS food_listings, COUNT(c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed, SUM(CASE WHEN c.Status='Cancelled' THEN 1 ELSE 0 END) AS cancelled, SUM(CASE WHEN c.Status='Pending' THEN 1 ELSE 0 END) AS pending, ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)*100.0/NULLIF(COUNT(c.Claim_ID),0),2) AS completion_rate_pct FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY Expiry_Status",
        "Q12 — Provider performance scorecard": "SELECT p.Name AS provider_name, p.Type, COUNT(DISTINCT f.Food_ID) AS food_listings, SUM(f.Quantity) AS total_quantity, COUNT(DISTINCT c.Claim_ID) AS claims_received, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed_claims, ROUND(COUNT(DISTINCT c.Claim_ID)*100.0/NULLIF(COUNT(DISTINCT f.Food_ID),0),2) AS claim_rate_pct FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY p.Provider_ID, p.Name, p.Type ORDER BY claim_rate_pct DESC LIMIT 15",
        "Q13 — Food distribution by location": "SELECT f.Location, COUNT(DISTINCT f.Food_ID) AS total_listings, SUM(f.Quantity) AS total_quantity, COUNT(DISTINCT c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed_claims, ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)*100.0/NULLIF(COUNT(DISTINCT c.Claim_ID),0),2) AS completion_rate_pct FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Location ORDER BY total_quantity DESC LIMIT 15",
        "Q14 — Meal type demand analysis": "SELECT f.Meal_Type, COUNT(DISTINCT f.Food_ID) AS food_listings, SUM(f.Quantity) AS total_quantity, COUNT(c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed_claims, ROUND(COUNT(c.Claim_ID)*100.0/NULLIF(COUNT(DISTINCT f.Food_ID),0),2) AS claims_per_listing, ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)*100.0/NULLIF(COUNT(c.Claim_ID),0),2) AS completion_rate_pct FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Meal_Type ORDER BY total_claims DESC",
        "Q15 — Food waste risk report": f"SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, {EXPIRY_DAYS} AS Days_Until_Expiry, {EXPIRY_CASE} AS Expiry_Status, f.Food_Type, f.Meal_Type, p.Name AS provider_name, p.Type AS provider_type, p.City, COUNT(c.Claim_ID) AS total_claims, SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS completed, SUM(CASE WHEN c.Status='Pending' THEN 1 ELSE 0 END) AS pending, CASE WHEN COUNT(c.Claim_ID)=0 THEN 'No Claims - High Risk' WHEN SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END)>0 THEN 'Claimed - Safe' WHEN SUM(CASE WHEN c.Status='Pending' THEN 1 ELSE 0 END)>0 THEN 'Pending - Monitor' ELSE 'Cancelled Only - At Risk' END AS waste_risk_label FROM food_listings f JOIN providers p ON f.Provider_ID=p.Provider_ID LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_ID,f.Food_Name,f.Quantity,f.Expiry_Date,f.Food_Type,f.Meal_Type,p.Name,p.Type,p.City ORDER BY f.Quantity DESC LIMIT 20",
    }
    df = run_query(queries[query_choice])
    st.markdown(f"**{len(df)} rows returned**")
    st.dataframe(df, use_container_width=True)
    if query_choice == "Q1 — Food listings by provider type":
        fig = px.bar(df, x='Provider_Type', y='total_quantity', color='Provider_Type', title="Total Quantity by Provider Type")
        st.plotly_chart(fig, use_container_width=True)
    elif query_choice == "Q4 — Claim status distribution":
        fig = px.pie(df, values='total_claims', names='Status', color_discrete_map={'Completed':'#2ecc71','Pending':'#f39c12','Cancelled':'#e74c3c'}, title="Claim Status Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    elif query_choice == "Q5 — Completion rate by receiver type":
        fig = px.bar(df, x='receiver_type', y='completion_rate_pct', color='receiver_type', title="Completion Rate by Receiver Type")
        st.plotly_chart(fig, use_container_width=True)
    elif query_choice == "Q10 — Daily claim activity trend":
        fig = px.bar(df, x='Claim_Day', y='total_claims', color='completion_rate_pct', color_continuous_scale='RdYlGn', title="Claims by Day of Week")
        st.plotly_chart(fig, use_container_width=True)
    elif query_choice == "Q14 — Meal type demand analysis":
        fig = px.bar(df, x='Meal_Type', y='total_claims', color='completion_rate_pct', color_continuous_scale='Greens', title="Claims by Meal Type")
        st.plotly_chart(fig, use_container_width=True)

# ── CRUD ─────────────────────────────────────────────────────
elif page == "➕ CRUD Operations":
    st.title("➕ CRUD Operations")
    crud_tab = st.selectbox("Choose operation", ["➕ Add Food Listing","✏️ Update Claim Status","🗑️ Delete Food Listing","➕ Add Provider","➕ Add Receiver","➕ Add Claim"])

    if crud_tab == "➕ Add Food Listing":
        st.subheader("Add New Food Listing")
        providers = run_query("SELECT Provider_ID, Name, Type FROM providers ORDER BY Name")
        with st.form("add_food"):
            col1,col2 = st.columns(2)
            with col1:
                food_name = st.text_input("Food Name*")
                quantity  = st.number_input("Quantity*", min_value=1, max_value=500, value=10)
                expiry    = st.date_input("Expiry Date*")
                food_type = st.selectbox("Food Type*", ALL_FOOD_TYPES)
            with col2:
                meal_type = st.selectbox("Meal Type*", ALL_MEAL_TYPES)
                location  = st.text_input("Location*")
                provider  = st.selectbox("Provider*", providers.apply(lambda r: f"{r['Provider_ID']} — {r['Name']} ({r['Type']})", axis=1).tolist())
            submitted = st.form_submit_button("Add Food Listing")
            if submitted:
                if not food_name or not location:
                    st.error("Food Name and Location are required.")
                else:
                    pid     = int(provider.split(" — ")[0])
                    ptype   = providers[providers['Provider_ID']==pid]['Type'].values[0]
                    next_id = run_query("SELECT MAX(Food_ID)+1 AS nid FROM food_listings")['nid'][0]
                    run_write("INSERT INTO food_listings (Food_ID,Food_Name,Quantity,Expiry_Date,Provider_ID,Provider_Type,Location,Food_Type,Meal_Type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                              (next_id,food_name,quantity,expiry,pid,ptype,location,food_type,meal_type))
                    st.success(f"✅ '{food_name}' added with ID {next_id}!")

    elif crud_tab == "✏️ Update Claim Status":
        st.subheader("Update Claim Status")
        with st.form("update_claim"):
            claim_id   = st.number_input("Claim ID*", min_value=1, step=1)
            new_status = st.selectbox("New Status*", ALL_STATUSES)
            submitted  = st.form_submit_button("Update Status")
            if submitted:
                existing = run_query("SELECT * FROM claims WHERE Claim_ID=%s", [claim_id])
                if existing.empty:
                    st.error(f"Claim ID {claim_id} not found.")
                else:
                    run_write("UPDATE claims SET Status=%s WHERE Claim_ID=%s", (new_status, claim_id))
                    st.success(f"✅ Claim {claim_id} updated to '{new_status}'!")
                    st.dataframe(run_query("SELECT * FROM claims WHERE Claim_ID=%s", [claim_id]))

    elif crud_tab == "🗑️ Delete Food Listing":
        st.subheader("Delete Food Listing")
        st.markdown('<div class="danger-box">⚠️ This will also delete all claims linked to this food item.</div>', unsafe_allow_html=True)
        with st.form("delete_food"):
            food_id   = st.number_input("Food ID to delete*", min_value=1, step=1)
            confirm   = st.checkbox("I confirm I want to delete this record")
            submitted = st.form_submit_button("Delete")
            if submitted:
                if not confirm:
                    st.error("Please tick the confirmation box.")
                else:
                    existing = run_query("SELECT * FROM food_listings WHERE Food_ID=%s", [food_id])
                    if existing.empty:
                        st.error(f"Food ID {food_id} not found.")
                    else:
                        run_write("DELETE FROM claims WHERE Food_ID=%s", (food_id,))
                        run_write("DELETE FROM food_listings WHERE Food_ID=%s", (food_id,))
                        st.success(f"✅ Food listing {food_id} and its claims deleted.")

    elif crud_tab == "➕ Add Provider":
        st.subheader("Add New Provider")
        with st.form("add_provider"):
            col1,col2 = st.columns(2)
            with col1:
                name  = st.text_input("Provider Name*")
                ptype = st.selectbox("Type*", ["Restaurant","Supermarket","Grocery Store","Catering Service"])
            with col2:
                city    = st.text_input("City*")
                contact = st.text_input("Contact")
                address = st.text_input("Address")
            submitted = st.form_submit_button("Add Provider")
            if submitted:
                if not name or not city:
                    st.error("Name and City are required.")
                else:
                    next_id = run_query("SELECT MAX(Provider_ID)+1 AS nid FROM providers")['nid'][0]
                    run_write("INSERT INTO providers (Provider_ID,Name,Type,Address,City,Contact) VALUES (%s,%s,%s,%s,%s,%s)", (next_id,name,ptype,address,city,contact))
                    st.success(f"✅ Provider '{name}' added with ID {next_id}!")

    elif crud_tab == "➕ Add Receiver":
        st.subheader("Add New Receiver")
        with st.form("add_receiver"):
            col1,col2 = st.columns(2)
            with col1:
                name  = st.text_input("Receiver Name*")
                rtype = st.selectbox("Type*", ["NGO","Charity","Shelter","Individual"])
            with col2:
                city    = st.text_input("City*")
                contact = st.text_input("Contact")
            submitted = st.form_submit_button("Add Receiver")
            if submitted:
                if not name or not city:
                    st.error("Name and City are required.")
                else:
                    next_id = run_query("SELECT MAX(Receiver_ID)+1 AS nid FROM receivers")['nid'][0]
                    run_write("INSERT INTO receivers (Receiver_ID,Name,Type,City,Contact) VALUES (%s,%s,%s,%s,%s)", (next_id,name,rtype,city,contact))
                    st.success(f"✅ Receiver '{name}' added with ID {next_id}!")

    elif crud_tab == "➕ Add Claim":
        st.subheader("Add New Claim")
        with st.form("add_claim"):
            col1,col2 = st.columns(2)
            with col1:
                food_id     = st.number_input("Food ID*", min_value=1, step=1)
                receiver_id = st.number_input("Receiver ID*", min_value=1, step=1)
            with col2:
                status = st.selectbox("Status*", ALL_STATUSES)
            submitted = st.form_submit_button("Add Claim")
            if submitted:
                food_ok = not run_query("SELECT Food_ID FROM food_listings WHERE Food_ID=%s", [food_id]).empty
                recv_ok = not run_query("SELECT Receiver_ID FROM receivers WHERE Receiver_ID=%s", [receiver_id]).empty
                if not food_ok:
                    st.error(f"Food ID {food_id} does not exist.")
                elif not recv_ok:
                    st.error(f"Receiver ID {receiver_id} does not exist.")
                else:
                    next_id = run_query("SELECT MAX(Claim_ID)+1 AS nid FROM claims")['nid'][0]
                    now = datetime.now()
                    run_write("INSERT INTO claims (Claim_ID,Food_ID,Receiver_ID,Status,Timestamp) VALUES (%s,%s,%s,%s,%s)",
                              (next_id,food_id,receiver_id,status,now))
                    st.success(f"✅ Claim {next_id} added successfully!")
