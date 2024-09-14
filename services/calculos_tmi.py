import pandas as pd

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
