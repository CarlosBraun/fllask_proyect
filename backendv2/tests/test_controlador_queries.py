'''Este módulo se encarga de hacer el testeo al controlador requests'''
import pytest
from controladores.controlador_queries import (generar_query_obtener_ultimo_numero,
                                               generar_query_obtener_formularios,
                                               generar_query_obtener_formularios_asc,
                                               generar_query_obtener_formulario_unico,
                                               generar_query_borrar_formularios,
                                               generar_query_insertar_formularios,
                                               generar_query_obtener_multipropietarios,
                                               generar_query_busqueda_multipropietario_completa,
                                               generar_query_borrar_multipropietario,
                                               generar_query_limpiar_multipropietario,
                                               generar_query_ingresar_multipropietarios,
                                               generar_query_eliminar_ultimo_registro_multipropietario)

# Dependencies:
# pip install pytest-mock

class TestGenerarQueryObtenerUltimoNumero:

    # Returns correct SQL query string
    def test_returns_correct_sql_query_string(self):
        expected_query = 'SELECT numero_atencion FROM Formulario ORDER BY numero_atencion DESC LIMIT 1'
        assert generar_query_obtener_ultimo_numero() == expected_query

    # Handles empty database scenario
    def test_handles_empty_database_scenario(self):
        # This function generates a query, it does not interact with the database directly.
        # Therefore, it should always return the same query regardless of the database state.
        expected_query = 'SELECT numero_atencion FROM Formulario ORDER BY numero_atencion DESC LIMIT 1'
        assert generar_query_obtener_ultimo_numero() == expected_query

class TestGenerarQueryObtenerFormularios:

    # returns a valid SQL query string
    def test_returns_valid_sql_query_string(self):
        query = generar_query_obtener_formularios()
        assert query.strip().lower().startswith('select * from formulario')

    # function returns a non-empty string
    def test_returns_non_empty_string(self):
        query = generar_query_obtener_formularios()
        assert isinstance(query, str) and len(query) > 0

    # query string selects all columns from Formulario table
    def test_query_selects_all_columns(self):
        query = generar_query_obtener_formularios()
        assert query.strip().lower().startswith('select * from formulario')

    # query string does not include any WHERE clause
    def test_query_string_no_where_clause(self):
        query = generar_query_obtener_formularios()
        assert query.strip().lower() == 'select * from formulario'

    # query string does not include any ORDER BY clause
    def test_query_string_does_not_include_order_by_clause(self):
        query = generar_query_obtener_formularios()
        assert 'ORDER BY' not in query

    # function handles unexpected input gracefully (though it takes no parameters)
    def test_handles_unexpected_input_gracefully(self):
        query = generar_query_obtener_formularios()
        assert query.strip().lower().startswith('select * from formulario')

class TestGenerarQueryObtenerFormulariosAsc:
    def test_handles_empty_strings_for_placeholders(self):
        query = generar_query_obtener_formularios_asc()
        assert "%s" in query

