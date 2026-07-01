import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Procedural Fairness in Healthcare AI",
    page_icon="🏥",
    layout="wide"
)

# ============================================================
# COLOUR SCHEME
# ============================================================

PRIMARY = "#c9748f"
LIGHT = "#f2c4ce"
DARK = "#1a1a1a"
BG = "#fdf8f9"
PASS_COLOR = "#2d6a4f"
FAIL_COLOR = "#9d0208"
PARTIAL_COLOR = "#856404"
PASS_BG = "#d8f3dc"
FAIL_BG = "#ffe0e0"
PARTIAL_BG = "#fff3cd"
RULE_LABEL = "#993556"

# ============================================================
# CSS
# ============================================================

st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; }}
    .block-container {{ padding: 2rem 3rem; max-width: 1200px; }}
    h1 {{ color: {PRIMARY}; font-family: Georgia, serif; font-size: 2rem; margin-bottom: 0; }}
    h2 {{ color: {DARK}; font-size: 1.3rem; font-weight: 600; margin-top: 2rem; }}
    h3 {{ color: {DARK}; font-size: 1.1rem; font-weight: 600; }}
    .subtitle {{ color: #666; font-size: 1rem; margin-top: 0.2rem; margin-bottom: 1.5rem; }}
    .big-number {{ font-size: 3.5rem; font-weight: 700; color: {PRIMARY}; line-height: 1; }}
    .big-label {{ font-size: 0.85rem; color: #666; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    .card {{ background: white; border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .pass-card {{ border-left: 4px solid {PASS_COLOR}; background: {PASS_BG}; }}
    .fail-card {{ border-left: 4px solid {FAIL_COLOR}; background: {FAIL_BG}; }}
    .partial-card {{ border-left: 4px solid {PARTIAL_COLOR}; background: {PARTIAL_BG}; }}
    .rule-name {{ font-weight: 700; font-size: 1.05rem; }}
    .rule-desc {{ font-size: 0.88rem; color: #444; margin-top: 0.3rem; }}
    .badge {{ display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }}
    .pass-badge {{ background: {PASS_COLOR}; color: white; }}
    .fail-badge {{ background: {FAIL_COLOR}; color: white; }}
    .partial-badge {{ background: {PARTIAL_COLOR}; color: white; }}
    .divider {{ border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }}
    .survey-stat {{ background: white; border-radius: 10px; padding: 1rem 1.2rem; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .survey-pct {{ font-size: 2.2rem; font-weight: 700; color: {PRIMARY}; }}
    .survey-label {{ font-size: 0.82rem; color: #555; margin-top: 0.2rem; }}
    .rec-box {{ background: white; border-radius: 10px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .high-priority {{ border-left: 4px solid {FAIL_COLOR}; }}
    .medium-priority {{ border-left: 4px solid {PARTIAL_COLOR}; }}
    .hero-number {{ font-size: 2.8rem; font-weight: 700; color: {DARK}; line-height: 1; }}
    .hero-desc {{ font-size: 0.85rem; color: #5a5a5a; margin-top: 0.3rem; }}
    .rule-label {{ font-size: 0.9rem; font-weight: 700; color: {RULE_LABEL}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.8rem; }}
    .tier-section {{ background: white; border-radius: 10px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .metric-value {{ font-size: 2rem; font-weight: 700; color: {DARK}; line-height: 1; }}
    .metric-change {{ font-size: 1.4rem; font-weight: 700; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING AND SURVEY PREP
# ============================================================

@st.cache_data
def load_survey():
    df = pd.read_excel("disssurvey (Responses).xlsx")
    df.columns = [
        'timestamp', 'age', 'gender', 'technical',
        'tool_choice', 'correctability', 'fairness_type',
        'responsibility', 'consent_use', 'human_involvement',
        'data_consent', 'trust'
    ]
    return df

survey = load_survey()
total_responses = len(survey)

# Survey percentages
tool_a_pct = round((survey['tool_choice'] == 'Tool A — equal performance across groups').sum() / total_responses * 100)
challenge_pct = round((survey['correctability'] == 'Yes — patients should always have the right to challenge a decision about their health').sum() / total_responses * 100)
consent_pct = round((survey['consent_use'] == 'Yes — patients have a right to know').sum() / total_responses * 100)
human_pct = round((survey['human_involvement'] == 'Yes — human involvement is essential regardless of accuracy').sum() / total_responses * 100)
data_consent_pct = round((survey['data_consent'] == 'Yes — patients should always be informed how their data is used').sum() / total_responses * 100)
trust_pct = round((survey['trust'] == 'I trust them somewhat — but there should always be human oversight').sum() / total_responses * 100)
same_rules_pct = round((survey['fairness_type'] == 'Using the same rules for every patient, no matter who they are').sum() / total_responses * 100)
equal_outcomes_pct = round((survey['fairness_type'] == 'Making sure the AI is equally accurate for all groups of patients').sum() / total_responses * 100)
non_technical_pct = round((survey['technical'] == 'No, I work or study in another field / I\'m a student in a non-technical subject').sum() / total_responses * 100)
female_pct = round((survey['gender'] == 'Female').sum() / total_responses * 100)

# ============================================================
# LEVENTHAL DATA
# ============================================================

leventhal = {
    "Accuracy": {
        "healthcare": "The tool must make reliable predictions with minimal errors. Mistakes in medical diagnosis carry direct patient safety risks.",
        "baseline": "PASS", "mitigated": "PASS",
        "baseline_detail": "84% accuracy and AUC-ROC of 0.90 — meets the 80% clinical threshold",
        "mitigated_detail": "80% accuracy and AUC-ROC of 0.84. A small reduction accepted to make the tool fairer for female patients."
    },
    "Bias Suppression": {
        "healthcare": "The tool must not perform worse for patients based on sex, age, race or other characteristics.",
        "baseline": "FAIL", "mitigated": "PARTIAL",
        "baseline_detail": "Female patients correctly identified 63% of the time vs 83% for male patients. Demographic parity difference 0.26 (threshold 0.10).",
        "mitigated_detail": "Female recall improved to 88%. Demographic parity difference reduced to 0.04. Equalised odds difference remains at 0.21."
    },
    "Representativeness": {
        "healthcare": "The data used to train the tool must reflect the full range of patients it will be used on.",
        "baseline": "FAIL", "mitigated": "FAIL",
        "baseline_detail": "Dataset is 21% female vs 33% in real world coronary heart disease cases. 76% of patients are under 60 despite CHD being concentrated in older populations.",
        "mitigated_detail": "Unchanged. Improvements require collecting more representative clinical data."
    },
    "Consistency": {
        "healthcare": "The tool must make stable and predictable decisions for similar patients every time.",
        "baseline": "FAIL", "mitigated": "FAIL",
        "baseline_detail": "8.7% of predictions changed under minor clinical variation. Patients under 45 showed the highest instability at 15.9%.",
        "mitigated_detail": "Unchanged. Consistency requires more representative training data."
    },
    "Correctability": {
        "healthcare": "There must be a way for doctors and patients to question or challenge the tool's decisions.",
        "baseline": "FAIL", "mitigated": "PARTIAL",
        "baseline_detail": "3 of 7 criteria met. No clinician override, no patient challenge process, no audit trail.",
        "mitigated_detail": "4 of 8 criteria met. Confidence flagging added — 20% of uncertain predictions now flagged for clinician review."
    },
    "Ethicality": {
        "healthcare": "The tool must meet ethical and legal standards and respect patient rights and dignity.",
        "baseline": "PASS", "mitigated": "PASS",
        "baseline_detail": "7 of 8 criteria met. Ethics approval granted. Data fully anonymised. GDPR compliant. Known limitation: patients unlikely to have consented to ML research use.",
        "mitigated_detail": "Unchanged."
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def badge(result):
    cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
    return f"<span class='badge {cls}-badge'>{result}</span>"

# ============================================================
# DASHBOARD DISPLAY
# ============================================================

tabs = st.tabs([
    "Overview",
    "How Fairness Was Assessed",
    "Pipeline Results",
    "Survey Results",
    "Survey × Pipeline",
])

# ── TAB 1: OVERVIEW ──────────────────────────────────────────
with tabs[0]:
    st.markdown("<h1>How fair is AI in detecting heart disease?</h1>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='subtitle'>
    A heart disease prediction tool was trained on 918 patient records and audited against
    six internationally recognised procedural fairness criteria.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div class='card' style='text-align:center; padding:2.5rem;'>
            <div style='font-size:4.5rem; font-weight:700; color:{PRIMARY}; line-height:1;'>2 of 6</div>
            <div class='big-label' style='margin-top:0.5rem;'>fairness standards met</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='card' style='padding:1.5rem 2rem;'>
            <div style='font-size:0.85rem; color:#666; text-transform:uppercase;
            letter-spacing:0.05em; margin-bottom:0.8rem;'>The heart disease prediction tool correctly identified</div>
            <div style='display:flex; gap:2rem; align-items:center;'>
                <div>
                    <span style='font-size:2.5rem; font-weight:700; color:{FAIL_COLOR};'>63%</span>
                    <span style='font-size:1rem; margin-left:0.3rem;'>❤️</span>
                    <div style='font-size:0.85rem; color:#666; margin-top:0.2rem;'>of women with heart disease</div>
                </div>
                <div style='font-size:1.5rem; color:#ccc;'>vs</div>
                <div>
                    <span style='font-size:2.5rem; font-weight:700; color:{PASS_COLOR};'>83%</span>
                    <span style='font-size:1rem; margin-left:0.3rem;'>❤️</span>
                    <div style='font-size:0.85rem; color:#666; margin-top:0.2rem;'>of men with heart disease</div>
                </div>
            </div>
            <div style='margin-top:1rem; font-size:0.9rem; color:#555;
            padding-top:0.8rem; border-top:1px solid #eee;'>
                That means 1 in 3 women with heart disease was missed compared to 1 in 6 men.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    show_mit = st.toggle(
        "Show improved model results",
        value=False,
        key="overview_toggle",
        help="After the tool was audited, adjustments were made to reduce the performance gap between male and female patients. Toggle this to see how the results changed."
    )

    col1, col2 = st.columns(2)
    rules = list(leventhal.items())
    for i, (name, data) in enumerate(rules):
        result = data["mitigated"] if show_mit else data["baseline"]
        cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class='card {cls}-card' style='margin-bottom:0.6rem;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span class='rule-name'>{name}</span>
                    {badge(result)}
                </div>
                <div class='rule-desc'>{data['healthcare']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 2: HOW FAIRNESS WAS ASSESSED ─────────────────────────
with tabs[1]:
    st.markdown("<h1>How Fairness Was Assessed</h1>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card' style='background:#fff0f3; border-left:4px solid {PRIMARY}; margin-bottom:1.5rem;'>
        <strong>What is procedural fairness?</strong><br><br>
        Procedural fairness is about whether the process used to make a decision is fair,
        not just whether the final decision is correct.<br><br>
        In this study, the heart disease prediction tool was evaluated using six fairness checks
        based on Leventhal's procedural justice framework.
    </div>
    """, unsafe_allow_html=True)

    show_mit2 = st.toggle(
        "Show improved model results",
        value=False,
        key="protocol_toggle",
        help="After the tool was audited, adjustments were made to reduce the performance gap between male and female patients. Toggle this to see how the results changed."
    )

    # Summary table
    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    col_headers = ["Procedural Rule", "How it applies in healthcare AI", ""]
    header_html = f"""
    <div style='display:grid; grid-template-columns:1.2fr 3fr 0.8fr; gap:0.5rem;
    padding:0.6rem 1rem; background:{PRIMARY}; border-radius:8px 8px 0 0; color:white;
    font-weight:600; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.04em;'>
        {''.join(f'<div>{h}</div>' for h in col_headers)}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    for i, (name, data) in enumerate(leventhal.items()):
        result = data["mitigated"] if show_mit2 else data["baseline"]
        row_bg = {"PASS": PASS_BG, "FAIL": FAIL_BG, "PARTIAL": PARTIAL_BG}[result]
        row_border = {"PASS": PASS_COLOR, "FAIL": FAIL_COLOR, "PARTIAL": PARTIAL_COLOR}[result]
        bg = "white" if i % 2 == 0 else "#fdf8f9"
        st.markdown(f"""
        <div style='display:grid; grid-template-columns:1.2fr 3fr 0.8fr; gap:0.5rem;
        padding:0.8rem 1rem; background:{bg}; border-bottom:1px solid #eee; font-size:0.86rem;'>
            <div style='font-weight:700; color:{PRIMARY};'>{name}</div>
            <div style='color:{DARK};'>{data['healthcare']}</div>
            <div style='text-align:center;'>{badge(result)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Assessment details")

    for name, data in leventhal.items():
        result = data["mitigated"] if show_mit2 else data["baseline"]
        detail = data["mitigated_detail"] if show_mit2 else data["baseline_detail"]
        cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
        st.markdown(f"""
        <div class='card {cls}-card' style='margin-bottom:0.5rem;'>
            <div style='display:flex; justify-content:space-between; align-items:start;'>
                <span class='rule-name'>{name}</span>
                {badge(result)}
            </div>
            <div class='rule-desc' style='margin-top:0.3rem;'>{data['healthcare']}</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("See assessment details"):
            st.markdown(f"**Finding:** {detail}")

# ── TAB 3: PIPELINE RESULTS ───────────────────────────────────
with tabs[2]:
    st.markdown("<h1>Pipeline Results</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Technical findings from the heart disease prediction tool before and after improvements were applied</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card' style='background:#fff0f3; border-left:4px solid {PRIMARY};'>
        Overall accuracy decreased slightly from 84% to 80%. This was a deliberate tradeoff
        to make the tool fairer for female patients.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Before improvements")
        st.metric("Accuracy", "84%",
                  help="Percentage of all predictions that were correct")
        st.metric("AUC-ROC", "0.90",
                  help="How well the tool separates patients with and without heart disease. 1.0 is perfect, 0.5 is random guessing.")
    with col2:
        st.markdown("### After improvements")
        st.metric("Accuracy", "80%",
                  help="Percentage of all predictions that were correct")
        st.metric("AUC-ROC", "0.84",
                  help="How well the tool separates patients with and without heart disease. 1.0 is perfect, 0.5 is random guessing.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Cases correctly identified by sex")
    st.caption("The percentage of actual heart disease cases the tool correctly identified. A lower percentage means more patients with heart disease were missed.")

    # Swapped: Male/Female as colours, Baseline/After improvements as groups
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Male',
        x=['Before improvements', 'After improvements'],
        y=[83, 77],
        marker_color=PRIMARY,
        text=['83%', '77%'],
        textposition='outside',
        width=0.3
    ))
    fig.add_trace(go.Bar(
        name='Female',
        x=['Before improvements', 'After improvements'],
        y=[63, 88],
        marker_color=LIGHT,
        text=['63%', '88%'],
        textposition='outside',
        width=0.3
    ))
    fig.add_hline(
        y=80,
        line_dash="dot",
        line_color="#999",
        annotation_text="80% clinical threshold",
        annotation_position="bottom right"
    )
    fig.update_layout(
        barmode='group',
        yaxis=dict(range=[0, 105], showgrid=False, showticklabels=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=1.1),
        margin=dict(t=20, b=20, l=0, r=120),
        font=dict(color=DARK, size=13),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### How the fairness gap changed")
    st.caption("This checks whether the tool treated men and women the same when deciding who might have heart disease. A gap means one group was more likely to be flagged than the other, even if their health was similar.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size:0.8rem; color:#888; text-transform:uppercase; margin-bottom:0.6rem;'>
                Gender prediction gap
                <span title='Difference in how often men and women were flagged for heart disease'
                style='cursor:help; margin-left:4px;'>❓</span>
            </div>
            <div style='color:{PASS_COLOR}; font-size:2rem; font-weight:700; line-height:1.2;'>
                Reduced from 26% to 4%
            </div>
            <div style='font-size:0.82rem; color:#555; margin-top:0.5rem;'>Now within the acceptable range</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size:0.8rem; color:#888; text-transform:uppercase; margin-bottom:0.6rem;'>
                Gender error gap
                <span title='Difference in how often men and women received incorrect results'
                style='cursor:help; margin-left:4px;'>❓</span>
            </div>
            <div style='color:{PARTIAL_COLOR}; font-size:2rem; font-weight:700; line-height:1.2;'>
                Remained similar at 21%
            </div>
            <div style='font-size:0.82rem; color:#555; margin-top:0.5rem;'>Still an area that needs improvement</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Predictions flagged for clinician review")
    st.caption("After improvements were applied, uncertain predictions were automatically flagged for a doctor to review. This was added to the updated model only.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall flagged", "20%",
                  help="1 in 5 predictions flagged as uncertain and recommended for human review")
    with col2:
        st.metric("Male patients flagged", "19%")
    with col3:
        st.metric("Female patients flagged", "26%",
                  help="Higher uncertainty consistent with underrepresentation of female patients in training data")

# ── TAB 4: SURVEY RESULTS ─────────────────────────────────────
with tabs[3]:
    st.markdown("<h1>Public Survey Results</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>325 members of the public answered questions about fairness in medical AI</div>", unsafe_allow_html=True)

    # Top stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>325</div><div class='survey-label'>Total responses</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>{female_pct}%</div><div class='survey-label'>Female respondents</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>{non_technical_pct}%</div><div class='survey-label'>Non-technical background</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Tier 1
    st.markdown("## Where respondents showed the strongest agreement")

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Correctability</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;'>
            <div>
                <div class='hero-number'>{challenge_pct}%</div>
                <div class='hero-desc'>said patients should always have the right to a human second opinion, even at a cost to the hospital</div>
            </div>
            <div>
                <div class='hero-number'>{human_pct}%</div>
                <div class='hero-desc'>said a human doctor should always be involved, even if the heart disease prediction tool is more accurate</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Ethicality</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;'>
            <div>
                <div class='hero-number'>{consent_pct}%</div>
                <div class='hero-desc'>said patients have a right to know when the heart disease prediction tool is being used in their care</div>
            </div>
            <div>
                <div class='hero-number'>{data_consent_pct}%</div>
                <div class='hero-desc'>said patients should be informed if their records are used to train an AI tool, even if anonymised</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Tier 2
    st.markdown("## Moderate but real agreement")

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Bias Suppression and Representativeness</div>
        <div style='display:grid; grid-template-columns:1fr 2fr; gap:1.5rem; align-items:center;'>
            <div>
                <div style='font-size:2.2rem; font-weight:700; color:{DARK};'>{tool_a_pct}%</div>
                <div class='hero-desc'>chose equal performance for all groups over higher overall accuracy</div>
            </div>
            <div style='font-size:0.82rem; color:#666; border-left:2px solid #eee; padding-left:1rem;'>
                This question maps to both Bias Suppression and Representativeness — it is one data point 
                covering both rules. Respondents were asked to choose between a tool that performs equally 
                well for all patients and one that is more accurate overall but misses more women.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Tier 3
    st.markdown("## Where the data does not show a clear public priority")

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Consistency</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;'>
            <div>
                <div style='font-size:2.2rem; font-weight:700; color:{DARK};'>{same_rules_pct}%</div>
                <div class='hero-desc'>favoured applying the same rules to every patient regardless of outcome</div>
            </div>
            <div>
                <div style='font-size:2.2rem; font-weight:700; color:{DARK};'>{equal_outcomes_pct}%</div>
                <div class='hero-desc'>prioritised equal accuracy across all patient groups over uniform rules</div>
            </div>
        </div>
        <div style='font-size:0.82rem; color:#666; margin-top:1rem; padding-top:0.8rem; border-top:1px solid #eee;'>
            This is the one rule where the majority view ran counter to the pattern seen elsewhere. 
            Most respondents prioritised equal outcomes over consistent process — a finding worth 
            noting in the context of procedural vs distributive fairness.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Accuracy</div>
        <div style='font-size:0.9rem; color:#555;'>
            No survey question directly isolated public views on accuracy as a fairness criterion. 
            The trust question (81% trust the tool somewhat but want human oversight) provides 
            indirect evidence but was not designed to measure accuracy perceptions specifically.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    with st.expander("See all survey questions and full responses"):
        questions = [
            ('tool_choice', 'Which AI tool should the hospital use?',
             ['Tool A — equal performance across groups', 'Tool B — higher overall accuracy', "I'm not sure"]),
            ('correctability', 'Should patients have the right to request human review?',
             ['Yes — patients should always have the right to challenge a decision about their health',
              'Only if the patient has a specific reason to doubt the result',
              'No — if the tool is correct most of the time, human reviews are an unnecessary cost']),
            ('fairness_type', 'When it comes to fairness in medical AI, which is more important?',
             ['Making sure the AI is equally accurate for all groups of patients',
              'Using the same rules for every patient, no matter who they are',
              'I am not sure']),
            ('responsibility', 'Who should be held responsible when AI makes a wrong diagnosis?',
             ['All of the above', 'No one — AI errors are unavoidable',
              'The doctor who relied on it', "I'm not sure",
              'The hospital that used the tool', 'The company that built the tool']),
            ('consent_use', 'Should patients be told when AI is used in their care?',
             ['Yes — patients have a right to know',
              "No — it doesn't matter how the decision is made as long as it's accurate",
              'Only if the patient asks']),
            ('human_involvement', 'Should a human doctor always be involved?',
             ['Yes — human involvement is essential regardless of accuracy',
              'No — accuracy should be the priority', "I'm not sure"]),
            ('data_consent', 'Should patients be informed when their data trains AI?',
             ['Yes — patients should always be informed how their data is used',
              'Only if there is a chance they could be identified from the data',
              'No — anonymised data can be used freely for medical research']),
            ('trust', 'How much do you trust AI in healthcare?',
             ['I trust them somewhat — but there should always be human oversight',
              "I don't trust them — medical decisions should be made by humans only",
              "I'm not sure", 'I trust them fully — AI is more objective than humans']),
        ]

        for col_name, title, main_options in questions:
            counts = survey[col_name].value_counts()
            filtered = counts[counts.index.isin(main_options)]
            other = counts[~counts.index.isin(main_options)].sum()
            if other > 0:
                filtered['Other responses'] = other
            pcts = (filtered / total_responses * 100).round(0).astype(int)

            fig = go.Figure(go.Bar(
                x=pcts.values,
                y=pcts.index,
                orientation='h',
                marker_color=PRIMARY,
                text=[f"{v}%" for v in pcts.values],
                textposition='outside',
            ))
            fig.update_layout(
                title=dict(text=title, font=dict(size=12)),
                xaxis=dict(showgrid=False, showticklabels=False, range=[0, 115]),
                yaxis=dict(showgrid=False, autorange='reversed'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=35, b=10, l=0, r=60),
                height=max(160, len(filtered) * 45),
                font=dict(color=DARK, size=11)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='color:#999; font-size:0.78rem; text-align:center; padding:0.5rem 0;'>
        n = 325 · Age: 41 to 60 (29%) · Under 25 (28%) · Over 60 (23%) · 25 to 40 (20%) ·
        Gender: Female (67%) · Male (32%) · Non-binary (1%) ·
        Technical background: 17% technical · 83% non-technical
    </div>
    """, unsafe_allow_html=True)

# ── TAB 5: SURVEY × PIPELINE ──────────────────────────────────
with tabs[4]:
    st.markdown("<h1>Survey × Pipeline</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Where public values align with the technical findings</div>", unsafe_allow_html=True)

    st.markdown("## Does the public agree with what the pipeline found?")

    connections = [
        {
            "rule": "Accuracy",
            "pipeline": "84% accuracy meets the 80% clinical threshold",
            "survey": "81% trust the tool but want a human doctor always involved",
            "pass": True
        },
        {
            "rule": "Bias Suppression",
            "pipeline": "The tool correctly identified only 63% of women compared to 83% of men",
            "survey": "74% chose equal performance for all groups over higher overall accuracy",
            "pass": False
        },
        {
            "rule": "Correctability",
            "pipeline": "No mechanism exists for patients or clinicians to challenge the tool's decisions",
            "survey": "93% said patients should always have the right to challenge an AI decision",
            "pass": False
        },
        {
            "rule": "Ethicality",
            "pipeline": "Patients unlikely to have consented to their data being used for AI research",
            "survey": "96% said patients should be told when AI is used in their care",
            "pass": False
        },
    ]

    col_headers = ["Leventhal Rule", "Pipeline Finding", "Public Said"]
    header_html = f"""
    <div style='display:grid; grid-template-columns:1fr 2fr 2fr; gap:0.5rem;
    padding:0.6rem 1rem; background:{PRIMARY}; border-radius:8px 8px 0 0; color:white;
    font-weight:600; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.04em;'>
        {''.join(f'<div>{h}</div>' for h in col_headers)}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    for i, c in enumerate(connections):
        row_bg = PASS_BG if c["pass"] else FAIL_BG
        row_border = PASS_COLOR if c["pass"] else FAIL_COLOR
        text_color = PASS_COLOR if c["pass"] else FAIL_COLOR
        st.markdown(f"""
        <div style='display:grid; grid-template-columns:1fr 2fr 2fr; gap:0.5rem;
        padding:0.8rem 1rem; background:{row_bg}; border-bottom:1px solid #eee;
        border-left:4px solid {row_border}; font-size:0.86rem;'>
            <div style='font-weight:600; color:{text_color};'>{c['rule']}</div>
            <div style='color:{DARK};'>{c['pipeline']}</div>
            <div style='color:{DARK};'>{c['survey']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size:0.78rem; color:#888; padding:0.5rem 1rem;
    background:#fdf8f9; border-radius:0 0 8px 8px; border:1px solid #eee; border-top:none;'>
        Bias Suppression, Correctability and Ethicality all failed in the pipeline.
        Public survey results confirm these as the areas of greatest concern.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## What improved after the tool was updated")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {PASS_COLOR};'>
            <div style='font-weight:600;'>Bias Suppression</div>
            <div style='font-size:0.88rem; margin-top:0.4rem; color:#444;'>
                Female patients correctly identified improved from 63% to 88%.
                74% of the public chose equal performance — they would support this tradeoff.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {PARTIAL_COLOR};'>
            <div style='font-weight:600;'>Correctability</div>
            <div style='font-size:0.88rem; margin-top:0.4rem; color:#444;'>
                Uncertain predictions now flagged for clinician review.
                93% of the public expect challenge rights. More work still needed.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## What still needs to change")

    gaps = [
        ("High", "Collect more representative clinical data", "Representativeness and Consistency",
         "Dataset is only 21% female vs 33% real world. Under 45 patients show 16% prediction instability."),
        ("High", "Implement patient and clinician challenge mechanisms", "Correctability",
         "93% of the public expect this right."),
        ("High", "Establish prediction audit trails", "Correctability",
         "Required for accountability and retrospective review."),
        ("Medium", "Require informed consent for AI research use", "Ethicality",
         "80% of the public say this is necessary."),
        ("Medium", "Wider adoption of fairness communication tools", "All criteria",
         "This dashboard is one step toward transparent AI deployment."),
    ]

    for priority, title, rule, detail in gaps:
        cls = "high-priority" if priority == "High" else "medium-priority"
        color = FAIL_COLOR if priority == "High" else PARTIAL_COLOR
        st.markdown(f"""
        <div class='rec-box {cls}'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div style='font-weight:600; font-size:0.92rem;'>{title}</div>
                <span style='background:{color}; color:white; padding:2px 8px; border-radius:10px;
                font-size:0.75rem; font-weight:600; white-space:nowrap; margin-left:1rem;'>{priority}</span>
            </div>
            <div style='font-size:0.78rem; color:{PRIMARY}; margin:0.2rem 0; font-weight:600;'>{rule}</div>
            <div style='font-size:0.84rem; color:#555;'>{detail}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center; padding:2rem 0 1rem; color:#aaa; font-size:0.82rem;'>
        Procedural Fairness in Healthcare ADM · Kaylee Scarce · Newcastle University 2026 · Supervised by Dr Vlad González-Zelaya
    </div>
    """, unsafe_allow_html=True)