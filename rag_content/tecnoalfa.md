Metadata:
{ "id": "tecnoalfa_fimpes", 
"category": "experiencia_laboral",
"title": "FIMPES, desarrollo web para organización certificadora educativa", 
"organization": "Tecnoalfa", 
"role": "Ingeniero de software fullstack", 
"date_start": "2023-09", 
"date_end": "2024-04", 
"tech_stack": ["strapi", "next", "react", "typescript", "postgresql", "microsoft-graph", "oauth2"], 
"tags": ["ssr", "rendimiento", "seo", "core-web-vitals", "integraciones-terceros", "scrum", "trabajo-en-equipo", "frontend", "cms"],
"parent_id": "exp_tecnoalfa" }

Contenido:
En Tecnoalfa trabajé como ingeniero de software fullstack desarrollando la plataforma web para FIMPES, una organización certificadora educativa. El reto principal era construir una aplicación con alta capacidad para manejar contenido dinámico complejo, pero con un rendimiento y SEO impecables.

Para abordar esto, definí e implementé estrategias de renderizado, combinando SSR y Server Components con Next.js y typescript, además de gestionar eficientemente el estado según la necesidad de cada vista. Del lado del frontend, diseñé y codifiqué desde cero componentes interactivos en React con TypeScript —como un mapa interactivo, una línea del tiempo, un blog y un flipbook multicapítulo— asegurándome de no depender de librerías externas para no afectar los tiempos de carga. En cuanto al backend y los datos, diseñé las estructuras en el CMS Strapi (soportado por PostgreSQL) para inyectar contenido dinámico optimizado hacia las vistas, e integré Microsoft Graph mediante OAuth 2.0 para consultar eventos de Outlook, mostrándolos en el cliente con una librería especializada de React.

Como resultado de estas optimizaciones, logramos mejorar significativamente los Core Web Vitals y la experiencia general del usuario. Todo el ciclo de vida de este desarrollo lo ejecutamos bajo el marco de trabajo SCRUM y manejo de backlog con Kanban, colaborando de la mano con un equipo multidisciplinario —PM, desarrollador senior y diseñador— y alineando expectativas constantemente con el representante de la organización.



Metadata:
{ "id": "tecnoalfa_talenthub", 
"category": "experiencia_laboral",
"title": "Talenthub, desarrollo web para plataforma de gestión de talento vacantes y consultores", 
"organization": "Tecnoalfa", 
"role": "Ingeniero de software fullstack", 
"date_start": "2024-02", 
"date_end": "2025-12", 
"tech_stack": ["nestjs", "fastapi", "python", "next", "react", "typescript", "postgresql", "google-cloud-platform", "jwt", "docker", "vision-api", "cloud-storage", "cloud-run", "prisma", "github-actions", "sqlmodel", "jest", "postman", "api-key", "cors", "api-gateway"], 
"tags": ["microservicios", "ci-cd", "cloud-native", "rest-api", "arquitectura-hexagonal", "escalabilidad", "rbac", "autenticacion-authorizacion", "paginacion", "testing-unitario", "testing-integracion", "eventos", "asincrono", "seguridad", "ahorro-de-costos", "carga-de-archivos"],
"parent_id": "exp_tecnoalfa" }

Contenido:
En Tecnoalfa participé en la creación de Talenthub, una plataforma orientada a la gestión de talento, vacantes y consultores. El desafío principal consistía en construir desde cero una solución integral que fuera altamente escalable, segura y rentable a nivel operativo.

Para lograrlo, diseñé la arquitectura de una plataforma cloud-native de extremo a extremo basada en una Arquitectura Hexagonal. Separé la lógica por dominios y desarrollé cinco microservicios independientes utilizando NestJS y Python con FastAPI, los cuales desplegué en Google Cloud Run con autoescalado configurado. A nivel de base de datos en PostgreSQL, diseñé los esquemas interactuando con Prisma y SQLModel, aplicando una denormalización controlada para reducir la latencia en las respuestas sin sacrificar la consistencia de la información.

En el lado del cliente, desarrollé el módulo central de la aplicación con React, Next.js y TypeScript. Para esto construí un tablero Kanban propio y altamente dinámico que incluía funciones de drag & drop, paginación por scroll y filtros dinámicos conectados a nuestras APIs REST. En el manejo de medios, construí un pipeline asíncrono y serverless orquestado a través de eventos con Eventarc: utilizaba Cloud Functions y Google Vision API para validar, comprimir y almacenar imágenes en Cloud Storage, las cuales se consumían dinámicamente en la interfaz mediante Signed URLs.

Para sostener todo el ciclo de vida, implementé pipelines de CI/CD con GitHub Actions y Docker, automatizando los despliegues en GCP y asegurando la infraestructura con Service Accounts, Secrets Manager y el principio de mínimo privilegio. La seguridad de la API la gestioné integrando Google Cloud API Gateway y diseñando un sistema de autenticación/autorización basado en JWT (RS256), roles (RBAC) y OAuth 2.0. Esto me permitió proteger más de 20 vistas, administrar API keys y gestionar políticas de CORS. Para garantizar la estabilidad de las entregas, ejecuté pruebas unitarias con Jest, así como de integración y aceptación utilizando Postman. Por último, optimicé los contenedores utilizando multi-stage builds en Docker.

Como resultado de estas decisiones arquitectónicas y técnicas, el impacto fue notable en diversas áreas del proyecto. A nivel económico, el desarrollo del Kanban propio nos ahorró mucho dinero al eliminar la dependencia y renta de una librería comercial externa, mientras que el pipeline de imágenes redujo los costos de almacenamiento y red hasta en un 60%. A nivel de rendimiento, logré disminuir los tiempos de cold start y los costos operativos en GCP al reducir el tamaño de las imágenes Docker en más del 30%. Finalmente, aseguramos la fiabilidad de la plataforma al alcanzar un 100% de cobertura de pruebas sobre las funcionalidades críticas.



