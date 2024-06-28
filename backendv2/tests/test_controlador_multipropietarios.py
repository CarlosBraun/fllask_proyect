'''Este módulo se encarga de hacer el testeo al controlador requests'''
import pytest
from controladores.controlador_multipropietarios import (construir_fila_adquirente,
                                                         validar_y_ajustar_fila,
                                                         construir_fila_general,
                                                         construir_fila_distribuir_100,
                                                         generar_registros_form_a_multi,
                                                         revisar_multipropietario,
                                                         inicializar_derechos,
                                                         calcular_derechos_enajenantes,
                                                         calcular_derechos_adquirentes,
                                                         actualizar_ano_vigencia_f,
                                                         obtener_rut_enajenantes_100,
                                                         calcular_total_enajenado_100,
                                                         llevar_a_cero_derechos_enajenantes_100,
                                                         crear_dict_derechos_menos_100,
                                                         actualizar_derechos_menos_100,
                                                         crear_dict_derechos_general,
                                                         actualizar_derechos_general,
                                                         copiar_lista,
                                                         acotar_ano_vigencia,
                                                         ajustar_derecho_negativo,
                                                         sumar_derechos,
                                                         actualizar_registro,
                                                         obtener_fecha_mas_antigua,
                                                         obtener_total_derecho_enajenado,
                                                         obtener_fantasmas,
                                                         eliminar_enas_con_derecho_cero,
                                                         ajustar_derechos_por_factor)

# Dependencies:
# pip install pytest-mock

class TestConstruirFilaAdquirente:
    '''En esta clase se testea la función que construye filas'''

    # correctly constructs a row with valid adquirente and propiedad data
    def test_constructs_row_with_valid_data(self):
        '''Testeo de función'''
        adquirente = {
            'RUNRUT': '12345678-9',
            'derecho': '50%'
        }
        propiedad = {
            'comuna': 'Santiago',
            'manzana': 'A',
            'predio': '123'
        }
        value = {
            'fojas': 100,
            'fecha_inscripcion': '2023-01-01',
            'numero_inscripcion': 1,
            'adquirentes': [adquirente]
        }
        expected_row = {
            'comuna': 'Santiago',
            'manzana': 'A',
            'predio': '123',
            'run': '12345678-9',
            'derecho': '50%',
            'fojas': 100,
            'fecha_inscripcion': '2023-01-01',
            'ano_inscripccion': 2023,
            'numero_inscripcion': 1,
            'ano_vigencia_i': 2023
        }
        assert construir_fila_adquirente(adquirente, propiedad, value) == expected_row

    # handles missing or null values in 'adquirente' dictionary
    def test_handles_missing_or_null_values_in_adquirente(self):
        '''Testeo de función'''
        adquirente = {
            'RUNRUT': None,
            'derecho': None
        }
        propiedad = {
            'comuna': 'Santiago',
            'manzana': 'A',
            'predio': '123'
        }
        value = {
            'fojas': 100,
            'fecha_inscripcion': '2023-01-01',
            'numero_inscripcion': 1,
            'adquirentes': [adquirente]
        }
        expected_row = {
            'comuna': 'Santiago',
            'manzana': 'A',
            'predio': '123',
            'run': None,
            'derecho': None,
            'fojas': 100,
            'fecha_inscripcion': '2023-01-01',
            'ano_inscripccion': 2023,
            'numero_inscripcion': 1,
            'ano_vigencia_i': 2023
        }
        assert construir_fila_adquirente(adquirente, propiedad, value) == expected_row

class TestValidarYAjustarFila:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # returns row when "derecho" is a positive float
    def test_returns_row_when_derecho_is_positive_float(self):
        '''Testeo de función'''
        row = {"derecho": "1.5"}
        result = validar_y_ajustar_fila(row)
        assert result == row

    # returns None when "derecho" is zero
    def test_returns_none_when_derecho_is_zero(self):
        '''Testeo de función'''
        row = {"derecho": "0"}
        result = validar_y_ajustar_fila(row)
        assert result is None

