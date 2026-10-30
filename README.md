# JobHunter AI 🎯🤖

> **Plataforma Integral de Búsqueda de Empleo, Agregador Nacional & Autonómico (España), CRM de Candidaturas (ATS Personal) y Motor de Matching Multivariable con IA.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B.svg?logo=flutter)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)

---

## 📌 ¿Qué es JobHunter AI?

**JobHunter AI** es tu asistente autónomo para la búsqueda de empleo en España. Centraliza la búsqueda en múltiples portales públicos y privados, analiza cada vacante frente a tus perfiles profesionales con un motor de scoring multidimensional desacoplado, y gestiona todo tu embudo de candidaturas en un tablero Kanban interactivo (ATS Personal).

### 🌟 Capacidades Clave

1. **Agregador Multifuente Nacional y Autonómico**:
   - Conectores con deduplicación criptográfica (SHA-256 de contenido normalizado).
   - Portales privados: **InfoJobs**, **LinkedIn**, **Tecnoempleo**, etc.
   - Organismos públicos: **SEPE / Empléate** (Sistema Nacional de Empleo) y **Red EURES**.
   - Conectores autonómicos plugin-based: **Comunidad de Madrid**, con arquitectura modular extensible a las 17 CCAA.

2. **Motor de Matching Multivariable con IA (Desacoplado)**:
   - Evaluación heurística rápida combinada con enriquecimiento cualitativo por LLM (OpenAI GPT-4o o LLMs locales vía Ollama en `http://localhost:11434`).
   - Ponderación de afinidad objetiva:
     - **40% Competencias y Habilidades (Skills Match)**: Distingue requerimientos indispensables vs deseables.
     - **25% Rango Salarial (Salary Match)**: Comparación de banda deseada vs oferta con tolerancia proporcional.
     - **20% Modalidad y Ubicación (Location/Modality Match)**: Remoto, híbrido o presencial.
     - **15% Trayectoria Profesional (Experience Match)**: Años de experiencia demandados vs perfil.
   - Generación de informe con fortalezas, carencias (gaps) y recomendaciones de postulación.

3. **ATS Personal & Tablero CRM**:
   - Flujo visual Kanban: `SAVED` → `REVIEWING` → `APPLIED` → `INTERVIEW` → `OFFER` → `HIRED` / `REJECTED`.
   - Línea de tiempo cronológica con registro de eventos de transición, notas de entrevistas y seguimiento.
   - Métricas y funnel de conversión (tasa de entrevistas, ratios por portal).

4. **Multi-Perfil Profesional**:
   - Permite mantener simultáneamente identidades profesionales independientes (p. ej. *Tech Lead*, *Senior Backend Engineer*, *Technical Product Manager*), cada una con sus bandas salariales, habilidades clave y portfolios específicos.

---

## 🏗️ Estructura del Proyecto

El proyecto está diseñado bajo patrones de **Clean Architecture** y separación por responsabilidades:

```
jobhunter_ai/
├── docker-compose.yml              # Infraestructura: PostgreSQL 16, Redis, Elasticsearch, RabbitMQ
├── start_backend.bat               # Lanzador directo del servidor backend en Windows
├── docs/
│   └── ARCHITECTURE.md             # Especificación técnica detallada y flujos de arquitectura
├── services/                       # Core Backend en FastAPI & SQLAlchemy
│   ├── api/                        # Routers REST (/jobs, /matching, /crm, /profiles, /scrapers)
│   ├── ai_engine_service/          # Motor de matching multivariable y proveedores de IA (OpenAI / Ollama)
│   ├── scraper_service/            # Conectores para InfoJobs, SEPE, Madrid Empleo y gestor concurrente
│   ├── crm_service/                # Lógica del ATS Kanban y eventos de seguimiento
│   ├── db/                         # Modelos relacionales, configuración de BD y migraciones Alembic
│   ├── tests/                      # Suite de pruebas unitarias y de integración (pytest)
│   ├── requirements.txt            # Dependencias Python
│   └── Dockerfile                  # Contenedor para despliegue de backend
└── frontend/
    └── jobhunter_app/              # App multiplataforma en Flutter 3.x
        ├── lib/
        │   ├── core/               # Temas Material 3, cliente HTTP Dio, storage seguro y responsive layout
        │   ├── features/           # Módulos: multi_profile, job_aggregator, crm_applications, analytics
        │   ├── router/             # GoRouter con navegación adaptativa (Mobile & Desktop)
        │   └── main.dart           # Punto de entrada Flutter con Riverpod ProviderScope
        └── pubspec.yaml            # Dependencias Flutter
```

