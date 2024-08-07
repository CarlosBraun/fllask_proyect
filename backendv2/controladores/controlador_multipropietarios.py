'''
En este módulo
'''
import copy
from flask import Blueprint, jsonify, request
from mysql.connector import Error
from controladores.controlador_requests import (
    obtener_conexion_db,
    obtener_multipropietario_data,
    request_algorithm_data,
    limpiar_multipropietario,
    ingresar_multipropietarios,
    eliminar_ultimo_registro_multipropietario

)
from controladores.constantes import (CODIGO_COMPRA_VENTA,CODIGO_REGULARIZACION_PATRIMONIO)
from controladores.controlador_queries import (
    generar_query_obtener_multipropietarios,
    generar_query_borrar_multipropietario
    )
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
        'fojas': None,
        'fecha_inscripcion': None,
        'ano_inscripccion': None,
        'numero_inscripcion': None,
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4]),
        'status': "fantasma"
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
    print("Algoritmo procesando, por favor espere, esto puede tomar un momento...")
    data = request_algorithm_data(datos)
    for lista in data:
        procesar_lista_formularios(lista, datos)
    return data

def procesar_lista_formularios(lista, datos):
    '''Procesa cada lista de formularios'''
    contador = 0
    ano_corte = 0
    ano_anterior = 0
    multipropietario_temp = None
    for formularios_dict in lista:
        propiedad = datos[contador]
        limpiar_multipropietario(propiedad)
        ultimo_registro = []
        for _, value in formularios_dict.items():
            ano_corte, multipropietario_temp, ultimo_registro, ano_anterior = procesar_formulario(
                value, propiedad, multipropietario_temp, ultimo_registro ,[ano_corte,ano_anterior] )
        if multipropietario_temp is not None:
            finalizar_procesamiento(multipropietario_temp, ultimo_registro, ano_anterior, propiedad)
        contador += 1

def procesar_formulario(value, propiedad, multipropietario_temp, ultimo_registro, anos):
    '''Procesa cada formulario individualmente'''
    ano_corte,ano_vigencia_anterior = anos
    ano_form = int(value['fecha_inscripcion'][0:4])
    cne = int(value["cne"])
    if ano_corte == 0:
        ano_corte = ano_form
    elif ano_corte < ano_form:
        multipropietario_temp, ultimo_registro, ano_corte = manejar_cambio_ano_corte(
            multipropietario_temp, ultimo_registro, ano_vigencia_anterior, propiedad)
    if multipropietario_temp is None:
        multipropietario_temp, ultimo_registro = inicializar_multipropietario_temp(
            propiedad, ano_form)
    multipropietario_temp = procesar_cne(cne, multipropietario_temp, value, propiedad)
    return ano_corte, multipropietario_temp, ultimo_registro, ano_form

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
    ultimo_registro = obtener_ultimo_registro(propiedad, ano_form)
    return multipropietario_temp, ultimo_registro

def procesar_cne(cne, multipropietario_temp, value, propiedad):
    '''Procesa el cne del formulario'''
    if cne == CODIGO_REGULARIZACION_PATRIMONIO:
        multipropietario_temp = procesar_resolucion_de_patrimonio(value, propiedad)
    elif cne == CODIGO_COMPRA_VENTA:
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
def calcular_total_adquirido_100(value):
    '''Calcula el total enajenado a partir de multipropietario_temp y los rut enajenantes'''
    total_adquirido = 0
    for i in value["adquirentes"]:
        total_adquirido += float(i["derecho"])
    return total_adquirido


def llevar_a_cero_derechos_enajenantes_100(value, multipropietario_temp):
    '''Lleva a cero los derechos de los enajenantes en multipropietario_temp'''
    for enajenante in value["enajenantes"]:
        for temp_row in multipropietario_temp:
            if temp_row['run'] == enajenante['RUNRUT']:
                temp_row['derecho'] = 0

