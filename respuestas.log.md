# Corrida del agente (2026-09-30 17:51)

Modelo: `deepseek/deepseek-v4-flash-0731`. Top-k de buscar_documentos: 2. Preguntas: 12.

**Total de la corrida:** 30007 tokens de entrada, 2354 de salida, USD 0.003313 según `usage.cost` de OpenRouter.

## A01

**Pregunta:** ¿Cuál es el horario de visita en neonatología para los abuelos?

1. **Modelo**: 1095 tokens de entrada, 90 de salida, USD 0.000126. Pide: buscar_documentos({"consulta": "horario de visita en neonatología para abuelos"})
2. **Tool `buscar_documentos`** con `{"consulta": "horario de visita en neonatología para abuelos"}`:

   ```
   Madre y padre tienen ingreso libre las 24 horas. Los abuelos pueden visitar martes y jueves de 16:00 a 17:00, uno por vez y con la presencia de uno de los padres. Los hermanos del recién nacido no ingresan al sector durante la temporada de virus respiratorios, de mayo a septiembre.
   
   La visita en la sala de puérperas es de 15:00 a 20:00. La persona acompañante de la madre puede quedarse también durante la noche.
   ```
3. **Modelo**: 1280 tokens de entrada, 44 de salida, USD 0.000069. Pide: respuesta final

**Respuesta:**

Los abuelos pueden visitar en neonatología los **martes y jueves de 16:00 a 17:00**, uno por vez y con la presencia de uno de los padres.

**Uso de la pregunta:** 2375 tokens de entrada, 134 de salida, USD 0.000195.

## A02

**Pregunta:** ¿Qué preparación necesita una colonoscopía?

1. **Modelo**: 1087 tokens de entrada, 82 de salida, USD 0.000116. Pide: buscar_documentos({"consulta": "preparación colonoscopía"})
2. **Tool `buscar_documentos`** con `{"consulta": "preparación colonoscopía"}`:

   ```
   Los tres días previos se sigue una dieta sin residuos: sin frutas, verduras, legumbres ni cereales integrales. La tarde anterior se toma la solución evacuante de polietilenglicol, cuatro litros repartidos en cuatro horas. Desde la medianoche solo se permiten líquidos claros, y el ayuno total es de 6 horas antes del turno. El paciente tiene que venir acompañado, porque el estudio se hace con sedación.
   
   Se requiere ayuno de sólidos de 8 horas. El agua se suspende 4 horas antes del estudio. Como también se hace con sedación, el paciente no puede manejar ese día.
   ```
3. **Modelo**: 1294 tokens de entrada, 189 de salida, USD 0.000255. Pide: respuesta final

**Respuesta:**

Según las normas del hospital, la preparación para una colonoscopía incluye:

- **Tres días previos:** dieta sin residuos (sin frutas, verduras, legumbres ni cereales integrales).
- **Tarde anterior:** tomar la solución evacuante de polietilenglicol, cuatro litros repartidos en cuatro horas.
- **Desde la medianoche:** solo líquidos claros; ayuno total de 6 horas antes del turno.
- **Ayuno de sólidos:** 8 horas; el agua se suspende 4 horas antes del estudio.
- **Acompañamiento:** el paciente debe venir acompañado porque el estudio se hace con sedación, y no puede manejar ese día.

**Uso de la pregunta:** 2381 tokens de entrada, 271 de salida, USD 0.000371.

## A03

**Pregunta:** ¿Qué documentos tengo que llevar a la primera consulta con un especialista?

1. **Modelo**: 1093 tokens de entrada, 88 de salida, USD 0.000124. Pide: buscar_documentos({"consulta": "documentos para primera consulta con especialista"})
2. **Tool `buscar_documentos`** con `{"consulta": "documentos para primera consulta con especialista"}`:

   ```
   DNI, credencial de la cobertura de salud, la derivación y los estudios previos relacionados con el motivo de consulta, en papel o en el teléfono.
   
   El día de la internación se presenta en admisión, en planta baja, el DNI, la credencial de la cobertura si la tiene, la orden de internación firmada por el médico y los estudios prequirúrgicos.
   ```
