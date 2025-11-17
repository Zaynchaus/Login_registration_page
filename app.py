import streamlit as st
import re
import sqlite3

# ---------- DATABASE SETUP ----------
def connect_db():
    return sqlite3.connect("users.db")

def create_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    db.commit()
    db.close()

# ---------- VALIDATION ----------
def validate_email(email):
    pattern = r'^[A-Za-z][A-Za-z0-9._]*@[A-Za-z]+\.[A-Za-z.]+$'
    if re.match(pattern, email) and not re.search(r'@\.', email):
        return True
    return False

def validate_password(password):
    if len(password) < 6 or len(password) > 16:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[@#$%^&*!]', password):
        return False
    return True

# ---------- USER FUNCTIONS ----------
def register_user(email, password):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        db.close()
        return "Email already registered! Please login."

    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    db.commit()
    db.close()
    return "Registration Successful!"

def login_user(email, password):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    result = cursor.fetchone()
    db.close()
    return result is not None

def reset_password(email, new_password):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
    db.commit()
    db.close()

# ---------- STREAMLIT UI ----------
def main():
    st.set_page_config(page_title="Login & Signup System", page_icon="🔐", layout="centered")
    st.title("🔐 User Login & Signup System")

    create_table()

    menu = ["Login", "Sign Up", "Forgot Password"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Sign Up":
        st.subheader("Create a New Account")

        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not validate_email(email):
                st.error("❌ Invalid email format.")
            elif not validate_password(password):
                st.warning("⚠️ Password must be 6–16 chars, include upper, lower, number & special char.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                msg = register_user(email, password)
                if "Successful" in msg:
                    st.success("✅ " + msg)
                else:
                    st.error("⚠️ " + msg)

    elif choice == "Login":
        st.subheader("Login to Your Account")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            if login_user(email, password):
                st.success(f"✅ Login Successful! Welcome, {email}")
                st.balloons()
            else:
                st.error("❌ Incorrect email or password.")

    elif choice == "Forgot Password":
        st.subheader("Reset Your Password")

        with st.form("forgot_form"):
            email = st.text_input("Registered Email")
            new_password = st.text_input("New Password", type="password")
            submitted = st.form_submit_button("Reset Password")

        if submitted:
            if not validate_email(email):
                st.error("❌ Invalid email format.")
            elif not validate_password(new_password):
                st.warning("⚠️ Password must be 6–16 chars, include upper, lower, number & special char.")
            else:
                reset_password(email, new_password)
                st.success("✅ Password updated successfully!")

if __name__ == "__main__":
    main()
