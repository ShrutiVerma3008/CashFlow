import streamlit as st
import pandas as pd
import time
import os
import json

# File storage setup
USER_FILE = "users.json"
FRIENDS_FILE = "friends.json"
TRANSACTIONS_FILE = "transactions.json"

# Load Data Functions
def load_data(filename, default_data):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return default_data

def save_data(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# Initialize Data
users = load_data(USER_FILE, {})
friends = load_data(FRIENDS_FILE, {})
transactions = load_data(TRANSACTIONS_FILE, [])

# Streamlit UI
st.title("💰 Splitwise-like Expense Manager")

# User Authentication
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if st.session_state.logged_in_user is None:
    st.sidebar.header("User Authentication")
    auth_option = st.sidebar.radio("Choose an option", ["Login", "Register"])
    
    if auth_option == "Register":
        new_username = st.sidebar.text_input("Enter a username")
        new_password = st.sidebar.text_input("Set a password", type="password")
        if st.sidebar.button("Register"):
            if new_username in users:
                st.sidebar.error("Username already exists. Please log in.")
            else:
                users[new_username] = {"password": new_password, "net_balance": 0}
                save_data(USER_FILE, users)
                st.sidebar.success("Registration successful! Please log in.")
    
    elif auth_option == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in_user = username
                st.sidebar.success(f"Welcome, {username}!")
            else:
                st.sidebar.error("Invalid username or password.")

else:
    username = st.session_state.logged_in_user
    st.sidebar.write(f"Logged in as: {username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
        st.experimental_rerun()
    
    # Add Transactions
    st.header("💸 Add Transaction")
    payer = st.text_input("Payer")
    payee = st.text_input("Payee")
    amount = st.number_input("Amount (Rs)", min_value=1)
    category = st.selectbox("Category", ["Food", "Motor", "Rent", "Miscellaneous", "Custom"])
    if category == "Custom":
        category = st.text_input("Enter Custom Category")
    
    if st.button("Record Transaction"):
        if payer and payee and amount > 0:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            transactions.append({"payer": payer, "payee": payee, "amount": amount, "category": category, "timestamp": timestamp})
            save_data(TRANSACTIONS_FILE, transactions)
            st.success("Transaction recorded successfully!")
        else:
            st.error("Please fill all fields correctly.")
    
    # Display Transactions
    st.header("📜 Transaction History")
    if transactions:
        df = pd.DataFrame(transactions)
        st.dataframe(df)
    else:
        st.write("No transactions found.")
    
    # Expenditure Analysis
    st.header("📊 Expenditure Analysis")
    if transactions:
        df = pd.DataFrame(transactions)
        category_totals = df.groupby("category")["amount"].sum()
        st.bar_chart(category_totals)
    
    # Debt Settlement
    st.header("🔄 Settle Debts")
    friend_balances = {}
    for tx in transactions:
        friend_balances[tx["payer"]] = friend_balances.get(tx["payer"], 0) - tx["amount"]
        friend_balances[tx["payee"]] = friend_balances.get(tx["payee"], 0) + tx["amount"]
    
    for friend, balance in friend_balances.items():
        if balance > 0:
            st.write(f"{friend} should receive Rs {balance}")
        elif balance < 0:
            st.write(f"{friend} owes Rs {-balance}")
        else:
            st.write(f"{friend} is settled up!")
    
    # Save Data
    if st.button("Save Data"):
        save_data(TRANSACTIONS_FILE, transactions)
        st.success("Data saved successfully!")
