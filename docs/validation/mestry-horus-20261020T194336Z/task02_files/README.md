# Saludo

La función `saludar(nombre)` devuelve un saludo con el formato `Hola, nombre!`.
Aplica `strip()` para quitar los espacios al inicio y al final del nombre.
Si el resultado está vacío, lanza `ValueError`.

Ejemplo: `saludar('Ana')` devuelve `Hola, Ana!`.
También `saludar('  Ana  ')` devuelve `Hola, Ana!`.

## Pruebas

Ejecuta desde este directorio:

```sh
python3 -B -m unittest -v
```

Las pruebas usan `unittest` de la biblioteca estándar y comprueban los saludos
para Ana y MESTRY, Ana rodeado de espacios, una cadena vacía y una cadena de
solo espacios. No se necesitan paquetes adicionales. La opción `-B` evita
generar archivos de caché de Python.
