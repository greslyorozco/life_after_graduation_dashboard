import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import os
import zipfile

st.set_page_config(page_title="Life After Graduation", layout="wide")

sns.set_theme(style="whitegrid")

school_colors = ["gold", "lightpink", "steelblue"]

st.sidebar.title("Life After Graduation")
st.sidebar.write("Student Debt + Post College Outcomes")

if os.path.exists("Images/graduation.png"):
    st.sidebar.image("Images/graduation.png", width=150)

st.sidebar.subheader("Team")
st.sidebar.write("Gresly Orozco")
st.sidebar.write("Elena Thomasson")
st.sidebar.write("Abraham Goffe")

st.sidebar.markdown("---")
st.sidebar.subheader("Dashboard Sections")
st.sidebar.write("Overview")
st.sidebar.write("Major Outcomes")
st.sidebar.write("Student Debt")
st.sidebar.write("Debt and Earnings")
st.sidebar.write("Data Cleaning")
st.sidebar.write("Conclusion")

with zipfile.ZipFile("Data/Most-Recent-Cohorts-Institution 3.csv.zip") as zipped_file:
    for file_name in zipped_file.namelist():
        if file_name.endswith(".csv") and "__MACOSX" not in file_name:
            with zipped_file.open(file_name) as csv_file:
                scorecard_df = pd.read_csv(csv_file, low_memory=False)

majors_df = pd.read_csv("Data/sample_recent_grads.csv")

loan_state_df = None
if os.path.exists("Data/student-loan-by-state.xlsx"):
    try:
        loan_state_df = pd.read_excel("Data/student-loan-by-state.xlsx")
    except:
        loan_state_df = None

scorecard_df["DEBT_MDN"] = pd.to_numeric(scorecard_df["DEBT_MDN"], errors="coerce")

if "MD_EARN_WNE_P10" in scorecard_df.columns:
    scorecard_df["MD_EARN_WNE_P10"] = pd.to_numeric(scorecard_df["MD_EARN_WNE_P10"], errors="coerce")

scorecard_df["School Type"] = scorecard_df["CONTROL"].map({
    1: "Public",
    2: "Private nonprofit",
    3: "Private for profit"
})

scorecard_df = scorecard_df.dropna(subset=["DEBT_MDN"])
scorecard_df = scorecard_df.dropna(subset=["School Type"])

majors_df["Median"] = pd.to_numeric(majors_df["Median"], errors="coerce")
majors_df["Unemployment_rate"] = pd.to_numeric(majors_df["Unemployment_rate"], errors="coerce")
majors_df = majors_df.dropna(subset=["Median", "Unemployment_rate"])

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

school_options = scorecard_df["School Type"].dropna().unique()

selected_school_types = st.sidebar.multiselect(
    "School type",
    school_options,
    default=school_options
)

scorecard_filtered = scorecard_df.loc[
    scorecard_df["School Type"].isin(selected_school_types)
]

major_categories = majors_df["Major_category"].dropna().unique()

selected_major_category = st.sidebar.selectbox(
    "Major category",
    major_categories
)

majors_filtered = majors_df.loc[
    majors_df["Major_category"] == selected_major_category
]

col_title, col_image = st.columns([2, 1])

with col_title:
    st.title("Life After Graduation")
    st.subheader("The Impact of Student Debt on Earnings and Employment")

    st.write("""
    College can open doors, but it can also leave students with debt.
    This dashboard looks at both sides: what students owe and what they may gain after graduation.
    """)

    st.write("""
    We compare student debt with salary, unemployment, school type, major choice, and location.
    """)

with col_image:
    if os.path.exists("Images/college.png"):
        st.image("Images/college.png", width=330)
    elif os.path.exists("Images/graduation.png"):
        st.image("Images/graduation.png", width=330)

st.markdown("---")

metric1, metric2 = st.columns(2)

with metric1:
    st.metric("Schools in the Data", scorecard_filtered["INSTNM"].nunique())

with metric2:
    st.metric("States in the Data", scorecard_filtered["STABBR"].nunique())

