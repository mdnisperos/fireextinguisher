import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

class FireExtinguisherApp:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extinguishers (
                id INTEGER PRIMARY KEY,
                building TEXT,
                room TEXT,
                type TEXT,
                weight REAL,
                date_refilled TEXT,
                date_expiration TEXT,
                supplier TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def add_extinguisher(self, building, room, type, weight, date_refilled, date_expiration, supplier, notes):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO extinguishers (building, room, type, weight, date_refilled, date_expiration, supplier, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (building, room, type, weight, date_refilled, date_expiration, supplier, notes))
        self.conn.commit()

    def get_all_extinguishers(self):
        return pd.read_sql_query("SELECT * from extinguishers", self.conn)

def main():
    st.title("Fire Extinguisher Inventory")

    app = FireExtinguisherApp()

    menu = ["View Inventory", "Add Extinguisher", "Generate Report"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "View Inventory":
        st.subheader("Current Inventory")
        st.dataframe(app.get_all_extinguishers())

    elif choice == "Add Extinguisher":
        st.subheader("Add New Extinguisher")
        building = st.text_input("Building")
        room = st.text_input("Room")
        type = st.selectbox("Type", ["Red", "Green", "Gray"])
        weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
        date_refilled = st.date_input("Date Refilled")
        date_expiration = st.date_input("Expiration Date")
        supplier = st.text_input("Supplier")
        notes = st.text_area("Notes")

        if st.button("Add Extinguisher"):
            app.add_extinguisher(building, room, type, weight, date_refilled.strftime('%Y-%m-%d'), 
                                 date_expiration.strftime('%Y-%m-%d'), supplier, notes)
            st.success("Extinguisher added successfully!")

    elif choice == "Generate Report":
        st.subheader("Generate Report")
        report_type = st.selectbox("Report Type", ["Full Inventory", "Expiring Soon"])
        if st.button("Generate"):
            if report_type == "Full Inventory":
                st.dataframe(app.get_all_extinguishers())
            elif report_type == "Expiring Soon":
                # Implement expiring soon logic here
                st.write("Expiring Soon report to be implemented")

if __name__ == "__main__":
    main()