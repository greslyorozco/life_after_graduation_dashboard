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

if os.path.exists("graduation.png"):
    st.sidebar.image("graduation.png", width=150)

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
st.sidebar.write("Key Findings")
st.sidebar.write("Conclusion")

with zipfile.ZipFile("Most-Recent-Cohorts-Institution 3.csv.zip") as zipped_file:
    for file_name in zipped_file.namelist():
        if file_name.endswith(".csv") and "__MACOSX" not in file_name:
            with zipped_file.open(file_name) as csv_file:
                scorecard_df = pd.read_csv(csv_file, low_memory=False)

majors_df = pd.read_csv("sample_recent_grads.csv")

loan_state_df = None
if os.path.exists("student-loan-by-state.xlsx"):
    try:
        loan_state_df = pd.read_excel("student-loan-by-state.xlsx")
    except:
        loan_state_df = None

scorecard_df["DEBT_MDN"] = pd.to_numeric(scorecard_df["DEBT_MDN"], errors="coerce")

if "MD_EARN_WNE_P10" in scorecard_df.columns:
    scorecard_df["MD_EARN_WNE_P10"] = pd.to_numeric(scorecard_df["MD_EARN_WNE_P10"], errors="coerce")
major_categories = majors_df["Major_category"].dropna().unique()

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
selected_major_category = st.sidebar.selectbox(
    "Major category",
    major_categories
)
majors_filtered = majors_df.loc[
    majors_df['Major_category'] == selected_major_category
]


school_options = scorecard_df["School Type"].dropna().unique()

selected_school_types = st.sidebar.multiselect(
    "School type",
    school_options,
    default=school_options
)

