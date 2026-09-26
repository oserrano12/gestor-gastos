from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta

def calcular_tasa_mv(tasa: Decimal, tipo_tasa: str) -> Decimal:
    """Convierte la tasa a Mes Vencido (MV) si está en Efectiva Anual (EA)."""
    if tipo_tasa.upper() == 'EA':
        # Fórmula: (1 + EA)^(1/12) - 1
        return Decimal(str((1 + float(tasa)) ** (1/12) - 1))
    return tasa

def calcular_cuota_fija(monto: Decimal, tasa_mv: Decimal, cuotas: int) -> Decimal:
    """Calcula el valor de la cuota fija mensual."""
    if tasa_mv == 0:
        return monto / cuotas
    
    # Fórmula: Cuota = P * [ i * (1+i)^n ] / [ (1+i)^n - 1 ]
    numerador = tasa_mv * (1 + tasa_mv) ** cuotas
    denominador = ((1 + tasa_mv) ** cuotas) - 1
    cuota = monto * (numerador / denominador)
    return cuota.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def generar_tabla_amortizacion(
    monto_total: Decimal, 
    tasa_interes: Decimal, 
    tipo_tasa: str, 
    numero_cuotas: int, 
    fecha_compra: date,
    dia_corte: int,
    dia_limite_pago: int
) -> list:
    """
    Genera la tabla de amortización mes a mes.
    Retorna una lista de diccionarios con el detalle de cada cuota.
    """
    tasa_mv = calcular_tasa_mv(tasa_interes, tipo_tasa)
    cuota_fija = calcular_cuota_fija(monto_total, tasa_mv, numero_cuotas)
    
    saldo_restante = monto_total
    tabla = []
    
    # Calcular la primera fecha de pago basada en el día límite y la fecha de compra
    # Si la compra es antes del corte, se paga el mes siguiente.
    # Para simplificar inicialmente, asumiremos pagos mensuales consecutivos.
    fecha_pago_actual = fecha_compra + relativedelta(months=1)
    # Ajustamos el día al día límite de pago
    try:
        fecha_pago_actual = fecha_pago_actual.replace(day=dia_limite_pago)
    except ValueError:
        # En caso de meses sin día 30/31
        fecha_pago_actual = fecha_pago_actual + relativedelta(day=31)

    for i in range(1, numero_cuotas + 1):
        interes_mes = (saldo_restante * tasa_mv).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # En la última cuota, ajustamos el capital para cuadrar decimales
        if i == numero_cuotas:
            capital_mes = saldo_restante
            cuota_mes = capital_mes + interes_mes
        else:
            capital_mes = cuota_fija - interes_mes
            cuota_mes = cuota_fija
            
        saldo_restante -= capital_mes
        
        tabla.append({
            "numero_cuota": i,
            "fecha_vencimiento": fecha_pago_actual,
            "capital": capital_mes,
            "interes": interes_mes,
            "cuota_total": cuota_mes,
            "saldo_restante": saldo_restante.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        })
        
        fecha_pago_actual += relativedelta(months=1)
        try:
            fecha_pago_actual = fecha_pago_actual.replace(day=dia_limite_pago)
        except ValueError:
            fecha_pago_actual = fecha_pago_actual + relativedelta(day=31)
            
    return tabla
