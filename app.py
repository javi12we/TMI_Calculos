import streamlit as st
from paginas import home, calculos_tmi, modelos_fatiga

# Configuración de la página para ancho completo
st.set_page_config(layout="wide")

# Diccionario de páginas
pages = {
    "Inicio": home,
    "Cálculo TMI": calculos_tmi,
    "Modelos de Fatiga": modelos_fatiga
}

titulo_color = '''
    <style>
    h1 {
        color: #ff7700; /* Naranja llamativo */
        font-family: 'Futura', sans-serif; /* Tipo de letra Futura */
    }
    </style>
'''
    
def main():
    st.sidebar.title("Navegación")
    st.markdown(titulo_color, unsafe_allow_html=True)
    
    # Navegación principal
    choice = st.sidebar.radio("Menú", list(pages.keys()))

    # Si la opción seleccionada es un diccionario (una categoría), mostramos un submenú
    if isinstance(pages[choice], dict):
        subpage = st.sidebar.radio(f"Submenú de {choice}", list(pages[choice].keys()))
        selected_page = pages[choice][subpage]
    else:
        selected_page = pages[choice]

    # Llamada a la página seleccionada
    selected_page.show()

if __name__ == "__main__":
    main()