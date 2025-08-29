import streamlit as st
import pandas as pd
import hashlib
from pathlib import Path
from streamlit_option_menu import option_menu

st.set_page_config(page_title="QHT Dashboard", layout="wide", page_icon="🎯")

# ---------- DARK THEME ----------
st.markdown(
    """
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stButton>button { background-color: #1F2937; color: #FFFFFF; }
    .stTextInput>div>div>input { background-color: #1F2937; color: #FFFFFF; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- USER AUTH ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    return pd.read_csv("users.csv")  # columns: username,password_hash,role,department

def login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        users = load_users()
        hashed_pw = hash_password(password)
        user = users[(users['username']==username) & (users['password_hash']==hashed_pw)]
        if not user.empty:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = user.iloc[0]['role']
            st.session_state['department'] = user.iloc[0]['department']
        else:
            st.sidebar.error("Invalid credentials")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    st.sidebar.success(f"Logged in as {st.session_state['username']} ({st.session_state['role']})")

    # ---------- DEPARTMENT MENU ----------
    departments = ["Doctors", "Welcome Team", "Sales Team", "DA Team", "HT Team"]
    selected_tab = option_menu("Departments", departments, orientation="horizontal", menu_icon="grid")

    st.title(f"{selected_tab} Dashboard")

    # ---------- MODULES ----------
    modules = ["SOP", "KPI & KRA", "Training Modules", "Assessments"]
    selected_module = st.sidebar.selectbox("Select Module", modules)

    dept_path = Path("data") / selected_tab.lower().replace(" ","_")

    if selected_module == "SOP":
        file_path = dept_path / "sop.csv"
    elif selected_module == "KPI & KRA":
        file_path = dept_path / "kpi_kra.csv"
    elif selected_module == "Training Modules":
        file_path = dept_path / "training.csv"
    elif selected_module == "Assessments":
        file_path = dept_path / "assessments.csv"

    if file_path.exists():
        df = pd.read_csv(file_path)
        st.dataframe(df)
    else:
        st.info(f"No data available for {selected_module} in {selected_tab}")
