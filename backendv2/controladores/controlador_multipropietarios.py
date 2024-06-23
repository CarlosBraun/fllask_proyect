'''
En este módulo
'''
import copy
from controladores.controlador_requests import (
    obtener_conexion_db,
    obtener_multipropietario_data,
    request_algorithm_data,
    limpiar_multipropietario,
    ingresar_multipropietarios,
    eliminar_ultimo_registro_multipropietario

)
from controladores.controlador_queries import (
    generar_query_obtener_multipropietarios,
    generar_query_borrar_multipropietario
    )
from flask import Blueprint, jsonify, request
from mysql.connector import Error
controlador_multipropietarios_bp = Blueprint(
    'controlador_multipropietarios', __name__)

def construir_fila_adquirente(adquirente, propiedad, value):
    '''Construye una fila con los datos del adquirente y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': adquirente['RUNRUT'],
        'derecho': adquirente['derecho'],
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def validar_y_ajustar_fila(row):
    '''Valida y ajusta los datos de la fila según las reglas de negocio.'''
    return row if float(row["derecho"]) > 0 else None

def construir_fila_general(persona, propiedad, value):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho': persona['derecho'],
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4]),
        'ano_vigencia_f': None
    }
def construir_fila_distribuir_100(persona, propiedad, value, a_distribuir):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':str(float(persona['derecho'])*a_distribuir/100),
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_var_ena_100(persona, propiedad, value):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':0,
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_adq(persona, propiedad, value, variacion_derecho_enajenante):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':float(persona['derecho']) * variacion_derecho_enajenante,
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_ena_fantasma(persona, propiedad, ano):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad['comuna'],
                'manzana': propiedad['manzana'],
                'predio': propiedad['predio'],
                'run': persona['RUNRUT'],
                'derecho': 0,
                'fecha_inscripcion': None,
                'ano_inscripccion': None,
                'numero_inscripcion': None,
                'fojas': None,
                'ano_vigencia_i': ano,
                'status': None
    }
def generar_registros_form_a_multi(adquirentes, enajenantes, propiedad, value):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 8'''
    result = []
    for adquirente in adquirentes:
        row = construir_fila_general(adquirente, propiedad, value)
        result.append(row)
    for enajenante in enajenantes:
        row = construir_fila_general(enajenante, propiedad, value)
        result.append(row)
    return result
def obtener_ultimo_registro(propiedad, ano_actual):
    '''Recibe todas las filas de la multipropietario y retorna las que no tienen ano_vigencia_f'''
    result = []
    data = obtener_multipropietario_data([propiedad])[0]
    for i in data:
        ano_vigencia_f = i.get('ano_vigencia_f')
        ano_vigencia_i = i.get('ano_vigencia_i')
        if ano_vigencia_f is None and (ano_vigencia_i is None or (isinstance(ano_vigencia_i, int)
                                                                  and ano_vigencia_i < ano_actual)):
            result.append(i)
    return result

def revisar_multipropietario(multipropietario):
    '''Recibe todas las filas de la multipropietario y retorna un arreglo vacío en caso
    de no existir registros
    '''
    result =[]
    for i in multipropietario:
        result.append(i)
    return result

def inicializar_derechos(multipropietario_temp):
    '''
    Inicializa el diccionario de derechos a partir de los datos de multipropietario_temp.
    '''
    derechos = {}
    for prop in multipropietario_temp:
        run = prop['run']
        derecho = float(prop['derecho'])
        if run in derechos:
            derechos[run] += derecho
        else:
            derechos[run] = derecho
    return derechos

def calcular_derechos_enajenantes(enajenantes, derechos, total_enajenado, multipropietario_temp):
    '''
    Procesa la lista de enajenantes, actualizando el diccionario de derechos,
    el total enajenado. Además retorna un count() de los enajenantes.
    '''
    conteo = 0
    derecho = 0
    for enajenante in enajenantes:
        conteo += 1
        run = enajenante["RUNRUT"]
        for i in multipropietario_temp:
            ano_vigencia_f = i.get('ano_vigencia_f')
            if i['run'] == run and ano_vigencia_f is None:
                derecho += float(i['derecho'])
                total_enajenado += derecho
        if run in derechos:
            derechos[run] -= derecho
    return total_enajenado, conteo

