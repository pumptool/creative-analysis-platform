# Product Requirements Document (PRD)
## AI Creative Pre-testing Analysis Platform

**Version:** 1.0  
**Date:** October 4, 2025  
**Author:** CTO & Senior Full Stack Engineering Team  
**Status:** In Development

---

## Executive Summary

### Problem Statement
Marketing teams invest significant budgets in brand campaigns without understanding which creative elements will resonate with their target audiences. Traditional pre-testing provides raw quantitative metrics and qualitative feedback, but lacks actionable insights on **what specific creative elements to change, add, or remove** to maximize campaign effectiveness.

### Solution Overview
An AI-powered platform that integrates:
- **Video content analysis** (via TwelveLabs API)
- **Quantitative performance metrics** (RCT experiment results)
- **Qualitative audience feedback** (open-ended survey responses)

To generate **segment-specific, objective-aligned creative recommendations** that marketing teams can act on immediately.

### Target Users
- **Primary:** Brand Managers, Creative Directors, Media Planners
- **Secondary:** Marketing Technology Leaders, Campaign Strategists
- **Persona:** Non-technical professionals who need actionable insights, not raw data

---

## Business Objectives

### Primary Goals
1. **Reduce campaign failure risk** by identifying weak creative elements before launch
2. **Increase ROI** on creative production by providing specific improvement recommendations
3. **Enable data-driven creative decisions** across diverse audience segments
4. **Accelerate time-to-insight** from weeks (manual analysis) to minutes (automated)

### Success Metrics
- **Intelligence Depth (50%):** Multi-modal analysis integrating video, quant, and qual data
- **Insights Reporting (35%):** Presentation-ready outputs for non-technical stakeholders
- **Speed & Scalability (15%):** Process 100+ experiments with minimal manual intervention

---

## User Stories

### US-1: Campaign Manager Reviews Creative Performance
**As a** brand manager  
**I want to** upload my pre-test video and data  
**So that** I can see which creative elements are underperforming with Gen Z audiences

**Acceptance Criteria:**
- Upload video file or provide URL
- Upload quantitative results CSV and qualitative comments CSV
- Receive segment-specific recommendations within 5 minutes
- View recommendations grouped by audience segment and brand objective

### US-2: Creative Director Identifies What to Change
**As a** creative director  
**I want to** see specific scenes/moments that need revision  
**So that** I can brief my team on precise edits rather than vague feedback

**Acceptance Criteria:**
- Recommendations reference specific timestamps in the video
- Visual elements, audio elements, and messaging are separately identified
- Quantitative impact (delta, confidence intervals) is shown for each recommendation
- Representative audience quotes support each recommendation

### US-3: Media Planner Optimizes for Purchase Intent
**As a** media planner  
**I want to** filter recommendations by "purchase intent" objective  
**So that** I can prioritize changes that drive conversions over brand awareness

**Acceptance Criteria:**
- Toggle between brand objectives (favorability, purchase intent, brand associations)
- Recommendations re-rank based on selected objective
- See differential impact across objectives for the same creative element

### US-4: Marketing Leader Exports Insights for Stakeholders
**As a** marketing technology leader  
**I want to** export a presentation-ready report  
**So that** I can share findings with C-suite and agency partners

**Acceptance Criteria:**
- Export to PDF with executive summary, key findings, and recommendations
- Export to JSON for integration with other marketing tech tools
- Include data visualizations (charts, confidence intervals, word clouds)

---

## Functional Requirements

### FR-1: Data Ingestion
- **FR-1.1:** Accept video files (MP4, MOV, AVI) or URLs (YouTube, S3, GitHub)
- **FR-1.2:** Parse quantitative results CSV with dynamic column detection
- **FR-1.3:** Parse qualitative comments CSV with dynamic segment flag detection
- **FR-1.4:** Validate data integrity (missing values, schema mismatches)
- **FR-1.5:** Support batch upload for multiple experiments

