import pandas as pd
import plotly.express as px
import streamlit as st

def calcular_modelos_microstrain(ni_transito, modulo_mezcla, rigidez_convertida, factor_ajuste_modelo, factor_ajuste_resistencia):
    df_microstrain_modelo = pd.DataFrame({"ni_transito": ni_transito})
    
    # Calculo SPDM DERECHO 
    df_microstrain_modelo['SPDM'] = (1000000 * (df_microstrain_modelo['ni_transito'] * 1/10 * (0.856 * 11 + 1.08)**-5 * (modulo_mezcla * 1000000)**1.8)**(-1/5))
    
    # Calculo de AI MS-1
    df_microstrain_modelo['AI MS-1'] = 1000000 * ((df_microstrain_modelo['ni_transito'] * rigidez_convertida**0.854) / (18.4 * 0.00432 * factor_ajuste_modelo))**(-1 / 3.291)
    
    # Calculo de Cedex-Shell
    df_microstrain_modelo['Cedex-Shell'] = 1000000 * (df_microstrain_modelo['ni_transito'] / 1.02e-13)**-0.2
    
    # Calculo de Cedex-COST
    df_microstrain_modelo['Cedex-COST'] = 1000000 * (df_microstrain_modelo['ni_transito'] / 0.00000000906)**(-1 / 3.6706)
    
    # Calculo de Illinois
    df_microstrain_modelo['Illinois'] = 1000000 * (df_microstrain_modelo['ni_transito'] / 0.000005)**(-1 / 3)
    
    # Calculo de Minnesota
    df_microstrain_modelo['Minnesota'] = 1000000 * (df_microstrain_modelo['ni_transito'] / 0.00000283)**(-1 / 3.206)
    
    # Calculo de USACE
    df_microstrain_modelo['USACE'] = 1000000 * (df_microstrain_modelo['ni_transito'] / 478.63 * (145 * modulo_mezcla)**2.66)**(-1 / 5)
    
    #Calculo de ME-PDG
    df_microstrain_modelo['ME-PDG'] = 1000000 * (df_microstrain_modelo['ni_transito'] * rigidez_convertida**1.281 / (18.4 * 0.00432 * factor_ajuste_modelo * 0.007566 * factor_ajuste_resistencia))**(-1 / 3.9492)
    
    #Calculo de AUSTROADS
    df_microstrain_modelo['AUSTROADS'] = ((df_microstrain_modelo['ni_transito'] / 2)**-0.2 * 6918 * (0.856 * 11 + 1.08) / (modulo_mezcla**0.36))

    return df_microstrain_modelo

def graficar_modelos_fatiga(df_microstrain_modelo):
    # Convertir el dataframe a formato largo (melt) para Plotly Express
    df_long = df_microstrain_modelo.melt(id_vars='ni_transito', var_name='Modelo', value_name='Valores')

    # Crear la gráfica usando Plotly Express con líneas y puntos
    fig = px.scatter(df_long, x='ni_transito', y='Valores', color='Modelo', symbol='Modelo', 
                     log_x=True, log_y=True, title='Comparación de Modelos de Fatiga en función del Número de Tránsitos',
                     labels={'ni_transito': 'Número de Tránsitos', 'Valores': 'Valores Modelos de Fatiga'})

    # Agregar líneas conectando los puntos
    fig.update_traces(mode='lines+markers')

    # # Ajustar el tamaño del gráfico
    # fig.update_layout(width=1000, height=600)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

def calcular_ni_transito_por_modelo(df_microstrain_modelo, modulo_mezcla, factor_ajuste_modelo, rigidez_convertida, factor_ajuste_resistencia):
    # Crear un data frame vacio
    df_indice_fatiga_modelo = pd.DataFrame()
    
    #Calcular SPDM
    df_indice_fatiga_modelo["SPDM"] = 10 * (0.856 * 11 + 1.08)**5 * (modulo_mezcla * 1000000)**-1.8 * (df_microstrain_modelo['SPDM'] / 1000000)**-5
    
    #Calcular AI MS-1
    df_indice_fatiga_modelo["AI MS-1"] = 18.4 * 0.00432 * factor_ajuste_modelo * (df_microstrain_modelo['AI MS-1'] / 1000000)**-3.291 * rigidez_convertida**-0.854
    
    #Calcular Cedex-Shell
    df_indice_fatiga_modelo["Cedex-Shell"] = 0.000000000000102 * (df_microstrain_modelo['Cedex-Shell'] / 1000000)**-5
    
    #Calcular Cedex-COST
    df_indice_fatiga_modelo["Cedex-COST"] = 0.00000000906 * (df_microstrain_modelo['Cedex-COST'] / 1000000)**-3.6706

    #Calcular Illinois
    df_indice_fatiga_modelo["Illinois"] = 0.000005 * (df_microstrain_modelo['Illinois'] / 1000000)**-3
    
    #Calcular Minnesota
    df_indice_fatiga_modelo["Minnesota"] = 0.00000283 * (df_microstrain_modelo['Minnesota'] / 1000000)** -3.206
    
    #Calcular USACE
    df_indice_fatiga_modelo["USACE"] = 478.63 * (df_microstrain_modelo['USACE'] / 1000000)**-5 * (145 * modulo_mezcla)**-2.66
    
    #Calcular ME-PDG
    df_indice_fatiga_modelo["ME-PDG"] = 18.4 * 0.00432 * 0.007566 * factor_ajuste_resistencia * factor_ajuste_modelo * (df_microstrain_modelo['ME-PDG'] / 1000000)**-3.9492 * (rigidez_convertida)**-1.281
    
    #Calcular AUSTROADS
    df_indice_fatiga_modelo["AUSTROADS"] = 2 * (6918 * (0.856 * 11 + 1.08) / (modulo_mezcla**0.36 * df_microstrain_modelo['AUSTROADS']))**5
    
    return df_indice_fatiga_modelo