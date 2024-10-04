import streamlit as st
from paginas import home, calculos_tmi

# Configuración de la página para ancho completo
st.set_page_config(layout="wide")

# Diccionario de páginas
pages = {
    "Inicio": home,
    "Cáculo TMI": calculos_tmi
}

def main():
    st.sidebar.title("Navegación")
    
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