import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

st.title("🏥 Hospital No-Show Analysis Dashboard")
st.caption("Analyzing patient behavior and reducing appointment drop-offs")


# PAGE CONFIG

st.set_page_config(page_title="Hospital Funnel Dashboard", layout="wide")


# CUSTOM CSS

st.markdown("""
<style>
.kpi-card {
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-weight: bold;
}
.kpi-blue { background-color: #1f77b4; }
.kpi-green { background-color: #2ca02c; }
.kpi-red { background-color: #d62728; }
.section {
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)


# LOAD DATA

file_path = os.path.join("data", "processed", "appointment_cleaned.csv")
df = pd.read_csv(file_path)


# PREPROCESS

df['scheduledday'] = pd.to_datetime(df['scheduledday'])
df['appointmentday'] = pd.to_datetime(df['appointmentday'])
df['waiting_days'] = (df['appointmentday'] - df['scheduledday']).dt.days

# Label mapping
df['sms_label'] = df['sms_received'].map({
    1: "SMS Sent",
    0: "No Reminder"
})

df['scholarship_label'] = df['scholarship'].map({
    1: "Eligible",
    0: "Not Eligible"
})


# SIDEBAR NAVIGATION

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Analysis", "Mitigation"])


# SIDEBAR FILTERS

st.sidebar.title("Filters")

gender = st.sidebar.multiselect("Gender", df['gender'].unique(), default=df['gender'].unique())
age_group = st.sidebar.multiselect("Age Group", df['age_group'].unique(), default=df['age_group'].unique())
weekday = st.sidebar.multiselect("Day of Week", df['appointment_dayofweek'].unique(), default=df['appointment_dayofweek'].unique())
sms = st.sidebar.multiselect("SMS Status", df['sms_label'].unique(), default=df['sms_label'].unique())
scholarship = st.sidebar.multiselect("Scholarship Status", df['scholarship_label'].unique(), default=df['scholarship_label'].unique())

# Apply filters
df = df[
    (df['gender'].isin(gender)) &
    (df['age_group'].isin(age_group)) &
    (df['appointment_dayofweek'].isin(weekday)) &
    (df['sms_label'].isin(sms)) &
    (df['scholarship_label'].isin(scholarship))
]


# METRICS

total = len(df)
attended = len(df[df['no_show'] == 0])
missed = len(df[df['no_show'] == 1])
show_rate = attended / total if total > 0 else 0
no_show_rate = 1 - show_rate


# ANALYSIS PAGE

if page == "Analysis":

    st.title("Hospital Appointment Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="kpi-card kpi-blue">Total Appointments<br><h2>{total}</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="kpi-card kpi-green">Show Rate<br><h2>{show_rate:.2%}</h2></div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="kpi-card kpi-red">Missed Appointments<br><h2>{missed}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Funnel", "Behavior", "Demographics"])

    # Funnel Tab
    with tab1:
        st.subheader("Overall Funnel")

        fig = go.Figure(go.Funnel(
            y=["Scheduled", "Attended"],
            x=[total, attended]
        ))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("SMS Impact Funnel")

        sms_yes = df[df['sms_received'] == 1]
        sms_no = df[df['sms_received'] == 0]

        fig_sms = go.Figure()

        fig_sms.add_trace(go.Funnel(
            name="SMS Sent",
            y=["Scheduled", "Attended"],
            x=[len(sms_yes), len(sms_yes[sms_yes['no_show'] == 0])]
        ))

        fig_sms.add_trace(go.Funnel(
            name="No Reminder",
            y=["Scheduled", "Attended"],
            x=[len(sms_no), len(sms_no[sms_no['no_show'] == 0])]
        ))

        st.plotly_chart(fig_sms, use_container_width=True)

    # Behavior Tab
    with tab2:
        st.subheader("Wait Time Impact")

        df['wait_bucket'] = pd.cut(
            df['waiting_days'],
            bins=[-1, 2, 7, 100],
            labels=["0-2", "3-7", "8+"]
        )

        wait_analysis = df.groupby("wait_bucket")['no_show'].mean()
        st.bar_chart(wait_analysis)

        worst_bucket = wait_analysis.idxmax()
        st.write(f"Highest no-show occurs in wait bucket: {worst_bucket}")

    # Demographics Tab
    with tab3:
        st.subheader("Age Group")

        age_analysis = df.groupby("age_group")['no_show'].mean()
        st.bar_chart(age_analysis)

        st.subheader("Weekday")

        weekday_analysis = df.groupby("appointment_dayofweek")['no_show'].mean()
        st.bar_chart(weekday_analysis)


# MITIGATION PAGE

elif page == "Mitigation":

    st.title("Mitigation and Recommendations")

    st.subheader("Problem Summary")
    st.write(f"No-show rate is {no_show_rate:.2%}, indicating a significant drop-off after scheduling.")

    st.markdown("---")

    # Wait Time Driver
    st.subheader("Key Driver: Wait Time")

    df['wait_bucket'] = pd.cut(
        df['waiting_days'],
        bins=[-1, 2, 7, 100],
        labels=["0-2", "3-7", "8+"]
    )

    wait_analysis = df.groupby("wait_bucket")['no_show'].mean()
    st.bar_chart(wait_analysis)

    worst_bucket = wait_analysis.idxmax()
    st.write(f"Patients in {worst_bucket} wait category have the highest no-show rate.")

    st.markdown("---")

    # SMS Driver
    st.subheader("SMS Effectiveness")

    sms_analysis = df.groupby("sms_label")['no_show'].mean()
    st.bar_chart(sms_analysis)

    st.markdown("---")

    # Recommendations
    st.subheader("Recommended Actions")

    st.write("""
    1. Reduce waiting time:
       - Prioritize appointments within 3-5 days.
       - Optimize scheduling to reduce backlog.

    2. Improve reminder system:
       - Send reminders 24 hours before appointment.
       - Add additional same-day reminders.

    3. Target high-risk groups:
       - Identify patients with long wait times.
       - Provide flexible rescheduling options.

    4. Optimize scheduling strategy:
       - Consider slight overbooking based on historical no-show rates.
    """)

    st.markdown("---")

    st.subheader("Expected Impact")

    st.write("""
    - Reducing wait times can significantly improve attendance rates.
    - Enhanced reminders can reduce last-minute no-shows.
    - Targeted interventions can improve operational efficiency.
    """)

st.markdown("---")
st.caption("Built by Arshya Nawas | Data Analyst Portfolio Project")
