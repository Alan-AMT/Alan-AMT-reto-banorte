Metadata:
{ "id": "codifying4u_eplanner", 
"category": "experiencia_laboral",
"title": "Eplanner, aplicación móvil multiplataforma para gestión de eventos sociales", 
"organization": "Codifying4u", 
"role": "Desarrollador movil y backend", 
"date_start": "2022-12", 
"date_end": "2024-06", 
"tech_stack": ["flutter", "firebase", "cloud-storage", "stripe", "ios", "android", "graphql", "postgresql", "prisma", "apple-pay"], 
"tags": ["diseño", "rendimiento", "pagos", "liderazgo", "trabajo-en-equipo", "frontend", "tokens", "autenticación"],
"parent_id": "exp_codifying4u" }

Contenido:
En Codifying4u trabajé como desarrollador móvil y backend en Eplanner, una aplicación multiplataforma para iOS y Android enfocada en la gestión de eventos sociales. El reto principal fue construir y conectar un ecosistema robusto, desde el diseño de la base de datos hasta la integración de flujos complejos de pago y autenticación en el cliente móvil, garantizando además su exitosa publicación en las tiendas de aplicaciones.

Del lado del backend y los datos, colaboré en el diseño del modelo relacional estructurando más de 15 tablas en PostgreSQL utilizando Prisma. Definí relaciones complejas y diseñé migraciones de esquema buscando un equilibrio óptimo entre la integridad de los datos y el rendimiento. Para conectar esto con la aplicación, extendí el modelo de negocio creando consultas y mutaciones en GraphQL. Al hacer esto, estructuré un modelo de datos normalizado estratégicamente para mitigar el clásico problema de consultas N+1 y optimicé el flujo de información implementando paginación por offset.

En cuanto al frontend móvil, desarrollé la aplicación en Flutter apoyándome en Cubits para la gestión del estado y utilizando el patrón Repository. Participé activamente en el diseño y desarrollo de más de 20 vistas de la aplicación, construyendo componentes interactivos y dinámicos que incluían filtros y caché del lado del cliente usando Apollo Client. Para dotar a la app de capacidades completas, integré Firebase Authentication para manejar sesiones de usuario y la renovación automática de tokens de forma segura. También conecté diversas APIs REST y servicios externos para flujos clave como geolocalización, almacenamiento con Google Cloud Storage (GCP), y pagos mediante Stripe y Apple Pay.

Como resultado de todo este ciclo de desarrollo, logré liderar con éxito el proceso de publicación en la App Store. Para alcanzar esto, tuve que resolver múltiples revisiones de la tienda, lo cual logré ajustando los permisos, los mensajes al usuario, integrando Apple Pay de forma nativa y asegurando el estricto cumplimiento de las políticas de Apple para pagos externos. Esto permitió que la aplicación llegara a los usuarios con un rendimiento fluido y una experiencia de pago segura.



Metadata:
{
  "id": "codifying4u_payments_api",
  "category": "experiencia_laboral",
  "title": "Payments API, API REST para procesar pagos mediante Stripe",
  "organization": "Codifying4u",
  "role": "Desarrollador backend",
  "date_start": "2023-01",
  "date_end": "2023-04",
  "tech_stack": ["stripe", "typescript", "express", "postman", "prisma", "postgresql", "jest"],
  "tags": ["api-rest", "pagos", "autenticación", "idempotencia", "manejo-errores", "suscripciones", "cors", "seguridad"],
  "parent_id": "exp_codifying4u"
}

Contenido:
En Codifying4u trabajé como desarrollador backend con el objetivo de construir la 'Payments API', una API REST dedicada al procesamiento de pagos usando stripe. El reto principal era crear un sistema capaz de gestionar el flujo completo de compra de manera impecable, soportando tanto pagos únicos como suscripciones.

Para abordar esto, diseñé la arquitectura de la API basándome en el patrón MVC utilizando TypeScript y Express. En cuanto a la persistencia de datos, diseñé el modelo relacional en PostgreSQL apoyándome en Prisma como ORM. Me enfoqué fuertemente en la seguridad y estabilidad de las transacciones, por lo que implementé flujos de pago de forma estrictamente idempotente, además de asegurar la integridad del proceso mediante validaciones rigurosas, configuraciones de seguridad como el uso de API keys y políticas de CORS, y un manejo centralizado de errores. Para garantizar que el sistema no fallara en producción, establecí flujos exhaustivos de pruebas unitarias con Jest y pruebas de integración utilizando Postman; esto me permitió validar el funcionamiento de la API en entornos locales y cloud, verificando el cumplimiento de los contratos REST, el comportamiento ante errores, la validación de los parámetros y la latencia del servicio.

Como resultado de este enfoque preventivo y estructurado, logramos entregar una API de pagos segura, estable y ampliamente probada, capaz de procesar transacciones financieras garantizando la integridad de los datos sin comprometer la experiencia de cobro.



Metadata:
{
  "id": "exp_codifying4u",
  "category": "experiencia_laboral",
  "title": "Codifying4u — resumen de rol",
  "organization": "Codifying4u",
  "role": "Desarrollador móvil y backend",
  "date_start": "2022-12",
  "date_end": "2024-06",
  "tech_stack": ["flutter", "graphql", "postgresql", "prisma", "stripe", "typescript"],
  "tags": ["resumen-empresa", "trabajo-en-equipo", "arquitectura", "crecimiento-profesional"],
  "parent_id": null,
  "child_ids": ["codifying4u_eplanner", "codifying4u_payments_api"]
}

Contenido:
En Codifying4u formé parte de una startup muy pequeña, conformada por menos de cinco personas. Empecé mi trayectoria ahí con un rol de desarrollador junior tomando tareas básicas, pero mi alcance evolucionó rápidamente. Poco a poco me fui involucrando de lleno en el desarrollo core del producto, asumiendo responsabilidades y arquitecturas mucho más complejas, y participando activamente en la revisión de código de mis compañeros.

A nivel de organización, el desarrollo recaía en un equipo muy ágil de tres desarrolladores fullstack. Juntos nos encargamos de sacar adelante los productos de la empresa. De manera transversal a lo largo de mi tiempo allí, trabajé constantemente con un stack enfocado en el diseño de bases de datos relacionales con PostgreSQL, el uso intensivo de Prisma como ORM, TypeScript en el ecosistema backend, y el consumo/diseño de APIs tanto REST como GraphQL.

Mi trabajo se dividió en dos proyectos principales a lo largo de 1 año y medio (diciembre 2022 – junio 2024):
Eplanner: Una aplicación móvil multiplataforma (iOS y Android) enfocada en la gestión de eventos sociales. Aquí desarrollé tanto el backend como el frontend (usando Flutter), y lideré el proceso para lograr su publicación exitosa en la App Store.
Payments API: Una API REST independiente diseñada para procesar el flujo completo de compras y suscripciones apoyada de la plataforma de pagos Stripe, con un enfoque muy riguroso en la seguridad, la idempotencia de los cobros y pruebas exhaustivas.
Al final, logramos desplegar el proyecto principal y llevarlo a producción exitosamente a nivel técnico. Sin embargo, al no tener el impacto ni la tracción comercial esperada en el mercado, se tomó la decisión de cerrar la iniciativa, concluyendo así mi ciclo en la empresa.