### FR-2: Video Content Analysis
- **FR-2.1:** Extract scene-level breakdowns (timestamps, descriptions)
- **FR-2.2:** Identify visual elements (objects, people, settings, colors, text overlays)
- **FR-2.3:** Transcribe and analyze audio (dialogue, voiceover, music, tone)
- **FR-2.4:** Detect pacing, transitions, and emotional arcs
- **FR-2.5:** Tag creative themes and motifs

### FR-3: Quantitative Analysis
- **FR-3.1:** Calculate segment-level treatment effects (delta, margins of error)
- **FR-3.2:** Identify statistically significant lifts/drops across metrics
- **FR-3.3:** Weight segments by population size (totalWeight)
- **FR-3.4:** Cross-tabulate metrics by segment × brand objective
- **FR-3.5:** Flag high-impact segments (large effect size + large population)

### FR-4: Qualitative Analysis
- **FR-4.1:** Perform sentiment analysis on open-ended responses
- **FR-4.2:** Extract topics/themes using NLP (BERTopic, LDA, or clustering)
- **FR-4.3:** Identify representative quotes for each theme
- **FR-4.4:** Segment qualitative insights by audience demographics
- **FR-4.5:** Detect recurring keywords and phrases

### FR-5: Recommendation Engine
- **FR-5.1:** Correlate video elements with quantitative performance
- **FR-5.2:** Map qualitative themes to specific creative elements
- **FR-5.3:** Generate "add/change/remove" recommendations per segment × objective
- **FR-5.4:** Rank recommendations by impact potential (effect size × confidence × segment weight)
- **FR-5.5:** Provide justifications with supporting data (quant + qual)

### FR-6: User Interface
- **FR-6.1:** Dashboard showing all experiments with summary metrics
- **FR-6.2:** Video player with timeline annotations for recommended changes
- **FR-6.3:** Interactive filters (segment, brand objective, recommendation type)
- **FR-6.4:** Metrics visualization (bar charts, confidence interval plots)
- **FR-6.5:** Qualitative insights panel (word clouds, theme clusters, quotes)
- **FR-6.6:** Recommendation cards with expand/collapse details

### FR-7: Export & Reporting
- **FR-7.1:** Generate PDF report with executive summary
- **FR-7.2:** Export structured JSON for API consumption
- **FR-7.3:** Create PowerPoint-ready slide deck
- **FR-7.4:** Include all visualizations and data tables

---

## Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1:** Process a 60-second video + datasets in < 5 minutes
- **NFR-1.2:** Support concurrent analysis of 10+ experiments
- **NFR-1.3:** UI response time < 200ms for interactions (filters, navigation)

### NFR-2: Scalability
- **NFR-2.1:** Handle videos up to 10 minutes in length
- **NFR-2.2:** Process datasets with 10,000+ survey responses
- **NFR-2.3:** Support 100+ experiments in a single workspace
- **NFR-2.4:** Horizontal scaling via containerization (Docker/Kubernetes)

### NFR-3: Reliability
- **NFR-3.1:** 99.5% uptime for API services
- **NFR-3.2:** Graceful error handling with user-friendly messages
- **NFR-3.3:** Retry logic for external API calls (TwelveLabs, ElevenLabs)
- **NFR-3.4:** Data persistence with backup/recovery

### NFR-4: Security
- **NFR-4.1:** API keys stored in environment variables (never hardcoded)
- **NFR-4.2:** HTTPS for all external communications
- **NFR-4.3:** User authentication and authorization (OAuth 2.0)
- **NFR-4.4:** Data encryption at rest and in transit

### NFR-5: Usability
- **NFR-5.1:** No technical knowledge required to operate
- **NFR-5.2:** Onboarding tutorial for first-time users
- **NFR-5.3:** Responsive design (desktop, tablet)
- **NFR-5.4:** Accessibility compliance (WCAG 2.1 AA)

---

## Technical Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, high-performance REST API)
- **Data Processing:** Pandas, NumPy
- **NLP:** Transformers (Hugging Face), BERTopic, spaCy, NLTK
- **Video Analysis:** TwelveLabs Python SDK
- **Audio Analysis:** ElevenLabs API
- **Database:** PostgreSQL (structured data), Redis (caching)
- **Task Queue:** Celery + Redis (async video processing)

