import pandas as pd
import numpy as np

def calcular_clasificacion_climatica(Im):
    """Calcula la clasificación climática según el índice de Thornthwaite."""
    if Im <= -40:
        return "E: Árido"
    elif -40 < Im <= -20:
        return "D: Semi-árido"
    elif -20 < Im <= 0:
        return "C1: Subhúmedo-seco"
    elif 0 < Im <= 20:
        return "C2: Subhúmedo-húmedo"
    elif 20 < Im <= 40:
        return "B1: Ligeramente húmedo"
    elif 40 < Im <= 60:
        return "B2: Moderadamente húmedo"
    elif 60 < Im <= 80:
        return "B3: Húmedo"
    elif 80 < Im <= 100:
        return "B4: Muy húmedo"
    else:
        return "A: Excesivamente húmedo"


def calcular_indices(datos_base, datos_n, grados, minutos, segundos, orientacion, amax):
    """Realiza los cálculos de balance hídrico e índices de Thornthwaite."""
    df=datos_base.copy()
    # Calcular la latitud en decimal y redondear
    latitud_decimal_corrected = grados + minutos / 60 + segundos / 3600
    LATITUD = round(latitud_decimal_corrected * 2) / 2
    print('LATITUD:', LATITUD)

    # Verificar la orientación válida
    if orientacion.lower() not in ['norte', 'sur']:
        raise ValueError("La orientación debe ser 'norte' o 'sur'.")

    # Calcular 'i' en el DataFrame
    df['i'] = (df['temperatura'] / 5) ** 1.514

    # Calcular P, I y el coeficiente 'a'
    P = df['precipitacion'].sum()
    I = df['i'].sum()
    a = (0.000000675 * I**3) - (0.0000771 * I**2) + (0.01792 * I) + 0.49239

    # Calcular ETPsc
    df['ETPsc'] = 16 * (10 * df['temperatura'] / I) ** a

    datos_n_select = datos_n[(datos_n['orientacion'] == orientacion) & (datos_n['latitud'] == LATITUD)]

    df['N'] = datos_n_select[df['mes'].to_list()].values[0]

    # Calcular ETPcrr
    df['ETPcrr'] = df['ETPsc'] * df['N'] / 12 * df['d'] / 30
    ETP = df['ETPcrr'].sum()

    # Crear lista para balance_integridad_asfalto
    balance_integridad_asfalto = []
    Ai_anterior = amax

    # Calcular balance_integridad_asfalto y Ai
    for index, row in df.iterrows():
        if index == 0:
            balance = amax + row['precipitacion'] - row['ETPcrr']
        else:
            balance = Ai_anterior + row['precipitacion'] - row['ETPcrr']
        balance_integridad_asfalto.append(balance)
        Ai_anterior = max(0, min(100, balance))

    df['balance_integridad_asfalto'] = balance_integridad_asfalto
    df['Ai'] = [max(0, min(100, balance)) for balance in balance_integridad_asfalto]

    # Calcular EXC y DEF
    df['EXC'] = df['balance_integridad_asfalto'].apply(lambda M: 0 if M <= 100 else M - 100)
    df['DEF'] = df['balance_integridad_asfalto'].apply(lambda M: 0 if M >= 0 else abs(M))

    EXC = df['EXC'].sum()
    DEF = df['DEF'].sum()

    # Cálculo de índices
    Ih = (EXC / ETP) * 100 if ETP > 0 else 0
    Ia = (DEF / ETP) * 100 if ETP > 0 else 0
    Im = Ih - 0.6 * Ia
    Im_1955 = 100 * (P / ETP - 1) if ETP > 0 else 0
    Im_Witzack = 75 * ((P / ETP) - 1) + 10 if ETP > 0 else 0

    # Usar la función separada para calcular la clasificación climática
    clasificacion_climatica = calcular_clasificacion_climatica(Im)

    # Resultados
    resultados = {
        'Índice de humedad (Ih)': Ih,
        'Índice de aridez (Ia)': Ia,
        'Índice de Thornthwaite (Im)': Im,
        'Índice de Thornthwaite 1955': Im_1955,
        'Índice de Thornthwaite, Witzack': Im_Witzack,
        'Clasificación climática': clasificacion_climatica
    }

    return df, resultados


