import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from services.modelos_fatiga import calcular_modelos_microstrain, graficar_modelos_fatiga, calcular_ni_transito_por_modelo


# Datos base
df_micro = pd.DataFrame(
    {
        "ni_transito": [
            10000,
            100000,
            1000000,
            10000000,
            100000000,
            1000000000,
        ]
    }
)

def show():
    # CSS personalizado para el fondo
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("https://c.pxhere.com/photos/c9/b6/asphalt_dark_lights_long_exposure_night_road_street-1145405.jpg!d");
        background-size: cover;
        background-position: top left;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    '''
    
    if 'df_micro' not in st.session_state:
        st.session_state.df_micro = df_micro.copy()
    
    st.title('MODELOS DE FATIGA')
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
    st.markdown('<p class="custom-text">Edite los valores en el formulario y la tabla (ni) para calcular:</p>', unsafe_allow_html=True)
    st.markdown("### Tabla editable de los niveles de transito")
    st.markdown("Puede editar los niveles de transito en la siguiente tabla:")
    
    gb = GridOptionsBuilder.from_dataframe(st.session_state.df_micro)
    gb.configure_default_column(editable=True)  # Permitir edición en la tabla
    
    # Configuración para ajustar la altura de la tabla al contenido
    gb.configure_grid_options(domLayout='normal')
    
    gridOptions = gb.build()

    grid_response = AgGrid(
        st.session_state.df_micro,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        theme='streamlit',
        height=210,
    )
    st.markdown("### Formulario de datos de entrada")
    st.markdown("Puede editar el Módulo de la Mezcla y Espesor de la Mezcla Asfaltica (cm) para calcular: ")
    with st.form("parametros_form"):
        modulo_mezcla = st.number_input("Módulo de la Mezcla", value=4500, min_value=0)
        espesor_mezcla_asfaltica_cm = st.number_input("Espesor de la Mezcla Asfaltica (cm)", value=15, min_value=0)
        
        # Botón para enviar el formulario
        submit_button = st.form_submit_button(label="Calcular Modelos")

    # Si el botón del formulario es presionado
    if submit_button:
        # Actualizar el DataFrame editado en session_state
        st.session_state.df_micro = pd.DataFrame(grid_response['data'])
        
        rigidez_convertida = 145 * modulo_mezcla
        espesor_mezcla_pulgadas = espesor_mezcla_asfaltica_cm / 2.54
        factor_ajuste_modelo = 10 ** (4.84 * (11 / (11 + 5) - 0.69))
        factor_ajuste_resistencia = float(1 / (0.000398 + (0.003602 / (1 + np.exp(11.02 - 3.49 * espesor_mezcla_pulgadas)))))
        
        # Llamar la función que calcula los modelos microstrain
        df_microstrain_modelo = calcular_modelos_microstrain(
            ni_transito=st.session_state.df_micro['ni_transito'],
            modulo_mezcla=modulo_mezcla,
            rigidez_convertida=rigidez_convertida,
            factor_ajuste_modelo=factor_ajuste_modelo,
            factor_ajuste_resistencia=factor_ajuste_resistencia
        )
        
        # Mostrar el DataFrame resultante
        st.write("### Microstrain Del Modelo Calculado:")
        st.dataframe(df_microstrain_modelo.round(2))
        
        graficar_modelos_fatiga(df_microstrain_modelo)
        
        st.write("### Niveles de Transito por Modelo Calculado:")
        df_indice_fatiga_modelo = calcular_ni_transito_por_modelo(
            df_microstrain_modelo=df_microstrain_modelo,
            modulo_mezcla=modulo_mezcla,
            factor_ajuste_modelo=factor_ajuste_modelo,
            rigidez_convertida=rigidez_convertida,
            factor_ajuste_resistencia=factor_ajuste_resistencia
        )
        
        st.dataframe(df_indice_fatiga_modelo.round(2))
        
        # Botón para reiniciar la página
        if st.button("Limpiar datos"):
            st.rerun()