TrendSpotter: The Automated Insight Engine

Tagline: A modular analytics pipeline that transforms raw AdTech marketing logs into structured campaign insights, platform-wise breakdowns, keyword analysis, charts, and AI-generated narratives delivered as final PDF reports.

1. The Problem
Context

AdTech teams receive daily CSV exports from Google Ads, Facebook Ads, DV360, and other advertising platforms. Account Managers must manually merge these files, compute CTR/CPM/CPC, analyze channels and keywords, create charts, and prepare client-ready reports.

Pain Point

This manual workflow is slow, repetitive, and error-prone. Decision-making suffers because insights arrive too late, and budget inefficiencies may continue unnoticed.

Solution

TrendSpotter fully automates the reporting pipeline.
You provide a raw CSV, and the system performs:

Campaign-level breakdown

Platform-level (ext_service_name) analysis

Channel-level segmentation

Keyword and search-tag insights

Time-series trends

LLM-generated narrative analysis

PDF report generation

TrendSpotter removes manual work and scales seamlessly to hundreds of campaigns.

2. Dataset Description

TrendSpotter is designed around a multi-platform AdTech dataset containing detailed metrics from advertising campaigns.

Key Fields

campaign_item_id
Unique campaign identifier.
TrendSpotter uses this to generate a separate analytical report for each campaign.

ext_service_id / ext_service_name
Advertising platforms (Google Ads, Facebook Ads, DV360).

channel_name
Channel type: Search, Display, Social, Video, or Mobile.

impressions, clicks, unique_reach, total_reach
Core engagement metrics used to compute CTR, CPM, CPC, and reach quality.

media_cost_usd, max_bid_cpm, campaign_budget_usd
Budget and spend metrics for cost-efficiency analysis.

creative_id, creative_width, creative_height, template_id
Creative metadata for performance interpretation.

keywords, search_tags
Intent-level metadata extracted for keyword performance analysis.

time, time_zone, weekday_cat
Used for time-based trend, daily behavior, and weekday/weekend comparison.

Why This Dataset Works

It contains all dimensions needed for deep AdTech reporting:

Campaign metrics

Platform comparisons

Channel efficiency

Keyword and search-tag performance

Creative-level insights

Daily trend analysis

This supports both numeric and AI-generated insight generation.

3. Campaign-Specific Reporting

A core feature of TrendSpotter is that each campaign receives its own independent analysis and its own PDF report.

For Every campaign_item_id, the system performs:

Extracts all related data

Computes CTR, CPM, CPC, spend, reach, creative performance

Breaks down performance by platform (ext_service_name)

Compares channel contributions (Search, Display, Social, Video, Mobile)

Analyzes keyword and search-tag effectiveness

Computes daily CTR and spend trends

Generates visualizations

Produces a narrative summary using Google Gemini

Generates a dedicated PDF report for that campaign

Output

If a CSV contains 157 campaigns, the pipeline produces:

157 individual PDF reports
+ 1 master summary (optional)


Each PDF contains tables, charts, insights, and recommendations.

4. Expected End Result
Input

A raw CSV file containing multi-campaign AdTech logs.

Output

For every campaign:

KPI summary (CTR, CPM, CPC, spend, reach)

Platform-level comparisons

Channel-level efficiency metrics

Keyword and search tag analysis

Creative analysis

Daily trend charts

LLM-generated insights

A standalone, multi-page PDF report

5. Technical Approach

TrendSpotter’s pipeline consists of several analytical layers.

Data Processing

Polars is used for ingestion, schema validation, and transformation.

Campaign-Level Analysis

Grouped by campaign_item_id and enriched with engineered metrics.

Platform-Level Analysis

Comparisons between Google Ads, Facebook Ads, and DV360 based on spend and performance.

Channel Analysis

Evaluation of Search, Display, Social, Video, and Mobile contributions.

Keyword Insights

High- and low-performing keywords extracted and ranked.

LLM Integration

Google Gemini generates executive summaries, platform comparisons, and optimization recommendations.

Reporting

ReportLab or WeasyPrint composes the final structured PDF.

6. Tech Stack

Python 3.11

Polars

Google Gemini API

Matplotlib / Plotly

ReportLab / WeasyPrint

Docker & Docker Compose
