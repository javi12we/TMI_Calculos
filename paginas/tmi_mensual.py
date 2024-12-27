import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math as math
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from services.calculos_tmi import calcular_tmi_suelos_finos, calcular_tmi_suelos_gruesos

# Datos de TMI  de entrada
TMI_tabla = pd.DataFrame(
    {
        "mes": [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ],
        "T(°C)": [  # Temperatura promedio mensual
            25.9866666666667,
            26.3933333333333,
            26.2400000000000,
            26.0733333333333,
            26.0800000000000,
            26.0400000000000,
            26.7533333333333,
            27.7266666666667,
            27.4933333333333,
            26.6466666666667,
            25.7200000000000,
            25.5866666666667,
        ],
        "Pi(mm)": [  # Precipitación mensual
            182.8800000000000,
            159.9800000000000,
            216.3200000000000,
            192.8000000000000,
            164.5933333333330,
            75.4333333333333,
            38.8933333333333,
            32.4400000000000,
            133.1666666666670,
            229.6666666666670,
            286.9200000000000,
            240.8266666666670,
        ],
        "d": [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
    }
)

def show():
    if 'TMI_tabla' not in st.session_state:
        st.session_state.TMI_tabla = TMI_tabla.copy()
    
    # CSS personalizado para el fondo
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("https://files.rcnradio.com/public/2021-09/whatsapp_image_2021-09-06_at_10.45.13_am_0.jpeg?VersionId=NwszBMNbYjJ7P_ihws.xyjBuD9OHiMFe");
        background-size: cover;
        background-position: top left;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    '''
    # Estilo para el mensaje de texto y la viñeta
    texto_color = '''
    <style>
    .custom-text {
        color: #ffffff; /* Blanco */
        font-size: 20px;
        font-weight: bold;
        font-family: 'Roboto', sans-serif; /* Tipo de letra */
        padding: 10px;
        border-radius: 10px;
        background-color: #4f4f4f; /* Gris oscuro */
        border: 2px solid #000000; /* Borde negro */
        max-width: 600px; /* Ancho máximo */
    }
    </style>
    '''
    st.title("Indices TMI Mensuales")
    # Viñeta del instructivo
    st.markdown('''
    <div class="custom-text">
        <h3>Instructivo</h3>
        <ol>
            <li>Modifique los valores de entrada de la tabla TMI por segun su:
                <ul>
                    <li>Temperatura t(°C)</li>
                    <li>Pi(mm)</li>
                    <li>d</li>
                </ul>
            </li>
            <li>Modifique los valores de entrada WPI para el calculo de TMI para suelos Finos y Gruesos :
                <ul>
                    <li>P200</li>
                    <li>PI</li>
                </ul>
            </li>
            <li>Modifique los valores de entrada D60 para el calculo de TMI para suelos Finos y Gruesos :
                <ul>
                    <li>D60</li>
                    <li>b D60</li>
                </ul>
            <li>Modifique los valores de entrada (Coeficientes):
                <ul>
                    <li>Alpha α</li>
                    <li>Beta β</li>
                    <li>Gamma γ</li>
                    <li>Delta δ</li>
                </ul>
            </li>
    </div>
    ''', unsafe_allow_html=True)
    # Incrustar el CSS en la aplicación
    st.markdown(texto_color, unsafe_allow_html=True)
    # Incrustar el CSS en la aplicación
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.markdown("### Tabla editable TMI")
    st.markdown("Puede editar los valores de temperatura mensual, dias(d) y el Pi(mm) en la siguiente tabla:")
    
    # Tabla editable
    st.subheader("Niveles de Tránsito")
    gb = GridOptionsBuilder.from_dataframe(st.session_state.TMI_tabla)
    gb.configure_default_column(editable=True)
    gridOptions = gb.build()
    grid_response = AgGrid(
        st.session_state.TMI_tabla,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        theme='streamlit'
    )
    
    st.markdown("### Formulario de datos de entrada")
    with st.form("parametros_form"):
        p200 = st.number_input("P200", value=80)
        PI = st.number_input("PI", value=25)
        D60 = st.number_input("D60", value=0.1)
        b_D60 = st.number_input("b D60", value=7.5)
        
        # Nuevos campos
        alpha = st.number_input("Alpha", value=0.3000, format="%.4f")
        beta = st.number_input("Beta", value=921.4080, format="%.4f")
        gamma = st.number_input("Gamma", value=150.9908, format="%.4f")
        delta = st.number_input("Delta", value=29.8440, format="%.4f")
        
        submit_button = st.form_submit_button("Calcular Indices TMI")
        
    if submit_button:
        # Actualizar DataFrame
        st.session_state.TMI_tabla = pd.DataFrame(grid_response['data'])
        
        wPI = PI * p200 / 100
        a_wpi = 0.00364 * (wPI ** 3.35) + 4 * wPI + 11
        c_wpi = 0.0514 * (wPI ** 0.465) + 0.5
        b_wpi = c_wpi * (-2.313 * (wPI ** 0.14) + 5)
        hr_wpi = a_wpi * 32.44 * math.exp(0.0186 * wPI)
        Sopt = (6.752 * (wPI ** 0.147) + 78) / 100
    
        a_D60 = 0.8627 * (D60 ** -0.751)
        c_D60 = 0.1772 * math.log(D60) + 0.7734
        hr_D60 = a_D60 / (D60 + 0.00097)
        
        # Calcular columnas adicionales para TMI
        st.session_state.TMI_tabla["i"] = (st.session_state.TMI_tabla["T(°C)"] / 5) ** 1.514
        suma_i = st.session_state.TMI_tabla["i"].sum()
        Alfa_promedio = (
            0.000000675 * suma_i**3
            - 0.0000771 * suma_i**2
            + 0.01792 * suma_i
            + 0.49239
        )
        st.session_state.TMI_tabla["ETPsc(mm/mes)"] = 16 * (
            10 * st.session_state.TMI_tabla["T(°C)"] / suma_i
        ) ** Alfa_promedio
        st.session_state.TMI_tabla["ETPcrr(mm/mes)"] = (
            st.session_state.TMI_tabla["ETPsc(mm/mes)"]
            * st.session_state.TMI_tabla["d"]
            / 30
        )
        st.session_state.TMI_tabla["TMI (1)"] = 100 * (
            st.session_state.TMI_tabla["Pi(mm)"]
            / st.session_state.TMI_tabla["ETPcrr(mm/mes)"]
            - 1
        )
        st.session_state.TMI_tabla["TMI (2)"] = 75 * (
            st.session_state.TMI_tabla["Pi(mm)"]
            / st.session_state.TMI_tabla["ETPcrr(mm/mes)"]
            - 1
        ) + 10
        
        # Mostrar el DataFrame actualizado
        st.markdown("### TMI Mensual")
        st.dataframe(st.session_state.TMI_tabla, use_container_width=True, height=460)
        
        TMI_tabla_finos = calcular_tmi_suelos_finos(
            st.session_state.TMI_tabla,
            alpha,
            beta,
            gamma,
            delta,
            hr_wpi,
            a_wpi,
            b_wpi,
            c_wpi,
            Sopt,
        )
        
        TMI_tabla_gruesos = calcular_tmi_suelos_gruesos(
            st.session_state.TMI_tabla,
            alpha,
            beta,
            gamma,
            delta,
            hr_D60,
            a_D60,
            b_D60,
            c_D60,
            Sopt,
        )
        
        st.markdown("### TMI Suelos Finos")
        st.dataframe(TMI_tabla_finos, use_container_width=True, height=460)
        
        st.markdown("### TMI Suelos Gruesos")
        st.dataframe(TMI_tabla_gruesos, use_container_width=True, height=460)