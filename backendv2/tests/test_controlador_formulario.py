'''Este módulo se encarga de hacer el testeo al controlador requests'''
from datetime import datetime # type: ignore
import pytest

from controladores.controlador_formularios import (parsear_fecha,
                                                   obtener_clave,
                                                   actualizar_fecha_inscripcion,
                                                   convertir_a_lista_de_diccionarios,
                                                   obtener_propiedades_agrupadas,
                                                   agrupar_formularios,
                                                   agregar_formulario_a_base_de_datos)
class TestParsearFecha:
    '''En este módulo se realizan test de parseo de fechas'''

    # correctly parses a valid date string in YYYYMMDD format
    def test_correctly_parses_valid_date_string(self):
        fecha = '20230101'
        resultado = parsear_fecha(fecha)
        assert resultado == datetime(2023, 1, 1)

    # returns None for an empty string
    def test_returns_none_for_empty_string(self):
        fecha = ''
        resultado = parsear_fecha(fecha)
        assert resultado is None

    # handles leap year dates correctly
    def test_handles_leap_year_dates_correctly(self):
        fecha = '20000229'  # Leap year date
        resultado = parsear_fecha(fecha)
        assert resultado == datetime(2000, 2, 29)

    # handles dates at the end of the year correctly
    def test_handles_dates_at_end_of_year_correctly(self):
        fecha = '20231231'
        resultado = parsear_fecha(fecha)
        assert resultado == datetime(2023, 12, 31)


    # returns None for a date string with invalid format
    def test_returns_none_for_invalid_date_format(self):
        fecha = '2023-01-01'  # Invalid date format
        resultado = parsear_fecha(fecha)
        assert resultado is None

    # returns None for a date string with non-numeric characters
    def test_returns_none_for_non_numeric_characters(self):
        fecha = '2023abc01'
        resultado = parsear_fecha(fecha)
        assert resultado is None

    # returns None for a date string with invalid month or day values
    def test_returns_none_for_invalid_date_string(self):
        fecha = '20231301'  # Invalid month (13)
        resultado = parsear_fecha(fecha)
        assert resultado is None

    # handles very old dates (e.g., 18000101) correctly
    def test_handles_very_old_dates_correctly(self):
        fecha = '18000101'
        resultado = parsear_fecha(fecha)
        assert resultado is not None
        assert resultado.year == 1800
        assert resultado.month == 1
        assert resultado.day == 1

    # handles future dates (e.g., 30001231) correctly
    def test_handles_future_dates_correctly(self):
        fecha = '30001231'
        resultado = parsear_fecha(fecha)
        assert resultado is not None
        assert resultado.year == 3000
        assert resultado.month == 12
        assert resultado.day == 31

    # handles dates with incorrect length (e.g., YYYYMM, YYYYMMDDDD) correctly
    def test_handles_dates_with_incorrect_length_correctly(self):
        fecha = '202301'
        resultado = parsear_fecha(fecha)
        assert resultado is None

        fecha = '20230101DDDD'
        resultado = parsear_fecha(fecha)
        assert resultado is None