class TestConstruirFilaGeneral:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly constructs a row with valid persona, propiedad, and value inputs
    def test_constructs_row_with_valid_inputs(self):
        '''Testeo de función'''
        persona = {'RUNRUT': '12345678-9', 'derecho': '50%'}
        propiedad = {'comuna': 'Santiago', 'manzana': 'A', 'predio': '1'}
        value = {
            'fojas': 123,
            'fecha_inscripcion': '2023-01-01',
            'numero_inscripcion': 456
        }
        expected = {
            'comuna': 'Santiago',
            'manzana': 'A',
            'predio': '1',
            'run': '12345678-9',
            'derecho': '50%',
            'fojas': 123,
            'fecha_inscripcion': '2023-01-01',
            'ano_inscripccion': 2023,
            'numero_inscripcion': 456,
            'ano_vigencia_i': 2023,
            'ano_vigencia_f': None
        }
        result = construir_fila_general(persona, propiedad, value)
        assert result == expected

class TestConstruirFilaDistribuir100:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly constructs a row with valid input data
    def test_constructs_row_with_valid_input(self):
        '''Testeo de función'''
        persona = {'RUNRUT': '12345678-9', 'derecho': '50'}
        propiedad = {'comuna': 'Santiago', 'manzana': 'A', 'predio': '1'}
        value = {'fojas': 100, 'fecha_inscripcion': '2023-01-01', 'numero_inscripcion': 1}
        a_distribuir = 100
        expected_row = {
            'comuna': 'Santiago',
            'manzana': 'A',
            'predio': '1',
            'run': '12345678-9',
            'derecho': '50.0',
            'fojas': 100,
            'fecha_inscripcion': '2023-01-01',
            'ano_inscripccion': 2023,
            'numero_inscripcion': 1,
            'ano_vigencia_i': 2023
        }
        result = construir_fila_distribuir_100(persona, propiedad, value, a_distribuir)
        assert result == expected_row
class TestGenerarRegistrosFormAMulti:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # handles empty adquirentes and enajenantes lists without errors
    def test_empty_adquirentes_enajenantes(self):
        '''Testeo de función'''
        adquirentes = []
        enajenantes = []
        propiedad = {"id": 1, "name": "Propiedad1"}
        value = {"adquirentes": adquirentes, "enajenantes": enajenantes}
        result = generar_registros_form_a_multi(adquirentes, enajenantes, propiedad, value)
        assert len(result) == 0

class TestRevisarMultipropietario:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # returns the same list when a non-empty list is provided
    def test_returns_same_list_for_non_empty_list(self):
        '''Testeo de función'''
        input_data = [1, 2, 3]
        expected_output = [1, 2, 3]
        assert revisar_multipropietario(input_data) == expected_output

    # handles lists with a single element correctly
    def test_handles_single_element_list(self):
        '''Testeo de función'''
        input_data = [42]
        expected_output = [42]
        assert revisar_multipropietario(input_data) == expected_output

class TestInicializarDerechos:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # initializes dictionary correctly with unique 'run' values
    def test_initializes_dictionary_with_unique_run_values(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '123', 'derecho': '50.0'},
            {'run': '456', 'derecho': '30.0'},
            {'run': '123', 'derecho': '20.0'}
        ]
        expected_output = {'123': 70.0, '456': 30.0}
        assert inicializar_derechos(multipropietario_temp) == expected_output

    # handles non-numeric 'derecho' values gracefully
    def test_handles_non_numeric_derecho_values_gracefully(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '123', 'derecho': '50.0'},
            {'run': '456', 'derecho': 'abc'}
        ]
        with pytest.raises(ValueError):
            inicializar_derechos(multipropietario_temp)

class TestCalcularDerechosEnajenantes:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # Handles an empty list of enajenantes without errors
    def test_handles_empty_list_of_enajenantes(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '12345678-9', 'derecho': '50.0', 'ano_vigencia_f': None},
            {'run': '98765432-1', 'derecho': '30.0', 'ano_vigencia_f': None}
        ]
        enajenantes = []
        derechos = {'12345678-9': 100.0, '98765432-1': 100.0}
        total_enajenado = 0
        result_total_enajenado, conteo = calcular_derechos_enajenantes(enajenantes,
                                 derechos, total_enajenado, multipropietario_temp)
        assert result_total_enajenado == 0
        assert conteo == 0
        assert derechos['12345678-9'] == 100
        assert derechos['98765432-1'] == 100

