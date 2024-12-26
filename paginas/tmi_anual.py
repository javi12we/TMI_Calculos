import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math as math

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
        "T(°C)": [ # Temperatura promedio mensual
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
            25.5866666666667
        ],
        "Pi(mm)": [ # Precipitación mensual
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
            240.8266666666670
        ],
    }
)

# Funciones de cálculo
def calcular_parametros_wpi(wPI):
    a_wpi = 0.00364 * (wPI ** 3.35) + 4 * wPI + 11
    c_wpi = 0.0514 * (wPI ** 0.465) + 0.5
    b_wpi = c_wpi * (-2.313 * (wPI ** 0.14) + 5)
    hr_wpi = a_wpi * 32.44 * math.exp(0.0186 * wPI)
    Sopt = (6.752 * (wPI ** 0.147) + 78) / 100
    return a_wpi, b_wpi, c_wpi, hr_wpi, Sopt

def calcular_parametros_d60(D60):
    a_D60 = 0.8627 * (D60 ** -0.751)
    c_D60 = 0.1772 * math.log(D60) + 0.7734
    hr_D60 = a_D60 / (D60 + 0.00097)
    return a_D60, c_D60, hr_D60

def show():
    # CSS personalizado para el fondo
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("https://chm.es/wp-content/uploads/2023/10/firmes_0007_IMG_0235.jpg");
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
                    <li>WPI</li>
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
    st.title("Indices TMI Anuales")
    # Incrustar el CSS en la aplicación
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.markdown("### Tabla editable TMI")
    st.markdown("Puede editar los valores de temperatura mensual, dias y el Pi(mm) en la siguiente tabla:")
    

    