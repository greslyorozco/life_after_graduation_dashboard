import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


st.title("Life After Graduation")
st.write("This dashboard explores student debt, salary, and employment outcomes after college.")


st.header("Project Questions")
st.write("""
1.Is student debt rising over time?
2.How does debt vary by state?
3.What is the link between debt and income?
4.Does more debt actually mean more pay?
5.How does debt impact finding a job?
6.How does Cost of Living change the story?
7.Public vs. Private: which pays off better?
""")
