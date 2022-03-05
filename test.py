import streamlit as st
import pandas as pd
import numpy as np

st.title("Test app")

st.markdown("Test")

st.header("Tabla")
dataframe = np.random.randn(10, 20)
st.dataframe(dataframe)