def calcular_derechos_adquirentes(adquirentes, derechos, total_adquirido):
    '''
    Procesa la lista de adquirentes, actualizando el diccionario de derechos
    y el total adquirido. Además retorna un count() de los adquirentes.
    '''
    conteo = 0
    for adquirente in adquirentes:
        conteo += 1
        run = adquirente["RUNRUT"]
        derecho = float(adquirente["derecho"])
        total_adquirido += derecho
        if run in derechos:
            derechos[run] += derecho
    return total_adquirido , conteo

def calcular_derechos_totales(multipropietario_temp, value):
    '''
    Retorna el cálculo del total de lo enajenado y de lo adquirido.
    '''
    derechos = inicializar_derechos(multipropietario_temp)
    total_enajenado = 0
    total_adquirido = 0
    total_enajenado = calcular_derechos_enajenantes(value["enajenantes"], derechos,
                                                     total_enajenado , multipropietario_temp)
    total_adquirido = calcular_derechos_adquirentes(value["adquirentes"], derechos, total_adquirido)

    return derechos ,total_enajenado, total_adquirido
###    CÓDIGO POR REFACTORIZAR
def actualizar_ano_vigencia_f(elementos, ano):
    '''Retorna el diccionario actualizado con el ano_vigencia_f actualizado'''
    elementos_temp = []
    for elemento in elementos:
        if elemento:
            ano_vigencia_f = elemento.get("ano_vigencia_f")
            if (ano_vigencia_f is None) and (int(ano_vigencia_f) < ano):
                elemento["ano_vigencia_f"] = ano - 1
                elementos_temp.append(elemento)
    return elementos_temp


def ejecutar_algoritmo(datos):
    '''Es el ejecutar_algoritmo central, procesa los formularios y rellena la Multipropietario'''
    print("COMIENZO ejecutar_ALGORITMO------------")
    data = request_algorithm_data(datos)
    for lista in data:
        procesar_lista_formularios(lista, datos)
    return data

def procesar_lista_formularios(lista, datos):
    '''Procesa cada lista de formularios'''
    contador = 0
    ano_corte = 0
    multipropietario_temp = None
    for formularios_dict in lista:
        propiedad = datos[contador]
        limpiar_multipropietario(propiedad)
        ultimo_registro = []
        for _, value in formularios_dict.items():
            ano_corte, multipropietario_temp, ultimo_registro = procesar_formulario(
                value, propiedad, multipropietario_temp, ano_corte, ultimo_registro)
        if multipropietario_temp is not None:
            finalizar_procesamiento(multipropietario_temp, ultimo_registro, ano_corte, propiedad)
        contador += 1

def procesar_formulario(value, propiedad, multipropietario_temp, ano_corte, ultimo_registro):
    '''Procesa cada formulario individualmente'''
    ano_form = int(value['fecha_inscripcion'][0:4])
    cne = int(value["cne"])
    if ano_corte == 0:
        ano_corte = ano_form
    elif ano_corte < ano_form:
        multipropietario_temp, ultimo_registro, ano_corte = manejar_cambio_ano_corte(
            multipropietario_temp, ultimo_registro, ano_form, propiedad)
    if multipropietario_temp is None:
        multipropietario_temp, ultimo_registro = inicializar_multipropietario_temp(
            propiedad, ano_form)
    multipropietario_temp = procesar_cne(cne, multipropietario_temp, value, propiedad)
    return ano_corte, multipropietario_temp, ultimo_registro

def manejar_cambio_ano_corte(multipropietario_temp, ultimo_registro, ano_form, propiedad):
    '''Maneja el cambio de año de corte'''
    multipropietario_temp = preparar_ingreso_multipropietario(multipropietario_temp)
    ultimo_registro = acotar_registro_anterior(ultimo_registro, ano_form)
    eliminar_ultimo_registro_multipropietario(propiedad)
    multipropietario = armar_multipropietario(ultimo_registro, multipropietario_temp)
    ingresar_multipropietarios(multipropietario)
    return None, ultimo_registro, ano_form

def inicializar_multipropietario_temp(propiedad, ano_form):
    '''Inicializa multipropietario_temp y ultimo_registro'''
    multipropietario_temp = obtener_ultimo_registro(propiedad, ano_form)
    print(propiedad)
    ultimo_registro = obtener_ultimo_registro(propiedad, ano_form)
    return multipropietario_temp, ultimo_registro