3. **Modelo**: 1247 tokens de entrada, 57 de salida, USD 0.000085. Pide: respuesta final

**Respuesta:**

Para la primera consulta con un especialista tenés que llevar:

- DNI
- Credencial de la cobertura de salud
- La derivación
- Los estudios previos relacionados con el motivo de consulta (en papel o en el teléfono)

**Uso de la pregunta:** 2340 tokens de entrada, 145 de salida, USD 0.000209.

## A04

**Pregunta:** ¿Quiénes pueden donar sangre?

1. **Modelo**: 1085 tokens de entrada, 80 de salida, USD 0.000113. Pide: buscar_documentos({"consulta": "requisitos para donar sangre"})
2. **Tool `buscar_documentos`** con `{"consulta": "requisitos para donar sangre"}`:

   ```
   El servicio de hemoterapia recibe donantes de lunes a sábado de 7:30 a 12:00, en el primer piso.
   
   Pueden donar personas de 18 a 65 años que pesen más de 50 kilos y se sientan bien. No hay que venir en ayunas: se recomienda un desayuno liviano, sin lácteos ni grasas. Entre una donación y la siguiente tienen que pasar al menos 2 meses en los hombres y 3 meses en las mujeres.
   ```
3. **Modelo**: 1266 tokens de entrada, 116 de salida, USD 0.000161. Pide: respuesta final

**Respuesta:**

Pueden donar sangre las personas de 18 a 65 años que pesen más de 50 kilos y se sientan bien. No hace falta ir en ayunas: se recomienda un desayuno liviano, sin lácteos ni grasas. Entre donación y donación deben pasar al menos 2 meses en hombres y 3 meses en mujeres.

El servicio de hemoterapia recibe donantes de lunes a sábado de 7:30 a 12:00, en el primer piso.

**Uso de la pregunta:** 2351 tokens de entrada, 196 de salida, USD 0.000274.

## A05

**Pregunta:** ¿Hay camas libres en terapia intensiva ahora?

1. **Modelo**: 1088 tokens de entrada, 81 de salida, USD 0.000115. Pide: consultar_camas({"sector": "terapia_intensiva"})
2. **Tool `consultar_camas`** con `{"sector": "terapia_intensiva"}`:

   ```
   {"sector": "terapia_intensiva", "fecha": "2026-10-05", "datos": {"total": 12, "ocupadas": 12, "libres": 0}}
   ```
3. **Modelo**: 1197 tokens de entrada, 25 de salida, USD 0.000044. Pide: respuesta final

**Respuesta:**

No, en este momento no hay camas libres en terapia intensiva: las 12 están ocupadas.

**Uso de la pregunta:** 2285 tokens de entrada, 106 de salida, USD 0.000159.

## A06

**Pregunta:** ¿Quién está de guardia en cardiología esta noche?

1. **Modelo**: 1089 tokens de entrada, 78 de salida, USD 0.000111. Pide: consultar_guardia({"especialidad": "cardiologia"})
2. **Tool `consultar_guardia`** con `{"especialidad": "cardiologia"}`:

   ```
   {"especialidad": "cardiologia", "fecha": "2026-10-05", "datos": [{"profesional": "Dr. Julián Ferreyra", "horario": "08:00-20:00"}, {"profesional": "Dra. Paula Benítez", "horario": "20:00-08:00"}]}
   ```
3. **Modelo**: 1231 tokens de entrada, 34 de salida, USD 0.000056. Pide: respuesta final

**Respuesta:**

Esta noche (guardia de 20:00 a 08:00) está de guardia en cardiología la **Dra. Paula Benítez**.

**Uso de la pregunta:** 2320 tokens de entrada, 112 de salida, USD 0.000167.

## A07

**Pregunta:** ¿Cuándo es el próximo turno disponible con traumatología?

1. **Modelo**: 1090 tokens de entrada, 73 de salida, USD 0.000104. Pide: consultar_turnos({"especialidad": "traumatologia"})
2. **Tool `consultar_turnos`** con `{"especialidad": "traumatologia"}`:

   ```
   {"especialidad": "traumatologia", "fecha": "2026-10-05", "datos": ["2026-10-07 08:40", "2026-10-07 09:00", "2026-10-08 14:20"]}
   ```
