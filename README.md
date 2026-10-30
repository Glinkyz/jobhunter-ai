# JobHunter AI 🎯🤖

> **Plataforma Inteligente de Búsqueda de Empleo, Agregador Nacional & Autonómico, CRM de Candidaturas (ATS Personal) y Motor de Matching con IA.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B.svg?logo=flutter)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?logo=fastapi)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-005571.svg?logo=elasticsearch)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql)

---

## 📌 Visión del Producto

JobHunter AI funciona como una combinación de **HubSpot CRM + LinkedIn Jobs + ATS Personal + Asistente Autónomo de IA**, diseñado específicamente para el mercado laboral español.

### Capacidades Clave
1. **Agregador Exhaustivo de Empleo**:
   - Portales Nacionales: LinkedIn, InfoJobs, Indeed, Tecnoempleo, Domestika, etc.
   - Organismos Públicos: SEPE, Red EURES.
   - Conectores Autonómicos Plugin-Based: Cobertura para las 17 Comunidades Autónomas más Ceuta y Melilla.
2. **Motor de IA Multimodal & Desacoplado**:
   - Soporte intercambiable para OpenAI (GPT-4o), Azure OpenAI y LLMs locales vía Ollama (Llama 3).
   - Matching multidimensional (0-100) en Skills, Rango Salarial, Experiencia y Modalidad.
   - Generador automático de CV optimizado para ATS y cartas de presentación personalizadas.
   - Interview Coach interactivo para simulación de entrevistas técnicas y de RRHH.
3. **CRM de Candidaturas**:
   - Tablero Kanban interactivo con estados: `SAVED` → `REVIEWING` → `APPLIED` → `INTERVIEW` → `OFFER` → `HIRED`.
   - Timeline de eventos, notas, contactos por empresa y recordatorios automáticos.
4. **Multi-Perfil Profesional**:
   - Gestión simultánea de perfiles independientes (p. ej. *Flutter Tech Lead*, *Backend Engineer*, *Product Manager*) con preferencias, keywords y portfolios diferenciados.

---

## 🏗️ Arquitectura del Sistema

El sistema implementa **Clean Architecture** en el frontend (Flutter 3.x) y una arquitectura de **microservicios orientada a eventos** en el backend.

```
jobhunter_ai/
├── docs/                      # Especificaciones OpenAPI, modelos ER y diagramas
├── frontend/
│   └── jobhunter_app/         # Frontend multiplataforma (iOS, Android, Web, Desktop)
│       └── lib/
│           ├── core/          # Networking, interceptores Dio, almacenamiento seguro
│           ├── features/      # Módulos: auth, multi_profile, job_aggregator, crm
│           └── router/        # GoRouter con guards de autenticación
├── services/
│   ├── ai_engine_service/     # Motor de IA, embeddings y matching scoring
│   ├── scraper_service/       # Crawlers y plugins autonómicos extensibles
│   ├── crm_service/           # Lógica de candidaturas, Kanban y timeline
│   └── auth_service/          # OAuth2, JWT, gestión de usuarios
├── docker-compose.yml         # Despliegue de infraestructura local
└── README.md
```

---

## 🚀 Despliegue Rápido (Entorno Local)

### Requisitos Previos
- Docker y Docker Compose
- Flutter SDK 3.22+
- Python 3.12+

### 1. Iniciar la Infraestructura
```bash
docker-compose up -d postgres redis elasticsearch rabbitmq
```

### 2. Ejecutar la API Central
```bash
docker-compose up --build backend_api
```

### 3. Iniciar el Cliente Flutter
```bash
cd frontend/jobhunter_app
flutter pub get
flutter run -d chrome # o macos / windows / linux / emulator
```

---

## 📄 Documentación Técnica
- [Arquitectura Detallada y Diagramas](docs/ARCHITECTURE.md)
- [Esquema de Base de Datos y Modelo Relacional](docs/DATABASE.md)
- [Especificación OpenAPI 3.1](docs/openapi.yaml)

---

## 👥 Equipo de Desarrollo Autónomo (MausBot Team)
- **Ada** — Tech Lead (Arquitectura y dirección técnica)
- **Lin** — Software Engineer (Microservicios, APIs y persistencia)
- **Pixel** — Frontend Engineer (Diseño UI/UX en Flutter y Material 3)
- **Rigel** — QA and Release Engineer (Planes de pruebas y observabilidad)
- **MausBot** — Chief of Staff & Orquestación
