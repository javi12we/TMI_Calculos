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
# Mostrar un fondo de pantalla para el aplicativo
import streamlit as st

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

# Incrustar el CSS en la aplicación
st.markdown(page_bg_img, unsafe_allow_html=True)


# Cargar y mostrar una imagen desde una URL
st.image("https://www.invias.gov.co/ambiental/img/logo_inv_letra_blanca.png", use_column_width=True)

# Mostrar la tabla interactiva editable con su titulo
import streamlit as st
st.title("Cálculo de Índices TMI")
titulo_color = '''
<style>
h1 {
    color: #ff7700; /* Naranja llamativo */
    font-family: 'Futura', sans-serif; /* Tipo de letra Futura */
}
</style>
'''
st.markdown(titulo_color, unsafe_allow_html=True)

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
}
</style>
'''

st.markdown(texto_color, unsafe_allow_html=True)



color_subtitulo = '''
<style>
.custom-text {
    color: #ffffff; /* Blanco */
    font-size: 20px;
    font-weight: bold;
}
</style>
'''

# Incrustar el CSS en la aplicación
st.markdown(texto_color, unsafe_allow_html=True)
st.markdown('<p class="custom-text">Puede editar la tabla para calcular los valores:</p>', unsafe_allow_html=True)
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
    grados = st.number_input("Grados", value=0, min_value=0)
    minutos = st.number_input("Minutos", value=0,min_value=0)
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
    st.write("### Resultados:")
    st.dataframe(df_result)

    # Mostrar los resultados en forma de diccionario
    st.metric(label="Índice de humedad (Ih)", value=f"{resultados['Índice de humedad (Ih)']:.2f}")
    st.metric(label="Índice de aridez (Ia)", value=f"{resultados['Índice de aridez (Ia)']:.2f}")
    st.metric(label="Índice de Thornthwaite (Im)", value=f"{resultados['Índice de Thornthwaite (Im)']:.2f}")
    st.metric(label="Índice de Thornthwaite 1955", value=f"{resultados['Índice de Thornthwaite 1955']:.2f}")
    st.metric(label="Clasificación climática", value=resultados['Clasificación climática'])
    