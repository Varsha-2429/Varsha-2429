import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import re

# --- Snowflake Connection Info ---
ACCOUNT = "VZIXLPJ-GUB99003"  # your Snowflake account
HOST = f"{ACCOUNT}.snowflakecomputing.com"
DATABASE = "SNOWFLAKE_LEARNING_DB"
SCHEMA = "PUBLIC"
WAREHOUSE = "COMPUTE_WH"
ROLE = "ACCOUNTADMIN"

# --- Semantic Model Path (YAML in your stage) ---
SEMANTIC_MODEL = '@"SNOWFLAKE_LEARNING_DB"."PUBLIC"."MY_STAGE"/atliq.yaml'

# --- Streamlit Page Config ---
st.set_page_config(page_title="Cortex Analyst - AtliQ Dashboard", layout="wide")

# --- Login ---
st.title("🏢 Cortex Analyst - AtliQ Business Dashboard")
st.markdown("Query your Snowflake data using natural language powered by Cortex Analyst!")

user = st.text_input("👤 Username:")
password = st.text_input("🔑 Password:", type="password")

if st.button("Login"):
    try:
        conn = snowflake.connector.connect(
            user="SRIVARSHA2429",
            password="Shri@2429",
            account=ACCOUNT,
            warehouse=WAREHOUSE,
            database=DATABASE,
            schema=SCHEMA,
            role=ROLE
        )
        st.session_state.conn = conn
        st.success("✅ Logged in successfully!")
    except Exception as e:
        st.error(f"❌ Login failed: {e}")

# --- Query Box ---
if "conn" in st.session_state:
    query = st.text_input(
        "💬 Ask a question about your AtliQ data:",
        placeholder="e.g., Show total sales by region for 2024"
    )

    if st.button("Run Query") and query:
        try:
            # --- Step 1: Generate SQL using Cortex Analyst ---
            cortex_query = f"""
            SELECT SNOWFLAKE.CORTEX.ANALYST('{query}', '{SEMANTIC_MODEL}') AS SQL_QUERY;
            """
            cur = st.session_state.conn.cursor()
            cur.execute(cortex_query)
            sql_query = cur.fetchone()[0]

            if not sql_query:
                st.warning("⚠️ No SQL generated. Try rephrasing your question.")
            else:
                st.markdown("### 🧠 Generated SQL")
                st.code(sql_query, language="sql")

                # --- Step 2: Run generated SQL ---
                cur.execute(sql_query)
                df = cur.fetch_pandas_all()

                if df.empty:
                    st.warning("No data returned.")
                else:
                    st.markdown("### 📊 Query Results")
                    st.dataframe(df)

                    # --- Step 3: Auto Chart Visualization ---
                    if len(df.columns) >= 2:
                        st.markdown("### 📈 Visualization")
                        col1, col2 = st.columns(2)
                        x_axis = col1.selectbox("X-axis", df.columns, index=0)
                        y_axis = col2.selectbox("Y-axis", [c for c in df.columns if c != x_axis], index=0)

                        # Chart type detection
                        if re.search(r"(month|date|year)", x_axis, re.IGNORECASE):
                            chart_type = "Line"
                        else:
                            chart_type = "Bar"

                        if chart_type == "Line":
                            fig = px.line(df, x=x_axis, y=y_axis, title="Line Chart")
                        else:
                            fig = px.bar(df, x=x_axis, y=y_axis, title="Bar Chart")

                        st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
