import pandas as pd
import os


# FILE PATH 

file_path = os.path.join("data", "raw", "appointments", "appointment.csv")


# LOAD DATA 

try:
    df = pd.read_csv(file_path)
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding="latin-1")

print("Original Shape:", df.shape)


# CLEAN COLUMN NAMES

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace('-', '_')
    .str.replace(' ', '_')
)

print("Columns after cleaning:")
print(df.columns.tolist())


# VALIDATE REQUIRED COLUMNS

required_cols = ['scheduledday', 'appointmentday', 'no_show', 'age']
for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")


# CONVERT DATES

df['scheduledday'] = pd.to_datetime(df['scheduledday'], errors='coerce')
df['appointmentday'] = pd.to_datetime(df['appointmentday'], errors='coerce')


# CREATE WAITING DAYS

df['waiting_days'] = (df['appointmentday'] - df['scheduledday']).dt.days

# Fix negatives
df['waiting_days'] = df['waiting_days'].apply(lambda x: x if pd.notnull(x) and x >= 0 else 0)


# CLEAN TARGET COLUMN

df['no_show'] = df['no_show'].map({'No': 0, 'Yes': 1})


# FEATURE ENGINEERING


# Day of week
df['appointment_dayofweek'] = df['appointmentday'].dt.day_name()

# Age groups
def age_group(age):
    if age < 18:
        return "Child"
    elif age < 40:
        return "Adult"
    elif age < 60:
        return "Middle Age"
    else:
        return "Senior"

df['age_group'] = df['age'].apply(age_group)


# CLEAN INVALID DATA

df = df[df['age'] >= 0]
df = df.dropna(subset=['scheduledday', 'appointmentday'])


# SAVE OUTPUT

output_path = os.path.join("data", "processed", "appointment_cleaned.csv")
df.to_csv(output_path, index=False)

print("\nCleaned data saved to:", output_path)
print("Final Shape:", df.shape)