3. **Modelo**: 1215 tokens de entrada, 27 de salida, USD 0.000047. Pide: respuesta final

**Respuesta:**

El próximo turno disponible con traumatología es el **7 de octubre de 2026 a las 08:40**.

**Uso de la pregunta:** 2305 tokens de entrada, 100 de salida, USD 0.000151.

## A08

**Pregunta:** ¿Tienen enalapril de 10 mg en la farmacia?

1. **Modelo**: 1092 tokens de entrada, 79 de salida, USD 0.000112. Pide: consultar_farmacia({"medicamento": "enalapril 10 mg"})
2. **Tool `consultar_farmacia`** con `{"medicamento": "enalapril 10 mg"}`:

   ```
   {"medicamento": "enalapril 10 mg", "fecha": "2026-10-05", "datos": {"stock": 0, "unidad": "comprimidos", "reposicion": "2026-10-09"}}
   ```
3. **Modelo**: 1215 tokens de entrada, 41 de salida, USD 0.000065. Pide: respuesta final

**Respuesta:**

No, en este momento no hay stock de enalapril 10 mg (0 comprimidos). La reposición está prevista para el 9 de octubre de 2026.

**Uso de la pregunta:** 2307 tokens de entrada, 120 de salida, USD 0.000177.

## A09

**Pregunta:** ¿Cuánto se está esperando hoy en la guardia si me clasifican como verde?

1. **Modelo**: 1097 tokens de entrada, 58 de salida, USD 0.000085. Pide: consultar_espera({})
2. **Tool `consultar_espera`** con `{}`:

   ```
   {"fecha": "2026-10-05", "minutos_por_nivel": {"rojo": 0, "naranja": 7, "amarillo": 48, "verde": 135, "azul": 210}}
   ```
3. **Modelo**: 1195 tokens de entrada, 23 de salida, USD 0.000041. Pide: respuesta final

**Respuesta:**

Para clasificación **verde**, la espera actual en la guardia es de **135 minutos**.

**Uso de la pregunta:** 2292 tokens de entrada, 81 de salida, USD 0.000127.

## A10

**Pregunta:** Quiero internar a mi nene en pediatría, ¿hay lugar y me puedo quedar con él?

1. **Modelo**: 1101 tokens de entrada, 173 de salida, USD 0.000232. Pide: consultar_camas({"sector": "pediatria"}), buscar_documentos({"consulta": "acompañante de paciente pediátrico internado puede quedarse"})
2. **Tool `consultar_camas`** con `{"sector": "pediatria"}`:

   ```
   {"sector": "pediatria", "fecha": "2026-10-05", "datos": {"total": 24, "ocupadas": 17, "libres": 7}}
   ```
3. **Tool `buscar_documentos`** con `{"consulta": "acompañante de paciente pediátrico internado puede quedarse"}`:

   ```
   Se permite un acompañante por paciente internado durante la noche, salvo en terapia intensiva. El acompañante recibe una tarjeta que presenta en el control de acceso.
   
   Si los síntomas empeoran durante la espera, el paciente o su acompañante avisan en el mostrador de triage y la enfermera vuelve a evaluar. La guardia pediátrica tiene su propio triage y su propia sala de espera, con ingreso por la calle Los Tilos.
   ```
4. **Modelo**: 1366 tokens de entrada, 68 de salida, USD 0.000101. Pide: respuesta final

**Respuesta:**

Sí, hay lugar: pediatría tiene 7 camas libres de 24.

Y sí, podés quedarte: se permite un acompañante por paciente internado durante la noche (salvo en terapia intensiva). Te dan una tarjeta que tenés que presentar en el control de acceso.

**Uso de la pregunta:** 2467 tokens de entrada, 241 de salida, USD 0.000333.

## A11

**Pregunta:** Necesito turno con cardiología, ¿cuál es el primero y qué tengo que llevar?

