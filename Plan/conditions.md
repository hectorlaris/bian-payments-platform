[1]: ¿Cuál es el alcance del "proyecto inicial" que quieres planear ahora?
a. **Prueba de concepto (PoC)** - Un solo dominio/capability BIAN end-to-end para validar el enfoque arquitectónico
b. **MVP productivo** - Un conjunto reducido de servicios de negocio listos para un entorno controlado (2-3 dominios)
c. **Fundaciones de plataforma** - Bootstrap de la plataforma (governance, plantillas API-first, backbone de eventos, CI/CD, landing zone AWS) sin un dominio funcional específico todavía
d. **Otro** - Descríbelo tú


[2]: ¿Qué dominio o capability de negocio BIAN quieres abordar primero como caso de referencia?
a. **Payments / Payment Execution** - Muy alineado con ISO 20022 (pain/pacs) y flujos de pago
b. **Current Account / Deposits** - Gestión de cuentas y movimientos
c. **Customer / Party Data Management** - Onboarding y datos de cliente
d. **Otro** - Indica el Service Domain BIAN específico (ej. Payment Order, Card Transaction, etc.)

[3]: Sobre el stack tecnológico de implementación, ¿qué prefieres dado tu perfil?
a. **ASP.NET Core (C#)** - Para los microservicios de dominio y APIs
b. **Python (FastAPI)** - Para los microservicios de dominio y APIs
c. **Híbrido** - .NET para servicios core de dominio y Python para componentes de datos/eventos/integración
d. **Otro** - Descríbelo tú

----
	1=b, 2=a, 3=c
	
	Alcance (1=b): MVP productivo con 2-3 dominios listos para un entorno controlado.
	Dominio de referencia (2=a): Payments / Payment Execution, alineado con ISO 20022 (pain/pacs).
	Stack (3=c): Híbrido - .NET (ASP.NET Core) para servicios core de dominio + Python para datos/eventos/integración.
	Esto define un MVP centrado en pagos. Voy a afinar el segundo bloque para entender fronteras del dominio, integración y restricciones AWS/EDA.
	
----

[4]: Para el MVP de Payments, ¿qué Service Domains BIAN y flujo de pago quieres cubrir?
a. **Payment Order + Payment Execution** - Iniciación de la orden y ejecución (flujo mínimo end-to-end)
b. **Payment Order + Payment Execution + Payment Initiation** - Incluye canal de iniciación (ej. desde app/cliente)
c. **Payment Execution + Payment Reconciliation** - Ejecución más conciliación/estado
d. **Otro** - Indica los Service Domains BIAN específicos que quieres

[5]: ¿Cómo procesará realmente el pago el MVP en este entorno controlado?
a. **Simulado (mock rail)** - Un simulador interno de red de pagos/liquidación para validar flujo y mensajería ISO 20022 sin conectar a rieles reales
b. **Sandbox externo** - Conectar a un sandbox de un riel/procesador (ej. RTP, SEPA, ACH sandbox); indícalo
c. **Ambos** - Mock por defecto con capa de adaptador lista para sandbox externo
d. **Otro** - Descríbelo

[6]: Para EDA en AWS, ¿qué backbone de eventos y estilo de mensajería prefieres?
a. **Amazon MSK (Kafka)** - Event streaming, event sourcing, mayor control y throughput
b. **EventBridge + SQS/SNS** - Serverless, menor operación, integración nativa AWS
c. **Kafka para eventos de dominio + EventBridge para integración/enrutamiento** - Híbrido
d. **Otro / aún no decidido** - Quiero tu recomendación basada en el caso

----
	4=b, 5=c, 6=c
	
	Service Domains (4=b): Payment Initiation + Payment Order + Payment Execution (flujo end-to-end desde canal de iniciación).
	Procesamiento (5=c): Ambos - mock rail por defecto con adaptador listo para sandbox externo.
	EDA (6=c): Híbrido - Kafka (MSK) para eventos de dominio + EventBridge para integración/enrutamiento.
	Último bloque para cerrar requisitos antes de investigar y armar el plan. Aquí me enfoco en seguridad/compliance, patrones de datos y criterios de éxito.



Una nota profesional: elegiste la seguridad básica (7=a) junto con 
Event Sourcing + CQRS + Saga (8=c). 
Esta combinación es adecuada para el MVP, pero en pagos reales, 
la auditabilidad de Event Sourcing suele ir acompañada de una idempotencia y trazabilidad estrictas.
 Incluí la idempotencia en la Tarea 6 y dejé FAPI/auditoría como una recomendación evolutiva para
 no ampliar el alcance del MVP.


----

[7]: ¿Qué nivel de seguridad y estándares de API financiera quieres desde el MVP?
a. **Base** - OAuth2 / OpenID Connect (Cognito), TLS, API Gateway con throttling
b. **FAPI (Financial-grade API)** - Perfil FAPI (mTLS, JWT firmados, PKCE), alineado a open banking
c. **FAPI + gestión de secretos y auditoría completa** - FAPI más KMS, Secrets Manager, trazabilidad/audit trail e idempotencia estricta
d. **Otro** - Descríbelo

[8]: Para consistencia de datos en el flujo de pagos con EDA, ¿qué patrones quieres adoptar?
a. **Saga (orquestada) + Outbox + Idempotencia** - Coordinación explícita del flujo de pago con garantías de entrega
b. **Saga coreografiada (event-driven) + Outbox** - Menor acoplamiento, cada dominio reacciona a eventos
c. **Event Sourcing + CQRS + Saga** - Auditabilidad total del ciclo de vida del pago (más complejo)
d. **Otro / recomiéndame** - Según el caso Payments

[9]: ¿Cuáles son los criterios de éxito del MVP y qué entregables esperas del plan?
a. **Flujo demoable end-to-end** - Iniciar un pago y verlo ejecutarse con mensajería ISO 20022 y eventos
b. **Demoable + artefactos de arquitectura** - Lo anterior más contratos OpenAPI (API-first), diagramas C4/EDA y mapeo BIAN↔ISO 20022
c. **Demoable + arquitectura + base de despliegue AWS (IaC)** - Todo lo anterior más infraestructura como código y CI/CD
d. **Otro** - Descríbelo

----
	(Responde a cualquier subconjunto, por ejemplo "7=c, 8=a, 9=c")
----

Seguridad (7=a): Base - OAuth2/OIDC (Cognito), TLS, API Gateway con throttling.
Consistencia de datos (8=c): Event Sourcing + CQRS + Saga (auditabilidad total del ciclo de vida del pago).
Criterios de éxito (9=c): Flujo demoable end-to-end + artefactos de arquitectura + base de despliegue AWS (IaC) y CI/CD.
Con esto tengo requisitos suficientes. Una nota profesional antes de continuar: elegiste seguridad Base (7=a) pero Event Sourcing + CQRS + Saga (8=c) para pagos. Esa combinación es coherente para el MVP, pero en pagos reales la auditabilidad de Event Sourcing suele ir de la mano de idempotencia estricta y trazabilidad. Lo incluiré como recomendación evolutiva sin inflar el alcance del MVP.

recursos:

[R1]: ¿Hay código, repositorio o estructura de proyecto existente que deba revisar para alinear el plan?
a. **Proyecto nuevo (greenfield)** - Empezamos desde cero, sin código previo
b. **Existe base** - Indícame la ruta/carpeta a revisar
c. **Otro**

[R2]: ¿Qué versiones/tecnologías fijo como base de la investigación y el diseño?
a. **.NET 8 (LTS) + Python 3.12 + FastAPI** - Stack por defecto que asumiré
b. **Otras versiones** - Indícalas
c. **Recomiéndame tú** las versiones y librerías (ISO 20022, Kafka clients, IaC con CDK vs Terraform, etc.)


[R3]: Sobre IaC y modelado ISO 20022, ¿tienes preferencia?
a. **AWS CDK (TypeScript o Python)** para IaC y **generar modelos ISO 20022 desde XSD oficiales**
b. **Terraform** para IaC y **usar librerías/DTOs propios ISO 20022** (pain.001, pacs.008, pacs.002)
c. **Recomiéndame** el enfoque según el stack híbrido y AWS

Anoto el bloque de investigación:

R1=a: Proyecto nuevo (greenfield), desde cero.
R2=a: .NET 8 (LTS) + Python 3.12 + FastAPI.
R3=b: Terraform para IaC + DTOs/modelos propios ISO 20022 (pain.001, pacs.008, pacs.002).
Con todo esto tengo lo necesario para armar el diseño y el plan de tareas. Aquí está la propuesta completa.

