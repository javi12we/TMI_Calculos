import streamlit as st
import math

def show():
    st.title("ECUACIONES K1")
    E = st.number_input("E", value=1500, min_value=0)
    Vd = st.number_input("Vd", value=11)
    Va = st.number_input("Va", value=5)
    C = 10**(4.84*(Vd/(Vd+Va)-0.69))
    hcm = st.number_input("hcm", value=10, min_value=0)
    hin = hcm/2.54
    εt = st.number_input("εt", value=1)
    k = 1 / (0.000398 + (0.003602 / (1 + math.exp(11.02 - 3.49 * hin))))
    
    