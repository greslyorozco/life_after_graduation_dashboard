import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


st.title("Life After Graduation")

st.subheader("Student Debt, and After College Outcomes")

st.markdown('---')

st.write("""
This project explores whether student debt is balanced by salary, employment outcomes,
school type, and location after graduation.
""")

st.write("""
Our dashboard tells a data story about life after college. We compare the cost of college
with what happens after graduation, including income, unemployment, major choice, and
public versus private schools.
""")

st.markdown('---')

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Main Topic", "Student Debt")

with col2:
    st.metric("Outcome Focus", "Salary + Jobs")

with col3:
    st.metric("Dashboard Tool", "Streamlit")

st.markdown('---')

st.subheader("Presentation Roadmap")

st.write("""
1. Motivation  
2. Project goal  
3. Research questions  
4. Datasets  
5. Data cleaning and preprocessing  
6. Dashboard visualizations  
7. Main insights  
8. Team contributions and conclusion  
""")