def agregar_adquirentes_100(value, propiedad, multipropietario_temp, a_distribuir, total_adquirido):
    '''Agrega los adquirentes a multipropietario_temp'''
    for adquirente in value["adquirentes"]:
        if revisar_caso_adquirentes_0_derecho(total_adquirido):
            adquirente["derecho"]= adaptar_adquirentes_0_derecho(a_distribuir,
                                                             len(value["adquirentes"]) )
        row = construir_fila_distribuir_100(adquirente, propiedad, value, a_distribuir)
        multipropietario_temp.append(row)

def adaptar_adquirentes_0_derecho(a_distribuir , cantidad_adquirentes):
    '''Retorna el valor de derecho para los casos en que los adquirentes suman 0 de derecho '''
    return (a_distribuir/cantidad_adquirentes)/a_distribuir*100

def revisar_caso_adquirentes_0_derecho(total_adquirido):
    '''Retorna un boolean en caso de que se cumpl ala condicion de sum de adq == 0'''
    if total_adquirido == 0:
        return True
    else:
        return False

def distribuir_100(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir 100%'''
    rut_enajenantes = obtener_rut_enajenantes_100(value)
    total_enajenado = calcular_total_enajenado_100(rut_enajenantes, multipropietario_temp)
    total_adquirido = calcular_total_adquirido_100(value)
    a_distribuir = total_enajenado if total_enajenado != 0 else 100
    llevar_a_cero_derechos_enajenantes_100(value, multipropietario_temp)
    agregar_adquirentes_100(value, propiedad, multipropietario_temp, a_distribuir , total_adquirido)

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
            variacion_derecho_enajenante =  definir_variacion_derecho_ena(multipropietario_dict,
                                                                           derecho, run)
        else:
            variacion_derecho_enajenante = 1
            multipropietario_temp.append(construir_fila_var_ena_100(enajenante, propiedad, value))
    return variacion_derecho_enajenante
def definir_variacion_derecho_ena(multipropietario_dict, derecho, run):
    '''Calcula y retorna la variacion de derechos en los enajenantes'''
    variacion_derecho_enajenante = float(multipropietario_dict[run]) / 100
    derecho_enajenante = variacion_derecho_enajenante * (100 - float(derecho))
    multipropietario_dict[run] = derecho_enajenante
    return variacion_derecho_enajenante

def actualizar_derechos_menos_100(multipropietario_temp, multipropietario_dict, ano_actual):
    '''Actualiza multipropietario_temp con los derechos ajustados'''
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            if multipropietario_dict[run] <= 0:
                prop['status'] = "fantasma"
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
    ano_actual = obtener_ano_actual(value)
    multipropietario_dict = crear_dict_derechos_menos_100(multipropietario_temp)
    variacion_derecho_enajenante = ajustar_derechos_enajenantes_menos_100(multipropietario_dict,
                                             value, multipropietario_temp, propiedad)
    actualizar_derechos_menos_100(multipropietario_temp, multipropietario_dict, ano_actual)
    insertar_adquirentes_menos_100(multipropietario_temp, value, propiedad,
                                    variacion_derecho_enajenante)
def obtener_ano_actual(value):
    '''Esta función retorna una fracción de la fecha de incripción.
    Pasa de formato YYYYMMDD a YYYY'''
    return value["fecha_inscripcion"][:4]

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

def restar_derechos_enajenante(multipropietario_dict, multipropietario_temp, enajenante,
                                propiedad, fecha_inscripcion):
    '''Resta el derecho del enajenante en multipropietario_dict o añade a 
    multipropietario_temp si no existe'''
    run = enajenante['RUNRUT']
    derecho = float(enajenante['derecho'])

    if run in multipropietario_dict:
        multipropietario_dict[run] -= derecho
    else:
        multipropietario_temp.append(construir_fila_ena_fantasma(enajenante, propiedad,
                                                                  fecha_inscripcion[:4]))

def restar_derechos_enajenantes_general(multipropietario_dict, value, multipropietario_temp,
                                         propiedad):
    '''Resta los derechos de los enajenantes en multipropietario_dict y actualiza 
    multipropietario_temp'''
    for enajenante in value['enajenantes']:
        restar_derechos_enajenante(multipropietario_dict, multipropietario_temp, enajenante,
                                    propiedad, value['fecha_inscripcion'])
    return multipropietario_dict

def actualizar_derechos_general(multipropietario_temp, multipropietario_dict, value):
    '''Actualiza multipropietario_temp con los derechos ajustados'''
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            if multipropietario_dict[run] <= 0:
                prop['status'] = "fantasma"

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

def actualizar_registro_si_mas_antiguo(registro_existente, nuevo_registro):
    '''Actualiza el registro existente si el nuevo registro tiene una fecha
      de inscripción más antigua'''
    if obtener_fecha_mas_antigua(nuevo_registro['fecha_inscripcion'],
                                  registro_existente['fecha_inscripcion']):
        actualizar_registro(registro_existente, nuevo_registro)

def procesar_registro_merge(agrupados_por_rut, registro):
    '''Procesa un registro individual para el merge'''
    rut = registro['run']

    if rut not in agrupados_por_rut:
        agrupados_por_rut[rut] = registro.copy()
    else:
        sumar_derechos(agrupados_por_rut[rut], registro)
        actualizar_registro_si_mas_antiguo(agrupados_por_rut[rut], registro)
        # Actualizar el año de vigencia inicial con el del nuevo registro si es más reciente
        key = 'ano_vigencia_i' # se define la key para respetar el n° máximo de caracteres
        #en la linea 565
        agrupados_por_rut[rut][key] = max(int(agrupados_por_rut[rut].get(key, 0)),
                                                        int(registro.get(key, 0)))



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
    '''Ajusta los derechos en multipropietario_temp para que la sumatoria sea 100'''
    total_derechos = obtener_total_derecho_enajenado(multipropietario_temp)
    fantasmas = obtener_fantasmas(multipropietario_temp)

    if total_derechos == 100:
        return multipropietario_temp  # No se necesita ajuste

    if total_derechos < 100 and fantasmas:
        ajustar_sobrante_por_fantasma(multipropietario_temp, fantasmas)

    elif total_derechos > 100:
        ajustar_exceso_por_factor(multipropietario_temp, total_derechos)

    return multipropietario_temp

def ajustar_sobrante_por_fantasma(multipropietario_temp, fantasmas):
    '''Ajusta los sobrantes en caso de ser necesario'''
    sobrante = calcular_sobrante(100, obtener_total_derecho_enajenado(multipropietario_temp))
    sobrante_por_fantasma = sobrante / len(fantasmas)
    for fantasma in fantasmas:
        for prop in multipropietario_temp:
            if prop['run'] == fantasma['run']:
                prop['derecho'] = sobrante_por_fantasma

def ajustar_exceso_por_factor(multipropietario_temp, total_derechos):
    '''Ajusta los valores y retorna el sobrante'''
    factor_ajuste = 100 / total_derechos
    ajustar_derechos_por_factor(multipropietario_temp, factor_ajuste)

def calcular_sobrante(total_objetivo, total_actual):
    '''Calcula el sobrante de derecho'''
    return total_objetivo - total_actual


def obtener_total_derecho_enajenado(multipropietario_temp):
    '''Retorna la suma de los derechos presentes en la multipropietario
     de los enajenantes'''
    return sum(float(prop['derecho']) for prop in multipropietario_temp)
def obtener_fantasmas(multipropietario_temp):
    '''Retorna los enajenantes fantasmas en una lista'''
    return [
        prop for prop in multipropietario_temp if (float(prop['derecho']) == 0 and
                                                   prop['fecha_inscripcion'] is None and
                                                   prop['ano_inscripccion'] is None and
                                                   prop['numero_inscripcion'] is None and
                                                   prop['fojas'] is None and
                                                   prop.get('status') is None) or
                                                   (prop.get('status') == "fantasma")
    ]

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

@ controlador_multipropietarios_bp.route('/buscar_total', methods=['POST'])
def buscar_datos_total():
    '''Retorna filas de la tabla Multipropietario según una búsqueda'''
    comuna = request.json.get("comuna")
    manzana = request.json.get("manzana")
    predio = request.json.get("predio")
    rows = ejecutar_consulta_busqueda_multipropietario_total(comuna, manzana, predio)
    return jsonify(rows)

def ejecutar_consulta_busqueda_multipropietario_total(comuna, manzana, predio):
    '''Ejecuta la consulta SQL para buscar datos en la tabla Multipropietario'''
    query = generar_query_obtener_multipropietarios()
    rows = obtener_datos_multipropietario(query)
    filtered_rows = filtrar_datos_multipropietario_total(rows, str(comuna),
                                                          int(manzana), int(predio))
    return filtered_rows

def obtener_datos_multipropietario(query):
    '''Ejecuta la consulta SQL y retorna los resultados'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def filtrar_datos_multipropietario_total(rows, comuna, manzana, predio):
    """
    Filtra los datos de la lista de diccionarios 'rows' según los parámetros especificados.
    """
    return [
        row for row in rows
        if (row['comuna'] == comuna and
            row['manzana'] == manzana and
            row['predio'] == predio)
    ]
@controlador_multipropietarios_bp.route('/buscar', methods=['POST'])
def buscar_datos():
    '''Retorna filas de la tabla Multipropietario según una búsqueda'''
    comuna = request.json.get("comuna")
    manzana = request.json.get("manzana")
    predio = request.json.get("predio")
    ano = request.json.get("ano")
    if not (comuna and manzana and predio and ano):
        return jsonify({'error': 'Parámetros de búsqueda incompletos'}), 400

    rows = buscar_multipropietarios(comuna, manzana, predio)
    selected_rows = filtrar_filas_por_ano(rows, ano)
    return jsonify(selected_rows)

def buscar_multipropietarios(comuna, manzana, predio):
    '''Busca datos en la tabla Multipropietario según los parámetros dados.'''
    rows = ejecutar_consulta_busqueda_multipropietario()
    return filtrar_datos_multipropietario(rows, str(comuna), int(manzana), int(predio))

def ejecutar_consulta_busqueda_multipropietario():
    '''Ejecuta la consulta SQL para obtener todos los datos de la tabla Multipropietario.'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    query = generar_query_obtener_multipropietarios()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()

def filtrar_datos_multipropietario(rows, comuna, manzana, predio):
    '''Filtra los datos de la lista de diccionarios 'rows' según los parámetros especificados.'''
    return [
        row for row in rows
        if (row['comuna'] == comuna and
            row['manzana'] == manzana and
            row['predio'] == predio)
    ]

def filtrar_filas_por_ano(rows, ano):
    '''Filtra las filas según el año especificado.'''
    key = "ano_vigencia_f" #key asignada para no sobrepasar el largo máximo en la linea 721 y 722
    return [
        row for row in rows
        if (int(row["ano_vigencia_i"])<=int(ano)<=int(row[key] if row[key] is not None else ano) or
            (int(row["ano_vigencia_i"]) <= int(ano) and row[key] is None))
    ]

@ controlador_multipropietarios_bp.route('/clean', methods=['GET'])
def borrar_datos():
    '''Elimina todas las filas de la tabla Multipropietario.'''
    try:
        ejecutar_borrado_multipropietario()
        mensaje = generar_mensaje_borrado_exitoso()
    except Error as e:
        mensaje = generar_mensaje_error(e)
    return jsonify(mensaje)

def generar_mensaje_borrado_exitoso():
    '''Genera un mensaje indicando que los datos fueron borrados exitosamente.'''
    return {'mensaje': 'Datos borrados exitosamente'}

def generar_mensaje_error(e):
    '''Genera un mensaje indicando que hubo un error al borrar los datos.'''
    return {'error': str(e)}
def ejecutar_query_borrado_multipropietario(query):
    '''Ejecuta una consulta SQL y maneja la conexión a la base de datos.'''
    conn = obtener_conexion_db()
    cursor = conn.cursor()
    try:
        ejecutar_cursor_borrado_multipropietario(cursor,conn,query)
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
def ejecutar_cursor_borrado_multipropietario(cursor,conn,query):
    '''Ejecuta la consulta SQL y confirma la transacción.'''
    cursor.execute(query)
    conn.commit()

def ejecutar_borrado_multipropietario():
    '''Ejecuta la consulta SQL para borrar todas las filas de la tabla Multipropietario.'''
    query = generar_query_borrar_multipropietario()
    ejecutar_query_borrado_multipropietario(query)
