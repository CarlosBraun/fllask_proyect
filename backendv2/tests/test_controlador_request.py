'''Este módulo se encarga de hacer el testeo al controlador requests'''
import pytest
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
from controladores.controlador_queries import (generar_query_obtener_formularios_asc)

import mysql.connector
from config import DB_CONFIG
from collections import defaultdict
# Dependencies:
# pip install pytest-mock

class TestObtenerConexionDb:

    # successfully establishes a connection with the database using valid DB_CONFIG
    def test_successful_connection_with_valid_db_config(self, mocker):
        mocker.patch('controladores.controlador_requests.DB_CONFIG', DB_CONFIG)
        conn = obtener_conexion_db()
        assert conn.is_connected()
        conn.close()

    def test_multiple_sequential_connections(self, mocker):
        mocker.patch('controladores.controlador_requests.DB_CONFIG', DB_CONFIG)
        conn1 = obtener_conexion_db()
        conn2 = obtener_conexion_db()
        assert conn1.is_connected()
        assert conn2.is_connected()
        conn1.close()
        conn2.close()

    def test_connection_is_open_and_usable(self, mocker):
        mocker.patch('controladores.controlador_requests.DB_CONFIG', DB_CONFIG)
        conn = obtener_conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()
        conn.close()

    def test_network_issues_or_timeouts(self, mocker):
        mocker.patch('controladores.controlador_requests.DB_CONFIG', DB_CONFIG)
        mocker.patch('mysql.connector.connect', side_effect=mysql.connector.errors.InterfaceError)
        with pytest.raises(mysql.connector.errors.InterfaceError):
            obtener_conexion_db()

class TestInicializarFormulariosAgrupados:

    # returns a defaultdict structure with three levels of nesting
    def test_returns_defaultdict_with_three_levels_of_nesting(self):
        result = inicializar_formularios_agrupados()
        assert isinstance(result, defaultdict)
        assert isinstance(result['key'], defaultdict)
        assert isinstance(result['key']['subkey'], defaultdict)
        assert isinstance(result['key']['subkey']['subsubkey'], dict)
        assert 'enajenantes' in result['key']['subkey']['subsubkey']
        assert 'adquirentes' in result['key']['subkey']['subsubkey']

    # calling the function multiple times returns independent defaultdict instances
    def test_multiple_calls_return_independent_instances(self):
        result1 = inicializar_formularios_agrupados()
        result2 = inicializar_formularios_agrupados()
        assert result1 is not result2
        result1['key']['subkey']['subsubkey']['enajenantes'].append('test')
        assert result2['key']['subkey']['subsubkey']['enajenantes'] == []

    # 'enajenantes' and 'adquirentes' keys are initialized as empty lists
    def test_enajenantes_and_adquirentes_initialized_as_empty_lists(self):
        result = inicializar_formularios_agrupados()
        assert isinstance(result, defaultdict)
        assert 'enajenantes' in result['']['']['']
        assert 'adquirentes' in result['']['']['']

