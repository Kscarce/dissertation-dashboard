import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Procedural Fairness in Healthcare AI",
    page_icon="🏥",
    layout="wide"
)

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

st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; }}
    .block-container {{ padding: 2rem 3rem; max-width: 1200px; }}
    h1 {{ color: {PRIMARY}; font-family: Georgia, serif; font-size: 2rem; margin-bottom: 0; }}
    h2 {{ color: {DARK}; font-size: 1.3rem; font-weight: 600; margin-top: 2rem; }}
    h3 {{ color: {DARK}; font-size: 1.1rem; font-weight: 600; }}
    .subtitle {{ color: #666; font-size: 1rem; margin-top: 0.2rem; margin-bottom: 1.5rem; }}
    .big-number {{ font-size: 3rem; font-weight: 700; color: {PRIMARY}; line-height: 1; }}
    .big-label {{ font-size: 0.85rem; color: #666; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    .card {{ background: white; border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .pass-card {{ border-left: 4px solid {PASS_COLOR}; background: {PASS_BG}; }}
    .fail-card {{ border-left: 4px solid {FAIL_COLOR}; background: {FAIL_BG}; }}
    .partial-card {{ border-left: 4px solid {PARTIAL_COLOR}; background: {PARTIAL_BG}; }}
    .rule-name {{ font-weight: 700; font-size: 1rem; }}
    .rule-desc {{ font-size: 0.88rem; color: #444; margin-top: 0.2rem; }}
    .badge {{ display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }}
    .pass-badge {{ background: {PASS_COLOR}; color: white; }}
    .fail-badge {{ background: {FAIL_COLOR}; color: white; }}
    .partial-badge {{ background: {PARTIAL_COLOR}; color: white; }}
    .divider {{ border: none; border-top: 1px solid #eee; margin: 1.5rem 0; }}
    .survey-stat {{ background: white; border-radius: 10px; padding: 1rem 1.2rem; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .survey-pct {{ font-size: 2.2rem; font-weight: 700; color: {PRIMARY}; }}
    .survey-label {{ font-size: 0.82rem; color: #555; margin-top: 0.2rem; }}
    .connection-box {{ background: white; border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid {PRIMARY}; }}
    .rec-box {{ background: white; border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
    .high-priority {{ border-left: 4px solid {FAIL_COLOR}; }}
    .medium-priority {{ border-left: 4px solid {PARTIAL_COLOR}; }}
</style>
""", unsafe_allow_html=True)

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

leventhal = {
    "Accuracy": {
        "healthcare": "The model must achieve acceptable accuracy for clinical use — errors in medical diagnosis carry direct patient safety risks",
        "baseline": "PASS", "mitigated": "PASS", "type": "Technical",
        "baseline_detail": "84% accuracy · AUC-ROC 0.90 — meets the 80% clinical threshold",
        "mitigated_detail": "80% accuracy · AUC-ROC 0.84 — marginal reduction, still above clinical threshold"
    },
    "Bias Suppression": {
        "healthcare": "Protected characteristics such as sex, age, race, and socioeconomic status must not unfairly drive predictions. In this audit, sex and age were assessed as the sensitive attributes available in the dataset",
        "baseline": "FAIL", "mitigated": "PARTIAL", "type": "Technical",
        "baseline_detail": "Female recall 63% vs male recall 83% — 20 point gap · Demographic parity difference 0.26 (threshold ±0.10)",
        "mitigated_detail": "Female recall improved to 88% · Demographic parity difference reduced to 0.04 — partially resolved · Equalised odds difference remains at 0.21"
    },
    "Representativeness": {
        "healthcare": "Training data must adequately represent all patient populations who will be subject to the system's decisions — underrepresentation leads to poorer performance for those groups",
        "baseline": "FAIL", "mitigated": "FAIL", "type": "Technical",
        "baseline_detail": "Dataset 21% female vs 33% real-world CHD prevalence · Representation ratio 0.64 (threshold 0.80) · 76% of patients under 60 despite CHD being concentrated in older populations",
        "mitigated_detail": "Unchanged — mitigation does not alter training data composition. Requires better data collection."
    },
    "Consistency": {
        "healthcare": "The same decision logic must be applied to all patients and produce stable, predictable results — similar patients should receive consistent predictions",
        "baseline": "FAIL", "mitigated": "FAIL", "type": "Technical",
        "baseline_detail": "8.7% of predictions changed under minor clinical variation (threshold 5%) · Under-45s worst at 15.9% — consistent with lower model confidence in underrepresented groups",
        "mitigated_detail": "Unchanged — consistency requires more representative training data, not algorithmic mitigation"
    },
    "Correctability": {
        "healthcare": "Mechanisms must exist for clinicians and patients to review, challenge, and override AI outputs — flawed decisions must be correctable",
        "baseline": "FAIL", "mitigated": "PARTIAL", "type": "Sociotechnical",
        "baseline_detail": "3 of 7 criteria met · No clinician override, no patient challenge process, no audit trail, no model version history",
        "mitigated_detail": "4 of 8 criteria met · Confidence flagging added — 20% of uncertain predictions now flagged for clinician review · Institutional mechanisms still absent"
    },
    "Ethicality": {
        "healthcare": "The system must respect patient dignity, rights, and data privacy — complying with GDPR, NHS AI ethics guidelines, and relevant legal frameworks",
        "baseline": "PASS", "mitigated": "PASS", "type": "Sociotechnical",
        "baseline_detail": "7 of 8 criteria met · Ethics approval granted · Data fully anonymised · GDPR compliant · Known limitation: patients unlikely to have consented explicitly to ML research use",
        "mitigated_detail": "Unchanged"
    }
}

def badge(result):
    cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
    return f"<span class='badge {cls}-badge'>{result}</span>"

def rule_card(name, data, show_mitigated):
    result = data["mitigated"] if show_mitigated else data["baseline"]
    detail = data["mitigated_detail"] if show_mitigated else data["baseline_detail"]
    cls = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}[result]
    st.markdown(f"""
    <div class='card {cls}-card'>
        <div style='display:flex; justify-content:space-between; align-items:start;'>
            <div>
                <div class='rule-name'>{name}</div>
                <div class='rule-desc' style='margin-top:0.4rem;'>{data['healthcare']}</div>
            </div>
            <div style='margin-left:1rem; flex-shrink:0;'>{badge(result)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("See assessment details"):
        st.markdown(f"**Assessment type:** {data['type']}")
        st.markdown(f"**Finding:** {detail}")

tabs = st.tabs([
    "Overview",
    "Fairness Protocol",
    "Pipeline Results",
    "Survey Results",
    "Survey × Pipeline",
])

# ── TAB 1: OVERVIEW ──────────────────────────────────────────
with tabs[0]:
    st.markdown("<h1>Procedural Fairness in Healthcare AI</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>A fairness audit of a heart disease prediction pipeline · Newcastle University MSc 2026 · Kaylee Scarce</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card' style='background:#fff0f3; border-left:4px solid {PRIMARY};'>
        <strong>What is procedural fairness?</strong><br>
        Procedural fairness means the AI system's decision-making <em>process</em> — not just its results — is fair to all patients.
        <br><br>
        A heart disease prediction model was trained on 918 patient records and audited against six internationally recognised 
        procedural fairness criteria. Here's what we found.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='card' style='text-align:center;'>
            <div class='big-number'>4 of 6</div>
            <div class='big-label'>Fairness criteria failed</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='card' style='text-align:center;'>
            <div class='big-number' style='color:{FAIL_COLOR};'>63%</div>
            <div class='big-label'>Female patient recall</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='card' style='text-align:center;'>
            <div class='big-number' style='color:{PASS_COLOR};'>83%</div>
            <div class='big-label'>Male patient recall</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center; color:#666; font-size:0.9rem; margin-top:-0.3rem;'>The model correctly identified heart disease in 83% of male patients but only 63% of female patients — a 20 point gap.</p>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Fairness Criteria — At a Glance")

    show_mit = st.toggle("Show results after bias mitigation", value=False, key="overview_toggle")

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
                <div class='rule-desc'>{data['healthcare'][:80]}...</div>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 2: FAIRNESS PROTOCOL ──────────────────────────────────
with tabs[1]:
    st.markdown("<h1>Fairness Protocol</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>How each of Leventhal's (1980) six procedural justice rules applies to this healthcare AI system — and whether this pipeline meets them</div>", unsafe_allow_html=True)

    show_mit2 = st.toggle("Show results after bias mitigation", value=False, key="protocol_toggle")

    for name, data in leventhal.items():
        rule_card(name, data, show_mit2)

# ── TAB 3: PIPELINE RESULTS ───────────────────────────────────
with tabs[2]:
    st.markdown("<h1>Pipeline Results</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Technical findings from the heart disease prediction model — before and after fairness mitigation</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Baseline Model")
        st.metric("Accuracy", "84%",
                  help="Percentage of all predictions that were correct")
        st.metric("AUC-ROC", "0.90",
                  help="How well the model separates patients with and without heart disease. 1.0 is perfect, 0.5 is random guessing.")
    with col2:
        st.markdown("### After Mitigation")
        st.metric("Accuracy", "80%", delta="-4%", delta_color="inverse",
                  help="Percentage of all predictions that were correct")
        st.metric("AUC-ROC", "0.84", delta="-0.06", delta_color="inverse",
                  help="How well the model separates patients with and without heart disease. 1.0 is perfect, 0.5 is random guessing.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Recall by Sex — Baseline vs Mitigated")
    st.caption("Recall = the % of actual heart disease cases the model correctly identified. Low recall means patients with heart disease are being missed.")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Baseline', x=['Male', 'Female'],
        y=[83, 63], marker_color=PRIMARY,
        text=['83%', '63%'], textposition='outside',
        width=0.3
    ))
    fig.add_trace(go.Bar(
        name='After Mitigation', x=['Male', 'Female'],
        y=[77, 88], marker_color=LIGHT,
        text=['77%', '88%'], textposition='outside',
        width=0.3
    ))
    fig.add_hline(y=80, line_dash="dot", line_color="#999",
                  annotation_text="80% clinical threshold",
                  annotation_position="right")
    fig.update_layout(
        barmode='group',
        yaxis=dict(range=[0, 105], showgrid=False, showticklabels=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=1.1),
        margin=dict(t=20, b=20, l=0, r=80),
        font=dict(color=DARK, size=13),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Fairness Metrics")
    st.caption("Closer to 0 means fairer. Values above ±0.10 indicate meaningful bias.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Demographic Parity Difference",
                  "0.04 after mitigation",
                  delta="improved from 0.26",
                  delta_color="normal",
                  help="Gap in positive prediction rates between male and female patients. 0 = perfectly equal rates.")
    with col2:
        st.metric("Equalised Odds Difference",
                  "0.21 after mitigation",
                  delta="unchanged from 0.20",
                  delta_color="off",
                  help="Gap in true positive and false positive rates between groups. 0 = equal error rates across groups.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### Confidence Flagging")
    st.caption("Predictions where the model was less than 70% confident were automatically flagged for clinician review.")

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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>325</div><div class='survey-label'>Total responses</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>83%</div><div class='survey-label'>Non-technical background</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='survey-stat'><div class='survey-pct'>67%</div><div class='survey-label'>Female respondents</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## Public support for each fairness criterion")
    st.caption("Each bar shows the % of respondents whose answer aligns with that Leventhal criterion being important.")

    criteria = ["Accuracy", "Bias Suppression", "Consistency", "Correctability", "Ethicality", "Trust in AI"]
    support = [84, 74, 64, 93, 96, 81]
    colors = [PASS_COLOR if s >= 80 else PRIMARY for s in support]

    fig_survey = go.Figure(go.Bar(
        x=support,
        y=criteria,
        orientation='h',
        marker_color=colors,
        text=[f"{v}%" for v in support],
        textposition='outside',
    ))
    fig_survey.update_layout(
        xaxis=dict(range=[0, 110], showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, autorange='reversed'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=0, r=60),
        height=320,
        font=dict(color=DARK, size=13)
    )
    st.plotly_chart(fig_survey, use_container_width=True)

    with st.expander("See all survey questions and responses"):
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
            pcts = (filtered / 325 * 100).round(0).astype(int)

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

# ── TAB 5: SURVEY × PIPELINE ──────────────────────────────────
with tabs[4]:
    st.markdown("<h1>Survey × Pipeline</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Where public values align with the technical findings</div>", unsafe_allow_html=True)
    st.markdown("## Does the public agree with what the pipeline found?")
    connections = [
        {
            "rule": "Bias Suppression",
            "pipeline": "63% female recall vs 83% male — 20pt gap",
            "survey": "74% chose equal performance over higher accuracy",
            "verdict": "Public would not accept this system as deployed",
            "pass": False
        },
        {
            "rule": "Correctability",
            "pipeline": "No override or challenge mechanism exists",
            "survey": "93% say patients should always challenge AI decisions",
            "verdict": "Near-universal demand validates this as a critical gap",
            "pass": False
        },
        {
            "rule": "Ethicality",
            "pipeline": "Patients unlikely to have consented to ML research use",
            "survey": "80% say patients must be informed when data trains AI",
            "verdict": "Public confirms this is a genuine ethical concern",
            "pass": False
        },
        {
            "rule": "Accuracy",
            "pipeline": "84% accuracy — meets clinical threshold",
            "survey": "81% trust AI somewhat but want human oversight",
            "verdict": "Accuracy passes, but public still wants human involvement",
            "pass": True
        },
    ]

    col_headers = ["Leventhal Rule", "Pipeline Finding", "Public Survey", "Verdict"]
    header_html = f"""
    <div style='display:grid; grid-template-columns:1fr 1.5fr 1.5fr 1.5fr; gap:0.5rem; 
    padding:0.6rem 1rem; background:{PRIMARY}; border-radius:8px 8px 0 0; color:white; 
    font-weight:600; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.04em;'>
        {''.join(f'<div>{h}</div>' for h in col_headers)}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    for i, c in enumerate(connections):
        bg = "white" if i % 2 == 0 else "#fdf8f9"
        verdict_bg = PASS_BG if c["pass"] else FAIL_BG
        verdict_color = PASS_COLOR if c["pass"] else FAIL_COLOR
        st.markdown(f"""
        <div style='display:grid; grid-template-columns:1fr 1.5fr 1.5fr 1.5fr; gap:0.5rem;
        padding:0.8rem 1rem; background:{bg}; border-bottom:1px solid #eee; font-size:0.86rem;'>
            <div style='font-weight:600; color:{PRIMARY};'>{c['rule']}</div>
            <div style='color:{DARK};'>{c['pipeline']}</div>
            <div style='color:{DARK};'>{c['survey']}</div>
            <div style='background:{verdict_bg}; color:{verdict_color}; font-weight:600; 
            padding:4px 8px; border-radius:6px; font-size:0.82rem;'> {c['verdict']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## What mitigation improved")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {PASS_COLOR};'>
            <div style='font-weight:600;'>Bias Suppression — improved</div>
            <div style='font-size:0.88rem; margin-top:0.4rem; color:#444;'>
                Female recall <strong>63% → 88%</strong> · 74% of the public chose equal performance — they would support this tradeoff
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {PARTIAL_COLOR};'>
            <div style='font-weight:600;'>Correctability — partially improved</div>
            <div style='font-size:0.88rem; margin-top:0.4rem; color:#444;'>
                20% of uncertain predictions now flagged for review · 93% of the public expect challenge rights — more work needed
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("## What still needs to change")

    gaps = [
        ("High", "Collect more representative clinical data", "Representativeness · Consistency", "Dataset 21% female vs 33% real-world. Under-45 instability at 16%."),
        ("High", "Implement clinician override and patient challenge mechanisms", "Correctability", "93% of the public expect this right."),
        ("High", "Establish prediction audit trails", "Correctability", "Required for accountability and retrospective review."),
        ("Medium", "Require informed consent for AI research use", "Ethicality", "80% of the public say this is necessary."),
        ("Medium", "Wider adoption of fairness communication tools", "All criteria", "This dashboard is one step toward transparent AI deployment."),
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