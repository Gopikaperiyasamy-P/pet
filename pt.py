import streamlit as st
import sqlite3
from datetime import datetime

# ---------- Database Setup ---------- #
conn = sqlite3.connect("pet_adoption.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    age INTEGER,
    status TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS adopters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS adoptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adopter_id INTEGER,
    pet_id INTEGER,
    date TEXT,
    FOREIGN KEY(adopter_id) REFERENCES adopters(id),
    FOREIGN KEY(pet_id) REFERENCES pets(id)
)
''')

conn.commit()

# ---------- Models ---------- #
class Pet:
    def _init_(self, name, pet_type, age):
        self.name = name
        self.pet_type = pet_type
        self.age = age

    def save(self):
        cursor.execute("INSERT INTO pets (name, type, age, status) VALUES (?, ?, ?, ?)",
                       (self.name, self.pet_type, self.age, 'Available'))
        conn.commit()

class Adopter:
    def _init_(self, name, contact):
        self.name = name
        self.contact = contact

    def save(self):
        cursor.execute("INSERT INTO adopters (name, contact) VALUES (?, ?)",
                       (self.name, self.contact))
        conn.commit()

# ---------- Streamlit App Layout ---------- #
st.set_page_config(page_title="Pet Adoption App", layout="centered")
st.title("🐾 Pet Adoption Management System")

# ---------- Navigation ---------- #
menu = st.sidebar.radio("Navigate", ["Home", "Add Pet", "Adopt Pet", "Available Pets", "Adoption History"])

if menu == "Home":
    st.subheader("Welcome to the Pet Adoption Center 🏠")
    st.write("Use the menu on the left to get started.")

elif menu == "Add Pet":
    st.subheader("➕ Add a Pet")
    name = st.text_input("Pet Name")
    pet_type = st.selectbox("Pet Type", ["Dog", "Cat", "Rabbit", "Other"])
    age = st.number_input("Pet Age", min_value=0, max_value=30)

    if st.button("Save Pet"):
        pet = Pet(name, pet_type, age)
        pet.save()
        st.success("✅ Pet added successfully!")

elif menu == "Adopt Pet":
    st.subheader("❤ Adopt a Pet")
    cursor.execute("SELECT * FROM pets WHERE status='Available'")
    pets = cursor.fetchall()

    if not pets:
        st.info("No pets currently available.")
    else:
        pet_options = {f"{p[1]} ({p[2]}) - ID {p[0]}": p[0] for p in pets}
        selected = st.selectbox("Select a Pet", list(pet_options.keys()))
        name = st.text_input("Your Name")
        contact = st.text_input("Your Contact")

        if st.button("Confirm Adoption"):
            adopter = Adopter(name, contact)
            adopter.save()

            pet_id = pet_options[selected]
            cursor.execute("SELECT id FROM adopters ORDER BY id DESC LIMIT 1")
            adopter_id = cursor.fetchone()[0]

            cursor.execute("UPDATE pets SET status='Adopted' WHERE id=?", (pet_id,))
            cursor.execute("INSERT INTO adoptions (adopter_id, pet_id, date) VALUES (?, ?, ?)",
                           (adopter_id, pet_id, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("🎉 Adoption successful!")

elif menu == "Available Pets":
    st.subheader("📋 Available Pets")
    cursor.execute("SELECT * FROM pets WHERE status='Available'")
    rows = cursor.fetchall()

    if not rows:
        st.info("No pets available right now.")
    else:
        for row in rows:
            st.write(f"*ID:* {row[0]}, *Name:* {row[1]}, *Type:* {row[2]}, *Age:* {row[3]}")

elif menu == "Adoption History":
    st.subheader("📜 Adoption History")
    cursor.execute('''
        SELECT a.id, d.name, p.name, a.date FROM adoptions a
        JOIN adopters d ON a.adopter_id = d.id
        JOIN pets p ON a.pet_id = p.id
    ''')
    history = cursor.fetchall()

    if not history:
        st.info("No adoptions yet.")
    else:
        for h in history:
            st.write(f"*Adoption ID:* {h[0]} | *Adopter:* {h[1]} | *Pet:* {h[2]} | *Date:* {h[3]}")
