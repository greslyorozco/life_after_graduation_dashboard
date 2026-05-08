import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import os
import zipfile


st.set_page_config(page_title="Life After Graduation Dashboard", layout="wide")

sns.set_theme(style="whitegrid")

school_colors = ["gold", "lightpink", "steelblue"]
mixed_colors = ["lightpink", "orange", "gold", "lightblue", "seagreen", "steelblue"]


def find_file(folder_name, file_name):
    folder_path = folder_name + "/" + file_name
    if os.path.exists(folder_path):
        return folder_path
    if os.path.exists(file_name):
        return file_name
    return folder_path


def read_scorecard_zip(file_name):
    file_path = find_file("Data", file_name)

    if file_path.endswith(".zip"):
        with zipfile.ZipFile(file_path) as zipped_file:
            csv_files = []

            for name in zipped_file.namelist():
                if name.endswith(".csv") and "__MACOSX" not in name:
                    csv_files.append(name)

            with zipped_file.open(csv_files[0]) as csv_file:
                return pd.read_csv(csv_file, low_memory=False)

    return pd.read_csv(file_path, low_memory=False)


def image_file(file_name):
    return find_file("Images", file_name)


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("Life After Graduation")
st.sidebar.write("Student Debt and Post College Outcomes")

if os.path.exists(image_file("graduation.png")):
    st.sidebar.image(image_file("graduation.png"), width=170)

st.sidebar.success("Use the filters below to explore the story.")

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


# -----------------------------
# DATA
# -----------------------------

scorecard_df = read_scorecard_zip("Most-Recent-Cohorts-Institution 3.csv.zip")
majors_df = pd.read_csv(find_file("Data", "sample_recent_grads.csv"))

loan_state_df = None
loan_state_file = find_file("Data", "student-loan-by-state.xlsx")
if os.path.exists(loan_state_file):
    loan_state_df = pd.read_excel(loan_state_file)


# -----------------------------
# CLEANING
# -----------------------------

scorecard_df["DEBT_MDN"] = scorecard_df["DEBT_MDN"].replace("PrivacySuppressed", np.nan)
scorecard_df["DEBT_MDN"] = pd.to_numeric(scorecard_df["DEBT_MDN"], errors="coerce")

if "MD_EARN_WNE_P10" in scorecard_df.columns:
    scorecard_df["MD_EARN_WNE_P10"] = scorecard_df["MD_EARN_WNE_P10"].replace("PrivacySuppressed", np.nan)
    scorecard_df["MD_EARN_WNE_P10"] = pd.to_numeric(scorecard_df["MD_EARN_WNE_P10"], errors="coerce")

scorecard_df["CONTROL"] = pd.to_numeric(scorecard_df["CONTROL"], errors="coerce")

scorecard_df["School Type"] = scorecard_df["CONTROL"].map({
    1: "Public",
    2: "Private nonprofit",
    3: "Private for profit"
})

scorecard_df = scorecard_df.dropna(subset=["DEBT_MDN"])
scorecard_df = scorecard_df.dropna(subset=["School Type"])

majors_df["Median"] = pd.to_numeric(majors_df["Median"], errors="coerce")
majors_df["Unemployment_rate"] = pd.to_numeric(majors_df["Unemployment_rate"], errors="coerce")
majors_df["Total"] = pd.to_numeric(majors_df["Total"], errors="coerce")
majors_df["Employed"] = pd.to_numeric(majors_df["Employed"], errors="coerce")
majors_df["College_jobs"] = pd.to_numeric(majors_df["College_jobs"], errors="coerce")
majors_df["Low_wage_jobs"] = pd.to_numeric(majors_df["Low_wage_jobs"], errors="coerce")

majors_df = majors_df.dropna(subset=["Median", "Unemployment_rate"])
majors_df["Employment Rate"] = 1 - majors_df["Unemployment_rate"]
majors_df["College Job Share"] = np.where(
    majors_df["Employed"] > 0,
    majors_df["College_jobs"] / majors_df["Employed"],
    np.nan
)

if "MD_EARN_WNE_P10" in scorecard_df.columns:
    scorecard_df["Debt Compared With Earnings"] = scorecard_df["DEBT_MDN"] / scorecard_df["MD_EARN_WNE_P10"]


# -----------------------------
# FILTERS
# -----------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

school_options = scorecard_df["School Type"].dropna().unique()