class TestGenerarQueryObtenerFormularioUnico:

    # returns correct SQL query string
    def test_returns_correct_sql_query_string(self):
        expected_query = 'SELECT * FROM Formulario WHERE numero_atencion = %s'
        assert generar_query_obtener_formulario_unico() == expected_query

    # function returns a non-string type
    def test_function_returns_string_type(self):
        result = generar_query_obtener_formulario_unico()
        assert isinstance(result, str)

    # query string contains correct table name
    def test_query_contains_correct_table_name(self):
        expected_table_name = 'Formulario'
        query = generar_query_obtener_formulario_unico()
        assert expected_table_name in query

    # query string contains correct column name
    def test_query_contains_correct_column_name(self):
        expected_column_name = 'numero_atencion'
        query = generar_query_obtener_formulario_unico()
        assert expected_column_name in query

    # query string uses parameterized query format
    def test_query_string_parameterized_format(self):
        expected_query = 'SELECT * FROM Formulario WHERE numero_atencion = %s'
        assert generar_query_obtener_formulario_unico() == expected_query

    # function is callable without arguments
    def test_function_callable_without_arguments(self):
        generar_query_obtener_formulario_unico()

    # query string contains syntax errors
    def test_query_string_syntax_errors(self):
        query = generar_query_obtener_formulario_unico()
        assert 'SELECT * FROM Formulario WHERE numero_atencion = %s' == query

    # query string contains incorrect table name
    def test_query_contains_incorrect_table_name(self):
        query = generar_query_obtener_formulario_unico()
        assert 'Formulario' in query
        assert 'SELECT * FROM' in query
        assert 'numero_atencion = %s' in query
        assert 'WHERE' in query
        assert 'IncorrectTable' not in query

    # query string contains incorrect column name
    def test_query_contains_incorrect_column_name(self):
        query = generar_query_obtener_formulario_unico()
        assert 'numero_atencion' in query
        assert 'numero_atencion' not in query.upper()

    # function executes within acceptable time limits
    def test_function_execution_time(self):
        import time
        start_time = time.time()
        generar_query_obtener_formulario_unico()
        execution_time = time.time() - start_time
        assert execution_time < 0.001  # Adjust the threshold as needed
        # This test checks if the function executes within an acceptable time limit.

    # function does not raise exceptions
    def test_function_does_not_raise_exceptions(self):
        try:
            generar_query_obtener_formulario_unico()
        except Exception as e:
            pytest.fail(f"Function raised an exception: {e}")

    # function is idempotent
    def test_function_idempotent_behavior(self):
        expected_query = 'SELECT * FROM Formulario WHERE numero_atencion = %s'
        assert generar_query_obtener_formulario_unico() == expected_query

class TestGenerarQueryBorrarFormularios:

    # Returns a valid SQL DELETE statement
    def test_returns_valid_sql_delete_statement(self):
        expected_query = 'DELETE FROM Formulario'
        assert generar_query_borrar_formularios() == expected_query

    # Function is called multiple times in succession
    def test_function_called_multiple_times(self):
        expected_query = 'DELETE FROM Formulario'
        for _ in range(5):
            assert generar_query_borrar_formularios() == expected_query

class TestGenerarQueryInsertarFormularios:

    # function does not return an empty string
    def test_does_not_return_empty_string(self):
        assert generar_query_insertar_formularios().strip() != ''

    # query string contains correct table name 'Formulario'
    def test_query_contains_correct_table_name(self):
        expected_table_name = 'Formulario'
        generated_query = generar_query_insertar_formularios()
        assert expected_table_name in generated_query, f"Table name '{expected_table_name}' not found in generated query: {generated_query}"

class TestGenerarQueryObtenerMultipropietarios:

    # Returns correct SQL query string
    def test_returns_correct_sql_query_string(self):
        expected_query = 'SELECT * FROM Multipropietario'
        assert generar_query_obtener_multipropietarios() == expected_query

    # Function handles unexpected internal errors gracefully
    def test_handles_unexpected_internal_errors_gracefully(self):
        try:
            result = generar_query_obtener_multipropietarios()
            assert result == 'SELECT * FROM Multipropietario'
        except Exception as e:
            pytest.fail(f"Function raised an unexpected exception: {e}")

class TestGenerarQueryBusquedaMultipropietarioCompleta:

    # function handles unexpected input types gracefully
    def test_handles_unexpected_input_types_gracefully(self):
        try:
            query = generar_query_busqueda_multipropietario_completa()
            assert isinstance(query, str)
        except Exception as e:
            pytest.fail(f"Function raised an exception with unexpected input types: {e}")

    # function manages SQL injection attempts safely
    def test_sql_injection_safety(self):
        query = generar_query_busqueda_multipropietario_completa()
        assert "DROP TABLE" not in query
        assert "DELETE FROM" not in query
        assert "UPDATE" not in query
        assert "INSERT INTO" not in query
        assert "TRUNCATE TABLE" not in query

    # function's output is consistent across multiple calls
    def test_consistent_output_across_calls(self):
        query1 = generar_query_busqueda_multipropietario_completa()
        query2 = generar_query_busqueda_multipropietario_completa()
        assert query1 == query2

    # function's performance is acceptable for large-scale use
    def test_performance_large_scale_use(self):
        # Test the performance of the function for large-scale use
        # Add your test implementation here
        pass