def procesar_cne(cne, multipropietario_temp, value, propiedad):
    '''Procesa el cne del formulario'''
    if cne == 99:
        multipropietario_temp = procesar_resolucion_de_patrimonio(value, propiedad)
    elif cne == 8:
        procesar_compra_venta(multipropietario_temp, value, propiedad)
    return multipropietario_temp

def finalizar_procesamiento(multipropietario_temp, ultimo_registro, ano_form, propiedad):
    '''Finaliza el procesamiento de la multipropietario_temp'''
    multipropietario_temp = preparar_ingreso_multipropietario(multipropietario_temp)
    ultimo_registro = acotar_registro_anterior(ultimo_registro, ano_form)
    eliminar_ultimo_registro_multipropietario(propiedad)
    multipropietario = armar_multipropietario(ultimo_registro, multipropietario_temp)
    ingresar_multipropietarios(multipropietario)



def preparar_ingreso_multipropietario(multipropietario_temp):
    '''Retorna el la TEMP con todos los ajustes realizados'''
    multipropietario_temp = realizar_merge(multipropietario_temp)
    multipropietario_temp = ajustar_derechos(multipropietario_temp)
    multipropietario_temp =eliminar_enas_con_derecho_cero(multipropietario_temp)
    return multipropietario_temp

def armar_multipropietario(ultimo_registro,multipropietario_temp):
    '''Retorna el registro a ingresar a la multipropietario con el registro previo
    acotado'''
    multipropietario = ultimo_registro
    for i in multipropietario_temp:
        multipropietario.append(i)
    return multipropietario


def procesar_resolucion_de_patrimonio(value, propiedad):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 99'''
    result = []
    for adquirente in value['adquirentes']:
        row = construir_fila_adquirente(adquirente, propiedad, value)
        row = validar_y_ajustar_fila(row)
        if row is not None:
            result.append(row)
    return result
def procesar_compra_venta(multipropietario_temp,value, propiedad):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 8'''
    generar_registros_form_a_multi(value["adquirentes"],
                                            value["enajenantes"], propiedad, value)
    data_temp = calcular_derechos_totales(multipropietario_temp, value)
    _,enajenado, adquirido = data_temp
    total_adquirido , cantidad_adq = adquirido
    _, cantidad_ena = enajenado
    if (total_adquirido == 100 or total_adquirido == 0):
        distribuir_100(value, propiedad, multipropietario_temp)
    elif (100>total_adquirido>0 and (cantidad_ena ==1 and cantidad_adq ==1)):
        distribuir_menos_100(value, propiedad, multipropietario_temp)
    else:
        distribuir_general(value, propiedad, multipropietario_temp)

def obtener_rut_enajenantes_100(value):
    '''Obtiene los RUNRUT de los enajenantes de value'''
    return [enajenante["RUNRUT"] for enajenante in value["enajenantes"]]

def calcular_total_enajenado_100(rut_enajenantes, multipropietario_temp):
    '''Calcula el total enajenado a partir de multipropietario_temp y los rut enajenantes'''
    total_enajenado = 0
    for rut in rut_enajenantes:
        for registro in multipropietario_temp:
            if rut == registro["run"]:
                total_enajenado += float(registro["derecho"])
    return total_enajenado

def llevar_a_cero_derechos_enajenantes_100(value, multipropietario_temp):
    '''Lleva a cero los derechos de los enajenantes en multipropietario_temp'''
    for enajenante in value["enajenantes"]:
        for temp_row in multipropietario_temp:
            if temp_row['run'] == enajenante['RUNRUT']:
                temp_row['derecho'] = 0

def agregar_adquirentes_100(value, propiedad, multipropietario_temp, a_distribuir):
    '''Agrega los adquirentes a multipropietario_temp'''
    for adquirente in value["adquirentes"]:
        row = construir_fila_distribuir_100(adquirente, propiedad, value, a_distribuir)
        multipropietario_temp.append(row)

