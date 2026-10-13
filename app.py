
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8001/research"

st.set_page_config(
    page_title="ResearchAI",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 ResearchAI")
st.subheader("Autonomous Multi-Agent Research & Decision System")
st.write(
    "Research any topic. Get AI-generated findings, "
    "evidence-based analysis, and actionable recommendations."
)

with st.sidebar:
    st.header("⚙️ Research Settings")
    audience = st.selectbox(
        "Target audience",
        [
            "General audience",
            "College students",
            "Researchers",
            "Business professionals",
            "Technical experts",
        ],
    )
    detail_level = st.selectbox(
        "Report detail",
        ["short", "medium", "detailed"],
        index=1,
    )

    st.divider()
    st.caption("Powered by FastAPI, Gemini and web research.")

with st.form("research_form"):
    topic = st.text_area(
        "What do you want to research?",
        placeholder="Example: AI applications in healthcare",
        height=100,
    )

    submitted = st.form_submit_button(
        "🚀 Start Research",
        use_container_width=True,
    )

if submitted:
    if len(topic.strip()) < 3:
        st.warning("Please enter a research topic with at least 3 characters.")
    else:
        payload = {
            "topic": topic.strip(),
            "audience": audience,
            "detail_level": detail_level,
        }

        try:
            with st.spinner(
                "Researching, analyzing, and preparing recommendations..."
            ):
                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=240,
                )

            if response.ok:
                data = response.json()

                st.success("Research workflow completed successfully!")

                st.subheader("📊 Research Overview")
                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Sources collected",
                    len(data.get("sources", [])),
                )
                c2.metric(
                    "Processing time",
                    f"{data.get('elapsed_seconds', 0)} sec",
                )
                c3.metric(
                    "AI model",
                    data.get("model", "Configured model"),
                )

                report_tab, analysis_tab, decision_tab, sources_tab = (
                    st.tabs(
                        [
                            "📄 Research Report",
                            "🧠 Analysis",
                            "🎯 Decision",
                            "🔗 Sources",
                        ]
                    )
                )

                with report_tab:
                    st.markdown(data.get("report") or "No report returned.")

                with analysis_tab:
                    st.markdown(
                        data.get("analysis") or "No analysis returned."
                    )

                with decision_tab:
                    st.markdown(
                        data.get("decision") or "No decision returned."
                    )

                with sources_tab:
                    sources = data.get("sources", [])

                    if not sources:
                        st.info("No web sources were returned.")
                    else:
                        for i, source in enumerate(sources, start=1):
                            st.markdown(
                                f"**{i}. [{source.get('title', 'Source')}]"
                                f"({source.get('url', '')})**"
                            )
                            st.write(source.get("snippet", ""))
                            st.divider()

            else:
                st.error(f"API error: HTTP {response.status_code}")
                st.code(response.text[:2000])

        except requests.ConnectionError:
            st.error(
                "Cannot connect to the backend. "
                "Start the FastAPI server on port 8001 first."
            )
        except requests.Timeout:
            st.error(
                "The request took too long. Check the backend terminal "
                "to see whether the agents are still running."
            )
        except requests.RequestException as error:
            st.error(f"Request failed: {error}")

st.divider()
st.caption("ResearchAI | Multi-Agent AI Research and Decision Support")
