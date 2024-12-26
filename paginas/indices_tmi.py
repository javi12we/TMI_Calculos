import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from db.client import MongoDBConnection
from services.calculos_tmi import calcular_indices

mongo_connection = MongoDBConnection()
db = mongo_connection.get_database()

# Lista de los meses en español en el orden correcto
meses_ordenados = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]

# Función para cargar y ordenar los datos por la columna "mes"
def cargar_datos_base():
    df_base = pd.DataFrame(list(db['tmi_valores_mensuales'].find({}, {'_id': 0})))
    df_base['mes'] = pd.Categorical(df_base['mes'], categories=meses_ordenados, ordered=True)
    return df_base.sort_values('mes')

def cargar_datos_n():
    return pd.DataFrame(list(db['n'].find({}, {'_id': 0})))

def show():

    # Estado inicial de la aplicación: cargar datos desde MongoDB si no se han cargado
    if 'df' not in st.session_state:
        st.session_state.df = cargar_datos_base()

    if 'datos_n' not in st.session_state:
        st.session_state.datos_n = cargar_datos_n()
    
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

    # Incrustar el CSS en la aplicación
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.title("ÍNDICES TMI")

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
    # Incrustar el CSS en la aplicación
    st.markdown(texto_color, unsafe_allow_html=True)

    # Viñeta del instructivo
    st.markdown('''
    <div class="custom-text">
        <h3>Instructivo</h3>
        <ol>
            <li>Ingrese los datos de entrada en la tabla TMI con las columnas:
                <ul>
                    <li>Mes</li>
                    <li>Temperatura</li>
                    <li>Precipitación</li>
                    <li>d</li>
                </ul>
            </li>
            <li>Ingrese los datos de entrada en el formulario con:
                <ul>
                    <li>Grados</li>
                    <li>Minutos</li>
                    <li>Segundos</li>
                    <li>Orientación (Norte o Sur)</li>
                    <li>Amax</li>
                </ul>
            </li>
            <li>Presione el botón "Calcular índices" para generar los resultados.</li>
            <li>Los resultados incluirán índices climáticos y su clasificación.</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)

    # Incrustar el CSS en la aplicación
    st.markdown("### Tabla de datos de entrada TMI")
    st.markdown("Puede editar el mes, la temperatiura, la precipitación y el dia (d): ")
    gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
    gb.configure_default_column(editable=True)  # Permitir edición en la tabla
    gridOptions = gb.build()

    grid_response = AgGrid(
        st.session_state.df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        theme='streamlit',  # Cambiar el tema si lo deseas
    )
    st.markdown("### Formulario de datos de entrada TMI")
    st.markdown("Adicionalmente edite los Grados, Minutos, Segundos, Orientación  y el Amax del modelo para calcular el TMI completo:")
    # Crear el formulario para los parámetros adicionales
    with st.form("parametros_form"):
        grados = st.number_input("Grados", value=0, min_value=0, max_value=14)
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
        