selected_school_types = st.sidebar.multiselect(
    "School type",
    school_options,
    default=school_options
)

state_options = sorted(scorecard_df["STABBR"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "State",
    state_options,
    default=[]
)

major_categories = sorted(majors_df["Major_category"].dropna().unique())

selected_major_category = st.sidebar.selectbox(
    "Major category",
    major_categories
)

scorecard_filtered = scorecard_df.loc[
    scorecard_df["School Type"].isin(selected_school_types)
]

if selected_states:
    scorecard_filtered = scorecard_filtered.loc[
        scorecard_filtered["STABBR"].isin(selected_states)
    ]

majors_filtered = majors_df.loc[
    majors_df["Major_category"] == selected_major_category
]


# -----------------------------
# TITLE AREA
# -----------------------------

col_title, col_image = st.columns([2, 1])

with col_title:
    st.title("Life After Graduation")
    st.subheader("The Impact of Student Debt on Earnings and Employment")

    st.write("""
    College can open doors, but it can also leave students with debt.
    This dashboard looks at both sides of that story.
    """)

    st.info("""
    Simple idea: we compare what students may owe with what they may earn,
    where they study, what they major in, and how likely they are to find work.
    """)

with col_image:
    if os.path.exists(image_file("college.png")):
        st.image(image_file("college.png"), width=330)
    elif os.path.exists(image_file("graduation.png")):
        st.image(image_file("graduation.png"), width=330)

st.markdown("---")


# -----------------------------
# QUICK NUMBERS
# -----------------------------

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("Schools in View", scorecard_filtered["INSTNM"].nunique())

with metric2:
    st.metric("States in View", scorecard_filtered["STABBR"].nunique())

with metric3:
    st.metric("Median Student Debt", "$" + str(round(scorecard_filtered["DEBT_MDN"].median(), 0)))

with metric4:
    st.metric("Selected Major Group", selected_major_category)

st.markdown("---")


# -----------------------------
# TABS
# -----------------------------

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
    Our project asks one main question:
    after students borrow money for college, what happens next?
    """)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if os.path.exists(image_file("debt.png")):
            st.image(image_file("debt.png"), width=120)
        st.subheader("Debt")
        st.write("This is the money students may owe after college.")

    with col_b:
        if os.path.exists(image_file("salary.png")):
            st.image(image_file("salary.png"), width=120)
        st.subheader("Salary")
        st.write("This shows how much graduates may earn after college.")

    with col_c:
        if os.path.exists(image_file("career.png")):
            st.image(image_file("career.png"), width=120)
        st.subheader("Jobs")
        st.write("This shows whether graduates are finding work.")

    st.markdown("---")

    st.success("""
    The story is not only about price. A school or major can cost more,
    but we also need to ask what students may get after graduation.
    """)

    with st.expander("Click to see our motivation"):
        st.write("""
        We chose this topic because student debt affects many college students.
        Tuition is expensive, and borrowing money can shape a person's future.
        Since we are students too, this topic feels personal and important.
        """)

    with st.expander("Click to see our project questions"):
        st.write("""
        1. Is student debt rising over time?
        2. How does debt vary by state?
        3. What is the link between debt and income?
        4. Does more debt lead to more pay?
        5. How does debt connect to job outcomes?
        6. How does location change the story?
        7. Which school type seems to pay off better?
        """)

    with st.expander("Click to see the data story in one sentence"):
        st.write("""
        We are comparing the cost of college with what happens after graduation.
        The best college choice is not just the cheapest choice.
        It is the choice where cost, pay, jobs, major, school type, and location make sense together.
        """)


with tab2:
    st.header("Major Outcomes")

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
            This chart shows the majors in this group that usually earn the most money.
            Higher bars mean higher typical pay after graduation.
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
            This chart checks job risk for the same majors.
            A major can pay well, but students also want to know if people in that major are finding jobs.
            """)

    st.markdown("---")

    st.subheader("Salary Compared With Unemployment")

    fig = px.scatter(
        majors_filtered,
        x="Unemployment_rate",
        y="Median",
        size="Total",
        color="Major",
        hover_name="Major",
        title="Salary and Job Risk by Major",
        template="plotly_white"
    )

    fig.update_layout(
        title_font_size=22,
        xaxis_title="Unemployment Rate",
        yaxis_title="Median Salary",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Click to interpret the major scatter plot"):
        st.write("""
        Each bubble is a major.
        Higher bubbles mean more pay.
        Bubbles farther left mean less unemployment.
        The strongest majors are usually high on the chart and closer to the left side.
        """)


with tab3:
    st.header("Student Debt")

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
        This chart compares debt across public, private nonprofit, and private for profit schools.
        The line inside each box is the middle debt value.
        The dots show schools with much higher or much lower debt.
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
        It helps us see that location can change the college debt story.
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
            hover_data=["STABBR"],
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
            Each dot is one college.
            Dots on the right have more student debt.
            Dots near the top have higher earnings.
            We are looking to see if higher debt also comes with higher pay.
            If the dots look scattered, then debt alone does not explain earnings.
            """)

        st.markdown("---")

        st.subheader("Debt and Earnings by School Type")

        school_money = scorecard_filtered.groupby("School Type")[["DEBT_MDN", "MD_EARN_WNE_P10"]].median()
        school_money = school_money.reset_index()

        fig = px.bar(
            school_money,
            x="School Type",
            y=["DEBT_MDN", "MD_EARN_WNE_P10"],
            barmode="group",
            title="Median Debt and Median Earnings by School Type",
            template="plotly_white",
            color_discrete_sequence=["orange", "steelblue"]
        )

        fig.update_layout(
            title_font_size=22,
            xaxis_title="School Type",
            yaxis_title="Dollars",
            legend_title="Measure"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Click to interpret the grouped bar chart"):
            st.write("""
            This chart puts debt and earnings next to each other.
            It helps us compare what students owe with what graduates may earn.
            A school type looks stronger when earnings are high compared with debt.
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Scorecard Rows", scorecard_df.shape[0])

    with col2:
        st.metric("Scorecard Columns", scorecard_df.shape[1])

    with col3:
        st.metric("Major Rows", majors_df.shape[0])

    with col4:
        st.metric("Major Columns", majors_df.shape[1])

    with st.expander("Click to see Scorecard columns"):
        st.write(scorecard_df.columns.tolist())

    with st.expander("Click to see missing values in key columns"):
        st.write(scorecard_df[["INSTNM", "STABBR", "CONTROL", "DEBT_MDN", "MD_EARN_WNE_P10"]].isna().sum())

    with st.expander("Click to see data sources"):
        st.write("""
        College Scorecard data gives school names, states, school type, student debt, and earnings.
        Recent graduates data gives major names, major groups, salaries, unemployment, and job information.
        Student loan by state data gives extra state level context.
        """)

    st.subheader("Cleaning Steps")

    st.write("""
    1. Loaded the College Scorecard dataset.
    2. Loaded the major outcomes dataset.
    3. Loaded the student loan by state file when available.
    4. Changed student debt values into numbers.
    5. Changed earnings values into numbers.
    6. Removed rows that did not have median debt.
    7. Created a School Type column from the CONTROL column.
    8. Used groupby to summarize debt by school type and state.
    9. Used Plotly charts to make the dashboard interactive.
    """)

    st.info("""
    The proposal included cost of living as a future question.
    The files in this version focus on debt, earnings, school type, major, job outcomes, and state.
    If a cost of living file is added later, it can be joined by state.
    """)


with tab6:
    st.header("Conclusion")

    st.success("""
    The main takeaway is simple:
    college is not only about how much it costs.
    Students also need to ask what happens after graduation.
    """)

    st.write("""
    A better choice is one where debt, salary, jobs, major, school type, and location make sense together.
    This dashboard helps compare those pieces side by side.
    """)

    st.write("""
    Our final message:
    do not only ask, "How much will college cost?"
    Also ask, "What opportunities might this choice create after graduation?"
    """)

    st.markdown("---")
    st.subheader("The Whole Story")

    img1, img2, img3, img4, img5 = st.columns(5)

    with img1:
        if os.path.exists(image_file("graduation.png")):
            st.image(image_file("graduation.png"), width=120)
            st.write("Graduation")

    with img2:
        if os.path.exists(image_file("debt.png")):
            st.image(image_file("debt.png"), width=120)
            st.write("Debt")

    with img3:
        if os.path.exists(image_file("salary.png")):
            st.image(image_file("salary.png"), width=120)
            st.write("Salary")

    with img4:
        if os.path.exists(image_file("career.png")):
            st.image(image_file("career.png"), width=120)
            st.write("Jobs")

    with img5:
        if os.path.exists(image_file("college.png")):
            st.image(image_file("college.png"), width=120)
            st.write("College Choice")



