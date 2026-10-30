# Arquitectura Técnica — JobHunter AI

## 1. Patrones Arquitectónicos
- **Frontend**: Clean Architecture dividida en capas `presentation`, `application`, `domain` e `infrastructure`, con gestión reactiva mediante Riverpod 2.5+.
- **Backend**: Microservicios desacoplados orientados a eventos (RabbitMQ) y CQRS para la separación de lecturas indexadas (Elasticsearch) y escrituras transaccionales (PostgreSQL).

## 2. Ingesta y Normalización de Ofertas
```
[Conectores Nacionales + Autonómicos]
                ↓
    [Raw Collector Worker]
                ↓
  [Deduplicador por Content-Hash]
                ↓
  [Extractor de Entidades y Skills]
                ↓
 [Indexador en Elasticsearch + PostgreSQL]
```

## 3. Motor de Matching con IA (Scoring 0-100)
Cada oferta es contrastada frente a los perfiles del usuario calculando:
- **Skill Affinity (40%)**: Embeddings semánticos + coincidencia de keywords clave.
- **Salary Match (25%)**: Alineación frente a las bandas salariales deseadas.
- **Location & Modality (20%)**: Remoto, híbrido o presencial con distancia geográfica.
- **Experience Match (15%)**: Años de trayectoria y nivel de responsabilidad.