### Frontend
- **Framework:** React 18 + TypeScript
- **UI Library:** shadcn/ui (Radix UI primitives)
- **Styling:** TailwindCSS
- **State Management:** Zustand
- **Data Visualization:** Recharts, D3.js
- **Video Player:** Video.js or React Player
- **Icons:** Lucide React

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes (production)
- **CI/CD:** GitHub Actions
- **Cloud:** AWS (S3 for video storage, EC2/ECS for compute)
- **Monitoring:** Prometheus + Grafana

---

## Data Models

### Experiment
```json
{
  "id": "uuid",
  "title": "string",
  "created_at": "timestamp",
  "video_url": "string",
  "video_id": "string (TwelveLabs)",
  "status": "pending | processing | completed | failed",
  "results_csv_path": "string",
  "comments_csv_path": "string"
}
```

### VideoAnalysis
```json
{
  "video_id": "string",
  "duration": "float (seconds)",
  "scenes": [
    {
      "scene_id": "string",
      "start_time": "float",
      "end_time": "float",
      "description": "string",
      "visual_tags": ["string"],
      "audio_description": "string",
      "sentiment": "positive | neutral | negative"
    }
  ],
  "transcript": "string",
  "topics": ["string"],
  "key_moments": [
    {
      "timestamp": "float",
      "description": "string",
      "importance_score": "float"
    }
  ]
}
```

### QuantitativeMetrics
```json
{
  "experiment_id": "uuid",
  "metrics": [
    {
      "metric": "brand_favorability | purchase_intent | brand_associations",
      "segment": "string",
      "breakdown": "string",
      "delta": "float",
      "margin_of_error": "float",
      "ci_95_interval": "[float, float]",
      "baseline_mean": "float",
      "test_group_mean": "float",
      "baseline_sample_size": "int",
      "test_group_sample_size": "int",
      "total_weight": "float"
    }
  ]
}
```

### QualitativeInsights
```json
{
  "experiment_id": "uuid",
  "segments": {
    "segment_name": {
      "themes": [
        {
          "theme_label": "string",
          "keywords": ["string"],
          "prevalence": "float (0-1)"
        }
      ],
      "sentiment_distribution": {
        "positive": "float",
        "neutral": "float",
        "negative": "float"
      },
      "representative_comments": [
        {
          "text": "string",
          "sentiment": "string",
          "theme": "string"
        }
      ]
    }
  }
}
```

### Recommendation
```json
{
  "id": "uuid",
  "experiment_id": "uuid",
  "segment": "string",
  "brand_goal": "brand_favorability | purchase_intent | brand_associations",
  "type": "add | change | remove",
  "creative_element": "string",
  "justification": "string",
  "priority": "high | medium | low",
  "quantitative_support": {
    "metric": "string",
    "delta": "float",
    "ci_95": "[float, float]",
    "statistical_significance": "boolean"
  },
  "qualitative_support": [
    {
      "comment": "string",
      "theme": "string"
    }
  ],
  "scene_reference": {
    "scene_id": "string",
    "start_time": "float",
    "end_time": "float"
  }
}
```

---

## API Endpoints

### Experiments
- `POST /api/experiments` - Create new experiment
- `GET /api/experiments` - List all experiments
- `GET /api/experiments/{id}` - Get experiment details
- `DELETE /api/experiments/{id}` - Delete experiment

### Analysis
- `POST /api/experiments/{id}/analyze` - Trigger analysis pipeline
- `GET /api/experiments/{id}/status` - Check analysis status
- `GET /api/experiments/{id}/video-analysis` - Get video insights
- `GET /api/experiments/{id}/metrics` - Get quantitative metrics
- `GET /api/experiments/{id}/qualitative` - Get qualitative insights
- `GET /api/experiments/{id}/recommendations` - Get recommendations

### Export
- `GET /api/experiments/{id}/export/json` - Export as JSON
- `GET /api/experiments/{id}/export/pdf` - Export as PDF
- `GET /api/experiments/{id}/export/pptx` - Export as PowerPoint

