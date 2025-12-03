# 🚀 TrendSpotter: The Automated Insight Engine

**Tagline:** Transform raw AdTech CSV data into executive-ready PDF reports with AI-generated insights in under 2 minutes.

---

## 📋 Table of Contents
- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Quick Start](#-quick-start)
- [Dataset](#-dataset)
- [Technical Approach](#-technical-approach)
- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Challenges & Learnings](#-challenges--learnings)

---

## 🎯 The Problem

**Real-World Scenario:** AdTech Account Managers waste 4-6 hours weekly manually downloading CSVs and creating performance reports. This manual process is:
- ⏰ **Slow** - Takes hours per report
- 😴 **Boring** - Repetitive copy-paste work  
- ❌ **Error-prone** - Manual calculations lead to mistakes
- 📉 **Delayed** - Campaign issues discovered days later

**Pain Point:** If a campaign wastes budget, clients might not know for days due to reporting lag.

---

## 💡 The Solution

**TrendSpotter** automates the entire reporting pipeline:
1. **Upload** raw CSV via drag-and-drop interface
2. **Analyze** 157 campaigns across 3 platforms and 5 channels
3. **Generate** comprehensive PDF with AI insights
4. **Download** executive-ready report in under 2 minutes

### What You Get:
- 📊 Campaign, Platform, and Overall analysis
- 📈 Trend charts (CTR, Spend, Impressions)
- 🤖 AI-generated insights explaining performance
- 📄 Professional PDF with actionable recommendations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gemini API key (free tier available)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd automated-insight-engine

# Install dependencies
pip install -r requirements.txt

# Get Gemini API key
# Visit: https://makersuite.google.com/app/apikey

# Add API key to config.py (line 73)
```

### Run Application

```bash
# Start backend
./start.sh          # Mac/Linux
start.bat           # Windows

# Open frontend
# Navigate to frontend/index.html in browser
```

### Usage
1. Upload CSV → Select campaigns → Generate report → Download PDF

---

## 📊 Dataset

### Marketing Campaign Dataset
- **157 campaigns** over 30 days
- **3 platforms:** Google Ads, Facebook Ads, DV360
- **5 channels:** Search, Display, Social, Mobile, Video
- **45M+ impressions**, **1M+ clicks** tracked

### Required Columns:
```
campaign_item_id, time, ext_service_name, channel_name,
impressions, clicks, media_cost_usd
```

### Optional Columns:
```
creative_width/height, keywords, search_tags, landing_page,
total_reach, unique_reach, campaign_budget_usd
```

---

## 🔧 Technical Approach

### Architecture

```
CSV Upload → Data Processing → AI Analysis → PDF Generation
    ↓              ↓               ↓              ↓
 Flask API    Pandas/NumPy    Gemini AI    ReportLab
```

### Data Pipeline

```
1. Ingestion    : Flask validates and stores CSV
2. Cleaning     : Pandas removes NaN, calculates metrics
3. Aggregation  : Group by campaign, platform, channel
4. Analysis     : Detect trends, anomalies, top performers
5. AI Insights  : Gemini generates natural language analysis
6. Visualization: Matplotlib creates charts
7. PDF Assembly : ReportLab builds final document
```

### Key Techniques

**1. Metric Calculation**
```python
# CTR (Click-Through Rate)
CTR = (clicks / impressions) × 100

# CPM (Cost Per Mille - per 1000 impressions)
CPM = (spend / impressions) × 1000

# CPC (Cost Per Click)
CPC = spend / clicks
```

**2. AI Integration with Guardrails**
```python
# Strict context prevents hallucinations
prompt = f"""Analyze ONLY this data: {metrics}
Rules: Base insights on provided metrics only.
If unknown, say 'Unknown'. No speculation."""

response = gemini_model.generate_content(prompt)
```

**3. Graceful Degradation**
- AI fails → Falls back to template insights
- Missing columns → Skips optional analysis
- Invalid data → Shows error, continues processing

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11** - Core language
- **Flask** - REST API framework
- **Pandas** - Data manipulation
- **NumPy** - Numerical computations
- **Matplotlib/Seaborn** - Visualization

### AI/ML
- **Google Gemini 1.5 Flash** - AI insights
- **Few-shot prompting** - Professional tone
- **Structured outputs** - Consistent format

### Report Generation
- **ReportLab** - PDF creation
- **Pillow** - Image processing

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling

### Why These Choices?

| Tech | Reason |
|------|--------|
| Pandas | Industry standard, robust transformations |
| Gemini Flash | Fast, 1M tokens/day free |
| Flask | Lightweight, easy deployment |
| ReportLab | Production-grade PDFs |

---

## ✨ Features

### 📊 Three Analysis Layers

**Layer 1: Campaign-Level** (Per Campaign)
- Metrics: Impressions, Clicks, CTR, CPM, CPC
- 4-panel trend charts
- Channel breakdown
- Platform distribution
- AI insights

**Layer 2: Platform-Level** (Google, Facebook, DV360)
- Cross-platform comparison
- Platform trends over time
- Keyword analysis
- Budget recommendations

**Layer 3: Overall Insights**
- Executive summary
- Top channels and keywords
- Strategic recommendations

### 🤖 AI-Powered Analysis

**Input:**
```
Campaign 3155: 123,456 impressions, 3,951 clicks, $4,860 spend
CTR: 3.2%, CPC: $1.23, CPM: $5.67
```

**AI Output:**
> "Campaign 3155 demonstrates exceptional performance with a 3.2% CTR, significantly exceeding the 2.1% industry average. The efficient $1.23 CPC indicates well-optimized audience targeting. To maximize ROI, consider scaling budget by 30% while maintaining current creative strategy."

### 📈 Professional Visualizations
- Bar charts (platform comparison)
- Line charts (trends)
- Pie charts (distribution)
- Multi-panel grids

---

## 🚧 Challenges & Learnings

### Challenge 1: Handling Missing Data

**Problem:** Code crashed when CSV lacked optional columns.

**Solution:**
```python
# Defensive programming
if 'creative_width' in df.columns:
    calculate_aspect_ratio()
else:
    df['aspect_ratio'] = 0
```

**Learning:** Always validate data structure first.

---

### Challenge 2: AI Hallucinations

**Problem:** AI invented explanations (e.g., "weather caused drop") without data.

**Solution:**
```python
prompt = f"""Analyze ONLY this data: {metrics}
RULES:
1. Use only provided metrics
2. If unknown, say 'Unknown'
3. No speculation
"""
```

**Learning:** AI needs strict guardrails and clear instructions.

---

### Challenge 3: F-String Syntax

**Problem:** Complex conditionals in f-strings caused errors.

**Solution:**
```python
# Before (breaks):
f"{val if cond else 'N/A'} ({other if other_cond else 'N/A'})"

# After (works):
val_text = val if cond else 'N/A'
other_text = other if other_cond else 'N/A'
f"{val_text} ({other_text})"
```

**Learning:** Keep f-strings simple, pre-compute complex logic.

---

### Challenge 4: Frontend-Backend Connection

**Problem:** Uploads appeared to work but processing failed.

**Solution:**
- Verified CORS in Flask
- Checked API URLs
- Added connection tester
- Implemented detailed logging

**Learning:** Build debugging tools early.

---

## 📁 Project Structure

```
automated-insight-engine/
├── backend/
│   ├── app.py                 # Flask API
│   ├── data_processor.py      # Analysis engine
│   ├── report_generator.py    # PDF generation
│   ├── ai_insights.py         # Gemini integration
│   ├── config.py              # Settings
│   └── requirements.txt       # Dependencies
├── frontend/
│   └── index.html             # Web interface
├── outputs/                   # Generated reports
├── uploads/                   # Uploaded CSVs
├── start.sh / start.bat       # Startup scripts
└── README.md
```

---

## 🎯 Future Enhancements

- [ ] Real-time dashboard
- [ ] Email delivery
- [ ] Database integration (PostgreSQL)
- [ ] Scheduled reports
- [ ] Predictive analytics
- [ ] Multi-user support
- [ ] PowerPoint export

---

## 📝 License

MIT License

---

## 🤝 Contributing

Contributions welcome! Open issues or PRs for:
- New chart types
- Additional AI models
- Advanced analytics
- Multi-language support

---

**Built for AdTech professionals who deserve better analytics** 🚀

*Version 1.0.0 - December 2024*