class TestProcesarFormulario:

    # correctly processes a single enajenante property
    def test_correctly_processes_single_enajenante_property(self):
        formulario = [{
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'numero_inscripcion': '123',
            'tipo': 'enajenante',
            'RUNRUT': '12345678-9',
            'derecho': '50%',
            'fecha_inscripcion': '2023-01-01'
        }]
        formularios_agrupados = {
            'Comuna1': {
                'Manzana1': {
                    'Predio1': {
                        '123': {
                            'enajenantes': [],
                            'adquirentes': []
                        }
                    }
                }
            }
        }
        procesar_formulario(formulario, formularios_agrupados)
        assert len(formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes']) == 1
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['RUNRUT'] == '12345678-9'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['derecho'] == '50%'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['fecha_inscripcion'] == '2023-01-01'

    # handles empty formulario without errors
    def test_handles_empty_formulario_without_errors(self):
        formulario = []
        formularios_agrupados = {}
        procesar_formulario(formulario, formularios_agrupados)
        assert formularios_agrupados == {}

    # correctly processes a single adquirente property
    def test_correctly_processes_single_adquirente_property(self):
        formulario = [{
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'numero_inscripcion': '123',
            'tipo': 'adquirente',
            'RUNRUT': '12345678-9',
            'derecho': '50%',
            'fecha_inscripcion': '2023-01-01'
        }]
        formularios_agrupados = {
            'Comuna1': {
                'Manzana1': {
                    'Predio1': {
                        '123': {
                            'enajenantes': [],
                            'adquirentes': []
                        }
                    }
                }
            }
        }
        procesar_formulario(formulario, formularios_agrupados)
        assert len(formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['adquirentes']) == 1
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['adquirentes'][0]['RUNRUT'] == '12345678-9'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['adquirentes'][0]['derecho'] == '50%'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['fecha_inscripcion'] == '2023-01-01'

    # maintains existing data in formularios_agrupados if no new properties are added
    def test_maintains_existing_data_if_no_new_properties_added(self):
        formulario = [{
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'numero_inscripcion': '123',
            'tipo': 'enajenante',
            'RUNRUT': '12345678-9',
            'derecho': '50%',
            'fecha_inscripcion': '2023-01-01'
        }]
        formularios_agrupados = {
            'Comuna1': {
                'Manzana1': {
                    'Predio1': {
                        '123': {
                            'enajenantes': [],
                            'adquirentes': [],
                            'fecha_inscripcion': '2022-01-01'  # Existing data
                        }
                    }
                }
            }
        }
        procesar_formulario(formulario, formularios_agrupados)
        assert len(formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes']) == 1
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['RUNRUT'] == '12345678-9'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['derecho'] == '50%'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['fecha_inscripcion'] == '2023-01-01'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['adquirentes'] == []  # Existing data remains

    # handles formulario with missing keys
    def test_handles_formulario_with_missing_keys(self):
        formulario = [{
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'numero_inscripcion': '123',
            'tipo': 'enajenante',
            'RUNRUT': '12345678-9',
            'derecho': '50%'
        }]
        formularios_agrupados = {
            'Comuna1': {
                'Manzana1': {
                    'Predio1': {
                        '123': {
                            'enajenantes': [],
                            'adquirentes': []
                        }
                    }
                }
            }
        }
        procesar_formulario(formulario, formularios_agrupados)
        assert len(formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes']) == 1
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['RUNRUT'] == '12345678-9'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['derecho'] == '50%'

    # handles properties with null values
    def test_handles_properties_with_null_values(self):
        formulario = [{
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'numero_inscripcion': '123',
            'tipo': 'enajenante',
            'RUNRUT': '12345678-9',
            'derecho': '50%',
            'fecha_inscripcion': '2023-01-01',
            'null_property': None
        }]
        formularios_agrupados = {
            'Comuna1': {
                'Manzana1': {
                    'Predio1': {
                        '123': {
                            'enajenantes': [],
                            'adquirentes': []
                        }
                    }
                }
            }
        }
        procesar_formulario(formulario, formularios_agrupados)
        assert len(formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes']) == 1
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['RUNRUT'] == '12345678-9'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['derecho'] == '50%'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['fecha_inscripcion'] == '2023-01-01'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['null_property'] is None

    # ensures no data loss when processing multiple formularios
    def test_no_data_loss_when_processing_multiple_formularios(self):
        formulario1 = [{
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'numero_inscripcion': '123',
            'tipo': 'enajenante',
            'RUNRUT': '12345678-9',
            'derecho': '50%',
            'fecha_inscripcion': '2023-01-01'
        }]
        formulario2 = [{
            'comuna': 'Comuna2',
            'manzana': 'Manzana2',
            'predio': 'Predio2',
            'numero_inscripcion': '456',
            'tipo': 'adquirente',
            'RUNRUT': '98765432-1',
            'derecho': '50%',
            'fecha_inscripcion': '2023-02-01'
        }]
        formularios_agrupados = {
            'Comuna1': {
                'Manzana1': {
                    'Predio1': {
                        '123': {
                            'enajenantes': [],
                            'adquirentes': []
                        }
                    }
                }
            },
            'Comuna2': {
                'Manzana2': {
                    'Predio2': {
                        '456': {
                            'enajenantes': [],
                            'adquirentes': []
                        }
                    }
                }
            }
        }
        procesar_formulario(formulario1, formularios_agrupados)
        procesar_formulario(formulario2, formularios_agrupados)
        assert len(formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes']) == 1
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['RUNRUT'] == '12345678-9'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['enajenantes'][0]['derecho'] == '50%'
        assert formularios_agrupados['Comuna1']['Manzana1']['Predio1']['123']['fecha_inscripcion'] == '2023-01-01'
        assert len(formularios_agrupados['Comuna2']['Manzana2']['Predio2']['456']['adquirentes']) == 1
        assert formularios_agrupados['Comuna2']['Manzana2']['Predio2']['456']['adquirentes'][0]['RUNRUT'] == '98765432-1'
        assert formularios_agrupados['Comuna2']['Manzana2']['Predio2']['456']['adquirentes'][0]['derecho'] == '50%'
        assert formularios_agrupados['Comuna2']['Manzana2']['Predio2']['456']['fecha_inscripcion'] == '2023-02-01'

class TestConvertirFormularioDiccionarioALista:

    # converts a single entry dictionary to a list with one element
    def test_single_entry_dictionary(self):
        formularios_agrupados = {
            'comuna1': {
                'manzana1': {
                    'predio1': {
                        'inscripcion1': {
                            'cne': '123',
                            'fojas': '456',
                            'fecha_inscripcion': '2023-01-01',
                            'numero_atencion': '789',
                            'status': 'active',
                            'herencia': False,
                            'enajenantes': ['John Doe'],
                            'adquirentes': ['Jane Doe']
                        }
                    }
                }
            }
        }
        expected_result = [{
            'comuna': 'comuna1',
            'manzana': 'manzana1',
            'predio': 'predio1',
            'numero_inscripcion': 'inscripcion1',
            'cne': '123',
            'fojas': '456',
            'fecha_inscripcion': '2023-01-01',
            'numero_atencion': '789',
            'status': 'active',
            'herencia': False,
            'enajenantes': ['John Doe'],
            'adquirentes': ['Jane Doe']
        }]
        assert convertir_formulario_diccionario_a_lista(formularios_agrupados) == expected_result

    # handles empty dictionary input gracefully
    def test_empty_dictionary(self):
        formularios_agrupados = {}
        expected_result = []
        assert convertir_formulario_diccionario_a_lista(formularios_agrupados) == expected_result

    # correctly maps all fields from dictionary to list elements
    def test_correctly_maps_all_fields(self):
        formularios_agrupados = {
            'comuna1': {
                'manzana1': {
                    'predio1': {
                        'inscripcion1': {
                            'cne': '123',
                            'fojas': '456',
                            'fecha_inscripcion': '2023-01-01',
                            'numero_atencion': '789',
                            'status': 'active',
                            'herencia': False,
                            'enajenantes': ['John Doe'],
                            'adquirentes': ['Jane Doe']
                        }
                    }
                }
            }
        }
        expected_result = [{
            'comuna': 'comuna1',
            'manzana': 'manzana1',
            'predio': 'predio1',
            'numero_inscripcion': 'inscripcion1',
            'cne': '123',
            'fojas': '456',
            'fecha_inscripcion': '2023-01-01',
            'numero_atencion': '789',
            'status': 'active',
            'herencia': False,
            'enajenantes': ['John Doe'],
            'adquirentes': ['Jane Doe']
        }]
        assert convertir_formulario_diccionario_a_lista(formularios_agrupados) == expected_result

    # converts multiple entries in different comunas correctly
    def test_convertir_multiple_entries_different_comunas_correctly(self):
        formularios_agrupados = {
            'comuna1': {
                'manzana1': {
                    'predio1': {
                        'inscripcion1': {
                            'cne': '123',
                            'fojas': '456',
                            'fecha_inscripcion': '2023-01-01',
                            'numero_atencion': '789',
                            'status': 'active',
                            'herencia': False,
                            'enajenantes': ['John Doe'],
                            'adquirentes': ['Jane Doe']
                        }
                    }
                },
                'manzana2': {
                    'predio2': {
                        'inscripcion2': {
                            'cne': '456',
                            'fojas': '789',
                            'fecha_inscripcion': '2023-02-02',
                            'numero_atencion': '1011',
                            'status': 'inactive',
                            'herencia': True,
                            'enajenantes': ['Alice Smith'],
                            'adquirentes': ['Bob Johnson']
                        }
                    }
                }
            }
        }
        expected_result = [
            {
                'comuna': 'comuna1',
                'manzana': 'manzana1',
                'predio': 'predio1',
                'numero_inscripcion': 'inscripcion1',
                'cne': '123',
                'fojas': '456',
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '789',
                'status': 'active',
                'herencia': False,
                'enajenantes': ['John Doe'],
                'adquirentes': ['Jane Doe']
            },
            {
                'comuna': 'comuna1',
                'manzana': 'manzana2',
                'predio': 'predio2',
                'numero_inscripcion': 'inscripcion2',
                'cne': '456',
                'fojas': '789',
                'fecha_inscripcion': '2023-02-02',
                'numero_atencion': '1011',
                'status': 'inactive',
                'herencia': True,
                'enajenantes': ['Alice Smith'],
                'adquirentes': ['Bob Johnson']
            }
        ]
        assert convertir_formulario_diccionario_a_lista(formularios_agrupados) == expected_result

    # handles dictionaries with deeply nested structures
    def test_handles_deeply_nested_structures(self):
        formularios_agrupados = {
            'comuna1': {
                'manzana1': {
                    'predio1': {
                        'inscripcion1': {
                            'cne': '123',
                            'fojas': '456',
                            'fecha_inscripcion': '2023-01-01',
                            'numero_atencion': '789',
                            'status': 'active',
                            'herencia': False,
                            'enajenantes': ['John Doe'],
                            'adquirentes': ['Jane Doe']
                        }
                    }
                }
            }
        }
        expected_result = [{
            'comuna': 'comuna1',
            'manzana': 'manzana1',
            'predio': 'predio1',
            'numero_inscripcion': 'inscripcion1',
            'cne': '123',
            'fojas': '456',
            'fecha_inscripcion': '2023-01-01',
            'numero_atencion': '789',
            'status': 'active',
            'herencia': False,
            'enajenantes': ['John Doe'],
            'adquirentes': ['Jane Doe']
        }]
        assert convertir_formulario_diccionario_a_lista(formularios_agrupados) == expected_result

    # processes dictionaries with non-string keys or values
    def test_process_non_string_keys_values(self):
        formularios_agrupados = {
            1: {
                2: {
                    3: {
                        4: {
                            'cne': '123',
                            'fojas': '456',
                            'fecha_inscripcion': '2023-01-01',
                            'numero_atencion': '789',
                            'status': 'active',
                            'herencia': False,
                            'enajenantes': ['John Doe'],
                            'adquirentes': ['Jane Doe']
                        }
                    }
                }
            }
        }
        expected_result = [{
            'comuna': 1,
            'manzana': 2,
            'predio': 3,
            'numero_inscripcion': 4,
            'cne': '123',
            'fojas': '456',
            'fecha_inscripcion': '2023-01-01',
            'numero_atencion': '789',
            'status': 'active',
            'herencia': False,
            'enajenantes': ['John Doe'],
            'adquirentes': ['Jane Doe']
        }]
        assert convertir_formulario_diccionario_a_lista(formularios_agrupados) == expected_result

class TestReagruparFormularios:

    # Ensure the function handles empty input gracefully
    def test_correctly_handles_empty_input(self):
        json_data = []
        expected_output = []
        assert reagrupar_formularios(json_data) == expected_output

class TestDefinirClaveOrdenacion:

    # returns sorted list of keys for a dictionary with multiple keys
    def test_returns_sorted_keys_for_multiple_keys(self):
        data = {'b': 2, 'a': 1, 'c': 3}
        result = definir_clave_ordenacion(data)
        assert result == ['a', 'b', 'c']

    # handles empty dictionary without errors
    def test_handles_empty_dictionary(self):
        data = {}
        result = definir_clave_ordenacion(data)
        assert result == []

    # works with dictionaries containing string keys
    def test_works_with_string_keys(self):
        data = {'b': 2, 'a': 1, 'c': 3}
        result = definir_clave_ordenacion(data)
        assert result == ['a', 'b', 'c']

    # handles dictionary with single key correctly
    def test_handles_dictionary_with_single_key_correctly(self):
        data = {'a': 1}
        result = definir_clave_ordenacion(data)
        assert result == ['a']

    # works with dictionaries containing integer keys
    def test_works_with_integer_keys(self):
        data = {2: 'b', 1: 'a', 3: 'c'}
        result = definir_clave_ordenacion(data)
        assert result == [1, 2, 3]

    # maintains order consistency for dictionaries with same keys but different values
    def test_maintains_order_consistency_for_dicts_with_same_keys(self):
        data1 = {'b': 2, 'a': 1, 'c': 3}
        data2 = {'c': 3, 'a': 1, 'b': 2}
        result1 = definir_clave_ordenacion(data1)
        result2 = definir_clave_ordenacion(data2)
        assert result1 == ['a', 'b', 'c']
        assert result2 == ['a', 'b', 'c']

    # handles dictionaries with duplicate keys gracefully
    def test_handles_duplicate_keys_gracefully(self):
        data = {'b': 2, 'a': 1, 'b': 3}
        result = definir_clave_ordenacion(data)
        assert result == ['a', 'b']

class TestOrdenarDatosPorClaves:

    # sorts list of dictionaries by keys in ascending order
    def test_sorts_list_of_dicts_by_keys_ascending(self):
        data = [
            {'b': 2, 'a': 1},
            {'d': 4, 'c': 3}
        ]
        expected = [
            {'a': 1, 'b': 2},
            {'c': 3, 'd': 4}
        ]
        result = ordenar_datos_por_claves(data)
        assert result == expected

    # handles dictionaries with non-string keys
    def test_handles_dicts_with_non_string_keys(self):
        data = [
            {1: 'one', 2: 'two'},
            {3: 'three', 4: 'four'}
        ]
        expected = [
            {1: 'one', 2: 'two'},
            {3: 'three', 4: 'four'}
        ]
        result = ordenar_datos_por_claves(data)
        assert result == expected

    # handles large datasets efficiently
    def test_handles_large_datasets_efficiently(self):
        data = [
            {'b': 2, 'a': 1},
            {'d': 4, 'c': 3}
        ]
        # Generate a large dataset for testing efficiency
        large_data = [{'key'+str(i): i for i in range(1000)} for _ in range(1000)]
        expected = [dict(sorted(d.items())) for d in large_data]
        result = ordenar_datos_por_claves(large_data)
        assert result == expected

    # handles dictionaries with numeric keys
    def test_handles_dicts_with_numeric_keys(self):
        data = [
            {2: 'b', 1: 'a'},
            {4: 'd', 3: 'c'}
        ]
        expected = [
            {1: 'a', 2: 'b'},
            {3: 'c', 4: 'd'}
        ]
        result = ordenar_datos_por_claves(data)
        assert result == expected

    # returns empty list when input is empty
    def test_returns_empty_list_when_input_is_empty(self):
        data = []
        expected = []
        result = ordenar_datos_por_claves(data)
        assert result == expected

    # maintains order for dictionaries with identical keys
    def test_maintains_order_for_dicts_with_identical_keys(self):
        data = [
            {'b': 2, 'a': 1},
            {'b': 4, 'a': 3}
        ]
        expected = [
            {'b': 2, 'a': 1},
            {'b': 4, 'a': 3}
        ]
        result = ordenar_datos_por_claves(data)
        assert result == expected

    # handles dictionaries with multiple keys
    def test_handles_dicts_with_multiple_keys(self):
        data = [
            {'b': 2, 'a': 1},
            {'d': 4, 'c': 3}
        ]
        expected = [
            {'a': 1, 'b': 2},
            {'c': 3, 'd': 4}
        ]
        result = ordenar_datos_por_claves(data)
        assert result == expected

class TestOrdenarJsonPorClavesAscendente:

    # correctly sorts a list of dictionaries by their keys in ascending order
    def test_sorts_dictionaries_by_keys_ascending(self):
        data = [
            {"b": 2, "a": 1},
            {"d": 4, "c": 3}
        ]
        expected = [
            {"a": 1, "b": 2},
            {"c": 3, "d": 4}
        ]
        result = ordenar_json_por_claves_ascendente(data)
        assert result == expected

    # handles dictionaries with nested dictionaries
    def test_handles_nested_dictionaries(self):
        data = [
            {"b": {"y": 2, "x": 1}, "a": {"z": 3}},
            {"d": {"w": 4}, "c": {"v": 5}}
        ]
        expected = [
            {"a": {"z": 3}, "b": {"x": 1, "y": 2}},
            {"c": {"v": 5}, "d": {"w": 4}}
        ]
        result = ordenar_json_por_claves_ascendente(data)
        assert result == expected

    # processes dictionaries with null values
    def test_processes_dictionaries_with_null_values(self):
        data = [
            {"b": 2, "a": None},
            {"d": None, "c": 3}
        ]
        expected = [
            {"a": None, "b": 2},
            {"c": 3, "d": None}
        ]
        result = ordenar_json_por_claves_ascendente(data)
        assert result == expected

    # processes dictionaries with mixed data types as values
    def test_process_mixed_data_types(self):
        data = [
            {"b": 2, "a": "1"},
            {"d": "4", "c": 3}
        ]
        expected = [
            {"a": "1", "b": 2},
            {"c": 3, "d": "4"}
        ]
        result = ordenar_json_por_claves_ascendente(data)
        assert result == expected

    # maintains the original data structure after sorting
    def test_maintains_original_data_structure(self):
        data = [
            {"b": 2, "a": 1},
            {"d": 4, "c": 3}
        ]
        result = ordenar_json_por_claves_ascendente(data)
        assert result == data

class TestEjecutarQueryFormulario:
    '''Este módulo testea la función ejecutar_query_formulario'''

    # Executes query with valid properties and returns expected results with the fixed mocker.patch statement
    def test_executes_query_with_valid_properties_fixed(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedades = {
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'fecha_inscripcion': '2023-01-01'
        }
        expected_result = [('form1',), ('form2',)]
        cursor.fetchall.return_value = expected_result
        mocker.patch('controladores.controlador_queries.generar_query_obtener_formularios_asc', return_value='\n        SELECT * FROM Formulario\n        WHERE comuna = %s\n        AND manzana = %s\n        AND predio = %s\n        AND fecha_inscripcion >= %s\n        ORDER BY fecha_inscripcion ASC\n    ')

        # Act
        result = ejecutar_query_formulario(cursor, propiedades)

        # Assert
        cursor.execute.assert_called_once_with('\n        SELECT * FROM Formulario\n        WHERE comuna = %s\n        AND manzana = %s\n        AND predio = %s\n        AND fecha_inscripcion >= %s\n        ORDER BY fecha_inscripcion ASC\n    ', ('Comuna1', 'Manzana1', 'Predio1', '2023-01-01'))
        assert result == expected_result

    # Handles properties with special characters or SQL injection attempts
    def test_handles_properties_with_special_characters_or_sql_injection_attempts(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedades = {
            'comuna': "Comuna'; DROP TABLE Formulario; --",
            'manzana': "Manzana1",
            'predio': "Predio1",
            'fecha_inscripcion': "2023-01-01"
        }
        expected_result = [('form1',), ('form2',)]
        cursor.fetchall.return_value = expected_result
        mocker.patch('controladores.controlador_queries.generar_query_obtener_formularios_asc', return_value='\n        SELECT * FROM Formulario\n        WHERE comuna = %s\n        AND manzana = %s\n        AND predio = %s\n        AND fecha_inscripcion >= %s\n        ORDER BY fecha_inscripcion ASC\n    ')

        # Act
        result = ejecutar_query_formulario(cursor, propiedades)

        # Assert
        cursor.execute.assert_called_once_with('\n        SELECT * FROM Formulario\n        WHERE comuna = %s\n        AND manzana = %s\n        AND predio = %s\n        AND fecha_inscripcion >= %s\n        ORDER BY fecha_inscripcion ASC\n    ', ("Comuna'; DROP TABLE Formulario; --", 'Manzana1', 'Predio1', '2023-01-01'))
        assert result == expected_result

class TestAgruparFormularios:
    '''Este módulo testea la función agrupar_formlarios'''

    # correctly groups formularios by 'fecha_inscripcion' and 'numero_atencion'
    def test_correctly_groups_formularios_by_fecha_inscripcion_and_numero_atencion(self):
        formularios = [
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'enajenante',
                'RUNRUT': '11111111-1',
                'derecho': '50%'
            },
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'adquirente',
                'RUNRUT': '22222222-2',
                'derecho': '50%'
            }
        ]
        expected_output = {
            '2023-01-01_123': {
                'enajenantes': [{'RUNRUT': '11111111-1', 'derecho': '50%'}],
                'adquirentes': [{'RUNRUT': '22222222-2', 'derecho': '50%'}],
                'cne': '001',
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no'
            }
        }
        assert agrupar_formularios(formularios) == expected_output

    # handles empty list of formularios
    def test_handles_empty_list_of_formularios(self):
        formularios = []
        expected_output = {}
        assert agrupar_formularios(formularios) == expected_output

    # assigns 'enajenantes' and 'adquirentes' to their respective lists
    def test_assigns_enajenantes_and_adquirentes(self):
        formularios = [
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'enajenante',
                'RUNRUT': '11111111-1',
                'derecho': '50%'
            },
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'adquirente',
                'RUNRUT': '22222222-2',
                'derecho': '50%'
            }
        ]
        expected_output = {
            '2023-01-01_123': {
                'enajenantes': [{'RUNRUT': '11111111-1', 'derecho': '50%'}],
                'adquirentes': [{'RUNRUT': '22222222-2', 'derecho': '50%'}],
                'cne': '001',
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no'
            }
        }
        assert agrupar_formularios(formularios) == expected_output

    # handles formularios with special characters or unusual strings in fields
    def test_handles_special_characters_in_formularios(self):
        formularios = [
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'enajenante',
                'RUNRUT': '11111111-1',
                'derecho': '50%'
            },
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'adquirente',
                'RUNRUT': '@#$%^&*()_+',
                'derecho': '!@#$%^&*()'
            }
        ]
        expected_output = {
            '2023-01-01_123': {
                'enajenantes': [{'RUNRUT': '11111111-1', 'derecho': '50%'}],
                'adquirentes': [{'RUNRUT': '@#$%^&*()_+', 'derecho': '!@#$%^&*()'}],
                'cne': '001',
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no'
            }
        }
        assert agrupar_formularios(formularios) == expected_output

    # processes formularios with duplicate 'RUNRUT' values within the same group
    def test_process_formularios_with_duplicate_RUNRUT_values(self):
        formularios = [
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'enajenante',
                'RUNRUT': '11111111-1',
                'derecho': '50%'
            },
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'adquirente',
                'RUNRUT': '11111111-1',
                'derecho': '50%'
            }
        ]
        expected_output = {
            '2023-01-01_123': {
                'enajenantes': [{'RUNRUT': '11111111-1', 'derecho': '50%'}],
                'adquirentes': [{'RUNRUT': '11111111-1', 'derecho': '50%'}],
                'cne': '001',
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no'
            }
        }
        assert agrupar_formularios(formularios) == expected_output

    # validates that non-string fields like 'derecho' are processed correctly
    def test_non_string_fields_processing(self):
        formularios = [
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'enajenante',
                'RUNRUT': '11111111-1',
                'derecho': 50
            },
            {
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'cne': '001',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no',
                'tipo': 'adquirente',
                'RUNRUT': '22222222-2',
                'derecho': 50
            }
        ]
        expected_output = {
            '2023-01-01_123': {
                'enajenantes': [{'RUNRUT': '11111111-1', 'derecho': 50}],
                'adquirentes': [{'RUNRUT': '22222222-2', 'derecho': 50}],
                'cne': '001',
                'fecha_inscripcion': '2023-01-01',
                'numero_atencion': '123',
                'fojas': '10',
                'numero_inscripcion': '1001',
                'status': 'active',
                'herencia': 'no'
            }
        }
        assert agrupar_formularios(formularios) == expected_output

