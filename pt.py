import sqlite3
from datetime import datetime

# ----------- Database Setup ----------- #
conn = sqlite3.connect('pet_adoption.db')
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

# ----------- Models ----------- #
class Pet:
    def __init__(self, name, pet_type, age):  # fixed typo from _init_ to __init__
        self.name = name
        self.pet_type = pet_type
        self.age = age

    def save(self):
        cursor.execute("INSERT INTO pets (name, type, age, status) VALUES (?, ?, ?, ?)",
                       (self.name, self.pet_type, self.age, 'Available'))
        conn.commit()

class Adopter:
    def __init__(self, name, contact):  # fixed typo from _init_ to __init__
        self.name = name
        self.contact = contact

    def save(self):
        cursor.execute("INSERT INTO adopters (name, contact) VALUES (?, ?)",
                       (self.name, self.contact))
        conn.commit()

# ----------- Operations ----------- #
def list_available_pets():
    cursor.execute("SELECT * FROM pets WHERE status='Available'")
    pets = cursor.fetchall()
    if not pets:
        print("No available pets.")
    for pet in pets:
        print(f"ID: {pet[0]}, Name: {pet[1]}, Type: {pet[2]}, Age: {pet[3]}")

def adopt_pet():
    list_available_pets()
    pet_id = input("Enter Pet ID to adopt: ")
    name = input("Your name: ")
    contact = input("Your contact: ")

    adopter = Adopter(name, contact)
    adopter.save()

    cursor.execute("SELECT id FROM adopters ORDER BY id DESC LIMIT 1")
    adopter_id = cursor.fetchone()[0]

    cursor.execute("UPDATE pets SET status='Adopted' WHERE id=?", (pet_id,))
    cursor.execute("INSERT INTO adoptions (adopter_id, pet_id, date) VALUES (?, ?, ?)",
                   (adopter_id, pet_id, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    print("🎉 Adoption successful!")

def view_adoption_history():
    cursor.execute('''
    SELECT a.id, d.name, p.name, a.date FROM adoptions a
    JOIN adopters d ON a.adopter_id = d.id
    JOIN pets p ON a.pet_id = p.id
    ''')
    records = cursor.fetchall()
    for rec in records:
        print(f"Adoption ID: {rec[0]}, Adopter: {rec[1]}, Pet: {rec[2]}, Date: {rec[3]}")

# ----------- Test for GitHub Actions (non-interactive) ----------- #
def test_app():
    print("🧪 Adding a test pet...")
    Pet("Tommy", "Dog", 2).save()
    
    print("\n📋 Listing available pets:")
    list_available_pets()
    
    print("\n📜 Viewing adoption history:")
    view_adoption_history()

# ----------- Entry Point ----------- #
if __name__ == "__main__":
    # Commented out menu for GitHub Actions compatibility
    # while True:
    #     print("\n--- PET ADOPTION SYSTEM ---")
    #     print("1. Add Pet")
    #     print("2. List Available Pets")
    #     print("3. Adopt a Pet")
    #     print("4. View Adoption History")
    #     print("5. Exit")
        
    #     choice = input("Enter choice: ")
    #     if choice == '1':
    #         name = input("Pet name: ")
    #         pet_type = input("Pet type (Dog/Cat/etc.): ")
    #         age = int(input("Pet age: "))
    #         Pet(name, pet_type, age).save()
    #         print("✅ Pet added.")
    #     elif choice == '2':
    #         list_available_pets()
    #     elif choice == '3':
    #         adopt_pet()
    #     elif choice == '4':
    #         view_adoption_history()
    #     elif choice == '5':
    #         print("👋 Goodbye!")
    #         break
    #     else:
    #         print("❌ Invalid choice. Try again.")

    # Run test instead
    test_app()
