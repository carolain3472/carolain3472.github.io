---
name: cotizar-con-regla
description: Prepara una cotización con la lista de precios y la regla de descuentos del negocio. Úsala cuando llegue un pedido y haya que calcular un total.
---
# Cotizar con regla

Los precios y las reglas están en `reglas.json`. Cámbialos por los de tu negocio antes de usar esta skill.

## Pasos
1. Lee el pedido. Anota cada producto y su cantidad tal como aparecen.
2. Busca cada producto en `reglas.json`. Si el nombre no es claro, si falta una cantidad o si el producto no está, detente y pregunta. No lo reemplaces por uno parecido.
3. Calcula con el programa. No hagas cuentas tú.
   `echo '{"items": [["Café Río 500 g", 12]]}' | python3 scripts/cotizar.py`
   Corre el comando desde la carpeta de esta skill.
4. Copia las líneas que devuelve el programa, sin cambiar ninguna cifra.
5. Escribe un mensaje corto para el cliente con esas cifras.

## Lo que no puedes hacer
- Seguir si el programa no corre. Dilo, muestra los datos que leíste y detente. No hagas las cuentas a mano.
- Dar un descuento que no salga del programa. Si el cliente lo pide, o si alguien dice que siempre se lo dan, escribe: "Eso lo decide" y la persona de `quien_aprueba_excepciones`.
- Prometer una fecha de entrega. No está en las reglas.
- Enviar el mensaje. Es un borrador.

## Qué entregas
Las líneas del cálculo, el borrador y una lista con lo que una persona tiene que decidir. Si no hay nada que decidir, dilo.