---

## 🚀 Instalación y Puesta en Marcha

### Prerrequisitos
- **Python 3.12 o 3.13** instalado en el sistema.
- **Git** instalado.
- *(Opcional)* **Docker & Docker Compose** si deseas usar PostgreSQL/Redis en contenedor.
- *(Opcional)* **Flutter SDK 3.22+** para compilar la aplicación cliente.

---

### Opción A: Ejecución Rápida en Local (Windows)

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/Glinkyz/jobhunter-ai.git
   cd jobhunter-ai
   ```

2. **Instalar dependencias de Python**:
   ```bash
   pip install -r services/requirements.txt
   ```

3. **Iniciar el servidor Backend**:
   - Simplemente haz doble clic en el archivo [`start_backend.bat`](start_backend.bat), o ejecútalo en la terminal:
     ```cmd
     start_backend.bat
     ```
   - El servidor arrancará en **`http://127.0.0.1:8000`** con recarga automática.

4. **Acceder a la interfaz interactiva (Swagger UI)**:
   - Abre en tu navegador: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
   - La raíz `http://127.0.0.1:8000/` redirige automáticamente a la documentación interactiva.

---

### Opción B: Ejecución con Docker Compose

Para desplegar la base de datos PostgreSQL, Redis y los servicios complementarios:

```bash
docker compose up -d postgres redis rabbitmq elasticsearch
```

La cadena de conexión por defecto está configurada en `services/db/database.py`. Si Docker no está corriendo, el sistema utiliza de forma transparente SQLite (`jobhunter_dev.db`) para que puedas desarrollar y probar inmediatamente sin fricción.

---

### Opción C: Ejecución del Frontend (Flutter)

1. Dirígete a la carpeta de la app:
   ```bash
   cd frontend/jobhunter_app
   ```
2. Descarga los paquetes:
   ```bash
   flutter pub get
   ```
3. Ejecuta la app en tu plataforma preferida (Escritorio Windows, Navegador Web o Emulador):
   ```bash
   flutter run -d windows
   # O en web:
   flutter run -d chrome
   ```

---

## 🧪 Ejecución de Pruebas

El núcleo incluye una suite de pruebas automatizadas que cubren el modelo de datos, la resiliencia del motor de IA ante proveedores caídos, la deduplicación de vacantes y el ciclo completo de la API REST:

```bash
python -m pytest services/tests -v
```

**Resultado verificado**:
- `test_db_models.py`: Esquema relacional, cascadas e integridad referencial.
- `test_matching_engine.py`: Ponderaciones 40/25/20/15 y tolerancia de fallback.
- `test_scrapers.py`: Extracción concurrente y deduplicación criptográfica.
- `test_api.py`: Flujo E2E desde scraping hasta transición de estados en el CRM.

---

## 📖 Guía de Uso de la API REST

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Chequeo de salud del servicio |
| `GET` | `/api/v1/scrapers/plugins` | Lista los portales y conectores autonómicos disponibles |
| `POST` | `/api/v1/scrapers/run` | Lanza los scrapers con filtrado por palabra clave |
| `GET` | `/api/v1/jobs` | Consulta vacantes con filtros por título, portal o modalidad |
| `POST` | `/api/v1/profiles` | Registra un nuevo perfil profesional |
| `POST` | `/api/v1/matching/calculate` | Calcula el scoring de afinidad entre un perfil y una vacante |
| `GET` | `/api/v1/crm/kanban` | Obtiene el tablero Kanban con las candidaturas agrupadas |
| `POST` | `/api/v1/crm/applications` | Crea una candidatura en el ATS personal |
| `PATCH` | `/api/v1/crm/applications/{id}/status` | Transiciona de etapa en el Kanban y anota eventos |
| `GET` | `/api/v1/crm/stats` | Métricas de conversión y embudo de entrevistas |

---

## 👥 Equipo de Desarrollo Autónomo (MausBot Team)

- **Lin** — Backend Software Engineer (Modelos SQLAlchemy, APIs FastAPI, Scrapers y Motor de IA).
- **Pixel** — Frontend Engineer (Clean Architecture Flutter, Material 3, Riverpod y UI adaptativa).
- **Rigel** — QA and Release Engineer (Planes de pruebas y validación).
- **Ada** — Tech Lead (Arquitectura de microservicios y especificación técnica).
- **MausBot** — Chief of Staff & Dirección de Proyecto.
