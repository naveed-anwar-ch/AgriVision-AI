import streamlit as st
import sqlite3
import pandas as pd

# ==============================
# DATABASE CONNECTION
# ==============================
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Admin Panel", layout="wide")

st.title("🛠 Admin Dashboard - AgriBot System")

# ==============================
# SIDEBAR MENU
# ==============================
menu = st.sidebar.selectbox(
    "Select Option",
    ["View Users", "Prediction Logs", "Analytics"]
)

# ==============================
# VIEW USERS
# ==============================
if menu == "View Users":
    st.subheader("👤 Registered Users")

    users = c.execute("SELECT * FROM users").fetchall()
    df = pd.DataFrame(users, columns=["ID", "Username", "Password", "Status"])

    st.dataframe(df, use_container_width=True)

    st.subheader("⚙ Manage Users")

    user_id = st.number_input("Enter User ID to Delete/Block", min_value=1, step=1)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Delete User"):
            c.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
            st.success("User Deleted Successfully")

    with col2:
        if st.button("🚫 Block User"):
            c.execute("UPDATE users SET status='blocked' WHERE id=?", (user_id,))
            conn.commit()
            st.success("User Blocked Successfully")

# ==============================
# PREDICTION LOGS
# ==============================
elif menu == "Prediction Logs":
    st.subheader("📊 Prediction History")

    logs = c.execute("SELECT * FROM predictions").fetchall()

    df = pd.DataFrame(
        logs,
        columns=["ID", "Username", "Disease", "Confidence", "Date"]
    )

    st.dataframe(df, use_container_width=True)

    st.success(f"Total Predictions: {len(df)}")

# ==============================
# ANALYTICS
# ==============================
elif menu == "Analytics":
    st.subheader("📈 System Analytics")

    logs = c.execute("SELECT disease FROM predictions").fetchall()

    if len(logs) > 0:
        df = pd.DataFrame(logs, columns=["Disease"])

        st.write("### Most Common Diseases")
        st.bar_chart(df["Disease"].value_counts())

        st.write("### Summary")
        st.info(f"Total Records: {len(df)}")

    else:
        st.warning("No prediction data available yet")