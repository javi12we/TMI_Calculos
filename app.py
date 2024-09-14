import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from db.client import MongoDBConnection
from services.calculos_tmi import calcular_indices

mongo_connection = MongoDBConnection()
db = mongo_connection.get_database()

# Función para cargar los datos desde MongoDB
def cargar_datos_base():
    return pd.DataFrame(list(db['tmi_valores_mensuales'].find({}, {'_id': 0})))

def cargar_datos_n():
    return pd.DataFrame(list(db['n'].find({}, {'_id': 0})))

# Estado inicial de la aplicación: cargar datos desde MongoDB si no se han cargado
if 'df' not in st.session_state:
    st.session_state.df = cargar_datos_base()

if 'datos_n' not in st.session_state:
    st.session_state.datos_n = cargar_datos_n()

# Cargar y mostrar una imagen desde una URL
st.image("https://www.invias.gov.co/ambiental/img/logo_inv_letra_blanca.png", caption="Imagen desde una URL", use_column_width=True)

# Mostrar la tabla interactiva editable
st.title("Cálculo de Índices")

st.write("Edita el DataFrame antes de calcular los índices:")
gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
gb.configure_default_column(editable=True)  # Permitir edición en la tabla
gridOptions = gb.build()

grid_response = AgGrid(
    st.session_state.df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    theme='streamlit',  # Cambiar el tema si lo deseas
)

# Crear el formulario para los parámetros adicionales
with st.form("parametros_form"):
    grados = st.number_input("Grados ()", value=2)
    minutos = st.number_input("Minutos", value=26)
    segundos = st.number_input("Segundos", value=0)
    orientacion = st.selectbox("Orientación", ['norte', 'sur'], index=0)
    amax = st.number_input("Amax", value=100)

    # Botón para enviar el formulario
    submit_button = st.form_submit_button(label="Calcular índices")

# Si el botón del formulario es presionado
if submit_button:
    # Actualizar el DataFrame editado en session_state
    st.session_state.df = pd.DataFrame(grid_response['data'])
    
    # Llamar a la función calcular_indices con los parámetros y el DataFrame editado
    df_result, resultados = calcular_indices(
        datos_base=st.session_state.df,
        datos_n=st.session_state.datos_n,
        grados=grados,
        minutos=minutos,
        segundos=segundos,
        orientacion=orientacion,
        amax=amax
    )
    
    # Mostrar el DataFrame resultante
    st.write("Resultado del DataFrame:")
    st.dataframe(df_result)

    # Mostrar los resultados en forma de diccionario
    st.write("Resultados:")
    for key, value in resultados.items():
        st.write(f"{key}: {value}")