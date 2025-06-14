import streamlit as st
import re
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Set page config
st.set_page_config(
    page_title="Financial Document Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    :root {
        --primary: #2c3e50;
        --secondary: #3498db;
        --success: #27ae60;
        --warning: #f39c12;
        --danger: #e74c3c;
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary) 0%, #1a2530 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid var(--secondary);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    
    .sentiment-indicator {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .positive { background: #e8f5e9; color: #27ae60; }
    .negative { background: #ffebee; color: #e74c3c; }
    .neutral { background: #e3f2fd; color: #3498db; }
    
    .summary-box {
        background: #f0f7ff;
        border-left: 4px solid var(--secondary);
        padding: 1.5rem;
        border-radius: 8px;
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    .stSelectbox div > div {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Document processing class (self-contained AI)
class FinancialDocumentAI:
    def __init__(self):
        self.financial_terms = [
            "revenue", "net income", "eps", "ebitda", "gross profit",
            "operating income", "cash flow", "assets", "liabilities", "equity"
        ]
        
        self.sentiment_words = {
            "positive": ["strong", "growth", "increase", "robust", "outperform", "gain", 
                         "record", "expansion", "improvement", "opportunity"],
            "negative": ["challenge", "decline", "risk", "volatility", "headwind", "loss",
                         "uncertainty", "pressure", "decrease", "weakness"]
        }
    
    def extract_financial_metrics(self, text):
        """Extract key financial metrics using rule-based NLP"""
        results = {}
        
        # Extract numbers near financial terms
        for term in self.financial_terms:
            pattern = r"(?i)" + re.escape(term) + r"[^\d]*([\d,\.]+)\s*(million|billion|)"
            matches = re.findall(pattern, text)
            if matches:
                values = []
                for match in matches:
                    try:
                        value = float(match[0].replace(',', ''))
                        if "billion" in match[1].lower():
                            value *= 1000
                        values.append(value)
                    except:
                        continue
                results[term] = max(values) if values else None
        
        return results
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using keyword analysis"""
        positive_count = sum(text.lower().count(word) for word in self.sentiment_words["positive"])
        negative_count = sum(text.lower().count(word) for word in self.sentiment_words["negative"])
        
        if positive_count + negative_count == 0:
            return "neutral", 0
        
        score = (positive_count - negative_count) / (positive_count + negative_count)
        if score > 0.2:
            return "positive", score
        elif score < -0.2:
            return "negative", score
        return "neutral", score
    
    def summarize_section(self, text, section_title):
        """Generate summary using extractive method"""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        relevant_sentences = [
            s for s in sentences 
            if any(term in s.lower() for term in self.financial_terms)
            or section_title.lower() in s.lower()
        ]
        return " ".join(relevant_sentences[:5])  # Return top 5 relevant sentences

# Sample financial documents
SAMPLE_DOCUMENTS = {
    "MSFT": """
    MICROSOFT CORPORATION
    ANNUAL REPORT 2023
    
    MANAGEMENT DISCUSSION
    We delivered strong financial results in fiscal year 2023, with revenue increasing 18% to $211 billion. 
    Net income grew 15% to $82 billion, driven by growth in our cloud offerings. 
    Azure revenue increased 27% year-over-year, demonstrating robust demand for our cloud infrastructure.
    
    Despite macroeconomic headwinds, we saw strong performance across our business segments. 
    Our Productivity and Business Processes segment grew 13% to $69 billion, 
    while Intelligent Cloud revenue increased 25% to $91 billion.
    
    RISK FACTORS
    We face intense competition in the cloud services market from Amazon Web Services and Google Cloud. 
    Currency fluctuations may impact our international revenue. 
    Regulatory challenges in key markets could affect future growth.
    
    FINANCIAL HIGHLIGHTS
    Revenue: $211.0 billion
    Net Income: $82.0 billion
    Earnings Per Share (EPS): $10.85
    Cash Flow from Operations: $95.3 billion
    """,
    
    "AAPL": """
    APPLE INC.
    ANNUAL REPORT 2023
    
    MANAGEMENT DISCUSSION
    Apple achieved record revenue of $394 billion in fiscal 2023, driven by strong iPhone and Services growth. 
    Net income increased to $99 billion, with EPS of $6.11. We saw particular strength in emerging markets.
    
    Services revenue reached an all-time high of $78 billion, growing 14% year-over-year. 
    Wearables and Home products also performed well, generating $41 billion in revenue.
    
    RISK FACTORS
    Our business depends on continued innovation in competitive markets. 
    Global supply chain constraints could impact product availability. 
    International trade regulations present ongoing challenges.
    
    FINANCIAL HIGHLIGHTS
    Revenue: $394.3 billion
    Net Income: $99.8 billion
    Earnings Per Share (EPS): $6.11
    Gross Margin: 43.3%
    """,
    
    "JPM": """
    JPMORGAN CHASE & CO.
    ANNUAL REPORT 2023
    
    MANAGEMENT DISCUSSION
    JPMorgan Chase reported solid results in 2023 with revenue of $158 billion and net income of $48 billion. 
    Consumer Banking performed particularly well, with deposit growth of 8%. 
    Investment Banking faced challenges due to market volatility.
    
    We maintained strong capital levels with CET1 ratio of 13.1%, above regulatory requirements. 
    Credit quality remained excellent with net charge-offs of $5.7 billion.
    
    RISK FACTORS
    Interest rate changes could impact net interest income. 
    Cybersecurity threats remain a significant concern. 
    Regulatory requirements continue to evolve and increase.
    
    FINANCIAL HIGHLIGHTS
    Revenue: $158.2 billion
    Net Income: $48.4 billion
    Return on Equity (ROE): 15%
    Book Value Per Share: $93.50
    """
}

# Initialize AI processor
doc_ai = FinancialDocumentAI()

# App header
st.markdown('<div class="header"><h1>💼 Financial Document Intelligence System</h1><p>AI-Powered Analysis of SEC Filings and Financial Reports</p></div>', unsafe_allow_html=True)

# Sidebar for company selection
with st.sidebar:
    st.subheader("Document Selection")
    company = st.selectbox("Select Company", ["MSFT", "AAPL", "JPM"], index=0)
    
    st.divider()
    st.subheader("About This System")
    st.markdown("""
    This AI-powered tool automates analysis of financial documents by:
    - Extracting key financial metrics
    - Analyzing management sentiment
    - Summarizing critical sections
    - Comparing peer performance
    
    **Technology:**
    - Custom NLP algorithms
    - Rule-based extraction
    - Financial domain-specific analysis
    """)
    
    st.divider()
    st.caption("Built for Morgan Stanley Technology Apprenticeship Program")

# Main content
if company in SAMPLE_DOCUMENTS:
    doc_text = SAMPLE_DOCUMENTS[company]
    
    # Process document
    with st.spinner("Analyzing document..."):
        metrics = doc_ai.extract_financial_metrics(doc_text)
        sentiment, sentiment_score = doc_ai.analyze_sentiment(doc_text)
        summary = doc_ai.summarize_section(doc_text, "Management Discussion")
        
        # Prepare comparison data
        comparison_data = []
        for comp, text in SAMPLE_DOCUMENTS.items():
            comp_metrics = doc_ai.extract_financial_metrics(text)
            comp_sentiment = doc_ai.analyze_sentiment(text)[0]
            comparison_data.append({
                "company": comp,
                "revenue": comp_metrics.get("revenue", 0),
                "net_income": comp_metrics.get("net income", 0),
                "sentiment": comp_sentiment
            })
    
    # Display results in two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"Company Analysis: {company}")
        
        # Sentiment indicator
        st.markdown(f"**Document Sentiment:**")
        st.markdown(f'<div class="sentiment-indicator {sentiment}">{sentiment.upper()}</div>', 
                   unsafe_allow_html=True)
        
        # Financial metrics
        st.subheader("Key Financial Metrics")
        if metrics:
            cols = st.columns(2)
            for i, (metric, value) in enumerate(metrics.items()):
                with cols[i % 2]:
                    if value:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-transform: capitalize;">{metric}</div>
                            <div class="metric-value">${value:,.1f}M</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-transform: capitalize;">{metric}</div>
                            <div>N/A</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("No financial metrics found in document")
        
        # Management summary
        st.subheader("Management Discussion Summary")
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
    
    with col2:
        # Peer comparison
        st.subheader("Peer Comparison")
        
        # Revenue comparison chart
        fig, ax = plt.subplots(figsize=(10, 5))
        companies = [d['company'] for d in comparison_data]
        revenues = [d['revenue'] or 0 for d in comparison_data]
        
        colors = []
        for d in comparison_data:
            if d['sentiment'] == 'positive': colors.append('#2ecc71')
            elif d['sentiment'] == 'negative': colors.append('#e74c3c')
            else: colors.append('#3498db')
        
        bars = ax.bar(companies, revenues, color=colors)
        ax.set_ylabel('Revenue (Millions USD)')
        ax.set_title('Revenue Comparison')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'${height:,.0f}M',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # Net income chart
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        net_incomes = [d['net_income'] or 0 for d in comparison_data]
        ax2.plot(companies, net_incomes, marker='o', color='#9b59b6', linewidth=2)
        ax2.set_ylabel('Net Income (Millions USD)')
        ax2.set_title('Net Income Comparison')
        ax2.grid(alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(net_incomes):
            ax2.annotate(f'${v:,.0f}M', (i, v), textcoords="offset points", 
                         xytext=(0,10), ha='center')
        
        st.pyplot(fig2)
        
        # Sentiment comparison
        st.subheader("Sentiment Analysis")
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for d in comparison_data:
            sentiment_counts[d['sentiment']] += 1
        
        sentiment_labels = list(sentiment_counts.keys())
        sentiment_values = list(sentiment_counts.values())
        
        fig3, ax3 = plt.subplots(figsize=(8, 3))
        ax3.barh(sentiment_labels, sentiment_values, 
                 color=['#2ecc71', '#3498db', '#e74c3c'])
        ax3.set_xlim(0, max(sentiment_values) + 1)
        ax3.set_title('Sentiment Distribution Across Companies')
        
        # Add value labels
        for i, v in enumerate(sentiment_values):
            ax3.text(v + 0.1, i, str(v), color='black', va='center')
        
        st.pyplot(fig3)
    
    # How it works section
    st.divider()
    st.subheader("How This AI System Works")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        ### Financial Metrics Extraction
        - Identifies key financial terms (revenue, EPS, EBITDA)
        - Extracts associated numerical values
        - Converts units (millions/billions) to standard format
        """)
    
    with c2:
        st.markdown("""
        ### Sentiment Analysis
        - Analyzes management discussion language
        - Scores positive/negative keywords
        - Classifies overall document sentiment
        """)
    
    with c3:
        st.markdown("""
        ### Peer Comparison
        - Processes multiple documents
        - Compares financial performance
        - Visualizes relative positioning
        """)
    
    st.markdown("""
    This system automates what traditionally takes hours of manual financial analysis, 
    providing Morgan Stanley analysts with instant insights from financial documents.
    """)
    
else:
    st.error("Selected company document not found")

# Add footer
st.divider()
st.caption("© 2024 Financial Document Intelligence System | Built for Morgan Stanley Technology Apprenticeship Program")