metric3, metric4 = st.columns(2)

with metric3:
    st.metric("Median Student Debt", "$" + str(round(scorecard_filtered["DEBT_MDN"].median(), 0)))

with metric4:
    st.metric("Selected Major Group", selected_major_category)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Major Outcomes",
    "Student Debt",
    "Debt and Earnings",
    "Data Cleaning",
    "Conclusion"
])

with tab1:
    st.header("Overview")

    st.write("""
    After students borrow money for college,
    what happens next?
    """)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if os.path.exists("Images/debt.png"):
            st.image("Images/debt.png", width=110)
        st.subheader("Debt")
        st.write("This is the money students may owe after college.")

    with col_b:
        if os.path.exists("Images/salary.png"):
            st.image("Images/salary.png", width=110)
        st.subheader("Salary")
        st.write("This shows how much graduates may earn after college.")

    with col_c:
        if os.path.exists("Images/career.png"):
            st.image("Images/career.png", width=110)
        st.subheader("Jobs")
        st.write("This helps us understand whether graduates are finding work.")

    st.markdown("---")

    st.write("""
    We do not want to look at debt by itself. Debt only makes sense when we also look at
    salary, jobs, school type, major choice, and state.
    """)

    with st.expander("Click to see our project questions"):
        st.write("""
        1. Is student debt rising over time?  
        2. How does debt vary by state?  
        3. What is the link between debt and income?  
        4. Does more debt lead to more pay?  
        5. How does debt connect to job outcomes?  
        6. How does cost of living change the story?  
        7. Which school type seems to pay off better?  
        """)