def calcular_tmi_suelos_finos(
    TMI_tabla: pd.DataFrame,
    alpha: float,
    beta: float,
    gamma: float,
    delta: float,
    hr_wpi: float,
    a_wpi: float,
    b_wpi: float,
    c_wpi: float,
    Sopt: float,
) -> pd.DataFrame:
    """
    Calcula los valores TMI para suelos finos y genera una tabla con resultados detallados.

    Args:
        TMI_tabla (pd.DataFrame): Tabla base que incluye valores TMI (1) y TMI (2) por mes.
        alpha (float): Factor de succión hídrica.
        beta (float): Ajuste de la curva hídrica.
        gamma (float): Factor relacionado con la retención de agua.
        delta (float): Ajuste adicional.
        hr_wpi (float): Valor hídrico calculado a partir de WPI.
        a_wpi (float): Coeficiente de ajuste basado en WPI.
        b_wpi (float): Exponente basado en WPI.
        c_wpi (float): Factor de ajuste basado en WPI.
        Sopt (float): Saturación óptima calculada a partir de WPI.

    Returns:
        pd.DataFrame: Tabla con columnas que incluyen los valores calculados para suelos finos.
    """
    # Crear la tabla base con los nombres de los meses
    TMI_tabla_finos = pd.DataFrame(
        {
            "mes": [
                "enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
            ],
        }
    )

    # Calcular h(1) y h(2) para cada mes en función de TMI(1) y TMI(2)
    TMI_tabla_finos["h(1)"] = alpha * (np.exp(beta / (TMI_tabla["TMI (1)"] + gamma)) + delta)
    TMI_tabla_finos["h(2)"] = alpha * (np.exp(beta / (TMI_tabla["TMI (2)"] + gamma)) + delta)

    # Calcular Ch(h1) y Ch(h2), capacidad hídrica
    TMI_tabla_finos["Ch(h1)"] = 1 - np.log(1 + TMI_tabla_finos["h(1)"] / hr_wpi) / np.log(1 + 1000000 / hr_wpi)
    TMI_tabla_finos["Ch(h2)"] = 1 - np.log(1 + TMI_tabla_finos["h(2)"] / hr_wpi) / np.log(1 + 1000000 / hr_wpi)

    # Calcular Sr(1) y Sr(2), grado de saturación
    TMI_tabla_finos["Sr(1)"] = TMI_tabla_finos["Ch(h1)"] / (
        (np.log(np.exp(1) + (TMI_tabla_finos["h(1)"] / a_wpi) ** b_wpi)) ** c_wpi
    )
    TMI_tabla_finos["Sr(2)"] = TMI_tabla_finos["Ch(h2)"] / (
        (np.log(np.exp(1) + (TMI_tabla_finos["h(2)"] / a_wpi) ** b_wpi)) ** c_wpi
    )

    # Calcular Mr 1/Mropt(Finos) y Mr 2/Mropt(Finos), relación de rigidez mecánica
    TMI_tabla_finos["Mr 1/Mropt(Finos)"] = 10 ** (
        -0.3123 +
        (0.3 - -0.3123) /
        (1 + np.exp(
            np.log(-0.3 / -0.3123) + 6.8157 * (TMI_tabla_finos["Sr(1)"] - Sopt)
        ))
    )
    TMI_tabla_finos["Mr 2/Mropt(Finos)"] = 10 ** (
        -0.3123 +
        (0.3 - (-0.3123)) /
        (1 + np.exp(
            np.log(-0.3 / -0.3123) + 6.8157 * (TMI_tabla_finos["Sr(2)"] - Sopt)
        ))
    )

    # Retornar la tabla final con todos los cálculos
    return TMI_tabla_finos