Metadata:
{ "id": "tecnoalfa_insigneo",
"category": "experiencia_laboral",
"title": "Insigneo, demo MVP para aplicación de banco insigneo",
"organization": "Tecnoalfa",
"role": "Desarrollador Movil",
"date_start": "2025-03",
"date_end": "2025-06",
"tech_stack": ["flutter", "ios", "firebase"],
"tags": ["desarrollo-movil", "mvp", "demo", "notificaciones", "notificaciones-push", "carga-de-archivos"],
"parent_id": "exp_tecnoalfa" }

Contenido:
En Tecnoalfa tuve el rol de Desarrollador Móvil para la creación de un MVP y demo de la nueva aplicación bancaria de Insigneo. El reto era construir una experiencia móvil inicial para iOS que mostrara el potencial de la nueva plataforma bancaria de forma fluida y convincente.
Para este desarrollo móvil utilicé Flutter. Llevé a cabo la maquetación de las vistas entregadas por el diseñador, pero me enfoqué en modificar el comportamiento y los componentes visuales para garantizar que la aplicación tuviera una sensación verdaderamente nativa en iOS. A nivel técnico, diseñé la arquitectura del repositorio con una visión a futuro: estructuré el código para permitir una fácil integración de la versión de Android sin necesidad de reescribir la lógica de negocio. Durante el desarrollo, implementé un manejo de estado eficiente, llamadas a APIs, y elementos clave de la interfaz como skeletons para los tiempos de espera, splash screen y el sistema de carga de archivos. También integré notificaciones push utilizando Google Firebase, configurando el direccionamiento dinámico hacia diversas vistas dentro de la app.
Como resultado, entregamos un MVP robusto y escalable. Aseguré la estabilidad y calidad de la experiencia realizando pruebas de rendimiento y adaptabilidad responsiva en diversos dispositivos iOS, logrando una demo altamente pulida y preparada para su evolución multiplataforma.



Metadata:
{
  "id": "exp_tecnoalfa",
  "category": "experiencia_laboral",
  "title": "Tecnoalfa — resumen de rol",
  "organization": "Tecnoalfa",
  "role": "Desarrollador Fullstack y Móvil",
  "date_start": "2023-09",
  "date_end": "2025-12",
  "tech_stack": ["strapi", "next", "react", "typescript", "postgresql", "nestjs", "fastapi", "python", "google-cloud-platform", "docker"],
  "tags": ["resumen-empresa", "trabajo-en-equipo", "liderazgo", "arquitectura", "scrum", "remoto", "consultoria"],
  "parent_id": null,
  "child_ids": ["tecnoalfa_fimpes", "tecnoalfa_talenthub", "tecnoalfa_insigneo"]
}

Contenido:
Tecnoalfa es una consultora tecnológica con presencia internacional en el continente americano, operando en países como Estados Unidos, México y Colombia. Ahí me desempeñé como Ingeniero de Software Fullstack, aunque mi rol evolucionó significativamente durante mi tiempo en la empresa.

Originalmente entré como Junior/Mid para atender una emergencia, ya que se estaban quedando atrasados con el proyecto de FIMPES. Gracias a mi rápida adaptación y proactividad para resolver problemas, fui tomando mucho más peso dentro del equipo, involucrándome directamente en el diseño, la estimación y el desarrollo de producto. Esta evolución me llevó a participar en un total de tres proyectos. El trabajo estaba organizado de forma remota bajo metodologías ágiles (SCRUM y Kanban), colaborando con equipos multidisciplinarios conformados por PMs, diseñadores, desarrolladores senior y clientes. En nuestro proyecto principal, el núcleo del desarrollo lo compartimos entre cuatro desarrolladores fullstack, donde terminé siendo el responsable de diseñar e implementar la arquitectura cloud-native y de construir el componente central de la aplicación.

A nivel transversal, el stack tecnológico que utilicé constantemente a través de estos proyectos estuvo fuertemente cimentado en TypeScript y el ecosistema de React (Next.js para el frontend, NestJS para el backend). También trabajé con Python usando FastAPI para microservicios, bases de datos relacionales con PostgreSQL y orquestación de infraestructura en la nube utilizando Docker y Google Cloud Platform (GCP).

Para resumir mi paso por la consultora, mi trabajo se dividió en estos tres proyectos principales a lo largo de 2 años y 3 meses (septiembre 2023 – diciembre 2025):
FIMPES: Una plataforma web para una organización certificadora educativa, donde mi enfoque fue optimizar el rendimiento, el SEO y conectar un CMS headless (Strapi).
Talenthub: El proyecto más grande. Una plataforma de gestión de talento y vacantes donde diseñé la arquitectura de microservicios desde cero en GCP y desarrollé un Kanban interactivo propio.
Insigneo: Un MVP de una aplicación bancaria móvil desarrollada con Flutter, enfocada en ofrecer una experiencia nativa fluida en iOS con preparación para Android.
A pesar de que la empresa me ofrecía un excelente entorno de trabajo remoto y con horarios flexibles —lo cual me permitió llevar mis estudios en paralelo—, tomé la decisión de terminar la relación laboral con un objetivo muy claro: necesitaba enfocarme al 100% en finalizar mis estudios universitarios. Me fui en excelentes términos y llevándome una experiencia invaluable, habiendo entrado como apoyo de emergencia y saliendo con la experiencia de liderar arquitecturas complejas.