# 1. Introduccion

## 1.1 Contexto del Proyecto

Atlas es una plataforma web orientada a la gestion integral de clientes y contratos, dirigida a pequeñas y medianas empresas (pymes) chilenas. El sistema permite el registro de empresas, administracion de usuarios con control de roles, gestion de clientes y contratos, y almacenamiento de documentos asociados. Dado que la plataforma maneja informacion sensible —incluyendo datos personales, RUT, direcciones, correos electronicos, telefonos y documentos contractuales—, resulta imperativo garantizar la calidad del software, la seguridad de la informacion y el cumplimiento de la normativa vigente.

> **Completar:** Describir brevemente el proposito del sistema Atlas segun el ERS. Mencionar que es un caso semestral para ISY1102.

## 1.2 Proposito del Plan de Pruebas

El presente documento establece el plan de pruebas integral para el sistema Atlas, con el objetivo de asegurar que el software cumpla con los requisitos funcionales y no funcionales definidos en la Especificacion de Requisitos de Software (ERS), garantizando la calidad del producto, la proteccion de los datos de los usuarios y el cumplimiento de las normativas legales aplicables en Chile.

> **Completar:** Explicitar que este plan busca garantizar calidad, seguridad y cumplimiento normativo.

## 1.3 Alcance

### Dentro del alcance:
- Pruebas funcionales del modulo de autenticacion (RF-1, RF-2)
- Pruebas funcionales del modulo de gestion de clientes (RF-3)
- Pruebas funcionales del modulo de gestion de contratos (RF-4, RF-5)
- Pruebas funcionales del modulo de auditoria (RF-6)
- Pruebas de seguridad (NFR-SEG-1 al NFR-SEG-9)
- Pruebas de rendimiento (NFR-PERF-1 al NFR-PERF-3)
- Pruebas de usabilidad (NFR-USAB-1 al NFR-USAB-4)
- Pruebas de compatibilidad (NFR-COMPAT-1, NFR-COMPAT-2)
- Validacion de reglas de negocio (RB-1 al RB-5)

### Fuera del alcance:
- Pruebas de instalacion y despliegue en produccion
- Pruebas de migracion de datos legacy
- Pruebas de interoperabilidad con sistemas externos no contemplados

> **Completar:** Ajustar segun lo que se discuta en el grupo.

## 1.4 Objetivos del Plan de Pruebas

| Objetivo | Descripcion | Indicador de Exito |
|----------|-------------|-------------------|
| O1 | Validar el 100% de los requerimientos funcionales (RF-1 a RF-6) | Todos los casos de prueba funcionales ejecutados con exito |
| O2 | Verificar el cumplimiento de los requerimientos de seguridad (NFR-SEG) | Sin vulnerabilidades criticas ni altas detectadas |
| O3 | Confirmar que el sistema cumple los umbrales de rendimiento definidos | 95% de operaciones bajo 300ms, soporte a 200 usuarios concurrentes |
| O4 | Garantizar la usabilidad y accesibilidad del sistema | Cumplimiento WCAG 2.1 nivel AA |
| O5 | Asegurar la trazabilidad completa entre requerimientos y casos de prueba | Matriz de trazabilidad con cobertura del 100% |

> **Completar:** Ajustar objetivos segun las prioridades del grupo.

## 1.5 Referencias

- Especificacion de Requisitos de Software (ERS) - Sistema Atlas
- Ley N° 19.628 sobre Proteccion de la Vida Privada (Proteccion de Datos Personales)
- Ley N° 20.422 sobre Igualdad de Oportunidades e Inclusion Social de Personas con Discapacidad (Accesibilidad)
- ISO/IEC 25010:2011 - Systems and Software Quality Requirements and Evaluation (SQuaRE)
- OWASP Testing Guide v4.2
- WCAG 2.1 (Web Content Accessibility Guidelines)

> **Completar:** Agregar mas referencias si es necesario.
