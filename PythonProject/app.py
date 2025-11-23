# app.py (final)
import streamlit as st
from regex_parser import to_postfix
from nfa_builder import thompson
from nfa_to_dfa import nfa_to_dfa
from dfa_simulator import simulate_dfa
from cfg_parser import CFG

st.set_page_config(page_title="Validator Bahasa Formal", layout="centered")

st.title('Sistem Validator Bahasa Formal\n(Regex → NFA → DFA  &  CFG Checker)')

# -----------------------
# Helpers: reset utilities
# -----------------------
def reset_regex_state():
    st.session_state.dfa_ready = False
    st.session_state.dfa_start = None
    st.session_state.dfa_trans = None
    st.session_state.dfa_accepts = None
    st.session_state.regex_text = ""

def reset_cfg_state():
    st.session_state.cfg = None
    st.session_state.grammar_text = ""
    st.session_state.cfg_loaded = False

# -----------------------
# Initialize session_state
# -----------------------
if 'dfa_ready' not in st.session_state:
    st.session_state.dfa_ready = False
if 'dfa_start' not in st.session_state:
    st.session_state.dfa_start = None
if 'dfa_trans' not in st.session_state:
    st.session_state.dfa_trans = None
if 'dfa_accepts' not in st.session_state:
    st.session_state.dfa_accepts = None
if 'regex_text' not in st.session_state:
    st.session_state.regex_text = ""

if 'cfg' not in st.session_state:
    st.session_state.cfg = None
if 'grammar_text' not in st.session_state:
    st.session_state.grammar_text = ""
if 'cfg_loaded' not in st.session_state:
    st.session_state.cfg_loaded = False

# -----------------------
# Mode selection
# -----------------------
mode = st.radio('Pilih Mode:', ['Regex → Test String', 'CFG Checker'])

# =======================
# MODE: Regex → Test
# =======================
if mode == 'Regex → Test String':
    st.header("Regex → NFA → DFA → Test String")

    col1, col2 = st.columns([3,1])
    with col1:
        regex = st.text_input('Masukkan regex (contoh: (a|b)*abb)', value=st.session_state.regex_text)
    with col2:
        if st.button('Reset Regex State'):
            reset_regex_state()
            st.experimental_rerun()

    # Build & convert button
    if st.button('Build & Convert') and regex:
        try:
            postfix = to_postfix(regex)
            frag = thompson(postfix)
            dfa_states, dfa_trans, dfa_start, dfa_accepts = nfa_to_dfa(frag)

            st.session_state.dfa_ready = True
            st.session_state.dfa_start = dfa_start
            st.session_state.dfa_trans = dfa_trans
            st.session_state.dfa_accepts = dfa_accepts
            st.session_state.regex_text = regex
            st.success("DFA berhasil dibuat dari regex.")
            st.write('Postfix:', postfix)
            st.write('Jumlah DFA states:', len(dfa_states))
            st.write('Accept states count:', len(dfa_accepts))

        except Exception as e:
            st.error(f"Gagal membangun DFA: {e}")

    # If DFA is ready, show test input
    if st.session_state.dfa_ready:
        st.markdown("---")
        st.subheader("Uji String pada DFA yang Dibangun")
        test = st.text_input('Masukkan string uji', key='test_string_input')

        test_col1, test_col2 = st.columns([3,1])
        with test_col2:
            if st.button('Reset Test String'):
                st.session_state['test_string_input'] = ""
                st.experimental_rerun()

        if st.button('Test String') and test is not None:
            try:
                ok = simulate_dfa(
                    st.session_state.dfa_start,
                    st.session_state.dfa_trans,
                    st.session_state.dfa_accepts,
                    test
                )
                if ok:
                    st.success('Accepted ✅')
                else:
                    st.error('Rejected ❌')
            except Exception as e:
                st.error(f"Kesalahan saat simulasi DFA: {e}")

    # Optional: show DFA transition table (compact)
    if st.checkbox('Tampilkan tabel transisi DFA (ringkas)') and st.session_state.dfa_ready:
        st.write("Format key: (frozenset_of_nfa_states, symbol) -> frozenset_of_nfa_states")
        st.write(st.session_state.dfa_trans)

# =======================
# MODE: CFG Checker
# =======================
else:
    st.header("CFG Checker (Top-Down Simple Parser)")

    colg1, colg2 = st.columns([3,1])
    with colg1:
        grammar_raw = st.text_area(
            'Masukkan grammar (format contoh: S->NP VP; NP->N|Det N; N->kucing|ikan; Det->si)',
            value=st.session_state.grammar_text,
            height=180
        )
    with colg2:
        if st.button('Reset Grammar'):
            reset_cfg_state()
            st.experimental_rerun()

    if st.button('Parse Grammar'):
        if not grammar_raw or '->' not in grammar_raw:
            st.error("Format grammar tidak valid. Contoh: S->NP VP; NP->N|Det N; N->kucing|ikan")
        else:
            try:
                rules = {}
                for part in grammar_raw.split(';'):
                    part = part.strip()
                    if not part:
                        continue
                    if '->' not in part:
                        continue
                    L, R = part.split('->', 1)
                    L = L.strip()
                    # setiap produksi alternatif dipisah dengan |
                    prods = [p.strip().split() for p in R.split('|')]
                    rules[L] = prods

                st.session_state.cfg = CFG(rules)
                st.session_state.grammar_text = grammar_raw
                st.session_state.cfg_loaded = True
                st.success("Grammar berhasil dimuat ke session.")
                st.write("Nonterminals:", list(rules.keys()))
            except Exception as e:
                st.error(f"Gagal mem-parsing grammar: {e}")

    if st.session_state.cfg_loaded and st.session_state.cfg is not None:
        st.markdown("---")
        tokens = st.text_input('Masukkan kalimat (pisah tiap token dengan spasi)', key='cfg_input').split()

        check_col1, check_col2 = st.columns([3,1])
        with check_col2:
            if st.button('Reset CFG Input'):
                st.session_state['cfg_input'] = ""
                st.experimental_rerun()

        if st.button('Check Grammar'):
            try:
                ok = st.session_state.cfg.parse(tokens)
                if ok:
                    st.success("Gramatikal ✅")
                else:
                    st.error("Tidak gramatikal ❌")
            except Exception as e:
                st.error(f"Kesalahan saat parsing: {e}")

    # show loaded grammar (optional)
    if st.checkbox('Tampilkan grammar yang dimuat') and st.session_state.cfg is not None:
        st.write(st.session_state.grammar_text)

# -----------------------
# Footer: info & template logbook path
# -----------------------
st.markdown('---')