def distribuir_100(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir 100%'''
    rut_enajenantes = obtener_rut_enajenantes_100(value)
    total_enajenado = calcular_total_enajenado_100(rut_enajenantes, multipropietario_temp)
    a_distribuir = total_enajenado if total_enajenado != 0 else 100
    llevar_a_cero_derechos_enajenantes_100(value, multipropietario_temp)
    agregar_adquirentes_100(value, propiedad, multipropietario_temp, a_distribuir)
    return 200

def crear_dict_derechos_menos_100(multipropietario_temp):
    '''Crea un diccionario de derechos a partir de multipropietario_temp'''
    multipropietario_dict = {}
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            multipropietario_dict[run] += float(prop['derecho'])
        else:
            multipropietario_dict[run] = float(prop['derecho'])
    return multipropietario_dict

def ajustar_derechos_enajenantes_menos_100(multipropietario_dict, value,
                                            multipropietario_temp, propiedad):
    '''Ajusta los derechos de los enajenantes en multipropietario_dict y
      actualiza multipropietario_temp'''
    for enajenante in value['enajenantes']:
        run = enajenante['RUNRUT']
        derecho = float(enajenante['derecho'])
        if run in multipropietario_dict and derecho > 0:
            variacion_derecho_enajenante = float(multipropietario_dict[run]) / 100
            derecho_enajenante = variacion_derecho_enajenante * (100 - float(derecho))
            multipropietario_dict[run] = derecho_enajenante
        else:
            variacion_derecho_enajenante = 100
            multipropietario_temp.append(construir_fila_var_ena_100(enajenante, propiedad, value))
    return variacion_derecho_enajenante

def actualizar_derechos_menos_100(multipropietario_temp, multipropietario_dict, ano_actual):
    '''Actualiza multipropietario_temp con los derechos ajustados'''
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            prop['derecho'] = multipropietario_dict[run]
            prop['ano_vigencia_i'] = int(ano_actual)

def insertar_adquirentes_menos_100(multipropietario_temp, value, propiedad,
                                    variacion_derecho_enajenante):
    '''Inserta los adquirentes en multipropietario_temp'''
    for adquirente in value['adquirentes']:
        multipropietario_temp.append(construir_fila_adq(adquirente, propiedad, value,
                                                         variacion_derecho_enajenante))

def distribuir_menos_100(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir <100%'''
    ano_actual = value["fecha_inscripcion"][:4]
    multipropietario_dict = crear_dict_derechos_menos_100(multipropietario_temp)
    variacion_derecho_enajenante = ajustar_derechos_enajenantes_menos_100(multipropietario_dict,
                                             value, multipropietario_temp, propiedad)
    actualizar_derechos_menos_100(multipropietario_temp, multipropietario_dict, ano_actual)
    insertar_adquirentes_menos_100(multipropietario_temp, value, propiedad,
                                    variacion_derecho_enajenante)
    return 200

def crear_dict_derechos_general(multipropietario_temp):
    '''Crea un diccionario de derechos a partir de multipropietario_temp'''
    multipropietario_dict = {}
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            multipropietario_dict[run] += float(prop['derecho'])
        else:
            multipropietario_dict[run] = float(prop['derecho'])
    return multipropietario_dict

def restar_derechos_enajenantes_general(multipropietario_dict, value,
                                         multipropietario_temp, propiedad):
    '''Resta los derechos de los enajenantes en multipropietario_dict
      y actualiza multipropietario_temp'''
    for enajenante in value['enajenantes']:
        run = enajenante['RUNRUT']
        derecho = float(enajenante['derecho'])
        if run in multipropietario_dict:
            multipropietario_dict[run] -= derecho
        else:
            multipropietario_temp.append(construir_fila_ena_fantasma(enajenante,
                                     propiedad, value["fecha_inscripcion"][:4]))
    return multipropietario_dict

def actualizar_derechos_general(multipropietario_temp, multipropietario_dict, value):
    '''Actualiza multipropietario_temp con los derechos ajustados'''
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            prop['derecho'] = multipropietario_dict[run]
            prop['ano_vigencia_i'] = value["fecha_inscripcion"][:4]

def insertar_adquirentes_general(multipropietario_temp, value, propiedad):
    '''Inserta los adquirentes en multipropietario_temp'''
    for adquirente in value['adquirentes']:
        multipropietario_temp.append(construir_fila_general(adquirente, propiedad, value))

def distribuir_general(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución en el resto de los casos
      que no fueron especificados previamente'''
    multipropietario_dict = crear_dict_derechos_general(multipropietario_temp)
    multipropietario_dict = restar_derechos_enajenantes_general(multipropietario_dict,
                                             value, multipropietario_temp, propiedad)
    actualizar_derechos_general(multipropietario_temp, multipropietario_dict, value)
    insertar_adquirentes_general(multipropietario_temp, value, propiedad)
    return 200


#refactorizado

def copiar_lista(multipropietario_temp):
    '''Realiza una copia profunda de la lista multipropietario_temp'''
    return copy.deepcopy(multipropietario_temp)

def acotar_ano_vigencia(registro, ano):
    '''Acota el año de vigencia final al año anterior si es None'''
    if registro.get('ano_vigencia_f') is None:
        registro['ano_vigencia_f'] = ano - 1
    return registro

def acotar_registro_anterior(multipropietario_temp, ano):
    '''Retorna la tabla multipropietario con los años anteriores acotados'''
    multi_temp = copiar_lista(multipropietario_temp)
    multi_temp = [acotar_ano_vigencia(registro, ano) for registro in multi_temp]
    return multi_temp

def obtener_fecha_mas_antigua(fecha_actual, fecha_agrupada):
    '''Determina si la fecha actual es más antigua que la fecha agrupada'''
    return fecha_actual is None or (fecha_agrupada is not None and fecha_actual < fecha_agrupada)

def actualizar_registro(agrupado, nuevo):
    '''Actualiza el registro agrupado con la información del nuevo registro'''
    for key, value in nuevo.items():
        if value is not None:
            agrupado[key] = value

def sumar_derechos(agrupado, nuevo):
    '''Suma los derechos del nuevo registro al registro agrupado'''
    agrupado['derecho'] = float(agrupado['derecho']) + float(nuevo['derecho'])

def procesar_registro_merge(agrupados_por_rut, registro):
    '''Procesa un registro individual para el merge'''
    rut = registro['run']
    if rut not in agrupados_por_rut:
        agrupados_por_rut[rut] = registro.copy()
    else:
        sumar_derechos(agrupados_por_rut[rut], registro)
        fecha_inscripcion_actual = registro.get('fecha_inscripcion')
        fecha_inscripcion_agrupada = agrupados_por_rut[rut].get('fecha_inscripcion')
        if obtener_fecha_mas_antigua(fecha_inscripcion_actual, fecha_inscripcion_agrupada):
            actualizar_registro(agrupados_por_rut[rut], registro)
        else:
            # Actualizar el año de vigencia inicial con el del nuevo registro si es más reciente
            agrupados_por_rut[rut]['ano_vigencia_i'] = registro.get(
                'ano_vigencia_i', agrupados_por_rut[rut]['ano_vigencia_i']
            )

def ajustar_derecho_negativo(merged_list):
    '''Establece el derecho en 0 si es negativo'''
    for registro in merged_list:
        if float(registro['derecho']) < 0:
            registro['derecho'] = 0

def realizar_merge(multipropietario_temp):
    '''Realiza y retorna el merge de los particulares en la multipropietario'''
    agrupados_por_rut = {}

    for registro in multipropietario_temp:
        procesar_registro_merge(agrupados_por_rut, registro)

    merged_list = list(agrupados_por_rut.values())
    ajustar_derecho_negativo(merged_list)
    return merged_list


def ajustar_derechos(multipropietario_temp):
    '''Ajusta los derechos de la multipropietario_temp para que la sumatoria de derechos sea 100'''
    total_derechos = obtener_total_derecho_enajenado(multipropietario_temp)
    fantasmas = obtener_fantasmas(multipropietario_temp)
    factor_ajuste = 1
    if total_derechos == 100:
        factor_ajuste = 1 # No se necesita ajuste
    elif total_derechos < 100 and fantasmas:
        sobrante = 100 - total_derechos
        sobrante_por_fantasma = sobrante / len(fantasmas)
        for fantasma in fantasmas:
            fantasma['derecho'] = sobrante_por_fantasma
            for prop in multipropietario_temp:
                if prop['run'] == fantasma['run']:
                    prop['derecho'] = fantasma['derecho']
    elif total_derechos >100:
        factor_ajuste = 100 / total_derechos

    ajustar_derechos_por_factor(multipropietario_temp, factor_ajuste)
    return multipropietario_temp
def obtener_total_derecho_enajenado(multipropietario_temp):
    '''Retorna la suma de los derechos presentes en la multipropietario
     de los enajenantes'''
    return sum(float(prop['derecho']) for prop in multipropietario_temp)
def obtener_fantasmas(multipropietario_temp):
    '''Retorna los enajenantes fantasmas en una lista'''
    return [prop for prop in multipropietario_temp if float(prop['derecho']) == 0 and
                 prop['fecha_inscripcion'] is None and
                 prop['ano_inscripccion'] is None and
                 prop['numero_inscripcion'] is None and
                 prop['fojas'] is None and
                 prop['status'] is None]

def ajustar_derechos_por_factor(multipropietario_temp, factor_ajuste):
    '''Retorna los valores ajustados por el factor correspondiente'''
    for prop in multipropietario_temp:
        prop['derecho'] = float(prop['derecho']) * factor_ajuste
    return multipropietario_temp


def eliminar_enas_con_derecho_cero(multipropietario_temp):
    '''Elimina las filas que no pertenecen a los fantasmas y tienen derecho 0 y negativo'''
    return [prop for prop in multipropietario_temp if float(prop['derecho']) > 0]


@ controlador_multipropietarios_bp.route('/', methods=['GET'])
def obtener_datos():
    '''Retorna todos los datos de la tabla Multipropietario'''
    try:
        conn = obtener_conexion_db()
        rows = ejecutar_consulta_multipropietario(conn)
        return jsonify(rows)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

def ejecutar_consulta_multipropietario(conn):
    '''Ejecuta la consulta para obtener todos los datos de Multipropietario'''
    with conn.cursor(dictionary=True) as cursor:
        query = generar_query_obtener_multipropietarios()
        cursor.execute(query)
        return cursor.fetchall()

@ controlador_multipropietarios_bp.route('/buscar', methods=['POST'])
def buscar_datos():
    '''Retorna filas de la tabla Multipropietario según una búsqueda'''
    comuna = request.json.get("comuna")
    manzana = request.json.get("manzana")
    predio = request.json.get("predio")
    ano = request.json.get("ano")
    rows = ejecutar_consulta_busqueda_multipropietario(comuna, manzana, predio, ano)
    return jsonify(rows)

def ejecutar_consulta_busqueda_multipropietario(comuna, manzana, predio, ano):
    '''Ejecuta la consulta SQL para buscar datos en la tabla Multipropietario'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    query = generar_query_obtener_multipropietarios()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        rows = filtrar_datos_multipropietario(rows,str(comuna),int(manzana),int(predio),int(ano))
        return rows
    finally:
        cursor.close()
        conn.close()

def filtrar_datos_multipropietario(rows, comuna, manzana, predio, ano):
    """
    Filtra los datos de la lista de diccionarios 'rows' según los parámetros especificados.
    La necesidad de crear esta función nace de la incompatibilidad de realizar la búsqueda
    mediante queries dinámicas.

    """
    resultado_filtrado = []
    for row in rows:
        if (row['comuna'] == comuna and
            row['manzana'] == manzana and
            row['predio'] == predio and
            (row['ano_vigencia_f'] is None or row['ano_vigencia_f'] >= ano)):
            resultado_filtrado.append(row)
    return resultado_filtrado

@ controlador_multipropietarios_bp.route('/clean', methods=['GET'])
def borrar_datos():
    '''Elimina todas las filas de la tabla Multipropietario'''
    mensaje = ejecutar_borrado_multipropietario()
    return jsonify(mensaje)

def ejecutar_borrado_multipropietario():
    '''Ejecuta la consulta SQL para borrar todas las filas de la tabla Multipropietario'''
    conn = obtener_conexion_db()
    cursor = conn.cursor()
    query = generar_query_borrar_multipropietario()
    try:
        cursor.execute(query)
        conn.commit()  # Confirmar la transacción
        mensaje = {'mensaje': 'Datos borrados exitosamente'}
    except Error as e:
        conn.rollback()  # Revertir la transacción en caso de error
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
    return mensaje