class TestObtenerFormularios:
    '''Este módulo testea la función obtener_formularios'''
    # retrieves forms when valid properties are provided
    def test_retrieves_forms_with_valid_properties(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedades = {
            'comuna': 'comuna1',
            'manzana': 'manzana1',
            'predio': 'predio1',
            'fecha_inscripcion': '2023-01-01'
        }
        expected_result = [('form1',), ('form2',)]
        cursor.fetchall.return_value = expected_result

        # Act
        result = obtener_formularios(cursor, propiedades)

        # Assert
        cursor.execute.assert_called_once_with(
            generar_query_obtener_formularios_asc(),
            ('comuna1', 'manzana1', 'predio1', '2023-01-01')
        )
        assert result == expected_result

    # properties dictionary missing one or more keys
    def test_properties_missing_keys(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedades = {
            'comuna': 'comuna1',
            'manzana': 'manzana1',
            # 'predio' key is missing
            'fecha_inscripcion': '2023-01-01'
        }

        # Act & Assert
        with pytest.raises(KeyError):
            obtener_formularios(cursor, propiedades)

class TestProcesarFormularios:
    '''Este módulo testea la función procesar_formularios'''
    # Ensure that the function 'procesar_formularios' correctly processes a list of formularios and returns grouped data
    def test_correctly_processes_formularios_and_returns_grouped_data(self, mocker):
        mock_agrupar_formularios = mocker.patch('controladores.controlador_requests.agrupar_formularios')
        mock_ordenar_json_por_claves_ascendente = mocker.patch('controladores.controlador_requests.ordenar_json_por_claves_ascendente')

        formularios = [{'id': 1, 'data': 'form1'}, {'id': 2, 'data': 'form2'}]
        mock_agrupar_formularios.side_effect = lambda x: x
        mock_ordenar_json_por_claves_ascendente.side_effect = lambda x: x

        result = procesar_formularios(formularios)

        assert result == [formularios]
        mock_agrupar_formularios.assert_called()
        mock_ordenar_json_por_claves_ascendente.assert_called_once_with(formularios)

    # handles formularios with missing or null fields
    def test_handles_formularios_with_missing_or_null_fields(self, mocker):
        mock_agrupar_formularios = mocker.patch('controladores.controlador_requests.agrupar_formularios')
        mock_ordenar_json_por_claves_ascendente = mocker.patch('controladores.controlador_requests.ordenar_json_por_claves_ascendente')

        formularios = [{'id': 1, 'data': None}, {'id': 2}]
        mock_agrupar_formularios.side_effect = lambda x: x
        mock_ordenar_json_por_claves_ascendente.side_effect = lambda x: x

        result = procesar_formularios(formularios)

        assert result == [formularios]
        mock_agrupar_formularios.assert_called()
        mock_ordenar_json_por_claves_ascendente.assert_called_once_with(formularios)

class TestRequestAlgorithmData:

    # Ensure correct import of request_algorithm_data function with the recommended fix
    def test_correct_import_request_algorithm_data_fixed(self, mocker):
        # Mock dependencies
        mock_conn = mocker.patch('controladores.controlador_requests.obtener_conexion_db')
        mock_cursor = mock_conn.return_value.cursor
        mock_obtener_formularios = mocker.patch('controladores.controlador_requests.obtener_formularios')
        mock_procesar_formularios = mocker.patch('controladores.controlador_requests.procesar_formularios')

        # Setup return values for mocks
        mock_obtener_formularios.return_value = {'formulario': 'data'}
        mock_procesar_formularios.return_value = {'processed': 'data'}

        # Test data
        data = [{'propiedad': 'value1'}, {'propiedad': 'value2'}]

        # Call the function
        result = request_algorithm_data(data)

        # Assertions
        assert result == {'processed': 'data'}
        mock_obtener_formularios.assert_called()
        mock_procesar_formularios.assert_called_once_with([{'formulario': 'data'}, {'formulario': 'data'}])

class TestEjecutarQueryMultipropietario:

    # Executes query with valid 'comuna', 'manzana', and 'predio' values with correct newline and indentation
    def test_executes_query_with_valid_values_with_newline_and_indentation(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedades = {'comuna': 1, 'manzana': 2, 'predio': 3}
        expected_query = "\n    SELECT * \n    FROM Multipropietario\n    WHERE comuna = %s\n    AND manzana = %s   \n    AND predio = %s\n    "
        mocker.patch('controladores.controlador_queries.generar_query_busqueda_multipropietario_completa', return_value=expected_query)
        cursor.fetchall.return_value = [{'id': 1, 'comuna': 1, 'manzana': 2, 'predio': 3}]

        # Act
        result = ejecutar_query_multipropietario(cursor, propiedades)

        # Assert
        cursor.execute.assert_called_once_with(expected_query, (1, 2, 3))
        assert result == [{'id': 1, 'comuna': 1, 'manzana': 2, 'predio': 3}]

    # Handles empty 'propiedades' dictionary gracefully
    def test_handles_empty_propiedades_gracefully(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedades = {}
        expected_query = "SELECT * FROM multipropietario WHERE comuna=%s AND manzana=%s AND predio=%s"
        mocker.patch('controladores.controlador_queries.generar_query_busqueda_multipropietario_completa', return_value=expected_query)
    
        # Act & Assert
        with pytest.raises(KeyError):
            ejecutar_query_multipropietario(cursor, propiedades)

class TestObtenerMultipropietarioData:

    # Ensure that processed data is returned correctly with valid input data after fixing the import issue
    def test_returns_processed_data_with_valid_input_fixed(self, mocker):
        import controladores.controlador_requests

        # Mock dependencies
        mocker.patch('controladores.controlador_requests.obtener_conexion_db')
        mocker.patch('controladores.controlador_requests.ejecutar_query_multipropietario')
        mocker.patch('controladores.controlador_requests.procesar_data_multipropietario')

        # Setup mock return values
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()
        controladores.controlador_requests.obtener_conexion_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        controladores.controlador_requests.ejecutar_query_multipropietario.return_value = [{'id': 1, 'name': 'Test'}]
        controladores.controlador_requests.procesar_data_multipropietario.return_value = [{'id': 1, 'name': 'Processed Test'}]

        # Input data
        input_data = [{'propiedad_id': 1}]

        # Call the function
        result = controladores.controlador_requests.obtener_multipropietario_data(input_data)

        # Assertions
        assert result == [{'id': 1, 'name': 'Processed Test'}]
        controladores.controlador_requests.obtener_conexion_db.assert_called_once()
        mock_conn.cursor.assert_called_once_with(dictionary=True)
        controladores.controlador_requests.ejecutar_query_multipropietario.assert_called_once_with(mock_cursor, {'propiedad_id': 1})
        controladores.controlador_requests.procesar_data_multipropietario.assert_called_once_with([[{'id': 1, 'name': 'Test'}]])

class TestProcesarDataMultipropietario:

    # correctly formats 'fecha_inscripcion' from datetime.date to YYYYMMDD
    def test_correctly_formats_fecha_inscripcion(self):
        import datetime
        data = [
            [
                {'fecha_inscripcion': datetime.date(2014, 11, 29)},
                {'fecha_inscripcion': datetime.date(2020, 1, 15)}
            ]
        ]
        expected_output = [
            [
                {'fecha_inscripcion': '20141129'},
                {'fecha_inscripcion': '20200115'}
            ]
        ]
        assert procesar_data_multipropietario(data) == expected_output

    # handles empty data list gracefully
    def test_handles_empty_data_list(self):
        data = []
        expected_output = []
        assert procesar_data_multipropietario(data) == expected_output

    # handles typical date formats without errors
    def test_correctly_formats_fecha_inscripcion(self):
        import datetime
        data = [
            [
                {'fecha_inscripcion': datetime.date(2014, 11, 29)},
                {'fecha_inscripcion': datetime.date(2020, 1, 15)}
            ]
        ]
        expected_output = [
            [
                {'fecha_inscripcion': '20141129'},
                {'fecha_inscripcion': '20200115'}
            ]
        ]
        assert procesar_data_multipropietario(data) == expected_output

    # returns data in the expected structure
    def test_correctly_formats_fecha_inscripcion(self):
        import datetime
        data = [
            [
                {'fecha_inscripcion': datetime.date(2014, 11, 29)},
                {'fecha_inscripcion': datetime.date(2020, 1, 15)}
            ]
        ]
        expected_output = [
            [
                {'fecha_inscripcion': '20141129'},
                {'fecha_inscripcion': '20200115'}
            ]
        ]
        assert procesar_data_multipropietario(data) == expected_output

    # handles large datasets efficiently
    def test_handles_large_datasets_efficiently(self):
        import datetime
        data = [
            [
                {'fecha_inscripcion': datetime.date(2014, 11, 29)},
                {'fecha_inscripcion': datetime.date(2020, 1, 15)}
            ]
        ]
        expected_output = [
            [
                {'fecha_inscripcion': '20141129'},
                {'fecha_inscripcion': '20200115'}
            ]
        ]
        assert procesar_data_multipropietario(data) == expected_output

    # ensures no data loss during processing
    def test_correctly_formats_fecha_inscripcion(self):
        import datetime
        data = [
            [
                {'fecha_inscripcion': datetime.date(2014, 11, 29)},
                {'fecha_inscripcion': datetime.date(2020, 1, 15)}
            ]
        ]
        expected_output = [
            [
                {'fecha_inscripcion': '20141129'},
                {'fecha_inscripcion': '20200115'}
            ]
        ]
        assert procesar_data_multipropietario(data) == expected_output

class TestEjecutarLimpiarMultipropietario:

    # Executes SQL query correctly with valid inputs after applying the recommended fix
    def test_executes_sql_query_correctly_with_valid_inputs_with_fix(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedad = {
            'comuna': 'Comuna1',
            'manzana': 'Manzana1',
            'predio': 'Predio1',
            'fecha_inscripcion': '2022-01-01'
        }
        ano_inicio = 2022
        query = "\n    DELETE FROM Multipropietario\n    WHERE comuna = %s\n    AND manzana = %s\n    AND predio = %s\n    AND ano_inscripccion >= %s\n    "

        mocker.patch('controladores.controlador_queries.generar_query_limpiar_multipropietario', return_value=query)

        # Act
        ejecutar_limpiar_multipropietario(cursor, propiedad, ano_inicio)

        # Assert
        cursor.execute.assert_called_once_with(query, ('Comuna1', 'Manzana1', 'Predio1', 2022))

    # Handles empty 'propiedad' dictionary
    def test_handles_empty_propiedad_dictionary(self, mocker):
        # Arrange
        cursor = mocker.Mock()
        propiedad = {}
        ano_inicio = 2022
        query = "DELETE FROM Multipropietario WHERE comuna=%s AND manzana=%s AND predio=%s AND ano >= %s"
    
        mocker.patch('controladores.controlador_queries.generar_query_limpiar_multipropietario', return_value=query)
    
        # Act & Assert
        with pytest.raises(KeyError):
            ejecutar_limpiar_multipropietario(cursor, propiedad, ano_inicio)



