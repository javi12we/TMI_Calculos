import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ===========================================
# Función para calcular la tabla de K1
# ===========================================
def calcular_tabla_k1(C, εt, E) -> pd.DataFrame:
    """
    Calcula una tabla con diferentes valores relacionados al diseño de pavimentos:
    - Módulo de resiliencia k1 (Bottom-Up y Top-Down).
    - Número de repeticiones de fatiga (Nf) para ambos métodos.
    
    Parámetros:
    -----------
    C : float
        Coeficiente relacionado con las cargas y propiedades del material.
    εt : float
        Deformación permisible de tracción del pavimento.
    E : float
        Módulo elástico del material (rigidez).

    Retorna:
    --------
    pd.DataFrame:
        Una tabla con los cálculos realizados para cada espesor del pavimento.
    """
    # Tabla base con espesores en pulgadas
    k1_tabla = pd.DataFrame(
        {
            "hc, in": [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
            ],           
        }
    )

    # Convertir espesores a centímetros
    k1_tabla["h, cm"] = round(k1_tabla["hc, in"] * 2.54, 1)

    # Calcular módulo de resiliencia k1 - Bottom-Up
    k1_tabla["k1_b-up"] = 1 / (
        0.000398 + (0.003602 / (1 + np.exp(11.02 - 3.49 * k1_tabla['hc, in'])))
    )

    # Calcular inverso del módulo de resiliencia (1/k1) - Bottom-Up
    k1_tabla["1/k1_b-up"] = 1 / k1_tabla["k1_b-up"]

    # Calcular módulo de resiliencia k1 - Top-Down
    k1_tabla["k1_u-down"] = 1 / (
        0.01 + 12 / (1 + np.exp(15.676 - 2.8186 * k1_tabla['hc, in']))
    )

    # Calcular inverso del módulo de resiliencia (1/k1) - Top-Down
    k1_tabla["1/k1_up-down"] = 1 / k1_tabla["k1_u-down"]

    # Calcular número de repeticiones de fatiga (Nf) - Bottom-Up
    k1_tabla["nf_k1_b-up"] = 0.00432 * k1_tabla["k1_b-up"] * C * (1 / εt) ** 3.9492 * (1 / E) ** 1.281

    # Calcular número de repeticiones de fatiga (Nf) - Top-Down
    k1_tabla["nf_k1_up-down"] = 0.00432 * k1_tabla["k1_u-down"] * C * (1 / εt) ** 3.9492 * (1 / E) ** 1.281
    
    return k1_tabla


# ===========================================
# Gráfica Bottom-Up
# ===========================================
def graficar_bottom_up(df_tabla_k1):
    """
    Genera una gráfica de 1/k1 (Bottom-Up) en función del espesor del pavimento.

    Parámetros:
    -----------
    df_tabla_k1 : pd.DataFrame
        Tabla con los cálculos de K1.

    Retorna:
    --------
    None
    """
    fig = px.line(
        df_tabla_k1, 
        x="hc, in", 
        y="1/k1_b-up", 
        markers=True, 
        title="Bottom - Up"
    )

    fig.update_traces(line=dict(color="darkblue", width=3))  # Estilo de línea
    fig.update_layout(
        title=dict(text="Bottom - Up", x=0.5, font=dict(size=20)),  # Título centrado
        xaxis_title=dict(text="hAC (cm)", font=dict(size=14)),  # Título del eje X
        yaxis_title=dict(text="1/k1 b-up", font=dict(size=14)),  # Título del eje Y
        xaxis=dict(showgrid=True, gridcolor="lightgrey", zeroline=False),  # Líneas de rejilla
        yaxis=dict(showgrid=True, gridcolor="lightgrey", zeroline=False),
        plot_bgcolor="whitesmoke"  # Fondo claro
    )

    st.plotly_chart(fig)


# ===========================================
# Gráfica Top-Down
# ===========================================
def graficar_top_down(df_tabla_k1):
    """
    Genera una gráfica de 1/k1 (Top-Down) en función del espesor del pavimento.

    Parámetros:
    -----------
    df_tabla_k1 : pd.DataFrame
        Tabla con los cálculos de K1.

    Retorna:
    --------
    None
    """
    fig = px.line(
        df_tabla_k1, 
        x="hc, in", 
        y="1/k1_up-down", 
        markers=True, 
        title="Top - Down"
    )

    fig.update_traces(line=dict(color="darkgreen", width=3))  # Estilo de línea
    fig.update_layout(
        title=dict(text="Top - Down", x=0.5, font=dict(size=20)),  # Título centrado
        xaxis_title=dict(text="hAC (cm)", font=dict(size=14)),  # Título del eje X
        yaxis_title=dict(text="1/k1 u-d", font=dict(size=14)),  # Título del eje Y
        xaxis=dict(showgrid=True, gridcolor="lightgrey", zeroline=False),  # Líneas de rejilla
        yaxis=dict(showgrid=True, gridcolor="lightgrey", zeroline=False),
        plot_bgcolor="whitesmoke"  # Fondo claro
    )
    
    st.plotly_chart(fig)