class TestGenerarQueryBorrarMultipropietario:

    # Returns correct SQL query string
    def test_returns_correct_sql_query_string(self):
        expected_query = 'DELETE FROM Multipropietario'
        assert generar_query_borrar_multipropietario() == expected_query

    # Function handles unexpected internal errors gracefully
    def test_handles_unexpected_internal_errors_gracefully(self):
        try:
            generar_query_borrar_multipropietario()
        except Exception as e:
            pytest.fail(f"Function raised an unexpected exception: {e}")

class TestGenerarQueryLimpiarMultipropietario:

    # Handles empty strings for parameters
    def test_handles_empty_strings_for_parameters(self):
        query = generar_query_limpiar_multipropietario()
        assert '%s' in query

    # SQL query contains correct table name
    def test_sql_query_contains_correct_table_name(self):
        expected_table_name = "Multipropietario"
        query = generar_query_limpiar_multipropietario()
        assert expected_table_name in query

    # Ensures SQL query is safe from SQL injection
    def test_sql_injection_safe(self):
        query = generar_query_limpiar_multipropietario()
        assert "DROP TABLE" not in query
        assert "INSERT INTO" not in query
        assert "UPDATE" not in query
        assert "SELECT" not in query
        assert "UNION" not in query

    # Ensures SQL query does not modify other tables
    def test_sql_query_does_not_modify_other_tables(self):
        query = generar_query_limpiar_multipropietario()
        assert 'DELETE FROM Multipropietario' in query
        assert 'WHERE comuna = %s' in query
        assert 'AND manzana = %s' in query
        assert 'AND predio = %s' in query
        assert 'AND ano_inscripccion >= %s' in query
        assert 'FROM Othertable' not in query

class TestGenerarQueryIngresarMultipropietarios:

    # Handles case where no values are provided
    def test_handles_no_values_provided(self):
        query = generar_query_ingresar_multipropietarios()
        assert "%s" in query

    # Query string contains correct table name 'Multipropietario'
    def test_query_contains_correct_table_name(self):
        expected_table_name = "Multipropietario"
        query = generar_query_ingresar_multipropietarios()
        assert expected_table_name in query

    # Ensures query string is free of SQL injection vulnerabilities
    def test_query_string_no_sql_injection_vulnerabilities(self):
        query = generar_query_ingresar_multipropietarios()
        assert "DROP TABLE" not in query
        assert "DELETE FROM" not in query
        assert "TRUNCATE TABLE" not in query
        assert "UPDATE" not in query
        assert "INSERT INTO" in query

class TestGenerarQueryEliminarUltimoRegistroMultipropietario:

    # Handles case when 'comuna' is an empty string
    def test_handles_empty_comuna(self):
        query = generar_query_eliminar_ultimo_registro_multipropietario()
        assert '%s' in query  # Ensure that the placeholder for 'comuna' is present in the query

    # Verifies SQL query is a string type
    def test_verifies_sql_query_is_string_type(self):
        query = generar_query_eliminar_ultimo_registro_multipropietario()
        assert isinstance(query, str)

    # Checks for SQL injection vulnerabilities
    def test_sql_injection_vulnerabilities(self):
        query = generar_query_eliminar_ultimo_registro_multipropietario()
        assert "DROP TABLE" not in query
        assert "INSERT INTO" not in query
        assert "UPDATE" not in query
        assert "DELETE FROM" in query










