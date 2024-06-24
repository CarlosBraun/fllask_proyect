# Entrega 3 Proyecto - "Grupo" 11b

### Se completó la funcionalidad requerida, de esta forma se solucionaron todos los problemas de las entregas pasadas.

Para probar esto se deben instalar las librerías requeridas por la aplicación y se debe correr el backend (v2) y el frontend, ambos con el comando python app.py.

### Se realizaron los test solicitados para cumplir con al menos un 30% del código del backend testeado.

#### Se excluyó el forntend, y los test, de los test y del linter.

Para correr los test se debe ejecutar el comando pytest, que arroja estadisticas de porcentaje de cobertura.

```bash
 pytest

```

Además se puede utilizar otra librería que detalla la cobertura, para esto se debe usar el comando pytest --cov=backendv2/controladores/.

```bash
  pytest --cov=backendv2/controladores/.

```

Se habilitó tanto la busqueda por año que especifica los propietarios en el año buscado, como una busqueda por propiedad de la multipropietario para poder analizar los valores.

El backend podría llegar a caerse sin tener que ver con errores de código, si ese es el caso, favor levantarlo nuevamente y repetir la solicitud. Suele ser por acumulación de requests que maneja mal la terminal.