1. **Modelo**: 1098 tokens de entrada, 150 de salida, USD 0.000203. Pide: consultar_turnos({"especialidad": "cardiologia"}), buscar_documentos({"consulta": "requisitos para turno con cardiología, qué documentación llevar"})
2. **Tool `consultar_turnos`** con `{"especialidad": "cardiologia"}`:

   ```
   {"especialidad": "cardiologia", "fecha": "2026-10-05", "datos": ["2026-10-14 09:30", "2026-10-14 10:00", "2026-10-16 15:00"]}
   ```
3. **Tool `buscar_documentos`** con `{"consulta": "requisitos para turno con cardiología, qué documentación llevar"}`:

   ```
   El día de la internación se presenta en admisión, en planta baja, el DNI, la credencial de la cobertura si la tiene, la orden de internación firmada por el médico y los estudios prequirúrgicos.
   
   - Salud Integral Andina: cobertura total en internación; copago de consulta de 2.500 pesos.
   - PrevenSur: cubre consultas e internación; los estudios de alta complejidad necesitan autorización previa, que tarda hasta 72 horas hábiles.
   - Obra Social de Empleados Viales (OSEV): cubre todo sin copago, con la credencial y el último recibo de sueldo.
   ```
4. **Modelo**: 1423 tokens de entrada, 99 de salida, USD 0.000141. Pide: buscar_documentos({"consulta": "qué llevar a una consulta ambulatoria de cardiología, documentación para el turno"})
5. **Tool `buscar_documentos`** con `{"consulta": "qué llevar a una consulta ambulatoria de cardiología, documentación para el turno"}`:

   ```
   El día de la internación se presenta en admisión, en planta baja, el DNI, la credencial de la cobertura si la tiene, la orden de internación firmada por el médico y los estudios prequirúrgicos.
   
   DNI, credencial de la cobertura de salud, la derivación y los estudios previos relacionados con el motivo de consulta, en papel o en el teléfono.
   ```
6. **Modelo**: 1587 tokens de entrada, 110 de salida, USD 0.000157. Pide: respuesta final

**Respuesta:**

El primer turno disponible en cardiología es el **14/10/2026 a las 09:30**.

Para la consulta tenés que llevar:
- DNI
- Credencial de la cobertura de salud (si tenés)
- La derivación
- Estudios previos relacionados con el motivo de consulta (en papel o en el teléfono)

**Uso de la pregunta:** 4108 tokens de entrada, 359 de salida, USD 0.000501.

## A12

**Pregunta:** Me recetaron insulina NPH, ¿la tienen y qué necesito para retirarla?

1. **Modelo**: 1097 tokens de entrada, 178 de salida, USD 0.000239. Pide: consultar_farmacia({"medicamento": "insulina NPH"}), buscar_documentos({"consulta": "requisitos para retirar medicamentos en farmacia"})
2. **Tool `consultar_farmacia`** con `{"medicamento": "insulina NPH"}`:

   ```
   {"medicamento": "insulina NPH", "fecha": "2026-10-05", "datos": {"stock": 0, "unidad": "frascos", "reposicion": "2026-10-12"}}
   ```
3. **Tool `buscar_documentos`** con `{"consulta": "requisitos para retirar medicamentos en farmacia"}`:

   ```
   Los medicamentos de alto costo, como los oncológicos y los biológicos, requieren un formulario de solicitud firmado por el especialista y aprobado por el comité de farmacia, que se reúne los miércoles.
   
   La farmacia de pacientes ambulatorios está en planta baja, junto a admisión, y atiende de lunes a viernes de 8:00 a 20:00. Entrega medicación a pacientes del hospital con receta de un profesional de la institución.
   ```
4. **Modelo**: 1379 tokens de entrada, 311 de salida, USD 0.000412. Pide: respuesta final

**Respuesta:**

Hoy no hay stock de insulina NPH en la farmacia. La reposición está prevista para el 12/10/2026.

Para retirar medicación en la farmacia de pacientes ambulatorios (planta baja, junto a admisión, lunes a viernes de 8:00 a 20:00) necesitás receta de un profesional del hospital.

**Uso de la pregunta:** 2476 tokens de entrada, 489 de salida, USD 0.000651.
