'''
En este módulo se definen las queries que ejecutan otras funciones.
En SQL.
'''

def generar_query_obtener_ultimo_numero():
    '''Genera la consulta SQL para obtener el último número de atención.'''
    return 'SELECT numero_atencion FROM Formulario ORDER BY numero_atencion DESC LIMIT 1'

def generar_query_obtener_formularios():
    '''Genera la consulta SQL para obtener todos los formularios.'''
    return 'SELECT * FROM Formulario'

def generar_query_obtener_formularios_asc():
    '''Genera la consulta SQL para obtener todos los formularios
      en orden por fecha de inscripción ascendente.'''
    return """
        SELECT * FROM Formulario
        WHERE comuna = %s
        AND manzana = %s
        AND predio = %s
        AND fecha_inscripcion >= %s
        ORDER BY fecha_inscripcion ASC
    """

def generar_query_obtener_formulario_unico():
    '''Genera la consulta SQL para obtener formulario único.'''
    return 'SELECT * FROM Formulario WHERE numero_atencion = %s'

def generar_query_borrar_formularios():
    '''Genera la consulta SQL para obtener formulario único.'''
    return 'DELETE FROM Formulario'

def generar_query_insertar_formularios():
    '''Genera la consulta SQL para obtener formulario único.'''
    return '''
                INSERT INTO Formulario(numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion, tipo, RUNRUT, derecho, status, herencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

def generar_query_obtener_multipropietarios():
    '''Genera la consulta SQL para obtener todos los formularios.'''
    return 'SELECT * FROM Multipropietario'

def generar_query_busqueda_multipropietario():
    '''Genera la consulta SQL para buscar datos en la tabla Multipropietario'''
    return """
    SELECT *
    FROM Multipropietario
    WHERE comuna = %s
    AND manzana = %s
    AND predio = %s
    AND (ano_vigencia_f >= %s OR ano_vigencia_f IS NULL)
    """


def generar_query_busqueda_multipropietario_completa():
    '''Genera la consulta SQL para obtener los datos de una Multipropietario sin filtro de año'''
    return """
    SELECT * 
    FROM Multipropietario
    WHERE comuna = %s
    AND manzana = %s   
    AND predio = %s
    """

def generar_query_borrar_multipropietario():
    '''Genera la consulta SQL para borrar todas las filas de la tabla Multipropietario'''
    return 'DELETE FROM Multipropietario'

def generar_query_limpiar_multipropietario():
    '''Genera la consulta SQL para eliminar registros de la tabla Multipropietario para cierta
    propiedad y desde una fecha'''
    return """
    DELETE FROM Multipropietario
    WHERE comuna = %s
    AND manzana = %s
    AND predio = %s
    AND ano_inscripccion >= %s
    """
def generar_query_ingresar_multipropietarios():
    '''Genera la consulta SQL para insertar registros en la tabla Multipropietario'''
    return """
    INSERT INTO Multipropietario (
        comuna, manzana, predio, run, derecho, fojas, fecha_inscripcion, 
        ano_inscripccion, numero_inscripcion, ano_vigencia_i, ano_vigencia_f, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