class TestCalcularDerechosAdquirentes:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly updates 'derechos' dictionary when 'adquirentes' have unique RUNRUT values
    def test_updates_derechos_with_unique_runrut(self):
        '''Testeo de función'''
        adquirentes = [
            {"RUNRUT": "12345678-9", "derecho": 10.0},
            {"RUNRUT": "98765432-1", "derecho": 20.0}
        ]
        derechos = {"12345678-9": 0.0, "98765432-1": 0.0}
        total_adquirido = 0.0
        total_adquirido, conteo = calcular_derechos_adquirentes(adquirentes,
                                             derechos, total_adquirido)
        assert derechos["12345678-9"] == 10
        assert derechos["98765432-1"] == 20
        assert total_adquirido == 30
        assert conteo == 2

    # handles empty 'adquirentes' list without errors
    def test_handles_empty_adquirentes_list(self):
        '''Testeo de función'''
        adquirentes = []
        derechos = {}
        total_adquirido = 0.0
        total_adquirido, conteo = calcular_derechos_adquirentes(adquirentes,
                                                 derechos, total_adquirido)
        assert total_adquirido == 0
        assert conteo == 0

class TestActualizarAnoVigenciaF:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # handles empty list input
    def test_handles_empty_list_input(self):
        '''Testeo de función'''
        elementos = []
        ano = 2023
        resultado = actualizar_ano_vigencia_f(elementos, ano)
        assert not resultado

class TestObtenerRutEnajenantes100:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # returns list of RUNRUTs when 'value' contains multiple enajenantes
    def test_returns_list_of_runruts_with_multiple_enajenantes(self):
        '''Testeo de función'''
        value = {
            "enajenantes": [
                {"RUNRUT": "12345678-9"},
                {"RUNRUT": "98765432-1"}
            ]
        }
        expected = ["12345678-9", "98765432-1"]
        result = obtener_rut_enajenantes_100(value)
        assert result == expected

    # handles empty 'enajenantes' list in 'value'
    def test_handles_empty_enajenantes_list(self):
        '''Testeo de función'''
        value = {
            "enajenantes": []
        }
        expected = []
        result = obtener_rut_enajenantes_100(value)
        assert result == expected

class TestCalcularTotalEnajenado100:
    '''Testeo de función'''

    # calculates total enajenado correctly when all
    # rut_enajenantes are present in multipropietario_temp
    def test_calculates_total_enajenado_correctly(self):
        '''Testeo de función'''
        rut_enajenantes = ["12345678-9", "98765432-1"]
        multipropietario_temp = [
            {"run": "12345678-9", "derecho": "50.0"},
            {"run": "98765432-1", "derecho": "50.0"}
        ]
        result = calcular_total_enajenado_100(rut_enajenantes, multipropietario_temp)
        assert result == 100

    # handles empty rut_enajenantes list
    def test_handles_empty_rut_enajenantes_list(self):
        '''Testeo de función'''
        rut_enajenantes = []
        multipropietario_temp = [
            {"run": "12345678-9", "derecho": "50.0"},
            {"run": "98765432-1", "derecho": "50.0"}
        ]
        result = calcular_total_enajenado_100(rut_enajenantes, multipropietario_temp)
        assert result == 0

