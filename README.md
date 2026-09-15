# ⚙️ PackCheck AI : AI-Powered Packaged Commodity Compliance Scanner

> **AI-powered system that scans packaged commodity labels and automatically detects compliance with Legal Metrology rules.**

---

## 🌍 Overview

An AI-powered compliance scanner that analyzes packaged commodity images and labels using **OCR, computer vision, and a rule-based engine** to identify mandatory declarations such as **MRP, net quantity, manufacturer/importer details**, and other required information.
It compares the extracted data against the **Legal Metrology (Packaged Commodities) Rules, 2011**, detects missing or potentially incorrect declarations, and generates an easy-to-understand compliance report highlighting violations and areas requiring verification.
**PackCheck AI** is an **AI-powered compliance scanner** that analyzes **packaged product labels** and automatically checks them against **the Legal Metrology (Packaged Commodities) Rules, 2011.**

---

## 🚀 Key Features
- **AI-Powered Product Scanning** – Analyze product and label images using computer vision.
- **OCR Text Extraction** – Extract packaging information using **Tesseract OCR**.
- **Automated Compliance Checking** – Check extracted data against **Legal Metrology (Packaged Commodities) Rules, 2011.**
- **Mandatory Declaration Detection** – Identify MRP, net quantity, manufacturer/importer details, customer care information, etc.
- **AI/ML-Based Analysis** – Intelligent classification, information extraction, and anomaly detection.
- **Image Processing** – Use **Python + OpenCV (cv2)** for image enhancement, preprocessing, and text-region detection.
- **Rule-Based Compliance Engine** – Apply relevant legal requirements and identify violations.
- **API Integration** – Connect **external product, barcode, and AI services** for additional verification.
- **FastAPI/Flask Backend** – Provide **scalable APIs** for scanning, analysis, and compliance results.
- **Compliance Report Generation** – Generate clear results with detected issues, evidence, and recommendations.
- **Human Review & Confidence Scoring** – Flag uncertain results for manual verification.

---

**Software Stack:**
- 🐍 **Python** — Core development & AI/ML processing  
- 🧩 **OpenCV (CV2)** — Image preprocessing & computer vision  
- 💎 **Tesseract OCR** — Extracting text from product labels  
- ⏩ **FastAPI** — High-performance backend & REST APIs  
- 🧿 **Flask** — Web services and application integration  
- 🔗 **External APIs** — Product/barcode data verification & additional AI services

---

## 🧪 Prototype Workflow
Product Image/Camera → Image Preprocessing (OpenCV) → Text Extraction (Tesseract OCR) → AI/ML Data Extraction → Legal Metrology Rule Engine → Compliance Analysis → Violation Detection → Compliance Score → Report Generation

---

## 🧮 Power Optimization Strategies
- **Lightweight AI/ML Models** — Reduce processing and computational load.
- **Optimized OCR** — Process only relevant text regions instead of the full image.
- **Efficient Image Processing** — Resize and compress images before analysis.
- **API & Backend Optimization** — Minimize API calls and use efficient asynchronous processing.

---

## 📅 Hackathon Development Plan

| Phase | Task |
|-----|------|
| **Phase 1** | Define requirements, study LMPC Rules, and design system architecture. |
| **Phase 2** | Build image processing, Tesseract OCR, backend APIs, and database. |
| **Phase 3** | Integrate AI/ML for data extraction and implement automated rule-based compliance checks. |
| **Phase 4** | Connect frontend, backend, OCR, AI, and external APIs; test with real product labels. |
| **Phase 5** | Improve accuracy and performance, fix bugs, and deploy the working prototype. |
| **Phase 6** | Prepare the UI, compliance reports, workflow demonstration, pitch, and documentation. |

---

## 📊 Results & Impact

- **Faster Compliance Checks** — Automates manual label inspection and reduces inspection time.
- **Improved Accuracy** — AI, OCR, and rule-based validation minimize human oversight errors.
- **Instant Violation Detection** — Identifies missing or potentially incorrect mandatory declarations.
- **Transparent Reports** — Generates clear, evidence-based compliance results for review.
- **Scalable Solution** — Can support inspectors, businesses, and consumers across large volumes of packaged products.

---

