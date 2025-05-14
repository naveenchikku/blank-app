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

# Title and description
st.title("🔮 Integration Fabric API Onboarding Cost Calculator")
st.markdown("### Forecast your onboarding costs with ease!")

# Input form
st.subheader("Input Parameters")
integration_pattern = st.selectbox("Integration Pattern", ["Synchronous", "Asynchronous", "Event-based"])
if integration_pattern != "Event-based":
    int_complexity = st.selectbox("Integration Complexity", ["Simple", "Medium", "Complex"])
    infra_model = st.selectbox("Infrastructure Model", ["Shared", "Dedicated"])
else:
    int_complexity = None
    infra_model = None
oper_complexity = st.selectbox("Operational Complexity", ["Simple", "Medium", "Complex"])   

if infra_model == "Dedicated":
    first_integration = st.checkbox("First Integration?")
else:
    first_integration = None
    
submitted = st.button("💰 Forecast Cost")

# Mock response and output
if submitted:
    params = {
        "integration_pattern": integration_pattern,
        "integration_complexity": int_complexity,
        "operational_complexity": oper_complexity,
        "infrastructure_model": infra_model,
        "first_integration": first_integration
    }

    try:
        # Call backend api
        response = requests.post(url="https://func-costmeter.azurewebsites.net/api/cost-meter-poc",params=params)
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()
            # result = {
            #     "infra_cost_per_month": 84.18,
            #     "infra_cost_per_year": 1010.12,
            #     "operational_cost": 5791.16,
            #     "total_cost": 6801.28,
            #     "azure_resource_costs": {
            #         "Function App ASP": 38.7,
            #         "API Management": 9.64,
            #         "Application Gateway": 1.01,
            #         "PostgreSQL Database": 7.92,
            #         "Blob storage ": 4.84,
            #         "Queue Storage": 0.34,
            #         "App insight": 6.96,
            #         "Redis cache": 6.54,
            #         "Linux Agent VM": 1.28
            #     },
            #     "tps_supported": 15,
            #     "storage_offered": "N/A",
            #     "operational_cost_breakdown": [
            #         {
            #             "Resource": "Dev -1",
            #             "Resource Type": "IN_140",
            #             "Effort in Days": 5
            #         },
            #         {
            #             "Resource": "SVT -1",
            #             "Resource Type": "IN_140",
            #             "Effort in Days": 4
            #         },
            #         {
            #             "Resource": "PO-1",
            #             "Resource Type": "IN_150",
            #             "Effort in Days": 1
            #         },
            #         {
            #             "Resource": "PM/SM-1",
            #             "Resource Type": "IN_150",
            #             "Effort in Days": 1
            #         },
            #         {
            #             "Resource": "PdM",
            #             "Resource Type": "US_170",
            #             "Effort in Days": 1
            #         },
            #         {
            #             "Resource": "DL",
            #             "Resource Type": "IN_160",
            #             "Effort in Days": 2
            #         },
            #         {
            #             "Resource": "UAT Support",
            #             "Resource Type": "IN_140",
            #             "Effort in Days": 3
            #         },
            #         {
            #             "Resource": "Architect",
            #             "Resource Type": "IN_150",
            #             "Effort in Days": 2
            #         },
            #         {
            #             "Resource": "Dev Manager",
            #             "Resource Type": "IN_150",
            #             "Effort in Days": 2
            #         },
            #         {
            #             "Resource": "SVT Manager",
            #             "Resource Type": "IN_150",
            #             "Effort in Days": 2
            #         }
            #     ]
            # }
            # Display metrics
            st.subheader("Cost Forecast")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="📊 Infra Cost per Month", value=f"${result['infra_cost_per_month']}")
            col2.metric(label="📊 Infra Cost per Year", value=f"${result['infra_cost_per_year']}")
            col3.metric(label="📊 Operational Cost", value=f"${result['operational_cost']}")
            col4.metric(label="📊 Total Cost", value=f"${result['total_cost']}")

            # Display Azure resource costs
            st.subheader("Azure Resource Costs")
            df = pd.DataFrame.from_dict(result["azure_resource_costs"], orient="index", columns=["Cost (USD)"])
            st.bar_chart(df)
            st.dataframe(df)

            # Display additional metrics
            st.subheader("Additional Information")
            col5, col6 = st.columns(2)
            col5.metric(label="📊 TPS Supported", value=f"{result['tps_supported']}")
            # col6.metric(label="📊 Storage Offered", value=f"{result['storage_offered']}")

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
