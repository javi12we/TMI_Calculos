import streamlit as st
import math
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from services.ecuaciones_k1 import (
    calcular_tabla_k1,
    graficar_bottom_up,
    graficar_top_down
)

def show():

    # CSS personalizado para el fondo
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("https://files.rcnradio.com/public/styles/sitemap_seo/public/2019-12/whatsapp_image_2019-12-19_at_1.29.22_pm_0.jpeg?VersionId=_u0aREPgq2e77kVoxkCRGmJ5flCV6H1v&itok=d9L30kt3");
        background-size: cover;
        background-position: top left;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    '''
    # Título principal
    st.title("Análisis de Resistencia de Pavimentos - Cálculo de Ecuaciones K1")
    st.write("""
    Esta aplicación calcula el módulo de resiliencia y la vida útil de pavimentos flexibles utilizando los enfoques
    **Bottom-Up** (daño desde la base) y **Top-Down** (daño desde la superficie). Introduzca los parámetros necesarios
    en el formulario y obtendrá los resultados en forma de tabla y gráficas interactivas.
    """)
    
    # Incrustar el CSS en la aplicación
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
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
            <li>Ingrese los datos de entrada en el formulario con:
                <ul>
                    <li>Módulo elástico del material (E) [MPa]</li>
                    <li>Volumen de vacíos del agregado mineral (Vd) [%]</li>
                    <li>Volumen de vacíos de aire (Va) [%]</li>
                    <li>Deformación permisible de tracción (εt) [%]</li>
                </ul>
            </li>
            <li>Presione el botón "Calcular" para generar los resultados.</li>
            <li>Los resultados determinan la rigidez inicial del material del pavimento, clave para modelar su capacidad de resistir cargas y deformaciones bajo condiciones específicas..</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)
    # Incrustar el CSS en la aplicación
    st.markdown(texto_color, unsafe_allow_html=True)
    st.markdown('<p class="custom-text">Edite los valores en el formulario:</p>', unsafe_allow_html=True)
    
    # Formulario de entrada
    st.header("Parámetros de entrada")
    st.write("""
    A continuación, ingrese los valores para las propiedades del pavimento y las condiciones de carga:
    """)

    with st.form("parametros_form_k"):
        # Campos de entrada con descripciones
        E = st.number_input(
            "Módulo elástico del material (E) [MPa]:", 
            value=1500, 
            min_value=0, 
            help="Rigidez del material del pavimento en megapascales (MPa)."
        )
        Vd = st.number_input(
            "Volumen de vacíos del agregado mineral (Vd) [%]:", 
            value=11, 
            help="Porcentaje del volumen total ocupado por vacíos en el agregado mineral."
        )
        Va = st.number_input(
            "Volumen de vacíos de aire (Va) [%]:", 
            value=5, 
            help="Porcentaje del volumen total ocupado por vacíos de aire en la mezcla asfáltica."
        )
        εt = st.number_input(
            "Deformación permisible de tracción (εt) [%]:", 
            value=1, 
            min_value=1, 
            help="Deformación máxima permitida antes de que ocurra fatiga en el pavimento."
        )
        
        # Botón para enviar el formulario
        submit_button = st.form_submit_button(label="Calcular")
        
    if submit_button:
        # Cálculo del coeficiente C
        C = 10 ** (4.84 * (Vd / (Vd + Va) - 0.69))

        # Sección de resultados
        st.header("Resultados del cálculo")
        st.write("""
        A continuación se muestra la tabla con los valores calculados del módulo de resiliencia (K1) y la
        vida útil del pavimento (Nf) para ambos enfoques (Bottom-Up y Top-Down).
        """)

        # Tabla de resultados
        st.write("### Tabla de Resultados:")
        df_tabla_k1 = calcular_tabla_k1(C, εt, E)
        st.dataframe(df_tabla_k1, height=460)

        # Gráficas de resultados
        st.subheader("Gráfica Bottom-Up")
        st.write("""
        Esta gráfica muestra la relación inversa entre el módulo de resiliencia \(1/k1\) y el espesor del pavimento 
        (\(hc\)) desde el enfoque Bottom-Up (fallas iniciadas desde la base).
        """)
        graficar_bottom_up(df_tabla_k1)

        st.subheader("Gráfica Top-Down")
        st.write("""
        Esta gráfica representa la relación inversa entre el módulo de resiliencia \(1/k1\) y el espesor del pavimento
        (\(hc\)) desde el enfoque Top-Down (fallas iniciadas desde la superficie).
        """)
        graficar_top_down(df_tabla_k1)
