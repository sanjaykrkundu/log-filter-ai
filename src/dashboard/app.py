import streamlit as st
import os
import sys
import json
from dotenv import load_dotenv

# Setup paths and env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

from src.analyzer.runtime_analyzer import RuntimeAnalyzer
from src.analyzer.learning_engine import LearningEngine
from src.analyzer.knowledge_retriever import KnowledgeRetriever

st.set_page_config(page_title="Log Filter AI", layout="wide")

# Paths
trained_dir = os.path.join(project_root, "trained")
workspace_dir = os.path.join(project_root, "workspace")
incoming_dir = os.path.join(project_root, "incoming")
staging_file = os.path.join(trained_dir, "_staging", "suggestions.json")

os.makedirs(incoming_dir, exist_ok=True)

st.title("Log Filter AI - Dashboard")

tab1, tab2, tab3 = st.tabs(["Analyze Dumpstate", "Learning Hub", "Knowledge Base"])

with tab1:
    st.header("Upload Dumpstate for Analysis")
    uploaded_file = st.file_uploader("Choose a dumpstate text file", type=['txt'])
    
    if uploaded_file is not None:
        file_path = os.path.join(incoming_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        if st.button("Run Analysis"):
            with st.spinner("Analyzing camera logs..."):
                try:
                    analyzer = RuntimeAnalyzer(trained_dir, workspace_dir)
                    results = analyzer.analyze_dumpstate(file_path)
                    
                    st.success("Analysis Complete!")
                    
                    findings = results.get("findings", [])
                    if not findings:
                        st.info("No camera errors detected.")
                    else:
                        for idx, f in enumerate(findings):
                            analysis = f.get("analysis", {})
                            with st.expander(f"Line {f.get('line_number')}: {analysis.get('issue_name', 'Unknown')}"):
                                st.write(f"**Classification:** {analysis.get('classification', 'N/A')} (Confidence: {analysis.get('confidence_score', 0):.2f})")
                                st.write(f"**Root Cause:** {analysis.get('root_cause', 'N/A')}")
                                st.write(f"**Suggested Fix:** {analysis.get('suggested_fix', 'N/A')}")
                                st.code(f.get('error_line', ''), language='text')
                                
                    # Trigger continuous learning
                    learner = LearningEngine(trained_dir)
                    learner.process_findings(findings, file_path)
                    st.toast("Continuous Learning Engine triggered.")
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

with tab2:
    st.header("Pending Suggestions (Unknown Issues)")
    
    if os.path.exists(staging_file):
        with open(staging_file, 'r', encoding='utf-8') as f:
            suggestions = json.load(f)
            
        pending = [s for s in suggestions if s.get("status") == "pending_review"]
        
        if pending:
            for idx, s in enumerate(pending):
                st.subheader(f"Suggestion #{idx + 1}")
                st.code(s.get("error_text"), language="text")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Train as New Issue", key=f"approve_{idx}"):
                        st.warning("Training workflow integration pending. Edit training/ folder directly for now.")
                with col2:
                    if st.button("Dismiss", key=f"reject_{idx}"):
                        st.info("Dismissed.")
        else:
            st.info("No pending suggestions.")
    else:
        st.info("No suggestions file found.")

with tab3:
    st.header("Domain Knowledge Base")
    st.write("Teach the AI what proprietary log snippets mean so it can understand them during analysis.")
    
    kr = KnowledgeRetriever(trained_dir)
    
    # Add new entry
    with st.form("add_kb_entry"):
        st.subheader("Add / Update Entry")
        col1, col2 = st.columns([1, 2])
        with col1:
            log_pattern = st.text_input("Log Snippet (e.g., 'CamX: node 5 stalled')")
        with col2:
            meaning = st.text_input("Meaning (e.g., 'ISP node 5 hung due to memory starvation')")
            
        if st.form_submit_button("Save Entry"):
            if log_pattern and meaning:
                kr.add_entry(log_pattern, meaning)
                st.success(f"Added knowledge for: '{log_pattern}'")
            else:
                st.error("Both fields are required.")
                
    # View/Delete entries
    st.subheader("Existing Knowledge")
    entries = kr.get_all()
    if not entries:
        st.info("Knowledge base is empty.")
    else:
        for idx, entry in enumerate(entries):
            col1, col2, col3 = st.columns([2, 4, 1])
            with col1:
                st.code(entry["log_pattern"], language="text")
            with col2:
                st.write(entry["meaning"])
            with col3:
                if st.button("Delete", key=f"del_kb_{idx}"):
                    kr.remove_entry(entry["log_pattern"])
                    st.rerun()