class TestObtenerClave:

    # returns a tuple with correct values for valid input
    def test_returns_tuple_with_correct_values_for_valid_input(self):
        # Arrange
        propiedad = {'comuna': 'Comuna1', 'manzana': 'Manzana1', 'predio': 'Predio1'}
        expected = ('Comuna1', 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # handles properties with missing comuna key
    def test_handles_properties_with_missing_comuna_key(self):
        propiedad = {'manzana': 'Manzana1', 'predio': 'Predio1'}
        with pytest.raises(KeyError):
            obtener_clave(propiedad)

    # handles properties with typical comuna, manzana, and predio values
    def test_handles_typical_values(self):
        '''
        Ahoy! Testing if the function handles properties with typical values like a true pirate!
        '''
        # Arrange
        propiedad = {'comuna': 'Comuna1', 'manzana': 'Manzana1', 'predio': 'Predio1'}
        expected = ('Comuna1', 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # processes properties with string values correctly
    def test_process_properties_with_string_values_correctly(self):
        '''
        Ahoy! Testing if the function processes properties with string values correctly.
        Let's see if the unique key is generated accurately for string values.
        Arrr! Time to sail through the code and check the treasure!
        '''
        # Arrange
        propiedad = {'comuna': 'Comuna1', 'manzana': 'Manzana1', 'predio': 'Predio1'}
        expected = ('Comuna1', 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # handles properties with numeric values in comuna, manzana, and predio
    def test_handles_properties_with_numeric_values(self):
        '''
        Ahoy matey! Testing if the function can handle properties with numeric values.
        Let's see if the function returns the correct unique key for numeric properties.
        Arrr! Time to sail the seas of testing!
        '''
        # Arrange
        propiedad = {'comuna': 123, 'manzana': 456, 'predio': 789}
        expected = (123, 456, 789)

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # works with properties containing additional irrelevant keys
    def test_behaviour_properties_with_irrelevant_keys(self):
        '''
        Test to verify that obtener_clave function works correctly
          with properties containing additional irrelevant keys.
        '''
        # Arrange
        propiedad = {'comuna': 'Comuna1', 'manzana': 'Manzana1',
                      'predio': 'Predio1', 'irrelevant_key': 'value'}
        expected = ('Comuna1', 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # processes properties with empty string values
    def test_process_properties_with_empty_string_values(self):
        '''
        Test to verify that the function handles properties with empty string values correctly.
        '''
        # Arrange
        propiedad = {'comuna': '', 'manzana': 'Manzana1', 'predio': 'Predio1'}
        expected = ('', 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # handles properties with None values for comuna, manzana, or predio
    def test_handles_properties_with_none_values(self):
        '''
        Test to check if obtener_clave handles properties with None values for comuna, manzana, or predio.
        '''
        # Arrange
        propiedad = {'comuna': None, 'manzana': 'Manzana1', 'predio': 'Predio1'}
        expected = (None, 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # processes properties with very long string values
    def test_long_string_values(self):
        '''
        Ahoy! Testing if the function can handle properties with very long string values.
        Let's see if the function still returns the correct unique key for such properties.
        Arrr! Time to sail through the code and check for correctness!
        '''
        # Arrange
        propiedad = {'comuna': 'VeryLongComunaName', 'manzana': 'VeryLongManzanaName', 'predio': 'VeryLongPredioName'}
        expected = ('VeryLongComunaName', 'VeryLongManzanaName', 'VeryLongPredioName')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # handles properties with special characters in comuna, manzana, or predio
    def test_handles_properties_with_special_characters(self):
        '''
        Test to ensure that obtener_clave handles properties with special characters properly.
        '''
        # Arrange
        propiedad = {'comuna': 'Comuna@#$', 'manzana': 'Manzana%^&', 'predio': 'Predio*()'}
        expected = ('Comuna@#$', 'Manzana%^&', 'Predio*()')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # handles properties with mixed data types in comuna, manzana, or predio
    def test_handles_mixed_data_types(self):
        '''
        Test to ensure obtaining unique key handles properties with mixed data types.
        '''
        # Arrange
        propiedad = {'comuna': 123, 'manzana': 'Manzana1', 'predio': True}
        expected = (123, 'Manzana1', True)

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # handles properties with nested dictionaries
    def test_handles_properties_with_nested_dictionaries(self):
        '''
        Test to ensure obtener_clave handles properties with nested dictionaries correctly.
        '''
        # Arrange
        propiedad = {'comuna': 'Comuna1', 'manzana': 'Manzana1', 'predio': 'Predio1'}
        expected = ('Comuna1', 'Manzana1', 'Predio1')

        # Act
        result = obtener_clave(propiedad)

        # Assert
        assert result == expected

    # returns consistent results for properties with similar but not identical values
    def test_returns_consistent_results_for_similar_properties(self):
        '''
        Test to ensure that properties with similar but not identical values return consistent results.
        '''
        # Arrange
        propiedad1 = {'comuna': 'Comuna1', 'manzana': 'Manzana1', 'predio': 'Predio1'}
        propiedad2 = {'comuna': 'Comuna1', 'manzana': 'Manzana2', 'predio': 'Predio1'}

        # Act
        result1 = obtener_clave(propiedad1)
        result2 = obtener_clave(propiedad2)

        # Assert
        assert result1[0] == result2[0]  # Comuna should be the same
        assert result1[2] == result2[2]  # Predio should be the same

class TestActualizarFechaInscripcion:

    # Updates the date when the new date is earlier than the current date
    def test_updates_date_when_new_date_is_earlier(self):
        unique_properties = {'prop1': '2023-10-10'}
        key = 'prop1'
        fecha_inscripcion = '2023-09-09'
    
        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)
    
        assert unique_properties[key] == '2023-09-09'

    # Handles None as fecha_inscripcion gracefully
    def test_handles_none_as_fecha_inscripcion_gracefully(self):
        unique_properties = {'prop1': '2023-10-10'}
        key = 'prop1'
        fecha_inscripcion = None
    
        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)
    
        assert unique_properties[key] == '2023-10-10'

    # Adds a new key with the date if the key does not exist
    def test_adds_new_key_with_date_if_key_does_not_exist(self):  
        unique_properties = {'prop1': '2023-10-10'}
        key = 'prop2'
        fecha_inscripcion = '2023-09-09'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-09-09'

    # Maintains the current date if the new date is later than the current date
    def test_maintains_current_date_if_new_date_is_later(self):
        unique_properties = {'prop1': '2023-10-10'}
        key = 'prop1'
        fecha_inscripcion = '2023-11-15'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-10-10'


    # Handles empty unique_properties dictionary
    def test_handles_empty_unique_properties_dictionary(self):
        unique_properties = {}
        key = 'prop1'
        fecha_inscripcion = '2023-09-09'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-09-09'

    # Handles non-existent key in unique_properties
    def test_handles_non_existent_key(self):
        unique_properties = {}
        key = 'prop1'
        fecha_inscripcion = '2023-09-09'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-09-09'

    # Handles fecha_inscripcion being None when current date is also None
    def test_handles_none_dates(self):
        unique_properties = {'prop1': None}
        key = 'prop1'
        fecha_inscripcion = None

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == None

    # Handles invalid date formats in fecha_inscripcion
    def test_handles_invalid_date_formats(self):
        unique_properties = {'prop1': '2023-10-10'}
        key = 'prop1'
        fecha_inscripcion = 'invalid_date_format'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-10-10'

    # Updates correctly when all dates are the same
    def test_updates_date_when_all_dates_are_same(self):
        unique_properties = {'prop1': '2023-10-10', 'prop2': '2023-10-10', 'prop3': '2023-10-10'}
        key = 'prop1'
        fecha_inscripcion = '2023-10-10'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-10-10'

    # Maintains dictionary integrity when updating dates
    def test_maintains_dictionary_integrity_when_updating_dates(self):
        unique_properties = {'prop1': '2023-10-10'}
        key = 'prop1'
        fecha_inscripcion = '2023-09-09'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2023-09-09'

    # Handles large number of properties efficiently
    def test_handles_large_number_of_properties_efficiently(self):
        unique_properties = {'prop1': '2023-10-10', 'prop2': '2022-05-05', 'prop3': '2024-12-12'}
        key = 'prop2'
        fecha_inscripcion = '2021-01-01'

        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

        assert unique_properties[key] == '2021-01-01'

    # Handles timezone-aware datetime objects
    def test_handles_timezone_aware_datetime_objects(self):
        self.test_updates_date_when_new_date_is_earlier()

class TestConvertirAListaDeDiccionarios:
    '''Test de conversion de listas a diccionarios'''

    # converts unique_properties with multiple entries to a list of dictionaries
    def test_converts_multiple_entries_to_list_of_dicts(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1),
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1',
              'predio': 'predio1', 'fecha_inscripcion': '2020'},
            {'comuna': 'comuna2', 'manzana': 'manzana2',
              'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # handles empty unique_properties gracefully
    def test_handles_empty_unique_properties(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {}
        expected_result = []
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # handles unique_properties with a single entry correctly
    def test_handles_single_entry_correctly(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1)}
        expected_result = [{'comuna': 'comuna1', 'manzana': 'manzana1',
                             'predio': 'predio1', 'fecha_inscripcion': '2020'}]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # formats fecha_inscripcion as a string in 'YYYY' format
    def test_formats_fecha_inscripcion_as_yyyy(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1)}
        expected_result = [{'comuna': 'comuna1', 'manzana': 'manzana1',
                             'predio': 'predio1', 'fecha_inscripcion': '2020'}]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # handles unique_properties without fecha_inscripcion correctly
    def test_handles_unique_properties_without_fecha_inscripcion_correctly(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): None,
            ('comuna2', 'manzana2', 'predio2'): None
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1', 'predio': 'predio1'},
            {'comuna': 'comuna2', 'manzana': 'manzana2', 'predio': 'predio2'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # includes all keys (comuna, manzana, predio) in the output dictionaries
    def test_includes_all_keys_in_output_dicts(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1),
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1',
              'predio': 'predio1', 'fecha_inscripcion': '2020'},
            {'comuna': 'comuna2', 'manzana': 'manzana2',
              'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # processes unique_properties with None as fecha_inscripcion
    def test_processes_unique_properties_with_none_as_fecha_inscripcion(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): None,
            ('comuna2', 'manzana2', 'predio2'): None
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1', 'predio': 'predio1'},
            {'comuna': 'comuna2', 'manzana': 'manzana2', 'predio': 'predio2'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # manages unique_properties with missing keys (comuna, manzana, predio)
    def test_manages_unique_properties_with_missing_keys(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): None,
            ('comuna2', 'manzana2', 'predio2'): None
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1', 'predio': 'predio1'},
            {'comuna': 'comuna2', 'manzana': 'manzana2', 'predio': 'predio2'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # handles large unique_properties efficiently
    def test_handles_large_unique_properties_efficiently(self):
        '''Test de conversion de listas a diccionarios'''
        from datetime import datetime
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1),
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1',
              'predio': 'predio1', 'fecha_inscripcion': '2020'},
            {'comuna': 'comuna2', 'manzana': 'manzana2',
              'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # maintains order of entries in the output list
    def test_maintains_order_of_entries(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1),
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1',
              'predio': 'predio1', 'fecha_inscripcion': '2020'},
            {'comuna': 'comuna2', 'manzana': 'manzana2',
              'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # processes unique_properties with duplicate keys correctly
    def test_processes_unique_properties_correctly(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): datetime(2020, 1, 1),
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1',
              'predio': 'predio1', 'fecha_inscripcion': '2020'},
            {'comuna': 'comuna2', 'manzana': 'manzana2',
              'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # handles unique_properties with mixed valid and invalid entries
    def test_handles_mixed_entries(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): None,
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1', 'predio': 'predio1'},
            {'comuna': 'comuna2', 'manzana': 'manzana2', 'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

    # ensures no data loss during conversion
    def test_converts_unique_properties_to_list_of_dicts(self):
        '''Test de conversion de listas a diccionarios'''
        unique_properties = {
            ('comuna1', 'manzana1', 'predio1'): datetime(2021, 1, 1),
            ('comuna2', 'manzana2', 'predio2'): datetime(2019, 1, 1)
        }
        expected_result = [
            {'comuna': 'comuna1', 'manzana': 'manzana1',
              'predio': 'predio1', 'fecha_inscripcion': '2021'},
            {'comuna': 'comuna2', 'manzana': 'manzana2',
              'predio': 'predio2', 'fecha_inscripcion': '2019'}
        ]
        result = convertir_a_lista_de_diccionarios(unique_properties)
        assert result == expected_result

class TestObtenerPropiedadesAgrupadas:
    '''En esta clase se realizan test para las propiedades'''

    def test_correctly_groups_properties(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # processes an empty list of properties without errors
    def test_process_empty_list(self):
        '''Test para las propiedades agrupadas'''
        '''En esta clase se realizan test para las propiedades'''
        datos_propiedades = []
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        assert not resultado

    # returns the earliest 'fecha_inscripcion' for grouped properties
    def test_returns_earliest_fecha_inscripcion(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '104', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '104', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '104', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # returns a list of dictionaries with the correct format
    def test_handles_properties_with_valid_fecha_inscripcion_format(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '103', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '103', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '103', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # processes properties with invalid 'fecha_inscripcion' format
    def test_process_properties_with_invalid_fecha_inscripcion_format(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': 'invalid_date'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # processes properties with 'fecha_inscripcion' in the future
    def test_properties_with_future_fecha_inscripcion(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20230101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20230202'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20240101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2023'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2024'}
        ]
        assert resultado == esperado

    # handles large lists of properties efficiently
    def test_handles_large_lists_efficiently(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # processes properties with duplicate 'comuna', 'manzana', and 'predio' but different 'fecha_inscripcion'
    def test_process_properties_with_duplicate_comuna_manzana_predio_different_fecha_inscripcion(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # handles properties with different 'comuna', 'manzana', and 'predio' combinations
    def test_handles_properties_with_different_combinations(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # maintains the order of properties in the output list
    def test_maintains_order_of_properties(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # ensures no data loss during the transformation
    def test_no_data_loss_during_transformation(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

    # handles properties with additional irrelevant fields
    def test_handles_properties_with_additional_irrelevant_fields(self):
        '''Test para las propiedades agrupadas'''
        datos_propiedades = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220101', 'irrelevant_field': 'value'},
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '20220102', 'irrelevant_field': 'value'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '20220101', 'irrelevant_field': 'value'}
        ]
        resultado = obtener_propiedades_agrupadas(datos_propiedades)
        esperado = [
            {'comuna': 'A', 'manzana': '1', 'predio': '101', 'fecha_inscripcion': '2022'},
            {'comuna': 'B', 'manzana': '2', 'predio': '202', 'fecha_inscripcion': '2022'}
        ]
        assert resultado == esperado

class TestAgruparFormularios:
    
    # groups rows correctly by 'numero_atencion'
    def test_groups_rows_correctly_by_numero_atencion(self):
        '''Test para las propiedades agrupadas'''
        rows = [
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '12345678-9', 'derecho': '50%', 'tipo': 'adquirente'},
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '98765432-1', 'derecho': '50%', 'tipo': 'enajenante'},
            {'numero_atencion': 2, 'cne': 'cne2', 'comuna': 'comuna2', 'fecha_inscripcion': '2023-02-01', 'fojas': 20, 'herencia': 'herencia2', 'id': 2, 'manzana': 'manzana2', 'numero_inscripcion': 200, 'predio': 'predio2', 'status': 'status2', 'RUNRUT': '12345678-9', 'derecho': '100%', 'tipo': 'adquirente'}
        ]
        expected_output = [
            {
                'numero_atencion': 1,
                'cne': 'cne1',
                'comuna': 'comuna1',
                'fecha_inscripcion': '2023-01-01',
                'fojas': 10,
                'herencia': 'herencia1',
                'id': 1,
                'manzana': 'manzana1',
                'numero_inscripcion': 100,
                'predio': 'predio1',
                'status': 'status1',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '50%'}],
                'enajenantes': [{'RUNRUT': '98765432-1', 'derecho': '50%'}]
            },
            {
                'numero_atencion': 2,
                'cne': 'cne2',
                'comuna': 'comuna2',
                'fecha_inscripcion': '2023-02-01',
                'fojas': 20,
                'herencia': 'herencia2',
                'id': 2,
                'manzana': 'manzana2',
                'numero_inscripcion': 200,
                'predio': 'predio2',
                'status': 'status2',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '100%'}],
                'enajenantes': []
            }
        ]
        assert agrupar_formularios(rows) == expected_output

    # handles empty input list
    def test_handles_empty_input_list(self):
        '''Test para las propiedades agrupadas'''
        rows = []
        expected_output = []
        assert agrupar_formularios(rows) == expected_output

    # handles multiple rows with the same 'numero_atencion'
    def test_handles_multiple_rows_same_numero_atencion(self):
        '''Test para las propiedades agrupadas'''
        rows = [
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '12345678-9', 'derecho': '50%', 'tipo': 'adquirente'},
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '98765432-1', 'derecho': '50%', 'tipo': 'enajenante'},
            {'numero_atencion': 2, 'cne': 'cne2', 'comuna': 'comuna2', 'fecha_inscripcion': '2023-02-01', 'fojas': 20, 'herencia': 'herencia2', 'id': 2, 'manzana': 'manzana2', 'numero_inscripcion': 200, 'predio': 'predio2', 'status': 'status2', 'RUNRUT': '12345678-9', 'derecho': '100%', 'tipo': 'adquirente'}
        ]
        expected_output = [
            {
                'numero_atencion': 1,
                'cne': 'cne1',
                'comuna': 'comuna1',
                'fecha_inscripcion': '2023-01-01',
                'fojas': 10,
                'herencia': 'herencia1',
                'id': 1,
                'manzana': 'manzana1',
                'numero_inscripcion': 100,
                'predio': 'predio1',
                'status': 'status1',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '50%'}],
                'enajenantes': [{'RUNRUT': '98765432-1', 'derecho': '50%'}]
            },
            {
                'numero_atencion': 2,
                'cne': 'cne2',
                'comuna': 'comuna2',
                'fecha_inscripcion': '2023-02-01',
                'fojas': 20,
                'herencia': 'herencia2',
                'id': 2,
                'manzana': 'manzana2',
                'numero_inscripcion': 200,
                'predio': 'predio2',
                'status': 'status2',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '100%'}],
                'enajenantes': []
            }
        ]
        assert agrupar_formularios(rows) == expected_output

    # adds 'adquirentes' to the correct 'numero_atencion'
    def test_adds_adquirentes_to_correct_numero_atencion(self):
        '''Test para las propiedades agrupadas'''
        rows = [
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '12345678-9', 'derecho': '50%', 'tipo': 'adquirente'},
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '98765432-1', 'derecho': '50%', 'tipo': 'enajenante'},
            {'numero_atencion': 2, 'cne': 'cne2', 'comuna': 'comuna2', 'fecha_inscripcion': '2023-02-01', 'fojas': 20, 'herencia': 'herencia2', 'id': 2, 'manzana': 'manzana2', 'numero_inscripcion': 200, 'predio': 'predio2', 'status': 'status2', 'RUNRUT': '12345678-9', 'derecho': '100%', 'tipo': 'adquirente'}
        ]
        expected_output = [
            {
                'numero_atencion': 1,
                'cne': 'cne1',
                'comuna': 'comuna1',
                'fecha_inscripcion': '2023-01-01',
                'fojas': 10,
                'herencia': 'herencia1',
                'id': 1,
                'manzana': 'manzana1',
                'numero_inscripcion': 100,
                'predio': 'predio1',
                'status': 'status1',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '50%'}],
                'enajenantes': [{'RUNRUT': '98765432-1', 'derecho': '50%'}]
            },
            {
                'numero_atencion': 2,
                'cne': 'cne2',
                'comuna': 'comuna2',
                'fecha_inscripcion': '2023-02-01',
                'fojas': 20,
                'herencia': 'herencia2',
                'id': 2,
                'manzana': 'manzana2',
                'numero_inscripcion': 200,
                'predio': 'predio2',
                'status': 'status2',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '100%'}],
                'enajenantes': []
            }
        ]
        assert agrupar_formularios(rows) == expected_output

    # adds 'enajenantes' to the correct 'numero_atencion'
    def test_adds_enajenantes_to_correct_numero_atencion(self):
        '''Test para las propiedades agrupadas'''
        rows = [
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '12345678-9', 'derecho': '50%', 'tipo': 'adquirente'},
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '98765432-1', 'derecho': '50%', 'tipo': 'enajenante'},
            {'numero_atencion': 2, 'cne': 'cne2', 'comuna': 'comuna2', 'fecha_inscripcion': '2023-02-01', 'fojas': 20, 'herencia': 'herencia2', 'id': 2, 'manzana': 'manzana2', 'numero_inscripcion': 200, 'predio': 'predio2', 'status': 'status2', 'RUNRUT': '12345678-9', 'derecho': '100%', 'tipo': 'adquirente'}
        ]
        expected_output = [
            {
                'numero_atencion': 1,
                'cne': 'cne1',
                'comuna': 'comuna1',
                'fecha_inscripcion': '2023-01-01',
                'fojas': 10,
                'herencia': 'herencia1',
                'id': 1,
                'manzana': 'manzana1',
                'numero_inscripcion': 100,
                'predio': 'predio1',
                'status': 'status1',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '50%'}],
                'enajenantes': [{'RUNRUT': '98765432-1', 'derecho': '50%'}]
            },
            {
                'numero_atencion': 2,
                'cne': 'cne2',
                'comuna': 'comuna2',
                'fecha_inscripcion': '2023-02-01',
                'fojas': 20,
                'herencia': 'herencia2',
                'id': 2,
                'manzana': 'manzana2',
                'numero_inscripcion': 200,
                'predio': 'predio2',
                'status': 'status2',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '100%'}],
                'enajenantes': []
            }
        ]
        assert agrupar_formularios(rows) == expected_output

    # ensures no modification to the original input rows
    def test_no_modification_to_original_rows(self):
        '''Test para las propiedades agrupadas'''
        rows = [
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '12345678-9', 'derecho': '50%', 'tipo': 'adquirente'},
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '98765432-1', 'derecho': '50%', 'tipo': 'enajenante'},
            {'numero_atencion': 2, 'cne': 'cne2', 'comuna': 'comuna2', 'fecha_inscripcion': '2023-02-01', 'fojas': 20, 'herencia': 'herencia2', 'id': 2, 'manzana': 'manzana2', 'numero_inscripcion': 200, 'predio': 'predio2', 'status': 'status2', 'RUNRUT': '12345678-9', 'derecho': '100%', 'tipo': 'adquirente'}
        ]
        original_rows = rows.copy()
        agrupar_formularios(rows)
        assert rows == original_rows


    # handles rows with mixed 'tipo' values for the same 'numero_atencion'
    def test_mixed_tipo_values(self):
        '''Test para las propiedades agrupadas'''
        rows = [
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '12345678-9', 'derecho': '50%', 'tipo': 'adquirente'},
            {'numero_atencion': 1, 'cne': 'cne1', 'comuna': 'comuna1', 'fecha_inscripcion': '2023-01-01', 'fojas': 10, 'herencia': 'herencia1', 'id': 1, 'manzana': 'manzana1', 'numero_inscripcion': 100, 'predio': 'predio1', 'status': 'status1', 'RUNRUT': '98765432-1', 'derecho': '50%', 'tipo': 'enajenante'},
            {'numero_atencion': 2, 'cne': 'cne2', 'comuna': 'comuna2', 'fecha_inscripcion': '2023-02-01', 'fojas': 20, 'herencia': 'herencia2', 'id': 2, 'manzana': 'manzana2', 'numero_inscripcion': 200, 'predio': 'predio2', 'status': 'status2', 'RUNRUT': '12345678-9', 'derecho': '100%', 'tipo': 'adquirente'}
        ]
        expected_output = [
            {
                'numero_atencion': 1,
                'cne': 'cne1',
                'comuna': 'comuna1',
                'fecha_inscripcion': '2023-01-01',
                'fojas': 10,
                'herencia': 'herencia1',
                'id': 1,
                'manzana': 'manzana1',
                'numero_inscripcion': 100,
                'predio': 'predio1',
                'status': 'status1',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '50%'}],
                'enajenantes': [{'RUNRUT': '98765432-1', 'derecho': '50%'}]
            },
            {
                'numero_atencion': 2,
                'cne': 'cne2',
                'comuna': 'comuna2',
                'fecha_inscripcion': '2023-02-01',
                'fojas': 20,
                'herencia': 'herencia2',
                'id': 2,
                'manzana': 'manzana2',
                'numero_inscripcion': 200,
                'predio': 'predio2',
                'status': 'status2',
                'adquirentes': [{'RUNRUT': '12345678-9', 'derecho': '100%'}],
                'enajenantes': []
            }
        ]
        assert agrupar_formularios(rows) == expected_output