class TestLlevarACeroDerechosEnajenantes100:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly sets 'derecho' to 0 for all enajenantes present in multipropietario_temp
    def test_set_derecho_to_zero_for_all_enajenantes(self):
        '''Testeo de función'''
        value = {
            "enajenantes": [
                {"RUNRUT": "12345678-9"},
                {"RUNRUT": "98765432-1"}
            ]
        }
        multipropietario_temp = [
            {"run": "12345678-9", "derecho": 50},
            {"run": "98765432-1", "derecho": 50},
            {"run": "11111111-1", "derecho": 100}
        ]
        llevar_a_cero_derechos_enajenantes_100(value, multipropietario_temp)
        assert multipropietario_temp[0]["derecho"] == 0
        assert multipropietario_temp[1]["derecho"] == 0
        assert multipropietario_temp[2]["derecho"] == 100

    # no enajenantes in value
    def test_no_enajenantes_in_value(self):
        '''Testeo de función'''
        value = {
            "enajenantes": []
        }
        multipropietario_temp = [
            {"run": "12345678-9", "derecho": 50},
            {"run": "98765432-1", "derecho": 50},
            {"run": "11111111-1", "derecho": 100}
        ]
        llevar_a_cero_derechos_enajenantes_100(value, multipropietario_temp)
        assert multipropietario_temp[0]["derecho"] == 50
        assert multipropietario_temp[1]["derecho"] == 50
        assert multipropietario_temp[2]["derecho"] == 100

class TestCrearDictDerechosMenos100:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly sums derechos for multiple entries with the same run
    def test_correctly_sums_derechos_for_same_run(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '12345678-9', 'derecho': '30.0'},
            {'run': '12345678-9', 'derecho': '20.0'},
            {'run': '98765432-1', 'derecho': '50.0'}
        ]
        expected_output = {
            '12345678-9': 50.0,
            '98765432-1': 50.0
        }
        assert crear_dict_derechos_menos_100(multipropietario_temp) == expected_output

    # handles entries with zero derecho values
    def test_handles_zero_derecho_values(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '12345678-9', 'derecho': '0.0'},
            {'run': '98765432-1', 'derecho': '50.0'},
            {'run': '12345678-9', 'derecho': '0.0'}
        ]
        expected_output = {
            '12345678-9': 0.0,
            '98765432-1': 50.0
        }
        assert crear_dict_derechos_menos_100(multipropietario_temp) == expected_output

class TestActualizarDerechosMenos100:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # updates 'derecho' for each 'run' in multipropietario_temp that exists in multipropietario_dict
    def test_updates_derecho_for_existing_run(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '123', 'derecho': 0.0, 'ano_vigencia_i': 0},
            {'run': '456', 'derecho': 0.0, 'ano_vigencia_i': 0}
        ]
        multipropietario_dict = {
            '123': 50.0,
            '456': 50.0
        }
        ano_actual = '2023'
        actualizar_derechos_menos_100(multipropietario_temp, multipropietario_dict, ano_actual)
        assert multipropietario_temp[0]['derecho'] == 50
        assert multipropietario_temp[0]['ano_vigencia_i'] == 2023
        assert multipropietario_temp[1]['derecho'] == 50
        assert multipropietario_temp[1]['ano_vigencia_i'] == 2023

    # handles empty multipropietario_temp list
    def test_handles_empty_multipropietario_temp(self):
        '''Testeo de función'''
        multipropietario_temp = []
        multipropietario_dict = {
            '123': 50.0,
            '456': 50.0
        }
        ano_actual = '2023'
        actualizar_derechos_menos_100(multipropietario_temp, multipropietario_dict, ano_actual)
        assert not multipropietario_temp

class TestCrearDictDerechosGeneral:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly sums 'derecho' values for unique 'run' keys
    def test_correctly_sums_derecho_values_for_unique_run_keys(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '123', 'derecho': '1.5'},
            {'run': '123', 'derecho': '2.5'},
            {'run': '456', 'derecho': '3.0'}
        ]
        expected_output = {'123': 4.0, '456': 3.0}
        assert crear_dict_derechos_general(multipropietario_temp) == expected_output

    # handles an empty list input without errors
    def test_handles_empty_list_input_without_errors(self):
        '''Testeo de función'''
        multipropietario_temp = []
        expected_output = {}
        assert crear_dict_derechos_general(multipropietario_temp) == expected_output

