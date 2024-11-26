import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from services.modelos_fatiga import calcular_modelos_microstrain, graficar_modelos_fatiga, calcular_ni_transito_por_modelo

# Datos base
df_micro = pd.DataFrame({"ni_transito": [10000, 100000, 1000000, 10000000, 100000000, 1000000000]})

def show():
    if 'df_micro' not in st.session_state:
        st.session_state.df_micro = df_micro.copy()

    # Título principal
    st.title('MODELOS DE FATIGA')

    # Introducción
    st.write("""
    Analiza el comportamiento de mezclas asfálticas frente a fatiga mediante microdeformaciones (\(microstrain\)) y niveles de tránsito.
    """)

    # Tabla editable
    st.subheader("Niveles de Tránsito")
    gb = GridOptionsBuilder.from_dataframe(st.session_state.df_micro)
    gb.configure_default_column(editable=True)
    gridOptions = gb.build()
    grid_response = AgGrid(
        st.session_state.df_micro,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        theme='streamlit',
        height=210,
    )

    # Formulario de entrada
    with st.form("parametros_form"):
        modulo_mezcla = st.number_input("Módulo de la Mezcla (MPa)", value=4500, min_value=0)
        espesor_mezcla_asfaltica_cm = st.number_input("Espesor Mezcla Asfáltica (cm)", value=15, min_value=0)
        submit_button = st.form_submit_button("Calcular Modelos")

    if submit_button:
        # Actualizar DataFrame
        st.session_state.df_micro = pd.DataFrame(grid_response['data'])
        rigidez_convertida = 145 * modulo_mezcla
        espesor_pulgadas = espesor_mezcla_asfaltica_cm / 2.54
        factor_modelo = 10 ** (4.84 * (11 / (11 + 5) - 0.69))
        factor_resistencia = float(1 / (0.000398 + (0.003602 / (1 + np.exp(11.02 - 3.49 * espesor_pulgadas)))))

        # Cálculo de modelos microstrain
        df_microstrain = calcular_modelos_microstrain(
            ni_transito=st.session_state.df_micro['ni_transito'],
            modulo_mezcla=modulo_mezcla,
            rigidez_convertida=rigidez_convertida,
            factor_ajuste_modelo=factor_modelo,
            factor_ajuste_resistencia=factor_resistencia
        )

        # Resultados
        st.write("### Microstrain Calculado:")
        st.dataframe(df_microstrain.round(2))

        # Gráfica de modelos de fatiga
        st.subheader("Gráfica de Modelos de Fatiga")
        graficar_modelos_fatiga(df_microstrain)

        # Índices de fatiga por modelo
        st.subheader("Niveles de Tránsito por Modelo")
        df_ni_transito = calcular_ni_transito_por_modelo(
            df_microstrain_modelo=df_microstrain,
            modulo_mezcla=modulo_mezcla,
            factor_ajuste_modelo=factor_modelo,
            rigidez_convertida=rigidez_convertida,
            factor_ajuste_resistencia=factor_resistencia
        )
        st.dataframe(df_ni_transito.round(2))

        # Reiniciar
        if st.button("Limpiar datos"):
            st.rerun()