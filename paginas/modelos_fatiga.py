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
    
    if 'df_micro' not in st.session_state:
        st.session_state.df_micro = df_micro.copy()
    
    st.title('MODELOS DE FATIGA')
    
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
        st.dataframe(df_microstrain_modelo)
        
        graficar_modelos_fatiga(df_microstrain_modelo)
        
        st.write("### Niveles de Transito por Modelo Calculado:")
        df_indice_fatiga_modelo = calcular_ni_transito_por_modelo(
            df_microstrain_modelo=df_microstrain_modelo,
            modulo_mezcla=modulo_mezcla,
            factor_ajuste_modelo=factor_ajuste_modelo,
            rigidez_convertida=rigidez_convertida,
            factor_ajuste_resistencia=factor_ajuste_resistencia
        )
        
        st.dataframe(df_indice_fatiga_modelo)
        # Botón para reiniciar la página
        if st.button("Limpiar datos"):
            st.experimental_rerun()