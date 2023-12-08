# login_script.py

import streamlit as st
import mysql.connector
import subprocess

def verify_login(username, password):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password312',
        database='crime_data'
        )

        # Create a cursor to execute SQL queries
        cursor = conn.cursor()

        # Query to check if the username and password match
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(query, (username, password))

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Return True if a matching record is found, otherwise False
        return result is not None

    except Exception as e:
        st.error(f"Error: {e}")
        return False

def login():
    st.markdown(
        """
        <style>
            body {
                background-color: #f0f0f0;
            }
            .main {
                max-width: 600px;
                padding: 20px;
                background-color: white;
                margin: auto;
                margin-top: 100px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
            }
            .title {
                color: #333333;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("User Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_login(username, password):
            st.success("Logged in successfully! Opening your app...")

            # Launch your main app in a new Streamlit process
            subprocess.Popen(["streamlit", "run", "trial4_user.py"])

        else:
            st.error("Invalid username or password")

if __name__ == "__main__":
    login()