class TestActualizarDerechosGeneral:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # updates 'derecho' for each 'run' present in multipropietario_dict
    def test_updates_derecho_for_each_run(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '123', 'derecho': 0.5, 'ano_vigencia_i': '2020'},
            {'run': '456', 'derecho': 0.3, 'ano_vigencia_i': '2020'}
        ]
        multipropietario_dict = {'123': 0.6, '456': 0.4}
        value = {"fecha_inscripcion": "2023-01-01"}
        actualizar_derechos_general(multipropietario_temp, multipropietario_dict, value)
        assert multipropietario_temp[0]['derecho'] == 0.6
        assert multipropietario_temp[0]['ano_vigencia_i'] == '2023'
        assert multipropietario_temp[1]['derecho'] == 0.4
        assert multipropietario_temp[1]['ano_vigencia_i'] == '2023'

    # handles empty multipropietario_temp list
    def test_handles_empty_multipropietario_temp(self):
        '''Testeo de función'''
        multipropietario_temp = []
        multipropietario_dict = {'123': 0.6, '456': 0.4}
        value = {"fecha_inscripcion": "2023-01-01"}
        actualizar_derechos_general(multipropietario_temp, multipropietario_dict, value)
        assert not multipropietario_temp

class TestCopiarLista:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # copying a list with multiple dictionaries
    def test_copying_list_with_multiple_dicts(self):
        '''Testeo de función'''
        original_list = [{'key1': 'value1'}, {'key2': 'value2'}, {'key3': 'value3'}]
        copied_list = copiar_lista(original_list)
        assert copied_list == original_list
        assert copied_list is not original_list
        for original, copied in zip(original_list, copied_list):
            assert copied is not original

    # copying a list with None values
    def test_copying_list_with_none_values(self):
        '''Testeo de función'''
        original_list = [None, {'key1': 'value1'}, None, {'key2': 'value2'}]
        copied_list = copiar_lista(original_list)
        assert copied_list == original_list
        assert copied_list is not original_list
        for original, copied in zip(original_list, copied_list):
            if original is not None:
                assert copied is not original

class TestAcotarAnoVigencia:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # Sets 'ano_vigencia_f' to ano - 1 if 'ano_vigencia_f' is None
    def test_sets_ano_vigencia_f_to_ano_minus_1_if_none(self):
        '''Testeo de función'''
        registro = {'ano_vigencia_f': None}
        ano = 2023
        resultado = acotar_ano_vigencia(registro, ano)
        assert resultado['ano_vigencia_f'] == 2022

    # Handles registros with 'ano_vigencia_f' explicitly set to None
    def test_handles_registros_with_ano_vigencia_f_none(self):
        '''Testeo de función'''
        registro = {'ano_vigencia_f': None}
        ano = 2025
        resultado = acotar_ano_vigencia(registro, ano)
        assert resultado['ano_vigencia_f'] == 2024

class TestAjustarDerechoNegativo:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # sets derecho to 0 if derecho is negative
    def test_sets_derecho_to_zero_if_negative(self):
        '''Testeo de función'''
        merged_list = [{'derecho': '-5'}, {'derecho': '10'}, {'derecho': '-1.5'}]
        ajustar_derecho_negativo(merged_list)
        assert merged_list[0]['derecho'] == 0
        assert merged_list[1]['derecho'] == '10'
        assert merged_list[2]['derecho'] == 0

    # handles an empty merged_list without errors
    def test_handles_empty_merged_list(self):
        '''Testeo de función'''
        merged_list = []
        ajustar_derecho_negativo(merged_list)
        assert not merged_list

class TestSumarDerechos:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # suma_derechos_correctamente_con_valores_positivos
    def test_suma_derechos_correctamente_con_valores_positivos(self):
        '''Testeo de función'''
        agrupado = {'derecho': 10.0}
        nuevo = {'derecho': 5.0}
        sumar_derechos(agrupado, nuevo)
        assert agrupado['derecho'] == 15

