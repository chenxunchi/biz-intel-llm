# 📊 Project Plan: Business Intelligence from Websites for Insurance Risk

## 🚀 Project Overview

This end-to-end AI project aims to infer business characteristics relevant to insurance underwriting, using publicly available business websites as the data source.

Given a business website URL, the system will:
- Scrape website **text and images**
- Generate a concise **business summary** using a Large Language Model (LLM)
- Predict the business’s **NAICS code**
- Extract insurance-relevant **risk indicators**:
  - 💳 E-commerce capability
  - 🚚 Vehicle use (from both text and image)
  - 🔐 Cyber risk exposure

---

## 🛠️ Tech Stack

| Component            | Tools |
|---------------------|-------|
| Frontend            | Streamlit |
| Backend/API         | Python, FastAPI (if needed) |
| LLM                 | OpenAI API or Azure OpenAI |
| CV (vehicle)        | YOLOv8 or Azure Computer Vision |
| Cloud Deployment    | Azure (App Service, Container Apps) |
| Monitoring          | Azure Monitor / Application Insights |
| Storage             | Local or Azure Blob (optional) |
| Orchestration       | Python scripts (potential to expand to DAGs) |

---

## 📁 Folder Structure

biz-intel-llm/
├── app/ # Streamlit or FastAPI entrypoint
│ ├── main.py # Main web app
│ └── frontend/ # (Optional) frontend components
├── core/ # Business logic modules
│ ├── scraper.py # Website scraping (text + images)
│ ├── summarizer.py # LLM summarization logic
│ ├── classifier.py # NAICS prediction
│ ├── image_analysis.py # Vehicle detection from images
│ ├── prompts/ # Prompt templates for LLM
│ └── utils.py
├── data/ # Sample data, test websites, labeled data
├── models/ # Trained models or checkpoints
├── monitor/ # Logging and monitoring tools
│ ├── logging_config.py
│ └── metrics_collector.py
├── notebooks/ # Prototyping & EDA
├── tests/ # Unit and integration tests
├── docs/ # Architecture diagrams, illustrations
├── azure-deploy/ # Azure-specific config or IaC
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md
└── PROJECT_PLAN.md
---

## 📆 10-Week Learning & Build Plan (1 Hour/Day)

### Week 1 – Project Setup
- Initialize GitHub repo and structure
- Draft `README.md`
- Add `.gitignore`, `Dockerfile`, `requirements.txt`, `.env.example`

### Week 2 – Scraper
- Build website scraper for text and HTML
- Add image scraper (and filtering logic)
- Save scraped content in standard format

### Week 3 – LLM Summarizer & Risk Classification
- Connect to OpenAI or Azure OpenAI
- Design prompt templates for:
  - Business summary
  - E-commerce / vehicle / cyber risk flags
- Build function for structured output parsing

### Week 4 – NAICS Code Predictor
- Collect NAICS labeled data (e.g., from Kaggle, U.S. Census)
- Build baseline model (TF-IDF + Logistic Regression or fine-tuned BERT)
- Integrate model into pipeline

### Week 5 – Vehicle Detection from Images
- Run YOLOv8 or Azure CV on scraped images
- Flag vehicle presence based on detected objects
- Combine with text inference

### Week 6 – Inference Pipeline Assembly
- Combine all feature extractors into one pipeline
- Create clean output JSON schema
- Save output examples for sample businesses

### Week 7 – Streamlit Frontend
- Build Streamlit interface:
  - URL input
  - Result display (summary, NAICS, flags)
  - (Bonus) Show image thumbnails and detections

### Week 8 – Azure Deployment
- Deploy backend/frontend to Azure App Service or Container Apps
- Add secrets and API key management
- Ensure app is publicly accessible

### Week 9 – Monitoring & Logging
- Add request logging, error tracking, latency/tokens used
- Integrate with Azure Monitor or App Insights

### Week 10 – Polish, Document & Demo
- Write full `README.md`
- Add screenshots or GIFs
- Record demo (video or Loom)
- Write testing functions for core modules

---

## 🧠 Learning Goals

By the end of this project, you will have:
- Built and deployed a multimodal LLM + CV system
- Used Azure App Services, Azure OpenAI, and (optionally) Azure Monitor
- Learned to build web apps with Streamlit
- Created a production-ready, portfolio-level GitHub repo

---

## 🏁 Stretch Goals (Post-v1)

- Add PDF/file ingestion (e.g., business proposals, brochures)
- Add user feedback loop (correct wrong predictions)
- Add industry/underwriter dashboard
- Integrate structured data sources (e.g., BBB, Yelp)

---

> Want to contribute or adapt this for another industry (e.g., fintech, legal, logistics)? Fork the repo and start building.

