import streamlit as st
import pandas as pd
import requests
import logging
# Set page configuration
st.set_page_config(page_title="Azure Cost Forecast", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stMetric {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        border: 2px solid #4CAF50;
    }
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
        border: 2px solid #4CAF50;
    }
    .stTable {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
        border: 2px solid #4CAF50;
    }
    .stBarChart {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
        border: 2px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)
# Set constants
infra_model = None
first_integration = None
tps = None
infra_model = None
storage_offered = None
no_of_fields = None
mapping_required = False
mapping_complexity = None
events_per_second = None
payload_kb = None

# Title and description
st.title("🔮 Integration Fabric API Onboarding Cost Calculator")
st.markdown("### Forecast your onboarding costs with ease!")

# Input form
st.subheader("Input Parameters")
integration_pattern = st.selectbox("Integration Pattern", ["Synchronous", "Asynchronous", "Event-based"])

if integration_pattern == "Synchronous":
    tps = st.slider("Expected TPS", 1, 50, 2,2)
    # events_per_month = st.slider("Expected requests per month",0,200000000,50,1000)
    payload_kb = st.number_input("Payload size (KB)", 1, 10000, 50,100)
    infra_model = st.selectbox("Infrastructure Model", ["Shared", "Dedicated"])
elif integration_pattern == "Asynchronous":
    events_per_second = st.slider("EventHub Ingress (events/second)",0,2000,50,25)
    storage_offered = st.slider("Storage offered(GB)",0,1000,50,50)
    infra_model = st.selectbox("Infrastructure Model", ["Shared", "Dedicated"])
    payload_kb = st.number_input("Payload size (KB)", 1, 1000, 50, 100)
else:
    events_per_second = st.slider("Events/second)",0,100,10,10)
    payload_kb = st.number_input("Payload size (KB)", 1, 10000, 50, 100)
    storage_offered = st.slider("Storage offered(GB)",0,1000,50,50)
# # pass_through_integration = st.checkbox("Pass through Integration?")
# if not pass_through_integration:
mapping_required = st.checkbox("Data transformation required?")
if mapping_required:
    no_of_fields = st.slider("No of fields",0,1000,2,10)
    mapping_complexity = st.selectbox("Transformation complexity", ["Simple", "Medium", "Complex"])   

if infra_model == "Dedicated":
    first_integration = st.checkbox("First Integration?")
else:
    first_integration = None
    
submitted = st.button("💰 Forecast Cost")

# Mock response and output
if submitted:
    payload = {
        "integration_pattern": integration_pattern,
        "infrastructure_model": infra_model,
        "first_integration": first_integration,
        "tps" :tps,
        "infra_model" : infra_model,
        "storage_offered" : storage_offered,
        "no_of_fields":no_of_fields,
        "mapping_required": mapping_required,
        "mapping_complexity": mapping_complexity,
        "events_per_second": events_per_second,
        "payload_kb":payload_kb
    }
    print(payload)
    try:
        # Call backend api
        response = requests.post(url="https://func-costmeter.azurewebsites.net/api/cost-meter-poc",json=payload)
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()
            # Display metrics
            st.subheader("Cost Forecast")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="📊 Infra Cost per Month", value=f"${result['infra_cost_per_month']}")
            col2.metric(label="📊 Infra Cost per Year", value=f"${result['infra_cost_per_year']}")
            col3.metric(label="📊 Operational Cost", value=f"${result['operational_cost']}")
            col4.metric(label="📊 Total Cost", value=f"${result['total_cost']}")

            # Display Azure resource costs
            st.subheader("Azure Resource Costs")
            df = pd.DataFrame.from_dict(result["azure_resource_costs"], orient="index", columns=["Cost (USD) /month"])
            st.bar_chart(df)
            st.dataframe(df)


            # Display operational cost breakdown
            st.subheader("Operational Resources Breakdown")
            oper_cost_df = pd.DataFrame(result["operational_cost_breakdown"])
            st.table(oper_cost_df)

            # Export button
            st.download_button("📥 Export Azure Resource Costs as CSV", df.to_csv(), "azure_resource_costs.csv", "text/csv")
        else:
            logging.error(f" Error in calling backend service : {str(response.content)}")
            raise Exception("Internal server error")
    except Exception as e:
        logging.error(f" Error in calling backend service : {str(response.content)}")
        raise