class TestActualizarRegistro:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # updates all fields in 'agrupado' with non-None values from 'nuevo'
    def test_updates_all_fields_with_non_none_values(self):
        '''Testeo de función'''
        agrupado = {'field1': 'value1', 'field2': 'value2', 'field3': None}
        nuevo = {'field1': 'new_value1', 'field2': None, 'field3': 'new_value3'}
        actualizar_registro(agrupado, nuevo)
        assert agrupado == {'field1': 'new_value1', 'field2': 'value2', 'field3': 'new_value3'}

    # handles empty 'agrupado' and non-empty 'nuevo'
    def test_handles_empty_agrupado_and_non_empty_nuevo(self):
        '''Testeo de función'''
        agrupado = {}
        nuevo = {'field1': 'new_value1', 'field2': 'new_value2'}
        actualizar_registro(agrupado, nuevo)
        assert agrupado == {'field1': 'new_value1', 'field2': 'new_value2'}

class TestObtenerFechaMasAntigua:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # fecha_actual is None and fecha_agrupada is not None
    def test_fecha_actual_none_fecha_agrupada_not_none(self):
        '''Testeo de función'''
        fecha_actual = None
        fecha_agrupada = '2023-01-01'
        assert obtener_fecha_mas_antigua(fecha_actual, fecha_agrupada) is True

    # fecha_actual is None and fecha_agrupada is None
    def test_fecha_actual_none_fecha_agrupada_none(self):
        '''Testeo de función'''
        fecha_actual = None
        fecha_agrupada = None
        assert obtener_fecha_mas_antigua(fecha_actual, fecha_agrupada) is True

class TestObtenerTotalDerechoEnajenado:
    '''Testeo de función'''

    # returns correct sum when all 'derecho' values are positive numbers
    def test_returns_correct_sum_with_positive_derecho_values(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '1', 'derecho': 30},
            {'run': '2', 'derecho': 40},
            {'run': '3', 'derecho': 30}
        ]
        resultado = obtener_total_derecho_enajenado(multipropietario_temp)
        assert resultado == 100

    # handles 'derecho' values that are zero
    def test_handles_zero_derecho_values(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '1', 'derecho': 0},
            {'run': '2', 'derecho': 50},
            {'run': '3', 'derecho': 50}
        ]
        resultado = obtener_total_derecho_enajenado(multipropietario_temp)
        assert resultado == 100

class TestObtenerFantasmas:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # returns empty list when no properties are present
    def test_returns_empty_list_when_no_properties_present(self):
        '''Testeo de función'''
        multipropietario_temp = []
        result = obtener_fantasmas(multipropietario_temp)
        assert result == []


class TestEliminarEnasConDerechoCero:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # removes entries with derecho 0
    def test_removes_entries_with_derecho_zero(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'id': 1, 'derecho': '0'},
            {'id': 2, 'derecho': '10'},
            {'id': 3, 'derecho': '-5'}
        ]
        result = eliminar_enas_con_derecho_cero(multipropietario_temp)
        expected = [{'id': 2, 'derecho': '10'}]
        assert result == expected

    # handles empty list without errors
    def test_handles_empty_list(self):
        '''Testeo de función'''
        multipropietario_temp = []
        result = eliminar_enas_con_derecho_cero(multipropietario_temp)
        expected = []
        assert result == expected

class TestAjustarDerechosPorFactor:
    '''En esta clase se testan funciones de el controlador multipropietario'''

    # correctly adjusts rights when factor_ajuste is 1
    def test_correctly_adjusts_rights_when_factor_is_1(self):
        '''Testeo de función'''
        multipropietario_temp = [
            {'run': '1', 'derecho': 30.0},
            {'run': '2', 'derecho': 70.0}
        ]
        factor_ajuste = 1
        resultado = ajustar_derechos_por_factor(multipropietario_temp, factor_ajuste)
        assert resultado == [
            {'run': '1', 'derecho': 30.0},
            {'run': '2', 'derecho': 70.0}
        ]

    # handles empty multipropietario_temp list
    def test_handles_empty_multipropietario_temp_list(self):
        '''Testeo de función'''
        multipropietario_temp = []
        factor_ajuste = 1
        resultado = ajustar_derechos_por_factor(multipropietario_temp, factor_ajuste)
        assert not resultado
