import pandas as pd
import os
import matplotlib.pyplot as plt

# LOAD CLEAN DATA

file_path = os.path.join("data", "processed", "appointment_cleaned.csv")
df = pd.read_csv(file_path)

print("Loaded data:", df.shape)


# BASIC FUNNEL METRICS

total_appointments = len(df)
attended = len(df[df['no_show'] == 0])
missed = len(df[df['no_show'] == 1])

show_rate = attended / total_appointments
no_show_rate = missed / total_appointments

print("\n=== FUNNEL METRICS ===")
print(f"Total Appointments: {total_appointments}")
print(f"Attended: {attended}")
print(f"Missed: {missed}")
print(f"Show Rate: {show_rate:.2%}")
print(f"No-Show Rate: {no_show_rate:.2%}")


# SAVE SUMMARY

summary = pd.DataFrame({
    "Metric": ["Total", "Attended", "Missed", "Show Rate", "No-Show Rate"],
    "Value": [total_appointments, attended, missed, show_rate, no_show_rate]
})

summary_path = os.path.join("results", "summary.csv")
summary.to_csv(summary_path, index=False)

import plotly.graph_objects as go

# Funnel values
stages = ["Scheduled", "Attended", "Missed"]
values = [total_appointments, attended, missed]

fig = go.Figure(go.Funnel(
    y=stages,
    x=values
))

fig.write_image("results/charts/funnel_chart.png")
fig.show()


# NO-SHOW BY AGE GROUP

age_analysis = df.groupby("age_group")['no_show'].mean()

plt.figure()
age_analysis.plot(kind='bar')
plt.title("No-Show Rate by Age Group")
plt.ylabel("No-Show Rate")

plt.savefig(os.path.join("results", "charts", "age_no_show.png"))
plt.close()


# NO-SHOW BY SMS

sms_analysis = df.groupby("sms_received")['no_show'].mean()

plt.figure()
sms_analysis.plot(kind='bar')
plt.title("No-Show Rate by SMS Received")
plt.ylabel("No-Show Rate")

plt.savefig(os.path.join("results", "charts", "sms_no_show.png"))
plt.close()


# NO-SHOW BY WEEKDAY

weekday_analysis = df.groupby("appointment_dayofweek")['no_show'].mean()

plt.figure()
weekday_analysis.plot(kind='bar')
plt.title("No-Show Rate by Day of Week")
plt.ylabel("No-Show Rate")

plt.savefig(os.path.join("results", "charts", "weekday_no_show.png"))
plt.close()


# FINAL INSIGHT

print("\nTop Insight:")
print(f"No-show rate: {no_show_rate:.2%}")

print("\n Analysis complete. Results saved in /results")
if no_show_rate > 0.2:
    print("\nHigh no-show rate detected!")
else:
    print("\nNo-show rate is within acceptable range")

print(f"No-show rate: {no_show_rate:.2%}")