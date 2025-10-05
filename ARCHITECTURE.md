# System Architecture Document
## AI Creative Pre-testing Analysis Platform

**Version:** 1.0  
**Date:** October 4, 2025  
**Status:** Design Complete

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Component Design](#component-design)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Security Architecture](#security-architecture)
9. [Scalability & Performance](#scalability--performance)

---

## System Overview

### Purpose
Enterprise-grade platform for automated creative pre-testing analysis, integrating video understanding, quantitative metrics, and qualitative feedback to generate actionable marketing recommendations.

### Key Capabilities
- **Multi-modal Analysis:** Video (TwelveLabs), Audio (ElevenLabs), Text (NLP)
- **Statistical Rigor:** Confidence intervals, effect sizes, segment weighting
- **Intelligent Recommendations:** Segment-specific, objective-aligned creative guidance
- **Scalable Processing:** Async pipelines handling 100+ experiments concurrently

---

## Architecture Principles

### 1. Separation of Concerns
- **Backend:** Data processing, AI integration, business logic
- **Frontend:** Presentation, user interaction, visualization
- **External Services:** Video/audio analysis, storage

### 2. Asynchronous Processing
- Long-running tasks (video indexing, NLP) run in background workers
- Real-time status updates via WebSocket or polling
- Non-blocking API responses

### 3. Modularity
- Each analysis component (video, quant, qual, recommendations) is independently testable
- Pluggable AI services (swap TwelveLabs for alternative if needed)
- Microservices-ready architecture

### 4. Data-Driven
- All recommendations backed by quantitative + qualitative evidence
- Versioned datasets and analysis results for reproducibility
- Audit trails for compliance

### 5. User-Centric Design
- API-first approach (frontend is one consumer among many)
- Export-friendly formats (JSON, PDF, PPTX)
- Progressive disclosure (summary → details)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React Frontend (TypeScript + TailwindCSS + shadcn/ui)   │  │
│  │  - Dashboard  - Video Player  - Recommendations UI       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTPS / REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         FastAPI Backend (Python 3.11+)                   │  │
│  │  ┌────────────┬────────────┬────────────┬─────────────┐ │  │
│  │  │ Experiment │  Analysis  │   Export   │    Auth     │ │  │
│  │  │  Manager   │   Engine   │  Service   │   Service   │ │  │
│  │  └────────────┴────────────┴────────────┴─────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PROCESSING LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Celery Workers (Async Task Queue)                │  │
│  │  ┌────────────┬────────────┬────────────┬─────────────┐ │  │
│  │  │   Video    │Quantitative│Qualitative │Recommendation│ │  │
│  │  │  Analyzer  │  Analyzer  │  Analyzer  │   Generator  │ │  │
│  │  └────────────┴────────────┴────────────┴─────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INTEGRATION LAYER                           │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │  TwelveLabs  │  ElevenLabs  │   Hugging    │   OpenAI    │  │
│  │     API      │     API      │     Face     │     API     │  │
│  │ (Video AI)   │  (Audio AI)  │ (NLP Models) │(Summarize)  │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │  PostgreSQL  │    Redis     │   AWS S3     │   Local FS  │  │
│  │ (Structured) │  (Cache +    │   (Videos,   │  (Temp CSVs)│  │
│  │              │   Queue)     │    Exports)  │             │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Frontend (React Application)

#### 1.1 Core Modules
```
src/
├── components/
│   ├── dashboard/
│   │   ├── ExperimentList.tsx
│   │   ├── ExperimentCard.tsx
│   │   └── SummaryMetrics.tsx
│   ├── experiment/
│   │   ├── VideoPlayer.tsx
│   │   ├── SceneTimeline.tsx
│   │   ├── MetricsTable.tsx
│   │   ├── QualitativeInsights.tsx
│   │   └── RecommendationsList.tsx
│   ├── recommendations/
│   │   ├── RecommendationCard.tsx
│   │   ├── RecommendationDetail.tsx
│   │   └── FilterControls.tsx
│   └── shared/
│       ├── Layout.tsx
│       ├── Navbar.tsx
│       └── LoadingSpinner.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── ExperimentDetail.tsx
│   ├── NewExperiment.tsx
│   └── Login.tsx
├── hooks/
│   ├── useExperiments.ts
│   ├── useRecommendations.ts
│   └── useAnalysisStatus.ts
├── services/
│   ├── api.ts
│   └── websocket.ts
├── store/
│   └── experimentStore.ts
└── utils/
    ├── formatters.ts
    └── validators.ts
```

#### 1.2 Key Features
- **Responsive Design:** Desktop-first, tablet-compatible
- **Real-time Updates:** WebSocket for analysis progress
- **Data Visualization:** Recharts for metrics, D3 for custom charts
- **Video Annotations:** Overlay markers on timeline for recommendations

---

### 2. Backend (FastAPI Application)

#### 2.1 Core Modules
```
backend/
├── api/
│   ├── routes/
│   │   ├── experiments.py
│   │   ├── analysis.py
│   │   ├── recommendations.py
│   │   └── export.py
│   ├── dependencies.py
│   └── middleware.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── database.py
├── models/
│   ├── experiment.py
│   ├── video_analysis.py
│   ├── metrics.py
│   ├── qualitative.py
│   └── recommendation.py
├── schemas/
│   ├── experiment.py
│   ├── analysis.py
│   └── recommendation.py
├── services/
│   ├── video_service.py
│   ├── quantitative_service.py
│   ├── qualitative_service.py
│   ├── recommendation_service.py
│   └── export_service.py
├── workers/
│   ├── celery_app.py
│   ├── tasks/
│   │   ├── video_tasks.py
│   │   ├── analysis_tasks.py
│   │   └── export_tasks.py
├── integrations/
│   ├── twelvelabs_client.py
│   ├── elevenlabs_client.py
│   └── openai_client.py
└── utils/
    ├── csv_parser.py
    ├── nlp_utils.py
    └── statistics.py
```

#### 2.2 API Design Patterns
- **RESTful Endpoints:** Resource-oriented URLs
- **Async Handlers:** FastAPI async/await for I/O operations
- **Pydantic Validation:** Type-safe request/response schemas
- **Error Handling:** Standardized error responses with status codes

---

### 3. Processing Layer (Celery Workers)

#### 3.1 Task Workflow
```python
# Orchestrator Task
@celery.task
def analyze_experiment(experiment_id: str):
    """Main orchestration task"""
    # 1. Video Analysis
    video_result = analyze_video.delay(experiment_id)
    
    # 2. Parallel: Quant + Qual Analysis
    quant_result = analyze_quantitative.delay(experiment_id)
    qual_result = analyze_qualitative.delay(experiment_id)
    
    # 3. Wait for all to complete
    video_data = video_result.get()
    quant_data = quant_result.get()
    qual_data = qual_result.get()
    
    # 4. Generate Recommendations
    recommendations = generate_recommendations.delay(
        experiment_id, video_data, quant_data, qual_data
    )
    
    return recommendations.get()
```

#### 3.2 Task Types
- **Video Tasks:** Upload, index, analyze (TwelveLabs API)
- **Audio Tasks:** Extract and analyze audio (ElevenLabs API)
- **Quantitative Tasks:** Parse CSV, compute statistics
- **Qualitative Tasks:** NLP processing (sentiment, topics, clustering)
- **Recommendation Tasks:** Correlation analysis, ranking, formatting

---

### 4. Integration Layer

#### 4.1 TwelveLabs Integration
```python
class TwelveLabsClient:
    def __init__(self, api_key: str):
        self.client = TwelveLabs(api_key=api_key)
        self.index_id = None
    
    def create_index(self, name: str) -> str:
        """Create video index with multimodal models"""
        resp = self.client.indexes.create(
            index_name=name,
            models=[
                IndexesCreateRequestModelsItem(
                    model_name="pegasus1.2",
                    model_options=["visual", "audio", "conversation"]
                )
            ]
        )
        return resp.id
    
    def upload_video(self, video_url: str) -> str:
        """Upload and index video"""
        task = self.client.tasks.create(
            index_id=self.index_id,
            video_url=video_url
        )
        task = self.client.tasks.wait_for_done(task_id=task.id)
        return task.video_id
    
    def analyze_video(self, video_id: str, prompt: str = None) -> dict:
        """Generate insights from video"""
        # Use Generate API for custom prompts
        result = self.client.generate.text(
            video_id=video_id,
            prompt=prompt or "Describe the creative elements, visual style, pacing, and emotional tone of this advertisement."
        )
        return result
    
    def get_video_segments(self, video_id: str) -> list:
        """Get scene-level breakdown"""
        # Use Classify or Segment APIs
        pass
```

#### 4.2 ElevenLabs Integration
```python
class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def analyze_audio_emotion(self, audio_file_path: str) -> dict:
        """Analyze emotional tone of audio"""
        # Use ElevenLabs voice analysis features
        pass
    
    def transcribe_with_emotion(self, audio_file_path: str) -> dict:
        """Transcribe with emotional markers"""
        pass
```

#### 4.3 NLP Pipeline
```python
class QualitativeAnalyzer:
    def __init__(self):
        self.sentiment_model = pipeline("sentiment-analysis")
        self.topic_model = BERTopic()
    
    def analyze_comments(self, comments: list[str]) -> dict:
        """Full qualitative analysis"""
        # 1. Sentiment Analysis
        sentiments = self.sentiment_model(comments)
        
        # 2. Topic Modeling
        topics, probs = self.topic_model.fit_transform(comments)
        
        # 3. Extract Representative Comments
        representatives = self._get_representative_comments(
            comments, topics, probs
        )
        
        # 4. Keyword Extraction
        keywords = self._extract_keywords(comments)
        
        return {
            "sentiments": sentiments,
            "topics": topics,
            "representatives": representatives,
            "keywords": keywords
        }
```

---

## Data Flow

### End-to-End Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER UPLOAD                                                   │
│    - Video file/URL                                              │
│    - Quantitative CSV (Results)                                  │
│    - Qualitative CSV (Comments)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. VALIDATION & STORAGE                                          │
│    - Validate CSV schemas                                        │
│    - Upload video to S3                                          │
│    - Create experiment record in PostgreSQL                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. TRIGGER ANALYSIS (Celery Task)                                │
│    - Queue: analyze_experiment(experiment_id)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────┴───────────────┬───────────────┐
         │                               │               │
         ▼                               ▼               ▼
┌─────────────────┐    ┌─────────────────────┐   ┌──────────────┐
│ 4a. VIDEO       │    │ 4b. QUANTITATIVE    │   │ 4c. QUAL     │
│     ANALYSIS    │    │     ANALYSIS        │   │    ANALYSIS  │
│                 │    │                     │   │              │
│ - Upload to     │    │ - Parse CSV         │   │ - Parse CSV  │
│   TwelveLabs    │    │ - Compute deltas    │   │ - Sentiment  │
│ - Index video   │    │ - CI calculations   │   │ - Topics     │
│ - Extract:      │    │ - Segment stats     │   │ - Clustering │
│   * Scenes      │    │ - Weight segments   │   │ - Keywords   │
│   * Transcript  │    │                     │   │              │
│   * Visual tags │    │                     │   │              │
│   * Audio tone  │    │                     │   │              │
│ - ElevenLabs    │    │                     │   │              │
│   audio analysis│    │                     │   │              │
└────────┬────────┘    └──────────┬──────────┘   └──────┬───────┘
         │                        │                     │
         └────────────────────────┴─────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. RECOMMENDATION GENERATION                                     │
│    For each (segment, brand_objective):                          │
│      - Correlate video elements with quant metrics               │
│      - Map qual themes to creative elements                      │
│      - Generate add/change/remove recommendations                │
│      - Rank by impact (delta × confidence × segment_weight)      │
│      - Attach supporting evidence (quant + qual)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. STORAGE & NOTIFICATION                                        │
│    - Save recommendations to PostgreSQL                          │
│    - Update experiment status to "completed"                     │
│    - Notify frontend via WebSocket                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. USER INTERACTION                                              │
│    - View recommendations in UI                                  │
│    - Filter by segment / objective                               │
│    - Export to PDF / JSON / PPTX                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend Stack
| Component | Technology | Justification |
|-----------|------------|---------------|
| **API Framework** | FastAPI | Async support, auto-docs, type safety |
| **Language** | Python 3.11+ | Rich AI/ML ecosystem, readability |
| **Task Queue** | Celery + Redis | Distributed async processing |
| **Database** | PostgreSQL 15 | ACID compliance, JSON support |
| **Cache** | Redis | Fast in-memory storage for sessions/queue |
| **ORM** | SQLAlchemy 2.0 | Mature, async support |
| **Validation** | Pydantic v2 | Type-safe schemas |
| **Testing** | Pytest | Industry standard |

### Frontend Stack
| Component | Technology | Justification |
|-----------|------------|---------------|
| **Framework** | React 18 | Component reusability, ecosystem |
| **Language** | TypeScript | Type safety, IDE support |
| **UI Library** | shadcn/ui | Modern, accessible, customizable |
| **Styling** | TailwindCSS | Utility-first, fast development |
| **State** | Zustand | Lightweight, simple API |
| **Charts** | Recharts | React-native, declarative |
| **Video** | Video.js | Feature-rich, extensible |
| **Build** | Vite | Fast HMR, optimized builds |

### AI/ML Stack
| Component | Technology | Justification |
|-----------|------------|---------------|
| **Video AI** | TwelveLabs API | State-of-art video understanding |
| **Audio AI** | ElevenLabs API | Voice/emotion analysis |
| **NLP** | Hugging Face Transformers | Pre-trained models (BERT, RoBERTa) |
| **Topic Modeling** | BERTopic | Coherent topics, embeddings-based |
| **Sentiment** | transformers pipeline | Easy integration, accurate |
| **Summarization** | OpenAI GPT-4 | High-quality text generation |

### Infrastructure
| Component | Technology | Justification |
|-----------|------------|---------------|
| **Containers** | Docker | Consistent environments |
| **Orchestration** | Kubernetes | Scalability, self-healing |
| **Storage** | AWS S3 | Scalable object storage |
| **CDN** | CloudFront | Fast video delivery |
| **CI/CD** | GitHub Actions | Integrated with repo |
| **Monitoring** | Prometheus + Grafana | Metrics visualization |

---

## Deployment Architecture

### Development Environment
```
docker-compose.yml
├── frontend (React dev server on :3000)
├── backend (FastAPI with hot-reload on :8000)
├── postgres (PostgreSQL on :5432)
├── redis (Redis on :6379)
├── celery-worker (Celery worker)
└── celery-beat (Scheduled tasks)
```

### Production Environment (AWS)
```
┌─────────────────────────────────────────────────────────────────┐
│                         CloudFront CDN                           │
│                    (Static Assets + Videos)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Load Balancer                   │
│                         (HTTPS Termination)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  ECS Service    │            │  ECS Service    │
│  (Frontend)     │            │  (Backend API)  │
│  - React build  │            │  - FastAPI      │
│  - Nginx        │            │  - Gunicorn     │
│  - Auto-scaling │            │  - Auto-scaling │
└─────────────────┘            └────────┬────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │                             │
                         ▼                             ▼
                ┌─────────────────┐          ┌─────────────────┐
                │  ECS Service    │          │  ElastiCache    │
                │  (Celery)       │          │  (Redis)        │
                │  - Workers      │          │  - Cache        │
                │  - Auto-scaling │          │  - Queue        │
                └────────┬────────┘          └─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  RDS PostgreSQL │
                │  - Multi-AZ     │
                │  - Automated    │
                │    backups      │
                └─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     S3 Bucket   │
                │  - Videos       │
                │  - Exports      │
                │  - Versioning   │
                └─────────────────┘
```

---

## Security Architecture

### 1. Authentication & Authorization
- **OAuth 2.0** with JWT tokens
- **Role-Based Access Control (RBAC):** Admin, Analyst, Viewer
- **API Key Management:** Environment variables, AWS Secrets Manager

### 2. Data Security
- **Encryption at Rest:** S3 server-side encryption, RDS encryption
- **Encryption in Transit:** HTTPS/TLS 1.3 for all communications
- **Secrets Management:** AWS Secrets Manager for API keys

### 3. Network Security
- **VPC Isolation:** Private subnets for backend/database
- **Security Groups:** Whitelist only necessary ports
- **WAF:** AWS WAF for DDoS protection

### 4. API Security
- **Rate Limiting:** 100 requests/minute per user
- **Input Validation:** Pydantic schemas, SQL injection prevention
- **CORS:** Whitelist frontend domain only

---

## Scalability & Performance

### Horizontal Scaling
- **Frontend:** CDN + multiple ECS tasks
- **Backend API:** Auto-scaling ECS tasks (target: 70% CPU)
- **Celery Workers:** Auto-scaling based on queue length
- **Database:** Read replicas for analytics queries

### Caching Strategy
- **Redis Cache:** 
  - Experiment metadata (TTL: 1 hour)
  - Video analysis results (TTL: 24 hours)
  - Recommendations (TTL: 1 hour)
- **CDN Cache:** Static assets, video files

### Performance Targets
| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 200ms (p95) | Prometheus |
| Video Analysis | < 5 min (60s video) | Celery task logs |
| Concurrent Users | 100+ | Load testing |
| Experiment Throughput | 20/hour | Queue metrics |

---

## Monitoring & Observability

### Metrics (Prometheus)
- Request rate, latency, error rate (RED metrics)
- Celery task duration, queue length
- Database connection pool usage
- External API call success/failure rates

### Logging (ELK Stack)
- Structured JSON logs
- Correlation IDs for request tracing
- Error stack traces

### Alerting (PagerDuty)
- API error rate > 5%
- Celery queue length > 100
- Database CPU > 80%
- External API failures

---

## Disaster Recovery

### Backup Strategy
- **Database:** Automated daily snapshots (7-day retention)
- **S3:** Versioning enabled, cross-region replication
- **Configuration:** Infrastructure as Code (Terraform)

### Recovery Procedures
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours
- **Runbooks:** Documented in Confluence

---

## Future Enhancements

### Phase 2 Features
- **Real-time Collaboration:** Multiple users annotating same experiment
- **A/B Test Comparison:** Side-by-side creative comparison
- **Custom Metrics:** User-defined KPIs beyond standard metrics

### Phase 3 Features
- **Predictive Analytics:** Forecast campaign performance pre-launch
- **Automated Creative Generation:** AI-suggested edits with mockups
- **Multi-language Support:** Internationalization

---

## Appendix

### System Dependencies
```yaml
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
celery==5.3.4
redis==5.0.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pandas==2.1.3
numpy==1.26.2
transformers==4.35.2
bertopic==0.16.0
twelvelabs-python==0.2.0
openai==1.3.7
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### Environment Variables
```bash
# .env.example
TWELVELABS_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/creative_analysis
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=creative-videos-bucket
JWT_SECRET_KEY=your_secret_key
ENVIRONMENT=development
```
