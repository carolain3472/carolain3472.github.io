---
name: cartera-del-lunes
description: Ordena las facturas por cobrar según los días de vencidas y prepara un borrador de cobro para cada cliente. Úsala una vez a la semana.
---
# Cartera del lunes

## Pasos
1. Pide un archivo `cartera.csv` con las columnas `cliente,factura,valor,vence,nota`. La fecha va como 2026-11-25 y el valor sin puntos. Con códigos en lugar de nombres funciona igual.
2. Corre `python3 scripts/cartera.py cartera.csv 2026-11-25`, con la fecha de hoy, y copia el resultado sin cambiar cifras.
3. Escribe un borrador por cliente que deba algo vencido. Si tiene varias facturas, un solo mensaje.
   - 1 a 15 días: un recordatorio. Supón que se le pasó.
   - 16 a 45 días: pregunta si hubo un problema y pide una fecha.
   - Más de 45 días: no escribas el mensaje. Ponlo en la lista para llamar.
4. Si la nota habla de un reclamo, un acuerdo o una enfermedad, no escribas cobro. Ponlo en la lista para decidir.

## Lo que no puedes hacer
- Seguir si el programa no corre. Dilo, muestra los datos que leíste y detente. No hagas las cuentas a mano.
- Amenazar, hablar de reportes o de abogados, o inventar intereses.
- Ofrecer descuentos o plazos.
- Enviar mensajes.

## Qué entregas
La tabla del programa, los borradores, la lista para llamar y la lista para decidir.
