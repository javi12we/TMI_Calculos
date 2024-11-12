import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px

# Datos base para WPI
df_WPI_base = pd.DataFrame(
    {
        "WPI": [
            0.1,
            0.9,
            3,
            5,
            10,
            15,
            20,
            30,
            40,
            50,
        ]
    }
)

# Función para calcular a, b, c y hr en función de WPI
def calcular_parametros(df):
    df["a"] = (0.00364 * df["WPI"] ** 3.35 + 4 * df["WPI"] + 11)
    df["c"] = 0.0514 * df["WPI"] ** 0.465 + 0.5
    df["b"] = df["c"] * (-2.313 * df["WPI"] ** 0.14 + 5)
    df["hr"] = (0.00364 * df["WPI"] ** 3.35 + 4 * df["WPI"] + 11) * 32.44 * np.exp(0.0186 * df["WPI"])
    return df

# Función para calcular C(h)
def calcular_ch(df_ch, hr_value):
    return df_ch["h"].apply(lambda h: 1 - np.log(1 + h / hr_value) / np.log(1 + 1000000 / hr_value))

# Función para calcular S
def calcular_s(df_ch, a_value, b_value, c_value, ch_values):
    return ch_values * (1 / (np.log(np.exp(1) + (df_ch["h"] / a_value)**b_value)**c_value))

def format_df_to_string(df):
    """Convertir los valores flotantes en el DataFrame a cadenas con 10 decimales, solo si no son enteros."""
    return df.applymap(lambda x: f"{x:.10f}".rstrip('0').rstrip('.') if isinstance(x, float) else x)

def show():
    # Estado inicial de la aplicación: cargar datos base de WPI si no se han cargado
    if 'df_WPI' not in st.session_state:
        st.session_state.df_WPI = df_WPI_base.copy()

    st.title("SWCC - Curva Característica de Retención de Agua en el Suelo")
    
    # Mostrar tabla editable de WPI
    st.markdown("### Tabla editable de WPI")
    st.markdown("Puede editar los valores de WPI en la siguiente tabla:")
    gb = GridOptionsBuilder.from_dataframe(st.session_state.df_WPI)
    gb.configure_default_column(editable=True)  # Permitir edición en la tabla
    gridOptions = gb.build()
    gridOptions["domLayout"] = 'autoHeight' 

    grid_response = AgGrid(
        st.session_state.df_WPI,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        theme='streamlit',
    )

    # Botón para calcular
    if st.button("Calcular Parámetros y Gráfico"):
        # Actualizar el DataFrame editado en session_state
        st.session_state.df_WPI = pd.DataFrame(grid_response['data'])
        
        # Crear una copia de la tabla WPI con los parámetros calculados
        st.session_state.df_WPI_parametros = calcular_parametros(st.session_state.df_WPI.copy())

        # Mostrar la tabla con los parámetros calculados, formateada para mostrar todos los decimales
        st.markdown("### Tabla con parámetros calculados")
        st.write(format_df_to_string(st.session_state.df_WPI_parametros))

        # Crear tabla de C(h) y S en función de h para cada WPI
        h_values = [0.1, 1, 10, 100, 1000, 10000, 100000, 1000000]
        df_CH = pd.DataFrame({"h": h_values})
        df_S = df_CH[["h"]].copy()

        # Calcular C(h) y S para cada WPI y agregar columnas en df_CH y df_S
        for index, row in st.session_state.df_WPI_parametros.iterrows():
            hr_value = row["hr"]
            a_value = row["a"]
            b_value = row["b"]
            c_value = row["c"]
            
            # Calcular C(h) y S para cada valor de h
            ch_values = calcular_ch(df_CH, hr_value)
            s_values = calcular_s(df_CH, a_value, b_value, c_value, ch_values)
            
            # Agregar columnas al DataFrame
            df_CH[f"C(h)_WPI_{row['WPI']}"] = ch_values
            df_S[f"S_WPI_{row['WPI']}"] = s_values

        # Convertir df_S a formato largo para el gráfico
        df_long = df_S.melt(id_vars=['h'], var_name='WPI', value_name='Grado de saturación')
        df_long.rename(columns={'h': 'Succión (kPa)'}, inplace=True)

        # Crear el gráfico
        fig = px.line(
            df_long,
            x="Succión (kPa)",
            y="Grado de saturación",
            color="WPI",
            log_x=True,
            title="Grado de Saturación vs Succión (kPa)"
        )

        # Personalizar el gráfico
        fig.update_layout(
            xaxis_title="Succión (kPa)",
            yaxis_title="Grado de saturación",
            legend_title="WPI",
            template="plotly_white"
        )

        # Mostrar el gráfico
        st.plotly_chart(fig)

        # Mostrar tablas de resultados con todos los decimales
        st.subheader("Tabla de C(h)")
        st.write(format_df_to_string(df_CH))

        st.subheader("Tabla de S")
        st.write(format_df_to_string(df_S))