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
    .kpi-label {{ font-size: 1.1rem; font-weight: 700; color: {DARK}; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.3rem; }}
    .kpi-number {{ font-size: 4.5rem; font-weight: 700; color: {PRIMARY}; line-height: 1; }}
    .kpi-sub {{ font-size: 0.85rem; color: #666; margin-top: 0.3rem; }}
    .source-tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; margin-right: 0.4rem; }}
    .source-pipeline {{ background: #e8d5f5; color: #5b2c8e; }}
    .source-survey {{ background: #d5e8f5; color: #1a5276; }}
    .source-both {{ background: #f5e6d5; color: #7d5a2f; }}
    .threshold-note {{ font-size: 0.78rem; color: #888; font-style: italic; margin-top: 0.3rem; }}
    .method-box {{ background: white; border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid {PRIMARY}; }}
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
# LEVENTHAL DATA — definitions adapted from Jabagi et al. (2025)
# ============================================================

leventhal = {
    "Accuracy": {
        "definition": "Decisions must be based on reliable information and sound reasoning.",
        "healthcare": "The heart disease prediction tool must make reliable predictions with minimal errors. Errors in medical diagnosis carry direct patient safety risks.",
        "baseline": "PASS", "mitigated": "PASS",
        "baseline_detail": "Overall accuracy: 84.2%. AUC-ROC: 0.904. Both exceed the 80% minimum accuracy floor used in clinical machine learning literature (Liu et al., 2025; Simon and Aliferis, 2024).",
        "mitigated_detail": "Overall accuracy: 80.4%. AUC-ROC: 0.84. A small reduction accepted as a deliberate tradeoff to reduce the performance gap between male and female patients. Still above the 80% clinical threshold.",
        "threshold": "80% minimum accuracy floor, following conventions in clinical machine learning literature (Liu et al., 2025; Simon and Aliferis, 2024).",
        "metric": "Overall accuracy, AUC-ROC, precision, recall, F1-score"
    },
    "Bias Suppression": {
        "definition": "Personal biases and self-interest must not influence decisions.",
        "healthcare": "The tool must not perform worse for patients based on sex, age, or other protected characteristics. Differences in how often the tool flags patients or how accurately it predicts for different groups indicate bias.",
        "baseline": "FAIL", "mitigated": "PARTIAL",
        "baseline_detail": "Female recall: 62.5% vs male recall: 82.8% (gap of 20.3pp). Demographic parity difference: 0.264. Equalised odds difference: 0.203. Both exceed the ±0.10 threshold derived from the four-fifths rule (Fairlearn, 2024).",
        "mitigated_detail": "After applying ExponentiatedGradient with an EqualizedOdds constraint (Agarwal et al., 2018), female recall improved to 87.5% (+25.0pp). Male recall decreased to 76.8% (−6.0pp). Demographic parity difference reduced to 0.041 (now within threshold). Equalised odds difference remained at 0.212, consistent with limited female representation in the test set (n=27).",
        "threshold": "±0.10 disparity threshold for demographic parity difference and equalised odds difference, consistent with the four-fifths rule used in algorithmic fairness literature (Fairlearn, 2024).",
        "metric": "Demographic parity difference, equalised odds difference, group-level recall"
    },
    "Representativeness": {
        "definition": "Decision-making processes must reflect the concerns and values of all affected groups.",
        "healthcare": "Training data must adequately represent all patient subgroups. Underrepresentation of a group risks poorer model performance for that group.",
        "baseline": "FAIL", "mitigated": "FAIL",
        "baseline_detail": "Female patients: 21.0% of dataset vs 33.0% of real-world CHD inpatient admissions in England (BHF, 2021), giving a representation ratio of 0.64 (below the 0.80 threshold). 75.9% of patients are under 60 despite CHD prevalence rising sharply with age.",
        "mitigated_detail": "Unchanged. Algorithmic mitigation cannot fix data composition. Improving representativeness requires collecting more diverse clinical data.",
        "threshold": "0.80 representation ratio, consistent with the four-fifths rule (Fairlearn, 2024). Dataset demographics compared against CHD prevalence data from the British Heart Foundation (2021).",
        "metric": "Representation ratio (dataset proportion / real-world proportion)"
    },
    "Consistency": {
        "definition": "Procedures must be applied uniformly across individuals and over time.",
        "healthcare": "The tool must make stable, predictable decisions. If a patient's clinical values change by a very small amount, the prediction should remain the same.",
        "baseline": "FAIL", "mitigated": "FAIL",
        "baseline_detail": "Prediction stability test applied ±1 unit of Gaussian noise to continuous features. Overall instability rate: 8.7% (exceeds the 5% threshold). Under-45 patients: 15.9% instability. Over-60 patients: 2.3%.",
        "mitigated_detail": "Unchanged. Consistency improvements require more representative training data so the model has stronger confidence across all patient groups.",
        "threshold": "5% instability threshold, defined as a conservative benchmark for clinical decision support. No established standard exists for this type of prediction stability testing; this threshold was set by the researcher.",
        "metric": "Percentage of predictions that change under minor input perturbation"
    },
    "Correctability": {
        "definition": "Flawed decisions must be able to be reviewed, challenged, and corrected.",
        "healthcare": "Clinicians must be able to override the tool's predictions. Patients must have a way to challenge decisions. Audit trails must record what the tool predicted and what action was taken.",
        "baseline": "FAIL", "mitigated": "PARTIAL",
        "baseline_detail": "Met 3 of 7 checklist criteria: predictions are visible and interpretable, confidence scores are produced, and the dashboard communicates uncertainty. Failed on: clinician override mechanism, patient challenge mechanism, audit trail, model version history.",
        "mitigated_detail": "A confidence-based flagging mechanism was added: predictions where the model is less than 70% confident are automatically flagged for clinician review. This applied to 20.1% of test cases (female patients: 25.9%, male: 19.1%). Met 4 of 8 criteria. Still below the 80% pass threshold, but a meaningful partial intervention.",
        "threshold": "80% of checklist criteria must be met for a PASS. Checklist covers: visible predictions, confidence scores, uncertainty communication, clinician override, patient challenge mechanism, audit trail, model version history, and (post-mitigation) confidence-based flagging.",
        "metric": "Proportion of correctability checklist criteria met (qualitative assessment)"
    },
    "Ethicality": {
        "definition": "Decision-making processes must be compatible with fundamental moral and ethical values.",
        "healthcare": "The tool must respect patient dignity and rights, comply with GDPR and relevant NHS AI ethics guidelines, and avoid unjust harm. Patients should be informed when AI is used in their care.",
        "baseline": "PASS", "mitigated": "PASS",
        "baseline_detail": "Met 7 of 8 checklist criteria (87.5%). Ethics approval granted by Newcastle University. Data fully anonymised. GDPR compliant. Known limitation: patients whose records form the dataset are unlikely to have consented to ML research use.",
        "mitigated_detail": "Unchanged. The informed consent limitation is inherent to retrospective clinical datasets and cannot be resolved within this project.",
        "threshold": "80% of checklist criteria must be met for a PASS. Checklist covers: ethics approval, data anonymisation, GDPR compliance, informed consent, transparency of findings, beneficence, non-maleficence, and patient autonomy.",
        "metric": "Proportion of ethicality checklist criteria met (qualitative assessment)"
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def badge(result):
    cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
    return f"<span class='badge {cls}-badge'>{result}</span>"

def source_tag(source):
    if source == "pipeline":
        return "<span class='source-tag source-pipeline'>Pipeline</span>"
    elif source == "survey":
        return "<span class='source-tag source-survey'>Survey</span>"
    else:
        return "<span class='source-tag source-both'>Pipeline + Survey</span>"

# ============================================================
# DASHBOARD DISPLAY — 4 TABS
# ============================================================

tabs = st.tabs([
    "Overview",
    "Procedural Fairness Assessment",
    "Public Survey",
    "Cross-Analysis and Recommendations",
])

# ── TAB 1: OVERVIEW ──────────────────────────────────────────
with tabs[0]:
    st.markdown("<h1>Procedural Fairness in Healthcare Automated Decision-Making</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='subtitle'>
    Evaluating whether a heart disease prediction tool meets six procedural fairness criteria
    based on Leventhal's (1980) procedural justice framework
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='method-box'>
        <strong>What this dashboard does</strong><br><br>
        This dashboard communicates the results of a procedural fairness assessment applied to a
        logistic regression heart disease classifier trained on the UCI Heart Disease dataset
        (fedesoriano, 2021; n=918 patient records, 11 clinical features).<br><br>
        The assessment evaluates the tool against six procedural justice rules originally defined
        by Leventhal (1980) and adapted for healthcare automated decision-making contexts following
        the approach of Jabagi et al. (2025). Each rule was operationalised as a measurable criterion
        with a defined threshold, and assessed either computationally (accuracy, bias suppression,
        representativeness, consistency) or qualitatively via structured checklists (correctability, ethicality).<br><br>
        Following the baseline assessment, two interventions were applied:
        <strong>ExponentiatedGradient</strong> with an <strong>EqualizedOdds</strong> constraint
        (Agarwal et al., 2018) to address bias suppression, and a <strong>confidence-based flagging
        mechanism</strong> (flagging predictions with &lt;70% model confidence for clinician review)
        to partially address correctability.<br><br>
        A public survey (n=325) was conducted separately to compare pipeline findings against
        public expectations of fairness in healthcare AI. Results from both are presented here.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    show_mit = st.toggle(
        "Show post-mitigation results",
        value=False,
        key="overview_toggle",
        help="Toggle between the baseline logistic regression model and the model after ExponentiatedGradient (EqualizedOdds) mitigation and confidence-based flagging were applied."
    )

    if show_mit:
        standards_met = "4 of 6"
        standards_sub = "2 PASS · 2 PARTIAL · 2 FAIL"
        female_recall = "87.5%"
        male_recall = "76.8%"
        female_color = PASS_COLOR
        missed_text = "After applying ExponentiatedGradient with an EqualizedOdds constraint (Agarwal et al., 2018), the recall gap between male and female patients narrowed substantially. Overall accuracy decreased from 84.2% to 80.4%, a deliberate tradeoff to improve fairness."
    else:
        standards_met = "2 of 6"
        standards_sub = "2 PASS · 0 PARTIAL · 4 FAIL"
        female_recall = "62.5%"
        male_recall = "82.8%"
        female_color = FAIL_COLOR
        missed_text = "The baseline model correctly identified only 62.5% of female patients with heart disease, compared to 82.8% of male patients — a gap of 20.3 percentage points. This disparity is driven by the underrepresentation of female patients in the training data (21.0% of records)."

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"""
        <div class='card' style='text-align:center; padding:2rem;'>
            <div class='kpi-label'>Fairness Criteria Met</div>
            <div class='kpi-number'>{standards_met}</div>
            <div style='font-size:0.82rem; color:#666; margin-top:0.3rem;'>{standards_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='card' style='padding:1.5rem 2rem;'>
            <div class='kpi-label' style='margin-bottom:0.8rem;'>Recall by Sex (Heart Disease Present Class)</div>
            <div style='display:flex; gap:2rem; align-items:center;'>
                <div>
                    <span style='font-size:2.5rem; font-weight:700; color:{female_color};'>{female_recall}</span>
                    <div style='font-size:0.85rem; color:#666; margin-top:0.2rem;'>Female patients</div>
                </div>
                <div style='font-size:1.5rem; color:#ccc;'>vs</div>
                <div>
                    <span style='font-size:2.5rem; font-weight:700; color:{PASS_COLOR};'>{male_recall}</span>
                    <div style='font-size:0.85rem; color:#666; margin-top:0.2rem;'>Male patients</div>
                </div>
            </div>
            <div style='margin-top:1rem; font-size:0.88rem; color:#555;
            padding-top:0.8rem; border-top:1px solid #eee;'>
                {missed_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Procedural Fairness Criteria at a Glance")

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

# ── TAB 2: PROCEDURAL FAIRNESS ASSESSMENT ─────────────────────
with tabs[1]:
    st.markdown("<h1>Procedural Fairness Assessment</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Detailed evaluation of each Leventhal criterion with technical results from the pipeline</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card' style='background:#fff0f3; border-left:4px solid {PRIMARY}; margin-bottom:1.5rem;'>
        <strong>Framework</strong><br><br>
        Each criterion below is based on one of Leventhal's (1980) six procedural justice rules,
        adapted for healthcare automated decision-making following the approach of
        <strong>Jabagi et al. (2025)</strong>, who applied the same framework to algorithmic
        decision-making in human resource management.<br><br>
        The healthcare-specific definitions, data requirements, and evaluation metrics were
        developed as part of this study's procedural fairness protocol. Technical criteria were
        assessed computationally against quantitative thresholds; sociotechnical criteria were
        assessed qualitatively using structured checklists, reflecting the argument of Selbst et al.
        (2019) that fairness in ADM systems cannot be fully addressed through technical
        intervention alone.
    </div>
    """, unsafe_allow_html=True)

    show_mit2 = st.toggle(
        "Show post-mitigation results",
        value=False,
        key="assessment_toggle",
        help="Toggle between the baseline logistic regression model and the model after ExponentiatedGradient (EqualizedOdds) mitigation and confidence-based flagging were applied."
    )

    if show_mit2:
        st.markdown(f"""
        <div class='card' style='background:#fff0f3; border-left:4px solid {PRIMARY};'>
            <strong>What changed in the mitigated model</strong><br><br>
            <strong>1. Bias mitigation:</strong> ExponentiatedGradient with an EqualizedOdds constraint
            (Agarwal et al., 2018) was applied during model training. This is an in-processing method that
            treats fairness-constrained learning as a series of repeated training steps, reweighting and
            retraining the model until the specified fairness constraint is approximately met. The EqualizedOdds
            constraint was chosen because it directly addresses differences in true positive and false positive
            rates between demographic groups, which were the main disparities observed at baseline.<br><br>
            <strong>2. Confidence-based flagging:</strong> Predictions where the model's confidence score
            falls between 30% and 70% are automatically flagged for clinician review, providing a basic
            computational mechanism for human-in-the-loop oversight.
        </div>
        """, unsafe_allow_html=True)

    for name, data in leventhal.items():
        result = data["mitigated"] if show_mit2 else data["baseline"]
        detail = data["mitigated_detail"] if show_mit2 else data["baseline_detail"]
        cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
        st.markdown(f"""
        <div class='card {cls}-card' style='margin-bottom:0.3rem;'>
            <div style='display:flex; justify-content:space-between; align-items:start;'>
                <span class='rule-name'>{name}</span>
                {badge(result)}
            </div>
            <div style='font-size:0.78rem; color:#888; margin-top:0.2rem;'>
                Leventhal (1980), adapted for healthcare ADM by Jabagi et al. (2025): <em>"{data['definition']}"</em>
            </div>
            <div class='rule-desc' style='margin-top:0.4rem;'>{data['healthcare']}</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Assessment details, metrics, and threshold"):
            st.markdown(f"**Finding:** {detail}")
            st.markdown(f"**Metric(s):** {data['metric']}")
            st.markdown(f"**Threshold:** {data['threshold']}")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Baseline vs Post-Mitigation: Recall by Sex")
    st.caption("Recall measures the percentage of actual heart disease cases the tool correctly identified. A lower recall means more patients with heart disease were missed.")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Male',
        x=['Baseline model', 'Post-mitigation model'],
        y=[82.8, 76.8],
        marker_color=PRIMARY,
        text=['82.8%', '76.8%'],
        textposition='outside',
        width=0.3
    ))
    fig.add_trace(go.Bar(
        name='Female',
        x=['Baseline model', 'Post-mitigation model'],
        y=[62.5, 87.5],
        marker_color=LIGHT,
        text=['62.5%', '87.5%'],
        textposition='outside',
        width=0.3
    ))
    fig.add_hline(
        y=80,
        line_dash="dot",
        line_color="#999",
        annotation_text="80% clinical threshold (Liu et al., 2025)",
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
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### How the Fairness Gap Changed")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size:0.85rem; font-weight:600; color:#555; text-transform:uppercase; margin-bottom:0.2rem;'>
                Demographic Parity Difference
            </div>
            <div style='font-size:0.78rem; color:#888; margin-bottom:0.6rem;'>
                Measures whether the tool flags men and women for heart disease at similar rates.
                Threshold: ±0.10 (four-fifths rule; Fairlearn, 2024).
            </div>
            <div style='color:{PASS_COLOR}; font-size:2rem; font-weight:700; line-height:1.2;'>
                Reduced from 0.264 to 0.041
            </div>
            <div style='font-size:0.82rem; color:#555; margin-top:0.5rem;'>Now within the ±0.10 acceptable threshold</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size:0.85rem; font-weight:600; color:#555; text-transform:uppercase; margin-bottom:0.2rem;'>
                Equalised Odds Difference
            </div>
            <div style='font-size:0.78rem; color:#888; margin-bottom:0.6rem;'>
                Measures whether the tool makes similar types of errors for men and women.
                Threshold: ±0.10 (four-fifths rule; Fairlearn, 2024).
            </div>
            <div style='color:{PARTIAL_COLOR}; font-size:2rem; font-weight:700; line-height:1.2;'>
                Remained at 0.212
            </div>
            <div style='font-size:0.82rem; color:#555; margin-top:0.5rem;'>Still above the ±0.10 threshold. Consistent with limited female test set representation (n=27).</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Predictions Flagged for Clinician Review")
    st.caption("After mitigation, the confidence-based flagging mechanism automatically flags predictions where the model's confidence falls between 30% and 70%, recommending them for human review.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall flagged", "20.1%",
                  help="Proportion of test predictions flagged as low-confidence and recommended for clinician review")
    with col2:
        st.metric("Male patients flagged", "19.1%")
    with col3:
        st.metric("Female patients flagged", "25.9%",
                  help="Higher flagging rate for female patients reflects the model's greater uncertainty for this underrepresented group")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Assessment Summary")

    summary_data = []
    for name, data in leventhal.items():
        assessment_type = "Qualitative" if name in ["Correctability", "Ethicality"] else "Quantitative"
        summary_data.append({
            "Rule": name,
            "Baseline": data["baseline"],
            "Post-Mitigation": data["mitigated"],
            "Assessment Type": assessment_type
        })
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

# ── TAB 3: PUBLIC SURVEY ──────────────────────────────────────
with tabs[2]:
    st.markdown("<h1>Public Survey Results</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Public attitudes towards procedural fairness in healthcare AI (n=325)</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='method-box'>
        <strong>Survey Methodology</strong><br><br>
        A public survey was designed to assess public perceptions of fairness in healthcare AI.
        Each question was aligned with one or more of Leventhal's (1980) six procedural fairness rules,
        presented as realistic healthcare AI scenarios in non-technical language. This alignment allows
        survey responses to be interpreted using the same theoretical framework as the computational
        pipeline evaluation.<br><br>
        <strong>Distribution:</strong> The survey used a snowball sampling approach. It was posted on
        social media platforms with a request for respondents to share it further, and physical QR codes
        were printed and placed in publicly accessible locations including the School of Computing building
        and student accommodation at Newcastle University.<br><br>
        <strong>Sample:</strong> 325 responses. No personally identifiable information was collected.
        Participation was voluntary and anonymous. Responses were collected via Google Forms.
        The survey was approved by Newcastle University's ethics board prior to distribution.<br><br>
        <strong>Limitations:</strong> Convenience sampling with potential self-selection bias. The sample
        skews female (67.4%) and non-technical (82.8%), and was conducted exclusively in English.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>325</div><div class='survey-label'>Total responses</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>{female_pct}%</div><div class='survey-label'>Female</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>{non_technical_pct}%</div><div class='survey-label'>Non-technical</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>4</div><div class='survey-label'>Age groups represented</div></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='color:#999; font-size:0.78rem; text-align:center; padding:0.5rem 0;'>
        Age distribution: 41–60 (29.2%) · Under 25 (28.3%) · Over 60 (22.8%) · 25–40 (19.7%) ·
        Gender: Female ({female_pct}%) · Male (32%) · Non-binary (&lt;1%)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Strongest Agreement: Correctability and Ethicality")

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Correctability — Leventhal (1980), adapted by Jabagi et al. (2025)</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;'>
            <div>
                <div class='hero-number'>{challenge_pct}%</div>
                <div class='hero-desc'>said patients should always have the right to request a human review of an AI decision, even where this incurs cost or delay</div>
            </div>
            <div>
                <div class='hero-number'>{human_pct}%</div>
                <div class='hero-desc'>said a human doctor should always be involved in medical decision-making, regardless of AI accuracy</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Ethicality — Leventhal (1980), adapted by Jabagi et al. (2025)</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;'>
            <div>
                <div class='hero-number'>{consent_pct}%</div>
                <div class='hero-desc'>said patients should be informed when an AI tool is being used in their healthcare</div>
            </div>
            <div>
                <div class='hero-number'>{data_consent_pct}%</div>
                <div class='hero-desc'>said patients should always be informed when their historical records are used to train an AI tool, even if fully anonymised</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Moderate Agreement: Bias Suppression and Representativeness")

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Bias Suppression / Representativeness — Leventhal (1980), adapted by Jabagi et al. (2025)</div>
        <div style='display:grid; grid-template-columns:1fr 2fr; gap:1.5rem; align-items:center;'>
            <div>
                <div style='font-size:2.2rem; font-weight:700; color:{DARK};'>{tool_a_pct}%</div>
                <div class='hero-desc'>chose equal performance across all patient groups over higher overall accuracy</div>
            </div>
            <div style='font-size:0.82rem; color:#666; border-left:2px solid #eee; padding-left:1rem;'>
                Respondents were asked to choose between Tool A (80% accuracy for both sexes) and
                Tool B (90% accuracy for male patients, 60% for female patients). This question maps
                to both Bias Suppression and Representativeness: the unequal performance in Tool B
                mirrors the pipeline's baseline disparity, which the technical analysis associated with
                the underrepresentation of female patients in the training data.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## No Clear Public Priority: Consistency and Accuracy")

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Consistency — Leventhal (1980), adapted by Jabagi et al. (2025)</div>
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
            This is the one criterion where the majority view diverged from the procedural fairness pattern
            seen elsewhere in the survey. Most respondents prioritised equal outcomes (a distributive
            fairness concern) over consistent application of rules (a procedural fairness concern).
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='tier-section'>
        <div class='rule-label'>Accuracy — Leventhal (1980), adapted by Jabagi et al. (2025)</div>
        <div style='font-size:0.9rem; color:#555; line-height:1.6;'>
            No survey question directly isolated public views on accuracy as a procedural fairness criterion.
            The trust question, in which {trust_pct}% of respondents reported trusting AI tools somewhat
            but believing there should always be human oversight, provides indirect insight into
            perceptions of model reliability. As this question was not designed to isolate accuracy
            perceptions specifically, it is reported here as a contextual finding only.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    with st.expander("See all survey questions and full response distributions"):
        questions = [
            ('tool_choice', 'Which AI tool should the hospital use? (Maps to: Bias Suppression, Representativeness)',
             ['Tool A — equal performance across groups', 'Tool B — higher overall accuracy', "I'm not sure"]),
            ('correctability', 'Should patients have the right to request human review? (Maps to: Correctability)',
             ['Yes — patients should always have the right to challenge a decision about their health',
              'Only if the patient has a specific reason to doubt the result',
              'No — if the tool is correct most of the time, human reviews are an unnecessary cost']),
            ('fairness_type', 'When it comes to fairness in medical AI, which is more important? (Maps to: Consistency)',
             ['Making sure the AI is equally accurate for all groups of patients',
              'Using the same rules for every patient, no matter who they are',
              'I am not sure']),
            ('responsibility', 'Who should be held responsible when AI makes a wrong diagnosis? (Maps to: Ethicality)',
             ['All of the above', 'No one — AI errors are unavoidable',
              'The doctor who relied on it', "I'm not sure",
              'The hospital that used the tool', 'The company that built the tool']),
            ('consent_use', 'Should patients be told when AI is used in their care? (Maps to: Ethicality)',
             ['Yes — patients have a right to know',
              "No — it doesn't matter how the decision is made as long as it's accurate",
              'Only if the patient asks']),
            ('human_involvement', 'Should a human doctor always be involved? (Maps to: Correctability)',
             ['Yes — human involvement is essential regardless of accuracy',
              'No — accuracy should be the priority', "I'm not sure"]),
            ('data_consent', 'Should patients be informed when their data trains AI? (Maps to: Ethicality)',
             ['Yes — patients should always be informed how their data is used',
              'Only if there is a chance they could be identified from the data',
              'No — anonymised data can be used freely for medical research']),
            ('trust', 'How much do you trust AI in healthcare? (Contextual — no single rule)',
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
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ── TAB 4: CROSS-ANALYSIS AND RECOMMENDATIONS ────────────────
with tabs[3]:
    st.markdown("<h1>Cross-Analysis and Recommendations</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Comparing pipeline findings with public survey results, and identifying priorities for improvement</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card' style='background:#fff0f3; border-left:4px solid {PRIMARY}; margin-bottom:1.5rem;'>
        <strong>How to read this tab</strong><br><br>
        Each finding below is tagged with its data source:
        {source_tag('pipeline')} findings come from the computational pipeline evaluation,
        {source_tag('survey')} findings come from the public survey (n=325), and
        {source_tag('both')} indicates where both sources produced convergent findings.<br><br>
        This separation ensures that pipeline-measured fairness and publicly perceived fairness
        are reported as distinct evidence streams, even where they align.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Where Pipeline and Public Agree")

    cross_findings = [
        {
            "rule": "Bias Suppression",
            "source": "both",
            "pipeline_finding": "Baseline model: female recall 62.5% vs male recall 82.8%. Demographic parity difference 0.264, exceeding the ±0.10 threshold.",
            "survey_finding": f"{tool_a_pct}% of respondents chose equal performance for all groups over higher overall accuracy.",
            "interpretation": "Both the pipeline and the public identify the performance gap between male and female patients as unacceptable. The public preference for equal performance supports the fairness-accuracy tradeoff made during mitigation.",
            "result": "FAIL"
        },
        {
            "rule": "Correctability",
            "source": "both",
            "pipeline_finding": "Baseline: 3 of 7 checklist criteria met. No clinician override or patient challenge mechanism. Post-mitigation: confidence flagging added (20.1% of predictions flagged).",
            "survey_finding": f"{challenge_pct}% said patients should always be able to challenge AI decisions. {human_pct}% said a human doctor should always be involved.",
            "interpretation": "The strongest survey finding directly reinforces the pipeline's most critical gap. The confidence-based flagging mechanism is a partial step, but full correctability requires institutional mechanisms beyond what a research pipeline can implement.",
            "result": "FAIL"
        },
        {
            "rule": "Ethicality",
            "source": "both",
            "pipeline_finding": "7 of 8 criteria met (PASS). Single failure: informed consent for ML research use of patient data.",
            "survey_finding": f"{consent_pct}% said patients should be told when AI is used. {data_consent_pct}% said patients should be informed when their data trains AI, even if anonymised.",
            "interpretation": "Although ethicality passed the pipeline threshold, the survey reveals strong public concern about the one area where it fell short. The consent gap, while inherent to retrospective datasets, represents a genuine public priority.",
            "result": "PASS"
        },
    ]

    for cf in cross_findings:
        result_cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[cf["result"]]
        st.markdown(f"""
        <div class='card' style='margin-bottom:0.5rem;'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;'>
                <div>
                    {source_tag(cf['source'])}
                    <span class='rule-name'>{cf['rule']}</span>
                </div>
                {badge(cf['result'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander(f"See details: {cf['rule']}"):
            st.markdown(f"{source_tag('pipeline')} **Pipeline finding:** {cf['pipeline_finding']}")
            st.markdown(f"{source_tag('survey')} **Survey finding:** {cf['survey_finding']}", unsafe_allow_html=True)
            st.markdown(f"**Interpretation:** {cf['interpretation']}")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Criteria Without Direct Survey Coverage")

    no_survey = [
        {
            "rule": "Accuracy",
            "source": "pipeline",
            "finding": "84.2% baseline accuracy and AUC-ROC of 0.904 both exceed the 80% clinical threshold. Post-mitigation: 80.4% accuracy, still above threshold.",
            "survey_note": f"No survey question directly isolated accuracy as a fairness criterion. {trust_pct}% of respondents reported trusting AI tools somewhat but wanting human oversight, which provides indirect context only.",
            "result": "PASS"
        },
        {
            "rule": "Representativeness",
            "source": "pipeline",
            "finding": "Female patients: 21.0% of dataset vs 33.0% real-world prevalence (representation ratio 0.64, below the 0.80 threshold). Age distribution also skews younger than real-world CHD prevalence.",
            "survey_note": "No survey question directly measured representativeness. However, the tool choice question (74% preferring equal performance) provides indirect support, as the unequal performance was associated with data underrepresentation.",
            "result": "FAIL"
        },
        {
            "rule": "Consistency",
            "source": "pipeline",
            "finding": "Overall instability rate 8.7% (exceeds 5% threshold). Under-45 patients showed 15.9% instability.",
            "survey_note": f"The consistency survey question produced mixed results: {equal_outcomes_pct}% prioritised equal outcomes, {same_rules_pct}% prioritised uniform rules. The majority preference aligns with distributive rather than procedural fairness.",
            "result": "FAIL"
        },
    ]

    for ns in no_survey:
        result_cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[ns["result"]]
        st.markdown(f"""
        <div class='card' style='margin-bottom:0.5rem;'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;'>
                <div>
                    {source_tag(ns['source'])}
                    <span class='rule-name'>{ns['rule']}</span>
                </div>
                {badge(ns['result'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander(f"See details: {ns['rule']}"):
            st.markdown(f"{source_tag('pipeline')} **Pipeline finding:** {ns['finding']}", unsafe_allow_html=True)
            st.markdown(f"{source_tag('survey')} **Survey note:** {ns['survey_note']}", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## What Improved After Mitigation")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {PASS_COLOR};'>
            <div style='font-weight:600;'>Bias Suppression: FAIL → PARTIAL</div>
            <div style='font-size:0.82rem; color:#888; margin-top:0.2rem;'>
                {source_tag('pipeline')} Pipeline evidence
            </div>
            <div style='font-size:0.88rem; margin-top:0.4rem; color:#444;'>
                ExponentiatedGradient with EqualizedOdds constraint improved female recall from
                62.5% to 87.5%. Demographic parity difference reduced from 0.264 to 0.041.
                Overall accuracy tradeoff: 84.2% → 80.4%.
            </div>
            <div style='font-size:0.82rem; margin-top:0.4rem; color:#888; border-top:1px solid #eee; padding-top:0.4rem;'>
                {source_tag('survey')} {tool_a_pct}% of the public chose equal performance, supporting this tradeoff.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {PARTIAL_COLOR};'>
            <div style='font-weight:600;'>Correctability: FAIL → PARTIAL</div>
            <div style='font-size:0.82rem; color:#888; margin-top:0.2rem;'>
                {source_tag('pipeline')} Pipeline evidence
            </div>
            <div style='font-size:0.88rem; margin-top:0.4rem; color:#444;'>
                Confidence-based flagging added: 20.1% of predictions flagged for clinician review
                (female: 25.9%, male: 19.1%). Met 4 of 8 criteria, still below 80% PASS threshold.
            </div>
            <div style='font-size:0.82rem; margin-top:0.4rem; color:#888; border-top:1px solid #eee; padding-top:0.4rem;'>
                {source_tag('survey')} {challenge_pct}% of the public expect challenge rights. More work needed.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Priorities for Future Work")
    st.caption("Each recommendation is tagged with the evidence source it is based on and the Leventhal criterion it addresses.")

    gaps = [
        ("High", "Collect more representative clinical data",
         "Representativeness, Consistency", "pipeline",
         "Dataset is 21.0% female vs 33.0% real-world CHD prevalence (BHF, 2021). Under-45 patients show 15.9% prediction instability. Both failures are driven by data composition, not model architecture."),
        ("High", "Implement clinician override and patient challenge mechanisms",
         "Correctability", "both",
         "Pipeline: only 4 of 8 correctability criteria met. Survey: 92.6% of the public expect patients to have challenge rights, and 92.3% expect human involvement regardless of AI accuracy."),
        ("High", "Establish prediction audit trails and model version control",
         "Correctability", "pipeline",
         "Pipeline: audit trail and model version history both absent. Required for accountability and retrospective review in clinical deployment."),
        ("Medium", "Address informed consent for retrospective data use",
         "Ethicality", "both",
         "Pipeline: patients unlikely to have consented to ML research use. Survey: 79.7% of the public say patients should always be informed when their data trains an AI tool."),
        ("Medium", "Develop fairness communication tools for non-technical stakeholders",
         "All criteria", "pipeline",
         "Pipeline: this dashboard is one approach. Future work should include user testing with clinicians, patients, and policymakers to evaluate accessibility and utility."),
    ]

    for priority, title, rule, source, detail in gaps:
        cls = "high-priority" if priority == "High" else "medium-priority"
        color = FAIL_COLOR if priority == "High" else PARTIAL_COLOR
        st.markdown(f"""
        <div class='rec-box {cls}'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div style='font-weight:600; font-size:0.92rem;'>{title}</div>
                <span style='background:{color}; color:white; padding:2px 8px; border-radius:10px;
                font-size:0.75rem; font-weight:600; white-space:nowrap; margin-left:1rem;'>{priority}</span>
            </div>
            <div style='font-size:0.78rem; margin:0.3rem 0; display:flex; align-items:center; gap:0.4rem;'>
                {source_tag(source)}
                <span style='color:{PRIMARY}; font-weight:600;'>{rule}</span>
            </div>
            <div style='font-size:0.84rem; color:#555;'>{detail}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center; padding:2rem 0 1rem; color:#aaa; font-size:0.82rem;'>
        Procedural Fairness in Healthcare ADM · Kaylee Scarce · Newcastle University 2026 · Supervised by Dr Vlad González-Zelaya
    </div>
    """, unsafe_allow_html=True)
