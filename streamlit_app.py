import streamlit as st
import requests
from datetime import date
import plotly.graph_objects as go
import pandas as pd
import time

# =============================
# CUSTOM STYLING
# =============================
st.set_page_config(
    page_title="AI Knowledge Retention Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced visuals
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .concept-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: transform 0.2s;
    }
    
    .concept-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .risk-high {
        border-left: 5px solid #ef4444;
        background: linear-gradient(to right, #fef2f2, white);
    }
    
    .risk-medium {
        border-left: 5px solid #f59e0b;
        background: linear-gradient(to right, #fffbeb, white);
    }
    
    .risk-low {
        border-left: 5px solid #10b981;
        background: linear-gradient(to right, #ecfdf5, white);
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .quiz-question {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .correct-answer {
        background: #d1fae5;
        border: 2px solid #10b981;
        animation: pulse 2s infinite;
    }
    
    .incorrect-answer {
        background: #fee2e2;
        border: 2px solid #ef4444;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .progress-bar {
        height: 10px;
        background: #e2e8f0;
        border-radius: 5px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.5s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/predict"

# =============================
# SESSION STATE INITIALIZATION
# =============================
session_defaults = {
    "concepts": [],
    "page": "main",
    "result": None,
    "answers": {},
    "checked": False,
    "learner_name": "",
    "concept_count": 0
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.markdown("### Study Dashboard")
    
    # Progress tracking
    if st.session_state.concepts:
        st.markdown("#### Progress")
        concepts_added = len(st.session_state.concepts)
        st.progress(concepts_added / max(concepts_added, 10))
        st.caption(f"{concepts_added} concept(s) added")
    
    # Quick actions
    st.markdown("#### Quick Actions")
    if st.button("Reset Session", use_container_width=True):
        for key in session_defaults:
            st.session_state[key] = session_defaults[key]
        st.rerun()
    
    if st.button("View Stats", use_container_width=True) and st.session_state.concepts:
        # Show quick statistics
        st.markdown("##### Current Statistics")
        df_stats = pd.DataFrame(st.session_state.concepts)
        avg_score = df_stats['quiz_score'].mean()
        difficulty_dist = df_stats['difficulty'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Score", f"{avg_score:.1f}%")
        with col2:
            st.metric("Total Concepts", len(st.session_state.concepts))

# =============================
# MAIN PAGE
# =============================
if st.session_state.page == "main":
    # Header with gradient
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0;">AI Knowledge Retention Predictor</h1>
        <p style="margin:0; opacity:0.9; font-size:1.1rem;">Predict forgetting patterns & get personalized revision strategies</p>
    </div>
    """, unsafe_allow_html=True)
    
    learner_name = st.text_input(
        "👤 Learner Name",
        value=st.session_state.learner_name,
        placeholder="Enter your name"
    )
    if learner_name:
        st.session_state.learner_name = learner_name
    
    st.markdown("---")
    
    # Main content in tabs
    tab1, tab2 = st.tabs(["Add Concepts", "View Analysis"])
    
    with tab1:
        # Add concept form with improved UI
        st.markdown("### Add New Study Concept")
        
        with st.container():
            with st.form("concept_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    topic = st.text_input(
                        "Topic Name",
                        placeholder="e.g., Neural Networks, Calculus"
                    )
                    last_revision = st.date_input(
                        "Last Revision Date",
                        date.today(),
                        help="When did you last study this topic?"
                    )
                
                with col2:
                    quiz_score = st.select_slider(
                        "Quiz Score (%)",
                        options=list(range(0, 101, 5)),
                        value=70,
                        help="Your last quiz score for this topic"
                    )
                    difficulty = st.selectbox(
                        "Difficulty Level",
                        ["Low", "Medium", "High"],
                        help="How difficult do you find this topic?"
                    )
                
                
                add = st.form_submit_button(
                    "➕ Add Concept",
                    use_container_width=True,
                    type="primary"
                )
                
                if add:
                    if not topic.strip():
                        st.error("Please enter a topic name")
                    else:
                        concept_data = {
                            "topic": topic,
                            "last_revision": str(last_revision),
                            "quiz_score": quiz_score,
                            "difficulty": difficulty
                        }
                        st.session_state.concepts.append(concept_data)
                        st.session_state.concept_count += 1
                        
                        # Success animation
                        success_msg = st.success(f"Added: **{topic}**")
                        time.sleep(1)
                        success_msg.empty()
                        st.rerun()
        
        # Display added concepts
        if st.session_state.concepts:
            st.markdown("### Your Study Concepts")
            
            for i, concept in enumerate(st.session_state.concepts, 1):
                # Determine card class based on difficulty
                difficulty_class = {
                    "High": "risk-high",
                    "Medium": "risk-medium",
                    "Low": "risk-low"
                }.get(concept['difficulty'], "")
                
                st.markdown(f"""
                <div class="concept-card {difficulty_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin:0;">{i}. {concept['topic']}</h4>
                            <p style="margin:0.2rem 0; color:#64748b;">
                                Last revised: {concept['last_revision']} | 
                                Score: {concept['quiz_score']}% | 
                                Difficulty: {concept['difficulty']}
                            </p>
                        </div>
                        <span style="background:{'#ef4444' if concept['difficulty'] == 'High' else '#f59e0b' if concept['difficulty'] == 'Medium' else '#10b981'}; 
                              color:white; padding:0.3rem 0.8rem; border-radius:20px; font-size:0.8rem;">
                            {concept['difficulty']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Clear all button
            if st.button("Clear All Concepts", type="secondary"):
                st.session_state.concepts = []
                st.session_state.result = None
                st.rerun()
        else:
            st.info("No concepts added yet. Start by adding your first study concept above!")
    
    with tab2:
        # Prediction section
        st.markdown("### Predict Retention")
        
        if not st.session_state.concepts:
            st.warning("Add at least one concept to get predictions")
        else:
            if st.button(
                "Analyze Knowledge Retention",
                use_container_width=True,
                type="primary"
            ):
                payload = {
                    "learner_name": st.session_state.learner_name or "Anonymous",
                    "concepts": st.session_state.concepts
                }
                
                with st.spinner("AI is analyzing your knowledge patterns..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    try:
                        response = requests.post(API_URL, json=payload)
                        if response.status_code == 200:
                            st.session_state.result = response.json()
                            st.success("Analysis complete!")
                        else:
                            st.error("Failed to connect to backend API")
                    except:
                        st.error("Connection error. Please check your API server.")
            
            # Display results
            if st.session_state.result:
                analysis = st.session_state.result.get("analysis", {})
                concepts_analysis = analysis.get("concepts_analysis", [])
                
                st.markdown("### Retention Analysis Report")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                high_risk = sum(1 for c in concepts_analysis if c.get("retention_risk") == "High")
                total_concepts = len(concepts_analysis)
                
                with col1:
                    st.metric("Total Concepts", total_concepts)
                with col2:
                    st.metric("High Risk", high_risk)
                with col3:
                    avg_risk = sum([{"High": 3, "Medium": 2, "Low": 1}[c.get("retention_risk", "Low")] 
                                  for c in concepts_analysis]) / total_concepts
                    risk_level = "High" if avg_risk > 2 else "Medium" if avg_risk > 1 else "Low"
                    st.metric("Average Risk", risk_level)
                
                st.markdown("---")
                
                # Detailed analysis
                for concept in concepts_analysis:
                    risk = concept.get("retention_risk", "Low")
                    risk_color = {
                        "High": "#ef4444",
                        "Medium": "#f59e0b",
                        "Low": "#10b981"
                    }.get(risk, "#64748b")
                    
                    # Expandable concept card
                    with st.expander(
                        f"{concept.get('topic')} - Risk: **{risk}**",
                        expanded=False
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            **Forgetting Window:**  
                            {concept.get('forgetting_window', 'N/A')}
                            
                            **Recommended Revision:**  
                            {concept.get('revision_timing', 'N/A')}
                            
                            **Study Advice:**  
                            {concept.get('study_advice', 'N/A')}
                            """)
                        
                        with col2:
                            # Visual risk indicator
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value={"High": 90, "Medium": 60, "Low": 30}[risk],
                                title={'text': "Retention Risk"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': risk_color},
                                    'steps': [
                                        {'range': [0, 30], 'color': "#10b981"},
                                        {'range': [30, 70], 'color': "#f59e0b"},
                                        {'range': [70, 100], 'color': "#ef4444"}
                                    ],
                                }
                            ))
                            fig.update_layout(height=200, margin=dict(t=0, b=0))
                            st.plotly_chart(fig, use_container_width=True, key=f"chart_{concept.get('topic', '')}_{i}")
                        
                        # Revision roadmap
                        roadmap = concept.get("revision_roadmap", [])
                        if roadmap:
                            st.markdown("**🗺️ Revision Roadmap:**")
                            for i, step in enumerate(roadmap, 1):
                                st.markdown(f"{i}. {step}")
                
                # Start quiz button
                if st.session_state.result.get("quizzes"):
                    st.markdown("---")
                    if st.button("Start Knowledge Quiz", use_container_width=True):
                        st.session_state.page = "quiz"
                        st.session_state.answers = {}
                        st.session_state.checked = False
                        st.rerun()

# =============================
# QUIZ PAGE
# =============================
if st.session_state.page == "quiz":
    # Quiz header with back button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
            <h1 style="margin:0;">Knowledge Check Quiz</h1>
            <p style="margin:0; opacity:0.9;">Test your understanding of reviewed concepts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Back to Analysis", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
    
    quizzes = st.session_state.result.get("quizzes", [])
    total_questions = 0
    correct_answers = 0
    
    # Quiz progress
    if quizzes:
        total_quizzes = len(quizzes)
        quiz_progress = st.progress(0)
    
    for quiz_idx, quiz_data in enumerate(quizzes):
        st.markdown(f"### Topic: {quiz_data.get('topic')}")
        
        quiz_questions = quiz_data.get("quiz", [])
        for q_idx, question in enumerate(quiz_questions):
            total_questions += 1
            q_key = f"q_{quiz_idx}_{q_idx}"
            
            # Quiz question container
            answer_class = ""
            if st.session_state.checked:
                user_answer = st.session_state.answers.get(q_key, {}).get("selected")
                correct_answer = question["correct_answer"]
                if user_answer == correct_answer:
                    answer_class = "correct-answer"
                    correct_answers += 1
                else:
                    answer_class = "incorrect-answer"
            
            st.markdown(f'<div class="quiz-question {answer_class}">', unsafe_allow_html=True)
            
            # Display question
            st.markdown(f"**Q{total_questions}. {question['question']}**")
            
            # Radio buttons for options
            selected = st.radio(
                "Select your answer:",
                question["options"],
                index=None,
                key=q_key,
                label_visibility="collapsed"
            )
            
            st.session_state.answers[q_key] = {
                "selected": selected,
                "correct": question["correct_answer"]
            }
            
            # Show feedback if checked
            if st.session_state.checked:
                if selected == question["correct_answer"]:
                    st.success(f"Correct! The answer is: {question['correct_answer']}")
                else:
                    st.error(f"The correct answer is: {question['correct_answer']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Update progress
        if quizzes:
            quiz_progress.progress((quiz_idx + 1) / total_quizzes)
    
    # Quiz controls
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.checked:
            if st.button("Check My Answers", use_container_width=True, type="primary"):
                st.session_state.checked = True
                st.rerun()
    
    with col2:
        if st.session_state.checked:
            if st.button("Retake Quiz", use_container_width=True):
                st.session_state.checked = False
                st.session_state.answers = {}
                st.rerun()
    
    # Results display
    if st.session_state.checked and total_questions > 0:
        st.markdown("---")
        
        # Score card
        score_percentage = (correct_answers / total_questions) * 100
        score_color = "#ef4444" if score_percentage < 50 else "#f59e0b" if score_percentage < 80 else "#10b981"
        
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;">
            <h2 style="margin:0;">Quiz Results</h2>
            <div style="font-size: 4rem; font-weight: bold; color: {score_color}; 
                        margin: 1rem 0;">
                {correct_answers}/{total_questions}
            </div>
            <div class="progress-bar" style="margin: 2rem auto; width: 80%;">
                <div class="progress-fill" style="width:{score_percentage}%; background:{score_color};"></div>
            </div>
            <p style="font-size: 1.2rem; color: #64748b;">
                Score: <strong>{score_percentage:.1f}%</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Performance message
        if score_percentage >= 80:
            st.success("Excellent! You have a strong understanding of these concepts!")
        elif score_percentage >= 60:
            st.info("Good work! Consider reviewing the missed concepts.")
        else:
            st.warning("Some concepts need more attention. Review the study advice above.")
        
        # Back to analysis button
        if st.button("Return to Analysis Dashboard", use_container_width=True):
            st.session_state.page = "main"
            st.session_state.checked = False
            st.rerun()

# =============================
# FOOTER
# =============================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.markdown(
        "<div style='text-align: center; color: #64748b; padding: 1rem;'>"
        "AI Knowledge Retention Predictor v2.0 • Powered by Streamlit"
        "</div>",
        unsafe_allow_html=True
    )