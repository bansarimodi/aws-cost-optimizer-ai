import streamlit as st
from graph_state import build_graph

graph = build_graph()

# Streamlit UI Config
st.set_page_config(
    page_title="AWS Cost Optimization using Agentic AI (LangGraph)",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("☁️ AWS Cost Optimization using Agentic AI (LangGraph)")

# Manual AWS credential input
st.header("🔐 Enter AWS Credentials")
with st.expander("Enter AWS Details Securely"):
    aws_key = st.text_input("AWS Access Key ID", type="password")
    aws_secret = st.text_input("AWS Secret Access Key", type="password")
    aws_region = st.text_input("AWS Region", value="us-east-1")

# Session state
if "final_state" not in st.session_state:
    st.session_state.final_state = None
if "detected_resources" not in st.session_state:
    st.session_state.detected_resources = []

# Run detection
if st.button("🚀 Run Recommendation Engine"):
    if not aws_key or not aws_secret or not aws_region:
        st.error("❌ Please complete AWS credentials before proceeding.")
    else:
        initial_state = {
            "aws_access_key": aws_key,
            "aws_secret_key": aws_secret,
            "aws_region": aws_region,
            "user_request": "idle resource detection"
        }

        with st.spinner("🔍 Scanning AWS resources..."):
            final_state = graph.invoke(initial_state)
            st.session_state.final_state = final_state
            st.session_state.detected_resources = final_state.get("detected_resources", [])

        st.success("✅ Scan Completed Successfully!")

# Show results
if st.session_state.final_state:
    st.subheader("📋 AI Recommendation Report")
    st.markdown(f"```{st.session_state.final_state.get('report', 'No idle resources detected.')}```")

    if st.session_state.detected_resources:
        st.subheader("🧾 Select Resources to Delete")
        selected = st.multiselect(
            "Choose specific unused resources for deletion:",
            options=st.session_state.detected_resources
        )

        if st.button("🗑️ Confirm Deletion of Selected Resources"):
            if not selected:
                st.warning("⚠️ Please select at least one resource.")
            else:
                feedback_state = {
                    "aws_access_key": aws_key,
                    "aws_secret_key": aws_secret,
                    "aws_region": aws_region,
                    "user_feedback": "yes",
                    "detected_resources": selected,
                    "user_request": "idle resource detection"
                }

                with st.spinner("⏳ Deleting selected resources..."):
                    final_state = graph.invoke(feedback_state)
                    st.session_state.final_state = final_state

                st.success("✅ Resources Deleted Successfully!")
                st.subheader("Final Cost Optimization Summary")
                st.markdown(f"```{final_state.get('final_message', '')}```")
    else:
        st.info("✅ No unused resources detected. Your AWS setup is already optimized!")
