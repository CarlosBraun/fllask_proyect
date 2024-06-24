import unittest
from unittest.mock import patch, MagicMock
import controladores.controlador_requests
from controladores.controlador_requests import (obtener_conexion_db,
                                                 inicializar_formularios_agrupados,
                                                 procesar_formulario,
                                                 convertir_formulario_diccionario_a_lista,
                                                 reagrupar_formularios,
                                                 definir_clave_ordenacion,
                                                 ordenar_datos_por_claves,
                                                 ordenar_json_por_claves_ascendente,
                                                 ejecutar_query_formulario,
                                                 agrupar_formularios,
                                                 obtener_formularios,
                                                 procesar_formularios,
                                                 request_algorithm_data,
                                                 ejecutar_query_multipropietario,
                                                 procesar_data_multipropietario,
                                                 ejecutar_limpiar_multipropietario
                                                 )

def limpiar_multipropietario(propiedad):
    '''Elimina los registros de la tabla Multipropietario un año en adelante para cierta propiedad'''
    ano_inicio = int(propiedad['fecha_inscripcion'][:4])
    conn = obtener_conexion_db()
    cursor = conn.cursor()

    try:
        ejecutar_limpiar_multipropietario(cursor, propiedad, ano_inicio)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

class TestLimpiarMultipropietario(unittest.TestCase):

    @patch('tu_modulo.obtener_conexion_db')
    @patch('tu_modulo.ejecutar_limpiar_multipropietario')
    def test_limpiar_multipropietario(self, mock_ejecutar_limpiar, mock_obtener_conexion):
        # Configuración del mock para la conexión y el cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_obtener_conexion.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Datos de prueba
        propiedad = {'fecha_inscripcion': '2020-01-01'}
        ano_inicio = 2020

        # Llamada a la función que se va a probar
        limpiar_multipropietario(propiedad)

        # Verificación de que se obtuvo la conexión a la base de datos
        mock_obtener_conexion.assert_called_once()

        # Verificación de que se creó el cursor
        mock_conn.cursor.assert_called_once()

        # Verificación de que se llamó a la función `ejecutar_limpiar_multipropietario` con los argumentos correctos
        mock_ejecutar_limpiar.called_once_with(mock_cursor, propiedad, ano_inicio)

        # Verificación de que se hizo commit a la conexión
        mock_conn.commit.assert_called_once()

        # Verificación de que se cerró el cursor y la conexión
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('tu_modulo.obtener_conexion_db')
    @patch('tu_modulo.ejecutar_limpiar_multipropietario')
    def test_limpiar_multipropietario_exception(self, mock_ejecutar_limpiar, mock_obtener_conexion):
        # Configuración del mock para la conexión y el cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_obtener_conexion.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Configuración para lanzar una excepción
        mock_ejecutar_limpiar.side_effect = Exception("Test Exception")

        # Datos de prueba
        propiedad = {'fecha_inscripcion': '2020-01-01'}

        # Verificación de que se lanza una excepción
        with self.assertRaises(Exception) as context:
            limpiar_multipropietario(propiedad)
        
        self.assertTrue('Test Exception' in str(context.exception))

        # Verificación de que se hizo rollback a la conexión
        mock_conn.rollback.assert_called_once()

        # Verificación de que se cerró el cursor y la conexión
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