def calcular_tmi_suelos_gruesos(
    TMI_tabla: pd.DataFrame,
    alpha: float,
    beta: float,
    gamma: float,
    delta: float,
    hr_D60: float,
    a_D60: float,
    b_D60: float,
    c_D60: float,
    Sopt: float,
) -> pd.DataFrame:
    """
    Calcula los valores TMI para suelos gruesos y genera una tabla con resultados detallados.

    Args:
        TMI_tabla (pd.DataFrame): Tabla base que incluye valores TMI (1) y TMI (2) por mes.
        alpha (float): Factor de succión hídrica.
        beta (float): Ajuste de la curva hídrica.
        gamma (float): Factor relacionado con la retención de agua.
        delta (float): Ajuste adicional.
        hr_D60 (float): Valor hídrico calculado a partir de D60.
        a_D60 (float): Coeficiente de ajuste basado en D60.
        b_D60 (float): Exponente basado en D60.
        c_D60 (float): Factor de ajuste basado en D60.
        Sopt (float): Saturación óptima calculada a partir de WPI.

    Returns:
        pd.DataFrame: Tabla con columnas que incluyen los valores calculados para suelos gruesos.
    """
    # Crear la tabla base con los nombres de los meses
    TMI_tabla_gruesos = pd.DataFrame(
        {
            "mes": [
                "enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
            ],
        }
    )

    # Calcular h(1) y h(2) para cada mes en función de TMI(1) y TMI(2)
    TMI_tabla_gruesos["h(1)"] = alpha * (np.exp(beta / (TMI_tabla["TMI (1)"] + gamma)) + delta)
    TMI_tabla_gruesos["h(2)"] = alpha * (np.exp(beta / (TMI_tabla["TMI (2)"] + gamma)) + delta)

    # Calcular Ch(h1) y Ch(h2), capacidad hídrica
    TMI_tabla_gruesos["Ch(h1)"] = 1 - np.log(1 + TMI_tabla_gruesos["h(1)"] / hr_D60) / np.log(1 + 1000000 / hr_D60)
    TMI_tabla_gruesos["Ch(h2)"] = 1 - np.log(1 + TMI_tabla_gruesos["h(2)"] / hr_D60) / np.log(1 + 1000000 / hr_D60)

    # Calcular Sr(1) y Sr(2), grado de saturación
    TMI_tabla_gruesos["Sr(1)"] = TMI_tabla_gruesos["Ch(h1)"] / (
        (np.log(np.exp(1) + (TMI_tabla_gruesos["Ch(h1)"] / a_D60) ** b_D60)) ** c_D60
    )
    TMI_tabla_gruesos["Sr(2)"] = TMI_tabla_gruesos["Ch(h2)"] / (
        (np.log(np.exp(1) + (TMI_tabla_gruesos["Ch(h2)"] / a_D60) ** b_D60)) ** c_D60
    )

    # Calcular Mr 1/Mropt(Gruesos) y Mr 2/Mropt(Gruesos), relación de rigidez mecánica
    TMI_tabla_gruesos["Mr 1/Mropt(Gruesos)"] = 10 ** (
        -0.3123 +
        (0.3 - -0.3123) /
        (1 + np.exp(
            np.log(-0.3 / -0.3123) + 6.8157 * (TMI_tabla_gruesos["Sr(1)"] - Sopt)
        ))
    )
    TMI_tabla_gruesos["Mr 2/Mropt(Gruesos)"] = 10 ** (
        -0.3123 +
        (0.3 - (-0.3123)) /
        (1 + np.exp(
            np.log(-0.3 / -0.3123) + 6.8157 * (TMI_tabla_gruesos["Sr(2)"] - Sopt)
        ))
    )

    # Retornar la tabla final con todos los cálculos
    return TMI_tabla_gruesos