scorecard_filtered = scorecard_df.loc[
    scorecard_df["School Type"].isin(selected_school_types)
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
    We compare how student debt connects to salary, unemployment, school type, major choice, and location.
    """)

with col_image:
    if os.path.exists("college.png"):
        st.image("college.png", width=330)
    elif os.path.exists("graduation.png"):
        st.image("graduation.png", width=330)

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Major Outcomes",
    "Student Debt",
    "Debt and Earnings",
    "Data Cleaning",
    "Key Findings",
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
        if os.path.exists("debt.png"):
            st.image("debt.png", width=110)
        st.subheader("Debt")
        st.write("This is the money students may owe after college.")

    with col_b:
        if os.path.exists("salary.png"):
            st.image("salary.png", width=110)
        st.subheader("Salary")
        st.write("This shows how much graduates may earn after college.")

    with col_c:
        if os.path.exists("career.png"):
            st.image("career.png", width=110)
        st.subheader("Jobs")
        st.write("This helps us understand whether graduates are finding work.")

    st.markdown("---")

    st.write("""
    We do not want to look at debt by itself. Debt only makes sense when we also look at
    salary, jobs, school type, major choice, and state.
    """)

    with st.expander("Click to see our project questions"):
        st.write("""
        1. How does major choice influence salary and unemployment outcomes after graduation?  
        2. How does debt vary across states?  
        3. What is the relationship between student debt and post-graduation earnings?  
        4. Does higher student debt lead to higher salaries?  
        5. How does student debt relate to employment outcomes?  
        6. How might geographic location and cost of living affect debt and earnings?  
        7. Which school type appears to provide the strongest financial outcomes?  
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
        color="Major",
        orientation="h",
        title="Top Majors by Median Salary",
        template="plotly_white",
        color_discrete_sequence=["steelblue", "gold", "lightpink", "seagreen", "orange"]
    )

    fig.update_layout(
        title_font_size=22,
        xaxis_title="Median Salary",
        yaxis_title="Major",
        showlegend=False
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
        color="Major",
        orientation="h",
        title="Unemployment Rate",
        template="plotly_white",
        color_discrete_sequence=["steelblue", "gold", "lightpink", "seagreen", "orange"]
    )

    fig.update_layout(
        title_font_size=22,
        xaxis_title="Unemployment Rate",
        yaxis_title="Major",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Click to interpret the unemployment chart"):
        st.write("""
        This chart looks at job risk. A major can have a strong salary, but if unemployment is higher,
        students may still face uncertainty after graduation.
        """)

st.caption("Use the major category filter in the sidebar to change the major outcomes.")
with tab3:
    st.header("Student Debt")

    debt_summary = scorecard_filtered.groupby("School Type", as_index=False)["DEBT_MDN"].median()

    st.subheader("Median Debt by School Type")

    fig = px.bar(
        debt_summary,
        x="School Type",
        y="DEBT_MDN",
        color="School Type",
        title="Median Student Debt by School Type",
        template="plotly_white",
        color_discrete_sequence=school_colors
    )

    fig.update_layout(
        title_font_size=22,
        xaxis_title="School Type",
        yaxis_title="Median Student Debt"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Click to interpret this bar chart"):
        st.write("""
        This chart compares the middle student debt amount for each school type.
        A taller bar means students from that school type usually owe more.
        We used a bar chart here because it is clean and easy to compare.
        """)

    with st.expander("Click to see the spread of student debt"):
        fig = px.box(
            scorecard_filtered,
            x="School Type",
            y="DEBT_MDN",
            color="School Type",
            points=False,
            title="Student Debt Spread by School Type",
            template="plotly_white",
            color_discrete_sequence=school_colors
        )

        fig.update_layout(
            title_font_size=22,
            xaxis_title="School Type",
            yaxis_title="Median Student Debt"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write("""
        This extra chart shows how spread out student debt is within each school type.
        We placed it inside a click section so the main dashboard stays clean.
        """)

    st.markdown("---")

    st.subheader("Top States by Median Student Debt")

    state_debt = scorecard_filtered.groupby("STABBR")["DEBT_MDN"].median()
    state_debt = state_debt.sort_values(ascending=False).head(10)
    state_debt = state_debt.reset_index()

    fig = px.bar(
        state_debt,
        x="DEBT_MDN",
        y="STABBR",
        color="DEBT_MDN",
        orientation="h",
        title="Top States by Median Student Debt",
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

    st.write("""
    This section compares what students may owe with what graduates may earn.
    It also shows how location can change the meaning of earnings.
    """)

    st.markdown("---")
    st.subheader("Cost of Living Example: CT vs GA vs FL")

    st.write("""
    This chart compares raw earnings and adjusted earnings across Connecticut, Georgia, and Florida.
    The adjustment shows that the same salary can feel different depending on where someone lives.
    """)

    states_of_interest = ["CT", "GA", "FL"]
    geo_df = scorecard_filtered[scorecard_filtered["STABBR"].isin(states_of_interest)].copy()
    geo_df = geo_df.dropna(subset=["MD_EARN_WNE_P10", "DEBT_MDN"])

    cost_index = {
        "CT": 1.20,
        "FL": 1.05,
        "GA": 0.90
    }

    geo_df["Adjusted Earnings"] = geo_df.apply(
        lambda row: row["MD_EARN_WNE_P10"] / cost_index.get(row["STABBR"], 1),
        axis=1
    )

    geo_grouped = geo_df.groupby("STABBR")[["MD_EARN_WNE_P10", "Adjusted Earnings", "DEBT_MDN"]].mean().reset_index()

    fig = px.bar(
        geo_grouped,
        x="STABBR",
        y=["MD_EARN_WNE_P10", "Adjusted Earnings"],
        barmode="group",
        title="Raw vs Adjusted Earnings by State",
        template="plotly_white",
        color_discrete_sequence=["steelblue", "gold"]
    )

    fig.update_layout(
        title_font_size=20,
        xaxis_title="State",
        yaxis_title="Earnings",
        legend_title="Measure"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        geo_grouped,
        x="STABBR",
        y="DEBT_MDN",
        color="STABBR",
        title="Average Student Debt by State",
        template="plotly_white",
        color_discrete_sequence=school_colors
    )

    fig2.update_layout(
        title_font_size=20,
        xaxis_title="State",
        yaxis_title="Student Debt"
    )

    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Click to interpret the cost of living section"):
        st.write("""
        This section shows that earnings do not mean the same thing in every state.
        A higher salary may not go as far in a more expensive state.
        This is why location matters when thinking about debt and earnings after graduation.
        """)

    st.markdown("---")
    st.subheader("Debt Compared With Earnings")

    if "MD_EARN_WNE_P10" in scorecard_filtered.columns:
        earnings_df = scorecard_filtered.dropna(subset=["MD_EARN_WNE_P10", "DEBT_MDN"])

        earnings_summary = earnings_df.groupby(
            ["STABBR", "School Type"],
            as_index=False
        ).agg({
            "DEBT_MDN": "median",
            "MD_EARN_WNE_P10": "median",
            "INSTNM": "count"
        })

        earnings_summary = earnings_summary.rename(columns={"INSTNM": "School Count"})

        fig = px.scatter(
            earnings_summary,
            x="DEBT_MDN",
            y="MD_EARN_WNE_P10",
            color="School Type",
            size="School Count",
            hover_name="STABBR",
            hover_data=["School Count"],
            title="Median Debt Compared With Median Earnings",
            template="plotly_white",
            color_discrete_sequence=school_colors
        )

        fig.update_layout(
            title_font_size=22,
            xaxis_title="Median Student Debt",
            yaxis_title="Median Earnings"
        )

        fig.update_traces(marker=dict(opacity=0.65))

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Click to interpret this scatter plot"):
            st.write("""
            Each dot is a group of schools in one state and one school type.
            Dots on the right have higher student debt.
            Dots near the top have higher earnings.
            If the dots are spread out, then debt alone does not explain earnings.
            """)
    else:
        st.write("The earnings column was not found in the dataset.")


with tab5:
    st.header("Data Cleaning and Preprocessing")

    st.subheader("College Scorecard Dataset Preview")
    st.dataframe(scorecard_df.head(), width=1200, height=300)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Scorecard Rows", scorecard_df.shape[0])

    with col2:
        st.metric("Scorecard Columns", scorecard_df.shape[1])

    with st.expander("Click to see Scorecard columns"):
        st.write(scorecard_df.columns.tolist())

    with st.expander("Click to see missing values"):
        st.write(scorecard_df.isna().sum())

    st.subheader("Major Outcomes Dataset Preview")
    st.dataframe(majors_df.head(), width=1200, height=300)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Majors Rows", majors_df.shape[0])

    with col2:
        st.metric("Majors Columns", majors_df.shape[1])


    with st.expander("Click to see Majors columns"):
        st.write(majors_df.columns.tolist())

    with st.expander("Click to see missing values"):
        st.write(majors_df.isna().sum())

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
    st.header("Key Findings")

    st.success('''
    - Public schools generally showed lower median debt compared to some private institutions.
    - Looking at debt alone does ot provide the full picture of college value.
    ''')
    st.info('''
    - Engineering and health majors tend to have higher major salaries but also involve higher debt.
    - Major choice appears to have a strong impact on salary and unemployment outcomes.
    ''')
    st.warning('''
    - Higher student debt does not always lead to higher earnings after graduation.
    - Debt and career outcomes can vary significantly depending on location, school type, and field of study.
    ''')

with tab7:
    st.header("Conclusion")

    st.write("""
    The big takeaway is that student debt should not be evaluated on its own.
    A school or major may lead to higher debt, but the real question is what happens after graduation.
    Career outcomes, salary potential, unemployment rates, school type, and geographic location all influence the long-term value of a college education.
    """)

    st.write("""
    Our final message is simple: students should not only ask, "How much will college cost?"
    They should also ask, "What opportunities might this choice create after graduation?"
    """)

    img1, img2, img3, img4, img5 = st.columns(5)

    with img1:
        if os.path.exists("graduation.png"):
            st.image("graduation.png", width=120)

    with img2:
        if os.path.exists("debt.png"):
            st.image("debt.png", width=120)

    with img3:
        if os.path.exists("salary.png"):
            st.image("salary.png", width=120)

    with img4:
        if os.path.exists("career.png"):
            st.image("career.png", width=120)

    with img5:
        if os.path.exists("college.png"):
            st.image("college.png", width=120)

    st.caption("""
    This dashbaord demonstrates how data can help students make more informed financial and educational decisions.
    """)