with tab2:
    st.header("Outcomes by Major")

    st.write("Use the sidebar to choose a major group.")

    top_10 = majors_filtered.sort_values("Median", ascending=False).head(10)

    col_left, col_right = st.columns(2)

    with col_left:
        fig = px.bar(
            top_10,
            x="Median",
            y="Major",
            color="Median",
            orientation="h",
            title="Top 10 Majors by Median Salary",
            template="plotly_white",
            color_continuous_scale=["lightpink", "orange", "gold"]
        )

        fig.update_layout(
            title_font_size=22,
            xaxis_title="Median Salary",
            yaxis_title="Major"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Click to interpret the salary chart"):
            st.write("""
            This chart shows which majors in the selected group have the highest typical salary.
            It helps us see which fields may lead to stronger earnings after graduation.
            """)

    with col_right:
        fig = px.bar(
            top_10,
            x="Unemployment_rate",
            y="Major",
            color="Unemployment_rate",
            orientation="h",
            title="Unemployment Rate for Those Same Majors",
            template="plotly_white",
            color_continuous_scale=["lightblue", "gold", "salmon"]
        )

        fig.update_layout(
            title_font_size=22,
            xaxis_title="Unemployment Rate",
            yaxis_title="Major"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Click to interpret the unemployment chart"):
            st.write("""
            This chart looks at job risk. A major can have a strong salary, but if unemployment is higher,
            students may still face uncertainty after graduation.
            """)

with tab3:
    st.header("Student Debt by School Type")

    debt_summary = scorecard_filtered.groupby("School Type")["DEBT_MDN"].median()

    st.subheader("Median Debt by School Type")
    st.write(debt_summary)

    fig = px.box(
        scorecard_filtered,
        x="School Type",
        y="DEBT_MDN",
        color="School Type",
        title="Distribution of Median Student Debt by School Type",
        template="plotly_white",
        color_discrete_sequence=school_colors
    )

    fig.update_layout(
        title_font_size=22,
        xaxis_title="School Type",
        yaxis_title="Median Student Debt"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Click to interpret this box plot"):
        st.write("""
        This chart compares student debt across public, private nonprofit, and private for profit schools.
        The line inside each box shows the middle debt value. The dots show schools with much higher or lower debt.
        """)

    st.markdown("---")

    st.subheader("Top 10 States by Median Student Debt")

    state_debt = scorecard_filtered.groupby("STABBR")["DEBT_MDN"].median()
    state_debt = state_debt.sort_values(ascending=False).head(10)
    state_debt = state_debt.reset_index()

    fig = px.bar(
        state_debt,
        x="DEBT_MDN",
        y="STABBR",
        color="DEBT_MDN",
        orientation="h",
        title="Top 10 States by Median Student Debt",
        template="plotly_white",
        color_continuous_scale=["lightgreen", "gold", "orange"]
    )

    fig.update_layout(
        title_font_size=22,
        xaxis_title="Median Student Debt",
        yaxis_title="State"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Click to interpret the state chart"):
        st.write("""
        This chart shows where student debt is highest in the data.
        It helps us compare college debt across different states.
        """)

with tab4:
    st.header("Debt and Earnings")

    if "MD_EARN_WNE_P10" in scorecard_filtered.columns:
        earnings_df = scorecard_filtered.dropna(subset=["MD_EARN_WNE_P10"])

        fig = px.scatter(
            earnings_df,
            x="DEBT_MDN",
            y="MD_EARN_WNE_P10",
            color="School Type",
            hover_name="INSTNM",
            title="Median Student Debt Compared With Median Earnings",
            template="plotly_white",
            color_discrete_sequence=school_colors
        )

        fig.update_layout(
            title_font_size=22,
            xaxis_title="Median Student Debt",
            yaxis_title="Median Earnings"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Click to interpret this scatter plot"):
            st.write("""
            Each dot is a college. Dots farther right have higher student debt.
            Dots higher up have higher earnings. If debt and earnings rise together,
            the dots should move upward as they move right. This chart helps us check if that pattern is clear.
            """)
    else:
        st.write("The earnings column was not found in the dataset.")

    if loan_state_df is not None:
        st.markdown("---")
        st.subheader("Student Loan by State Dataset Preview")
        st.dataframe(loan_state_df.head(), width=1000, height=300)

with tab5:
    st.header("Data Cleaning and Preprocessing")

    st.subheader("College Scorecard Dataset Preview")
    st.dataframe(scorecard_df.head(), width=1200, height=300)

    st.subheader("Major Outcomes Dataset Preview")
    st.dataframe(majors_df.head(), width=1200, height=300)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Scorecard Rows", scorecard_df.shape[0])

    with col2:
        st.metric("Scorecard Columns", scorecard_df.shape[1])

    with col3:
        st.metric("Major Rows", majors_df.shape[0])

    with st.expander("Click to see Scorecard columns"):
        st.write(scorecard_df.columns.tolist())

    with st.expander("Click to see missing values"):
        st.write(scorecard_df.isna().sum())

    st.subheader("Cleaning Steps")

    st.write("""
    1. Loaded the College Scorecard dataset.  
    2. Loaded the major outcomes dataset.  
    3. Changed student debt values into numbers.  
    4. Changed earnings values into numbers when they were available.  
    5. Removed rows that did not have median debt.  
    6. Created a School Type column from the CONTROL column.  
    7. Used groupby to summarize debt by school type and state.  
    """)

with tab6:
    st.header("Conclusion")

    st.write("""
    The big takeaway is that college debt is only one piece of the story.
    A school or major may cost more, but the real question is what happens after graduation.
    This dashboard helps compare debt with salary, job outcomes, school type, and location.
    """)

    st.write("""
    Our final message is simple: students should not only ask, "How much will college cost?"
    They should also ask, "What opportunities might this choice create after graduation?"
    """)

    img1, img2, img3, img4, img5 = st.columns(5)

    with img1:
        if os.path.exists("Images/graduation.png"):
            st.image("Images/graduation.png", width=120)

    with img2:
        if os.path.exists("Images/debt.png"):
            st.image("Images/debt.png", width=120)

    with img3:
        if os.path.exists("Images/salary.png"):
            st.image("Images/salary.png", width=120)

    with img4:
        if os.path.exists("Images/career.png"):
            st.image("Images/career.png", width=120)

    with img5:
        if os.path.exists("Images/college.png"):
            st.image("Images/college.png", width=120)
