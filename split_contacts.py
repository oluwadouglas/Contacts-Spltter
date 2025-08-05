import pandas as pd
from datetime import datetime, timedelta
import os

# ✅ Load CSV
filename = "contacts.csv"
if not os.path.exists(filename):
    print(f"❌ File '{filename}' not found.")
    exit()

# ✅ Automatically detect header (assumes first row is header)
df = pd.read_csv(filename)

# ✅ Clean column headers
df.columns = df.columns.str.strip()

# ✅ Check for 'DATE' column (case-insensitive)
date_column = None
for col in df.columns:
    if col.strip().upper() == "DATE":
        date_column = col
        break

if not date_column:
    print("❌ No 'DATE' column found. Available columns:", list(df.columns))
    exit()

# ✅ Parse 'DATE' column to date only (ignore time)
def try_parse_date(value):
    try:
        # Handles formats like "8/1/2025" or "8/1/2025 12:47:28"
        return datetime.strptime(str(value).split()[0], "%m/%d/%Y").date()
    except:
        return None

df['DATE_PARSED'] = df[date_column].apply(try_parse_date)
df = df[df['DATE_PARSED'].notna()]

if df.empty:
    print("⚠️ No valid dates found after parsing.")
    exit()

# ✅ Ask for filtering
filter_choice = input("📌 Filter contacts by date? (yes/no): ").strip().lower()

if filter_choice == 'yes':
    print("👉 Choose date filter:")
    print("   1. Today")
    print("   2. Yesterday")
    print("   3. Both Today and Yesterday")
    print("   4. Custom date range")
    choice = input("Enter choice (1-4): ").strip()

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    if choice == '1':
        df = df[df['DATE_PARSED'] == today]
    elif choice == '2':
        df = df[df['DATE_PARSED'] == yesterday]
    elif choice == '3':
        df = df[df['DATE_PARSED'].isin([today, yesterday])]
    elif choice == '4':
        try:
            start_str = input("🔽 Enter START date (MM/DD/YYYY): ").strip()
            end_str = input("🔼 Enter END date (MM/DD/YYYY): ").strip()
            start_date = datetime.strptime(start_str, "%m/%d/%Y").date()
            end_date = datetime.strptime(end_str, "%m/%d/%Y").date()
            df = df[(df['DATE_PARSED'] >= start_date) & (df['DATE_PARSED'] <= end_date)]
        except ValueError:
            print("❌ Invalid date format. Use MM/DD/YYYY.")
            exit()
    else:
        print("❌ Invalid choice.")
        exit()

    if df.empty:
        print("⚠️ No contacts match the selected date range.")
        exit()
    else:
        print(f"✅ {len(df)} contacts found for your selection.")
else:
    print(f"📂 Using all {len(df)} contacts without filtering.")

# ✅ Ask how many parts to split into
while True:
    try:
        num_parts = int(input("🔢 How many parts do you want to split the contacts into?: "))
        if num_parts > 0:
            break
        else:
            print("❌ Enter a number greater than 0.")
    except ValueError:
        print("❌ Invalid number. Try again.")

# ✅ Split and export
chunk_size = len(df) // num_parts + (len(df) % num_parts > 0)

for i in range(num_parts):
    start = i * chunk_size
    end = start + chunk_size
    chunk = df.iloc[start:end]
    if not chunk.empty:
        output_filename = f"contacts_part_{i+1}.csv"
        chunk.to_csv(output_filename, index=False)
        print(f"✅ Saved: {output_filename} ({len(chunk)} contacts)")

print("🎉 Done! Contacts successfully split.")

