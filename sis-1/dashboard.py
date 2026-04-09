import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. Database Setup & Mock Data Injection
# ==========================================
DB_FILE = "agency_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Table for listings
    c.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            status TEXT,
            features_extracted TEXT,
            cost REAL,
            english_variant TEXT,
            russian_variant TEXT,
            kazakh_variant TEXT,
            manager_comment TEXT,
            best_variant_vote TEXT
        )
    ''')
    
    # Inject Mock Data if empty
    c.execute("SELECT COUNT(*) FROM listings")
    if c.fetchone()[0] == 0:
        for i in range(20): # Generate 20 random past logs
            status = random.choice(["Approved", "Approved", "Approved", "Rejected", "Pending"])
            features = random.choice(["2BR, Balkony", "City Center, 120sqm", "Luxury, Furnished", "Mountain View, Studio"])
            cost = round(random.uniform(0.01, 0.05), 4)
            date_str = (datetime.now() - timedelta(hours=random.randint(0, 48))).strftime("%Y-%m-%d %H:%M:%S")
            vote = random.choice(["Professional", "Practical", "Emotional"]) if status == "Approved" else "None"
            
            c.execute('''
                INSERT INTO listings (date, status, features_extracted, cost, english_variant, russian_variant, kazakh_variant, manager_comment, best_variant_vote)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date_str, status, features, cost, "English variant base text...", "Russian text...", "Kazakh text...", "", vote))
        conn.commit()
    conn.close()

def execute_query(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def update_status(listing_id, status, comment, best_variant):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE listings SET status=?, manager_comment=?, best_variant_vote=? WHERE id=?", 
              (status, comment, best_variant, listing_id))
    conn.commit()
    conn.close()

# ==========================================
# 2. Main Application Flow
# ==========================================
st.set_page_config(page_title="KazRE Manager Dashboard", layout="wide")

# Mobile Friendly - Auto Refresh every 30 seconds
count = st_autorefresh(interval=30000, limit=None, key="dashboard_autorefresh")

# Initialize DB on first run
init_db()

# --- Authentication ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("## 🔐 Manager Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username == "admin" and password == "kazre2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials. (Hint: admin/kazre2026)")
    st.stop()

# --- Logout ---
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

# --- Dashboard Layout ---
st.title("📈 KazRE Manager Dashboard")
if st.button("🔄 Manual Refresh"):
    st.rerun()

tab1, tab2, tab3 = st.tabs(["📊 Analytics Overview", "✅ Review Queue", "📤 Export"])

# ================ TAB 1: ANALYTICS ================
with tab1:
    df = execute_query("SELECT * FROM listings")
    
    st.header("Today's Activity Overview")
    
    # KPIs
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df['date'].str.startswith(today_str)]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Listings Generated (Today)", len(today_df))
    col2.metric("Total Pending", len(df[df['status'] == 'Pending']))
    
    approval_rate = (len(df[df['status'] == 'Approved']) / len(df[df['status'] != 'Pending'])) * 100 if len(df[df['status'] != 'Pending']) > 0 else 0
    col3.metric("Overall Approval Rate", f"{approval_rate:.1f}%")
    
    avg_cost = df['cost'].mean() if not df.empty else 0
    col4.metric("Avg Cost / Listing", f"${avg_cost:.4f}")

    # Charts Layout
    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Approval Rate Chart
        st.subheader("Approval Rate")
        status_counts = df[df['status'] != 'Pending']['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        if not status_counts.empty:
            fig1 = px.pie(status_counts, names='Status', values='Count', hole=0.4, color='Status', 
                          color_discrete_map={'Approved':'green', 'Rejected':'red'})
            st.plotly_chart(fig1, use_container_width=True)
            
    with col_chart2:
        # Cost Trend
        st.subheader("Cost per Listing Trend")
        df['date_day'] = df['date'].str[:10]
        cost_trend = df.groupby('date_day')['cost'].mean().reset_index()
        if not cost_trend.empty:
            fig2 = px.line(cost_trend, x='date_day', y='cost', markers=True)
            st.plotly_chart(fig2, use_container_width=True)
            
    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        # Most Common Features
        st.subheader("Extracted Features Distribution")
        feature_counts = df['features_extracted'].value_counts().reset_index().head(5)
        feature_counts.columns = ['Feature', 'Count']
        if not feature_counts.empty:
            fig3 = px.bar(feature_counts, x='Feature', y='Count')
            st.plotly_chart(fig3, use_container_width=True)
            
    with col_chart4:
        # Feedback Analytics (Highest Rating)
        st.subheader("Winning Tones (Feedback)")
        votes = df[df['best_variant_vote'] != 'None']['best_variant_vote'].value_counts().reset_index()
        votes.columns = ['Tone Variant', 'Votes']
        if not votes.empty:
            fig4 = px.bar(votes, x='Tone Variant', y='Votes', color='Tone Variant')
            st.plotly_chart(fig4, use_container_width=True)


# ================ TAB 2: REVIEW QUEUE ================
with tab2:
    st.header("Pending Approvals")
    pending_df = execute_query("SELECT * FROM listings WHERE status='Pending'")
    
    if pending_df.empty:
        st.success("🎉 Inbox Zero! No listings pending review.")
    else:
        for index, row in pending_df.iterrows():
            with st.expander(f"📝 Listing #{row['id']} - Extracted: {row['features_extracted']}", expanded=True):
                # Placeholder for Original Photo thumbnail
                st.image("https://via.placeholder.com/150", caption="Original Extracted Floorplan/Photo")
                
                # Variants display
                v_col1, v_col2, v_col3 = st.columns(3)
                with v_col1:
                    st.markdown("**English Variant**")
                    st.text_area("English text", row['english_variant'], height=150, key=f"en_{row['id']}", disabled=True)
                with v_col2:
                    st.markdown("**Russian Variant**")
                    st.text_area("Russian text", row['russian_variant'], height=150, key=f"ru_{row['id']}", disabled=True)
                with v_col3:
                    st.markdown("**Kazakh Variant**")
                    st.text_area("Kazakh text", row['kazakh_variant'], height=150, key=f"kz_{row['id']}", disabled=True)
                    
                # Action Form
                with st.form(key=f"review_form_{row['id']}"):
                    st.markdown("### Manager Decision")
                    decision = st.radio("Action", ["Approve", "Reject"], horizontal=True)
                    manager_comment = st.text_input("Manager Comments (required on rejection)")
                    best_vote = st.selectbox("Which tone variant worked best?", ["Professional", "Practical", "Emotional", "None"])
                    
                    submit_action = st.form_submit_button("Submit Review")
                    if submit_action:
                        if decision == "Reject" and not manager_comment:
                            st.error("Please provide a reason for rejection.")
                        else:
                            update_status(row['id'], f"{decision}d", manager_comment, best_vote)
                            st.success(f"Listing #{row['id']} {decision}d!")
                            st.rerun()

# ================ TAB 3: EXPORT ================
with tab3:
    st.header("Export for Krisha.kz")
    approved_df = execute_query("SELECT id, date, features_extracted, russian_variant, kazakh_variant FROM listings WHERE status='Approved'")
    
    st.dataframe(approved_df, use_container_width=True)
    
    if not approved_df.empty:
        csv = approved_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Approved Listings as CSV",
            data=csv,
            file_name=f'krisha_kz_export_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
    else:
        st.info("No approved listings available to export.")
