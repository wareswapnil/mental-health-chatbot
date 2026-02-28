import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import matplotlib.pyplot as plt
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Health Companion",
    page_icon="💪",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
.header-box {
    background: linear-gradient(90deg, #4CAF50, #1B5E20);
    padding: 25px;
    border-radius: 15px;
    color: white;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
.stButton>button {
    background-color: #1B5E20;
    color: white;
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #2E7D32;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD API KEY (Cloud + Local) ----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]  # Streamlit Cloud
except:
    load_dotenv()  # Local
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found. Set it in Streamlit Secrets or .env file.")
    st.stop()

genai.configure(api_key=api_key)

# IMPORTANT: Correct model path for Cloud
model = genai.GenerativeModel("gemini-1.0-pro")

# ---------------- USER STORAGE ----------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "last_request" not in st.session_state:
    st.session_state.last_request = 0

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="header-box">🤖 AI Health Companion</div>', unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        option = st.radio("Select Option", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if option == "Register":
                if username in users:
                    st.warning("Username already exists.")
                else:
                    users[username] = {"password": password, "history": []}
                    save_users(users)
                    st.success("Registered successfully. Please login.")
            else:
                if username in users and users[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ---------------- MAIN HEADER ----------------
st.markdown('<div class="header-box">💪 Your Personal AI Diet Planner</div>', unsafe_allow_html=True)
st.write("")

# ---------------- SIDEBAR ----------------
st.sidebar.header("👤 User Details")

weight = st.sidebar.number_input("Weight (kg)", 30, 150, 60)
height = st.sidebar.number_input("Height (cm)", 120, 210, 165)
age = st.sidebar.number_input("Age", 10, 80, 22)

medical = st.sidebar.text_input("Medical Conditions", "None")
food_pref = st.sidebar.selectbox("Food Preference", ["Veg", "Non-Veg", "Vegan"])
diet_restrict = st.sidebar.text_input("Dietary Restrictions", "None")

bmi = weight / ((height/100)**2)
calories = int(22 * weight)

st.sidebar.success(f"📊 BMI: {round(bmi,2)}")
st.sidebar.info(f"🔥 Target Calories: {calories} kcal")

tabs = st.tabs(["🍽 Daily Plan", "📅 Weekly Plan", "📊 Calorie Chart", "📜 History"])

# ---------------- COOLDOWN ----------------
def check_cooldown():
    if time.time() - st.session_state.last_request < 15:
        st.warning("Please wait 15 seconds before next request.")
        st.stop()
    st.session_state.last_request = time.time()

# ---------------- DAILY PLAN ----------------
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.button("Generate Daily Plan"):
        check_cooldown()

        prompt = f"""
        Create simple Indian diet plan.
        Age:{age}, Weight:{weight}, BMI:{round(bmi,2)}, Calories:{calories}
        Medical:{medical}
        Food:{food_pref}
        Restriction:{diet_restrict}
        """

        try:
            response = model.generate_content(prompt)
            result = response.text

            st.success("✅ Daily Plan Generated")
            st.write(result)

            users[st.session_state.username]["history"].append(result)
            save_users(users)

        except Exception as e:
            st.error("AI Error")
            st.write(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- WEEKLY PLAN ----------------
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.button("Generate Weekly Plan"):
        check_cooldown()

        prompt = f"""
        Create 7-day Indian diet plan.
        Age:{age}, Weight:{weight}, BMI:{round(bmi,2)}, Calories:{calories}
        Medical:{medical}
        Food:{food_pref}
        Restriction:{diet_restrict}
        """

        try:
            response = model.generate_content(prompt)
            result = response.text

            st.success("✅ Weekly Plan Generated")
            st.write(result)

            users[st.session_state.username]["history"].append(result)
            save_users(users)

        except Exception as e:
            st.error("AI Error")
            st.write(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALORIE CHART ----------------
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    labels = ["Breakfast", "Lunch", "Snacks", "Dinner"]
    values = [calories*0.25, calories*0.35, calories*0.15, calories*0.25]

    fig = plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("Calorie Distribution")
    st.pyplot(fig)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HISTORY ----------------
with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    history = users[st.session_state.username]["history"]

    if history:
        for i, plan in enumerate(history):
            st.markdown(f"### Plan {i+1}")
            st.write(plan)
    else:
        st.info("No plans generated yet.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
