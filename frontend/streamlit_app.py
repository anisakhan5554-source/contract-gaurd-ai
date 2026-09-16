import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="ContractGuard AI", layout="wide")
st.title("🛡️ ContractGuard AI")

if "token" not in st.session_state:
    st.session_state["token"] = None

if not st.session_state["token"]:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            r = requests.post(f"{API_BASE}/login", data={"username": email, "password": password})
            if r.status_code == 200:
                st.session_state["token"] = r.json()["access_token"]
                st.rerun()
            else:
                st.error("Login failed")
    with col2:
        if st.button("Sign Up"):
            r = requests.post(f"{API_BASE}/signup", params={"email": email, "password": password})
            if r.status_code == 200:
                st.success("Account created. Now login.")
            else:
                st.error(r.text)
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

tab1, tab2, tab3,tab4 = st.tabs(["Upload & Analyze", "Contract Review","Version Compare", "Audit Log"])

with tab1:
    uploaded_file = st.file_uploader("Upload contract", type=["txt", "pdf"])
    if uploaded_file and st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        r = requests.post(f"{API_BASE}/contracts/upload", files=files, headers=headers)
        if r.status_code == 200:
            data = r.json()
            st.success(f"Uploaded. Contract ID: {data['contract_id']} (v{data.get('version')})")
            st.session_state["last_contract_id"] = data["contract_id"]
        else:
            st.error(r.text)

    if "last_contract_id" in st.session_state:
        cid = st.session_state["last_contract_id"]
        if st.button("Run Analysis"):
            with st.spinner("Analyzing..."):
                r = requests.post(f"{API_BASE}/contracts/{cid}/analyze", headers=headers)
            if r.status_code == 200:
                st.success("Analysis complete")
            else:
                st.error(r.text)

with tab2:
    st.header("Contract Risk Review")

    contracts_resp = requests.get(f"{API_BASE}/contracts", headers=headers)
    contract_options = {}
    if contracts_resp.status_code == 200:
        for c in contracts_resp.json():
            contract_options[f"{c['filename']} - {c['id'][:8]}"] = c['id']

    if contract_options:
        selected_label = st.selectbox("Select your contract", list(contract_options.keys()))
        cid = contract_options[selected_label]
    else:
        cid = st.text_input("Contract ID (no contracts found, paste manually)", value=st.session_state.get("last_contract_id", ""))

    if cid:
        r = requests.get(f"{API_BASE}/contracts/{cid}/clauses", headers=headers)
        if r.status_code == 200:
            for c in r.json():
                risk = c.get("risk_score")
                if risk is None:
                    continue
                icon = "🔴" if risk >= 0.75 else "🟡" if risk >= 0.5 else "🟢"
                with st.expander(f"{icon} {c.get('clause_type')} — Risk {risk} ({'HIGH' if risk>=0.75 else 'MEDIUM' if risk>=0.5 else 'LOW'})"):
                    st.markdown(f"*Clause:*")
                    st.write(c["text"][:500])
                    st.markdown(f"*Why this risk level?*")
                    st.write(c.get('rationale', 'N/A'))
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Confidence", f"{c.get('confidence', 0)*100:.0f}%")
                    col2.metric("Risk Score", f"{risk}")
                    col3.metric("Human Review", "Required ⚠️" if c.get('reviewed_by_human') else "Not needed ✅")

                    if st.button(f"Show precedent evidence", key=f"ev_{c['clause_id']}"):
                        ev_r = requests.get(f"{API_BASE}/clauses/{c['clause_id']}/evidence", headers=headers)
                        if ev_r.status_code == 200:
                            st.markdown("*Grounded by comparing against these reference clauses:*")
                            for p in ev_r.json()["precedents"]:
                                st.write(f"📄 {p['source']} — Similarity: {p.get('hybrid_score', 0):.0%}")
                                st.caption(f'"{p["text"][:200]}..."')
                                st.divider()
        else:
            st.error(r.text)

with tab3:
    st.header("Version Comparison")
    v2_id = st.text_input("Version 2/3 Contract ID (must have a previous version)")

    if st.button("Compare Versions"):
        response = requests.post(f"{API_BASE}/contracts/{v2_id}/compare", headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.info(data["summary"])

            if data["regressions_detected"]:
                st.error(f"⚠️ {len(data['regressions'])} risk regression(s) detected!")
                for r in data["regressions"]:
                    st.write(f"{r['v1_risk_level']} → {r['v2_risk_level']}")
                    st.write(r["v2_text_preview"])
                    st.divider()

            if data["improvements"]:
                st.success(f"✅ {len(data['improvements'])} improvement(s)")

            with st.expander("Full comparison details"):
                st.json(data["full_comparison"])
        else:
            st.error(f"Compare failed: {response.text}")



with tab4:
    r = requests.get(f"{API_BASE}/audit-log", headers=headers)
    if r.status_code == 200:
        for log in r.json()[:50]:
            st.text(f"[{log['timestamp']}] {log['actor']} — {log['action']}")