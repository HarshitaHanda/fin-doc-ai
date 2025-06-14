import streamlit as st
import re
import PyPDF2
import io
import matplotlib.pyplot as plt
import pandas as pd
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
    
    .upload-section {
        background: #e3f2fd;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stSelectbox div > div {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Document processing class
class FinancialDocumentAI:
    def __init__(self):
        self.financial_terms = [
            "revenue", "net income", "eps", "ebitda", "gross profit",
            "operating income", "cash flow", "assets", "liabilities", "equity",
            "dividend", "market share", "debt", "operating margin", "net profit"
        ]
        
        self.sentiment_words = {
            "positive": ["strong", "growth", "increase", "robust", "outperform", "gain", 
                         "record", "expansion", "improvement", "opportunity", "upside"],
            "negative": ["challenge", "decline", "risk", "volatility", "headwind", "loss",
                         "uncertainty", "pressure", "decrease", "weakness", "threat"]
        }
        
        self.risk_keywords = [
            "competition", "regulation", "cybersecurity", "litigation", 
            "compliance", "breach", "fraud", "recession", "inflation"
        ]
    
    def extract_text_from_pdf(self, uploaded_file):
        """Extract text from uploaded PDF file"""
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def extract_financial_metrics(self, text):
        """Extract key financial metrics using NLP"""
        results = {}
        
        # Enhanced pattern matching for financial metrics
        patterns = {
            "revenue": r"(revenue|sales|total income)[^\d]*([\d,\.]+)\s*(million|billion|)",
            "net income": r"(net income|net profit|net earnings)[^\d]*([\d,\.]+)\s*(million|billion|)",
            "eps": r"(eps|earnings per share)[^\d]*([\d,\.]+)",
            "ebitda": r"(ebitda)[^\d]*([\d,\.]+)\s*(million|billion|)",
            "gross profit": r"(gross profit|gross margin)[^\d]*([\d,\.]+)\s*(million|billion|)"
        }
        
        for metric, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                values = []
                for match in matches:
                    try:
                        value = float(match[1].replace(',', ''))
                        if "billion" in match[2].lower():
                            value *= 1000
                        values.append(value)
                    except:
                        continue
                results[metric] = max(values) if values else None
        
        return results
    
    def analyze_sentiment(self, text):
        """Analyze document sentiment"""
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
    
    def identify_risk_factors(self, text):
        """Identify and categorize risk factors"""
        risk_categories = {
            "Market Risks": ["competition", "market share", "demand", "pricing"],
            "Regulatory Risks": ["regulation", "compliance", "legal", "litigation"],
            "Operational Risks": ["supply chain", "production", "cybersecurity", "fraud"],
            "Financial Risks": ["debt", "liquidity", "interest rates", "inflation"],
            "Strategic Risks": ["acquisition", "innovation", "disruption", "technology"]
        }
        
        risks_found = defaultdict(list)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        
        for sentence in sentences:
            for category, keywords in risk_categories.items():
                if any(keyword in sentence.lower() for keyword in keywords):
                    risks_found[category].append(sentence.strip())
        
        # Return top 3 risks per category
        return {category: sentences[:3] for category, sentences in risks_found.items()}
    
    def summarize_key_sections(self, text):
        """Generate summaries for key sections"""
        sections = {
            "Financial Highlights": ["financial highlight", "key metric", "performance summary"],
            "Management Discussion": ["management discussion", "executive summary", "ceo letter"],
            "Risk Factors": ["risk factor", "risk consideration"],
            "Future Outlook": ["outlook", "forward-looking", "future plan"]
        }
        
        summaries = {}
        for section, keywords in sections.items():
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
            relevant = [s for s in sentences if any(kw in s.lower() for kw in keywords)]
            summaries[section] = " ".join(relevant[:5]) or f"No {section} section found"
        
        return summaries

# Initialize AI processor
doc_ai = FinancialDocumentAI()

# App header
st.markdown('<div class="header"><h1>💼 Financial Document Intelligence System</h1><p>AI-Powered Analysis of SEC Filings, Annual Reports, and Earnings Documents</p></div>', unsafe_allow_html=True)

# Document upload section
with st.container():
    st.markdown('<div class="upload-section"><h3>📤 Upload Financial Document</h3></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a PDF or text file", type=["pdf", "txt"], label_visibility="collapsed")

# Sidebar for document type selection
with st.sidebar:
    st.subheader("Analysis Options")
    doc_type = st.selectbox("Document Type", ["10-K Annual Report", "10-Q Quarterly Report", "8-K Current Report", "Earnings Release", "Investor Presentation"])
    
    analysis_options = st.multiselect(
        "Analysis Focus", 
        ["Financial Metrics", "Management Sentiment", "Risk Factors", "Peer Comparison"],
        ["Financial Metrics", "Risk Factors"]
    )
    
    st.divider()
    st.subheader("About This System")
    st.markdown("""
    This AI-powered tool automates financial document analysis:
    - Extracts key financial metrics
    - Analyzes management sentiment
    - Identifies risk factors
    - Summarizes critical sections
    
    **Supported Documents:**
    - SEC filings (10-K, 10-Q, 8-K)
    - Earnings releases
    - Annual reports
    - Investor presentations
    """)
    
    st.divider()
    st.caption("Built for Morgan Stanley Technology Apprenticeship Program")

# Main processing logic
if uploaded_file is not None:
    # Read file content
    if uploaded_file.type == "application/pdf":
        with st.spinner("Extracting text from PDF..."):
            doc_text = doc_ai.extract_text_from_pdf(uploaded_file)
    else:
        doc_text = uploaded_file.getvalue().decode("utf-8")
    
    # Show document preview
    with st.expander("Document Preview", expanded=False):
        st.text(doc_text[:5000] + "..." if len(doc_text) > 5000 else doc_text)
    
    # Process document
    with st.spinner("Analyzing document. This may take 20-30 seconds..."):
        # Perform selected analyses
        results = {}
        
        if "Financial Metrics" in analysis_options:
            results['metrics'] = doc_ai.extract_financial_metrics(doc_text)
        
        if "Management Sentiment" in analysis_options:
            results['sentiment'], results['sentiment_score'] = doc_ai.analyze_sentiment(doc_text)
        
        if "Risk Factors" in analysis_options:
            results['risks'] = doc_ai.identify_risk_factors(doc_text)
        
        if "Peer Comparison" in analysis_options or True:  # Always generate summaries
            results['summaries'] = doc_ai.summarize_key_sections(doc_text)
    
    # Display results
    st.success("Analysis Complete!")
    st.subheader(f"Document Analysis: {uploaded_file.name}")
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4 = st.tabs(["Financial Metrics", "Sentiment & Risks", "Document Summaries", "Full Report"])
    
    with tab1:
        if 'metrics' in results and results['metrics']:
            st.subheader("Key Financial Metrics")
            cols = st.columns(3)
            metric_count = 0
            
            for metric, value in results['metrics'].items():
                with cols[metric_count % 3]:
                    if value:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="text-transform: capitalize; font-weight: bold;">{metric}</div>
                            <div class="metric-value">${value:,.1f}M</div>
                        </div>
                        """, unsafe_allow_html=True)
                metric_count += 1
        else:
            st.warning("No financial metrics found in document")
        
        # Visualization
        if 'metrics' in results and results['metrics']:
            st.subheader("Financial Metrics Distribution")
            fig, ax = plt.subplots(figsize=(10, 4))
            metrics = list(results['metrics'].keys())
            values = [v or 0 for v in results['metrics'].values()]
            
            # Only show metrics with values
            valid_metrics = [m for m, v in zip(metrics, values) if v]
            valid_values = [v for v in values if v]
            
            if valid_metrics:
                ax.bar(valid_metrics, valid_values, color='#3498db')
                ax.set_ylabel('Value (Millions USD)')
                plt.xticks(rotation=45)
                st.pyplot(fig)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'sentiment' in results:
                st.subheader("Document Sentiment")
                sentiment = results['sentiment']
                st.markdown(f'<div class="sentiment-indicator {sentiment}">{sentiment.upper()}</div>', 
                           unsafe_allow_html=True)
                
                # Sentiment meter
                score = results.get('sentiment_score', 0)
                st.metric("Sentiment Score", f"{score:.2f}")
                st.progress((score + 1) / 2)
                
                st.markdown("**Sentiment Keywords Found**")
                pos_count = sum(doc_text.lower().count(word) for word in doc_ai.sentiment_words["positive"])
                neg_count = sum(doc_text.lower().count(word) for word in doc_ai.sentiment_words["negative"])
                st.write(f"✅ Positive: {pos_count} | ❌ Negative: {neg_count}")
        
        with col2:
            if 'risks' in results and results['risks']:
                st.subheader("Risk Factor Analysis")
                
                for category, risks in results['risks'].items():
                    with st.expander(f"{category} ({len(risks)} risks)"):
                        for i, risk in enumerate(risks):
                            st.markdown(f"{i+1}. {risk}")
            else:
                st.info("No risk factors analyzed or detected")
    
    with tab3:
        if 'summaries' in results:
            for section, summary in results['summaries'].items():
                st.subheader(section)
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
    
    with tab4:
        st.subheader("Comprehensive Analysis Report")
        
        # Create downloadable report
        report_content = f"# Financial Document Analysis Report\n\n"
        report_content += f"**Document:** {uploaded_file.name}\n"
        report_content += f"**Type:** {doc_type}\n\n"
        
        if 'metrics' in results:
            report_content += "## Financial Metrics\n"
            for metric, value in results['metrics'].items():
                report_content += f"- **{metric.capitalize()}:** ${value:,.1f}M\n"
            report_content += "\n"
        
        if 'sentiment' in results:
            report_content += f"## Sentiment Analysis\n- **Overall Sentiment:** {results['sentiment'].upper()}\n"
            report_content += f"- **Sentiment Score:** {results.get('sentiment_score', 0):.2f}\n\n"
        
        if 'risks' in results:
            report_content += "## Risk Factors\n"
            for category, risks in results['risks'].items():
                report_content += f"### {category}\n"
                for risk in risks:
                    report_content += f"- {risk}\n"
            report_content += "\n"
        
        if 'summaries' in results:
            report_content += "## Document Summaries\n"
            for section, summary in results['summaries'].items():
                report_content += f"### {section}\n{summary}\n\n"
        
        # Show and download report
        st.download_button(
            label="Download Full Report",
            data=report_content,
            file_name=f"{uploaded_file.name}_analysis_report.md",
            mime="text/markdown"
        )
        
        st.markdown(report_content)

else:
    st.info("Please upload a financial document to begin analysis")
    st.image("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80", 
             caption="Upload PDF annual reports, SEC filings, or earnings documents")

# Add footer
st.divider()
st.caption("© 2024 Financial Document Intelligence System | Built for Morgan Stanley Technology Apprenticeship Program")
