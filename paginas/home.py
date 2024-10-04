import streamlit as st

def show():
    st.title("Bienvenido a CÁLCULOS INVIAS")
    st.write("""
    Esta es la página de inicio...
    """)
    
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