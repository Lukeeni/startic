import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Tuple

# Define sound mastery ages (in months) based on typical development (Australian norms)
mastery_ages = {
    'h': 36, 'p': 36, 'm': 36, 'ŋ': 48, 'n': 36, 'w': 48, 'b': 36, 'k': 36, 'g': 36, 'd': 36, 't': 36,
    'j': 48, 'f': 48, 'ʒ': 72, 'l': 60, 'ʃ': 60, 'tʃ': 60, 's': 48, 'dʒ': 72, 'z': 60, 'r': 72, 'v': 60,
    'ð': 84, 'θ': 72,
    'sm': 60, 'sp': 60, 'sw': 60, 'sk': 60, 'sl': 60, 'sn': 60, 'st': 60,
    'bl': 48, 'fl': 48, 'pl': 48, 'br': 48, 'fr': 48, 'pr': 48, 'kw': 48, 'tw': 48,
    'gl': 48, 'kl': 48, 'dr': 48, 'gr': 48, 'kr': 48, 'tr': 48, 'θr': 48,
    'skr': 60, 'spr': 60, 'skw': 60, 'spl': 60
}

# Define positions for each sound
target_positions = {
    'sm': ['initial'], 'sp': ['initial'], 'sw': ['initial'], 'sk': ['initial'], 'sl': ['initial'], 'sn': ['initial'], 'st': ['initial'],
    'bl': ['initial'], 'fl': ['initial'], 'pl': ['initial'], 'br': ['initial'], 'fr': ['initial'], 'pr': ['initial'], 'kw': ['initial'],
    'tw': ['initial'], 'gl': ['initial'], 'kl': ['initial'], 'dr': ['initial'], 'gr': ['initial'], 'kr': ['initial'], 'tr': ['initial'],
    'θr': ['initial'], 'skr': ['initial'], 'spr': ['initial'], 'skw': ['initial'], 'spl': ['initial'], 'ð': ['initial', 'medial'], 'j': ['initial'], 'h': ['initial'],
    'tʃ': ['initial', 'medial', 'final'], 'dʒ': ['initial', 'medial', 'final'], 'ʒ': ['medial'],
    'w': ['initial', 'medial'], 'r': ['initial', 'medial'],
    'ŋ': ['medial', 'final']
}
for sound in mastery_ages:
    if sound not in target_positions:
        target_positions[sound] = ['initial', 'medial', 'final']

# Phonological processes and their age appropriateness (Australian norms)
phonological_processes = {
    'backing': 'atypical', 'interdental lisp': 'atypical', 'fronting': 36, 'gliding': 60, 'stopping': 48, 'vowelisation': 48, 'affrication': 48, 'deaffrication': 48,
    'alveolarization': 48, 'depalatisation': 48, 'labialisation': 48, 'assimilation': 36, 'denasalisation': 48,
    'final consonant devoicing': 60, 'prevocalic voicing': 48, 'coalescence': 36, 'reduplication': 30,
    'cluster reduction (no /s/)': 48, 'cluster reduction (with /s/)': 60, 'final consonant deletion': 48, 'initial consonant deletion': 'atypical',
    'weak syllable deletion': 48, 'epenthesis': 60, 'frontal lisp': 60
}

process_rules = [
    ('gliding', {'r': 'w', 'l': 'w'}),
    ('fronting', {'k': 't', 'g': 'd', 'ŋ': 'n'}),
    ('backing', {'t': 'k', 'd': 'g', 'n': 'ŋ'}),
    ('stopping', {
        'f': ['p', 'b'], 'v': ['b', 'p'], 's': ['t', 'd'], 'z': ['d', 't'], 'ʃ': ['t', 'd'],
        'ʒ': ['d', 't'], 'θ': ['t'], 'ð': ['d']
    }),
    ('deaffrication', {'tʃ': 'ʃ', 'dʒ': 'ʒ'}),
    ('affrication', {'ʃ': 'tʃ', 'ʒ': 'dʒ'}),
    ('labialisation', {'t': 'p', 'd': 'b'}),
    ('alveolarization', {'f': 's', 'v': 'z'}),
    ('depalatisation', {'ʃ': 's', 'ʒ': 'z'}),
    ('final consonant devoicing', {'b': 'p', 'd': 't', 'g': 'k', 'v': 'f', 'z': 's'}),
    ('prevocalic voicing', {'p': 'b', 't': 'd', 'k': 'g'}),
    ('frontal lisp', {'s': 'θ', 'z': 'ð'})
]

def detect_process(target, produced):
    for process, rules in process_rules:
        if target in rules:
            if isinstance(rules[target], list) and produced in rules[target]:
                return process
            elif rules[target] == produced:
                return process
    return None

def detect_cluster_reduction(target, produced):
    return "cluster reduction" if len(produced) == 1 and len(target) > 1 and produced[0] in target else None

def get_age_in_months(age_str: str) -> int:
    try:
        years, months = age_str.split(';')
        return int(years) * 12 + int(months)
    except:
        return 0

st.set_page_config(page_title="Starticulation Assessment", layout="wide")
st.title("Starticulation Articulation Assessment")

if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = True