---

## User Workflows

### Workflow 1: New Experiment Analysis
1. User clicks "New Experiment" in dashboard
2. User uploads video file or provides URL
3. User uploads quantitative results CSV
4. User uploads qualitative comments CSV
5. System validates files and creates experiment record
6. User clicks "Analyze"
7. System triggers async pipeline:
   - Upload video to TwelveLabs
   - Index video and extract insights
   - Parse and analyze quantitative data
   - Parse and analyze qualitative data
   - Generate recommendations
8. User sees progress indicator
9. Upon completion, user navigates to experiment detail view
10. User reviews recommendations, filters by segment/objective
11. User exports report for stakeholders

### Workflow 2: Reviewing Recommendations
1. User opens experiment from dashboard
2. User selects segment filter (e.g., "age_18_24")
3. User selects brand objective (e.g., "purchase_intent")
4. Recommendations re-rank based on filters
5. User clicks on a recommendation card
6. Detail modal opens showing:
   - Video player cued to relevant scene
   - Quantitative metrics with confidence intervals
   - Representative audience quotes
   - Suggested action
7. User marks recommendation as "accepted" or "noted"
8. User repeats for other segments/objectives

---

## Risks & Mitigations

### Risk 1: TwelveLabs API Rate Limits
- **Impact:** High (blocks core functionality)
- **Mitigation:** Implement request queuing, caching, and retry logic; upgrade to enterprise tier if needed

### Risk 2: Poor NLP Quality on Qualitative Data
- **Impact:** Medium (reduces recommendation quality)
- **Mitigation:** Use state-of-the-art models (BERT, GPT-4 for summarization); implement human-in-the-loop validation

### Risk 3: Scalability Bottlenecks
- **Impact:** Medium (limits concurrent users)
- **Mitigation:** Horizontal scaling with Kubernetes; async task processing with Celery; CDN for video delivery

### Risk 4: User Adoption (Too Complex)
- **Impact:** High (product fails if users don't adopt)
- **Mitigation:** Extensive UX testing; onboarding tutorials; focus on simplicity over feature bloat

---

## Success Criteria

### MVP (Minimum Viable Product)
- ✅ Process 1 experiment end-to-end
- ✅ Generate recommendations for 3+ segments
- ✅ Integrate TwelveLabs + ElevenLabs APIs
- ✅ Display recommendations in web UI
- ✅ Export JSON report

### V1.0 (Production Ready)
- ✅ Process 100+ experiments
- ✅ Sub-5-minute analysis time
- ✅ PDF/PPTX export
- ✅ User authentication
- ✅ Responsive UI

### V2.0 (Enterprise)
- ✅ Multi-tenant support
- ✅ Custom branding
- ✅ API for third-party integrations
- ✅ Advanced analytics (A/B test comparison)

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Foundation** | Week 1 | PRD, architecture, project setup |
| **Phase 2: Backend Core** | Week 2-3 | Data pipelines, API integrations |
| **Phase 3: NLP & Recommendations** | Week 4 | Qualitative analysis, recommendation engine |
| **Phase 4: Frontend** | Week 5-6 | React dashboard, visualizations |
| **Phase 5: Integration & Testing** | Week 7 | End-to-end testing, bug fixes |
| **Phase 6: Demo & Documentation** | Week 8 | Live demo, presentation, docs |

---

## Appendix

### Glossary
- **Delta:** Mean treatment effect (test group mean - baseline mean)
- **Margin of Error:** Range around delta forming confidence interval
- **Segment:** Audience subgroup (e.g., age_18_24, uses_instagram)
- **Breakdown:** Dimension for segmentation (e.g., Gender, Age)
- **Treatment:** The video creative being tested
- **Baseline:** Control group that did not see the creative

### References
- TwelveLabs API Documentation: https://docs.twelvelabs.io/
- ElevenLabs API Documentation: https://elevenlabs.io/docs
- Swayable Hackathon Repository: https://github.com/swayable/adweeknyc2025-hackathon
