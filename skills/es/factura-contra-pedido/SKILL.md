---
name: factura-contra-pedido
description: Compara la factura de un proveedor con el pedido y muestra las diferencias de producto, cantidad y precio. Úsala antes de pagar.
---
# Factura contra pedido

## Pasos
1. Pasa el pedido a `pedido.csv` y la factura a `factura.csv`, con las columnas `producto,cantidad,precio`. El precio es por unidad y sin separador de miles.
2. Usa el mismo nombre en los dos archivos solo cuando estés seguro de que es el mismo producto. Si los nombres no coinciden y dudas, déjalos distintos y anota la duda.
3. Muestra las dos tablas a la persona, para que pueda revisar la lectura.
4. Corre `python3 scripts/comparar.py pedido.csv factura.csv` y copia el resultado. No compares de memoria.
5. Escribe un borrador corto para el proveedor que mencione solo las diferencias del programa.

## Lo que no puedes hacer
- Seguir si el programa no corre. Dilo, muestra los datos que leíste y detente. No hagas las cuentas a mano.
- Decir "puedes pagar". Di qué coincide y qué no. Pagar lo decide una persona.
- Adivinar una cifra que no se lee. Escribe "no se lee" y detente.
- Incluir impuestos, fletes o descuentos que no estén en los dos documentos. Anótalos aparte.

## Qué entregas
Las dos tablas, el resultado del programa, las dudas y el borrador.