if st.session_state.show_instructions:
    with st.expander("Welcome to Starticulation - Click to Continue"):
        st.markdown("""
        Welcome to Starticulation, a tool for assessing consonant articulation. Starticulation is made by speech pathologists, for speech pathologists.

        HOW TO USE: Fill in each box with the actual sound produced by the child. Target boxes are filled in by default. For example, if the child produces the /p/ sound accurately, leave the boxes unchanged.

        To report bugs and suggestions, please email lakestundun@gmail.com.

        Please note: Speech pathologists must use their clinical judgement to determine whether phonological processes such as cluster reduction and syllable deletion are truly present, especially when blends are simplified.
        """)
        if st.button("Continue"):
            st.session_state.show_instructions = False

child_name = st.text_input("Child's First Name")
age_input = st.text_input("Child's Age (e.g., 4;6 for 4 years 6 months)")
age_in_months = get_age_in_months(age_input)

ordered_sounds = list(mastery_ages.keys())

if child_name and age_in_months:
    st.header("Articulation Assessment")

    records = []
    for sound in ordered_sounds:
        for pos in target_positions[sound]:
            if sound == 'r' and pos == 'final':
                continue  # Remove /r/ in final position
            records.append({"Sound": sound, "Position": pos.title(), "Produced": sound})

    df = pd.DataFrame(records)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.subheader("Assessment Results")
    results = []
    delayed = []
    age_appropriate_incorrect = []
    correct = []
    process_records = []

    for _, row in edited_df.iterrows():
        sound = row["Sound"]
        pos = row["Position"]
        produced = row["Produced"].strip()
        mastery_age = mastery_ages[sound]
        if produced == sound:
            results.append((sound, pos, "Age Appropriate"))
            correct.append(f"/{sound}/ ({pos})")
        else:
            process = detect_process(sound, produced) or detect_cluster_reduction(sound, produced)
            if process:
                status = phonological_processes.get(process)
                if status == 'atypical' or (isinstance(status, int) and age_in_months >= status):
                    process_records.append((process, sound, produced, 'Delayed'))
                else:
                    process_records.append((process, sound, produced, 'Age Appropriate'))

            if age_in_months >= mastery_age:
                results.append((sound, pos, "Delayed"))
                delayed.append((sound, pos, mastery_age))
            else:
                results.append((sound, pos, "Incorrect but Age Appropriate"))
                age_appropriate_incorrect.append((sound, pos, mastery_age))

    color_map = {
        "Age Appropriate": "#d4edda",
        "Incorrect but Age Appropriate": "#ffe082",
        "Delayed": "#f8d7da"
    }

    def highlight_result(val):
        return f"background-color: {color_map[val]}; color: black;"

    result_df = pd.DataFrame(results, columns=["Sound", "Position", "Result"])
    styled_table = result_df.style.applymap(lambda v: highlight_result(v) if v in color_map else "").to_html()
    st.markdown(styled_table, unsafe_allow_html=True)

    if process_records:
        st.subheader("Detected Phonological Processes")
        proc_df = pd.DataFrame(process_records, columns=["Process", "Target", "Produced", "Status"])
        styled_proc = proc_df.style.applymap(lambda v: highlight_result(v) if v in color_map else "").to_html()
        st.markdown(styled_proc, unsafe_allow_html=True)

    st.subheader("Summary Report")
    delayed_html = ''.join([f'<li>{s[0]} ({s[1]}) – expected mastery by {s[2]//12} years</li>' for s in delayed]) or "<li>None</li>"
    age_app_html = ''.join([f'<li>{s[0]} ({s[1]}) – expected mastery by {s[2]//12} years</li>' for s in age_appropriate_incorrect]) or "<li>None</li>"

    summary = f"""
    <div style='font-size:16px;'>
    The following report summarises the findings of <strong>{child_name}</strong>.<br><br>
    <strong>Delayed Sounds</strong><br>
    These sounds were produced incorrectly and are typically mastered by {child_name}'s age:<br>
    <ul>{delayed_html}</ul><br>
    <strong>Incorrect but Age Appropriate Sounds</strong><br>
    These sounds were produced incorrectly, but are not typically expected to be mastered until an older age:<br>
    <ul>{age_app_html}</ul>
    </div>
    """
    st.markdown(summary, unsafe_allow_html=True)

    csv = result_df.to_csv(index=False).encode('utf-8')
    
    st.subheader("Phonological Process Summary")
    if process_records:
        typical_list = []
        atypical_list = []

        for proc, target, produced, status in process_records:
            if phonological_processes.get(proc) == 'atypical':
                atypical_list.append(f"{proc} (e.g., /{target}/ → /{produced}/)")
            else:
                typical_list.append(f"{proc} (e.g., /{target}/ → /{produced}/) – expected resolution by {phonological_processes[proc] // 12 if isinstance(phonological_processes[proc], int) else 'unknown'} years")

        summary_text = "<div style='font-size:16px;'>"
        if atypical_list:
            summary_text += "<strong>Atypical Processes</strong><br>These phonological patterns are not typical at any age and may indicate a more significant speech delay:<ul>"
            summary_text += ''.join(f"<li>{desc}</li>" for desc in set(atypical_list))
            summary_text += "</ul><br>"
        if typical_list:
            summary_text += "<strong>Typical but Delayed Processes</strong><br>These patterns are part of normal development but should have resolved by now:<ul>"
            summary_text += ''.join(f"<li>{desc}</li>" for desc in set(typical_list))
            summary_text += "</ul><br>"
        summary_text += "</div>"

        st.markdown(summary_text, unsafe_allow_html=True)


st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name=f"{child_name}_articulation_results.csv",
        mime='text/csv'
    )
