"""
Economics View page for Streamlit MVP.

Handles economic modeling, budget impact analysis, and cost-effectiveness calculations.
"""

import streamlit as st
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import pandas as pd

from utils.session_state import (
    get_session_data, 
    set_session_data, 
    show_success_message,
    clear_success_message
)


def render() -> None:
    """Render the economics view page."""
    
    st.header("💰 Economics View")
    
    # Show success message if any
    if st.session_state.get("show_success_message"):
        st.success(st.session_state.get("success_message", ""))
        clear_success_message()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Economic Models", "💵 Budget Impact", "⚖️ Cost-Effectiveness", "📈 Analytics"])
    
    with tab1:
        render_economic_models()
    
    with tab2:
        render_budget_impact()
    
    with tab3:
        render_cost_effectiveness()
    
    with tab4:
        render_economics_analytics()


def render_economic_models() -> None:
    """Render economic models overview and management."""
    
    economics_data = get_session_data("economics_data", {})
    dossiers = get_session_data("dossiers", {})
    
    st.subheader("📊 Economic Models Overview")
    
    if not economics_data:
        st.info("💼 No economic models created yet. Use the sections below to build your first model!")
    else:
        # Display existing models summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget_models = sum(1 for e in economics_data.values() if e.get('budget_impact'))
            st.metric("Budget Impact Models", budget_models)
        
        with col2:
            ce_models = sum(1 for e in economics_data.values() if e.get('cost_effectiveness'))
            st.metric("Cost-Effectiveness Models", ce_models)
        
        with col3:
            total_models = len(economics_data)
            st.metric("Total Economic Models", total_models)
    
    # Quick model creation
    st.markdown("---")
    st.subheader("🚀 Quick Model Creation")
    
    # Select dossier for association
    if dossiers:
        dossier_options = ["Select Dossier"] + [f"{did}: {d.get('title', 'Untitled')}" for did, d in dossiers.items()]
        selected_dossier = st.selectbox("Associate with Dossier", dossier_options)
        
        if selected_dossier != "Select Dossier":
            dossier_id = selected_dossier.split(":")[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💵 Create Budget Impact Model", use_container_width=True):
                    create_economic_model(dossier_id, "budget_impact")
            
            with col2:
                if st.button("⚖️ Create Cost-Effectiveness Model", use_container_width=True):
                    create_economic_model(dossier_id, "cost_effectiveness")
    else:
        st.info("📋 Create a dossier first to associate economic models.")


def render_budget_impact() -> None:
    """Render budget impact analysis interface."""
    
    st.subheader("💵 Budget Impact Analysis")
    
    economics_data = get_session_data("economics_data", {})
    dossiers = get_session_data("dossiers", {}) 
    
    # Model selection
    budget_models = {k: v for k, v in economics_data.items() if v.get('budget_impact')}
    
    if not budget_models:
        st.info("💼 No budget impact models exist. Create one from the Economic Models tab.")
        return
    
    # Model selector
    model_options = ["Select Model"] + [f"{mid}: {get_model_title(mid, m, dossiers)}" for mid, m in budget_models.items()]
    selected_model = st.selectbox("Select Budget Impact Model", model_options)
    
    if selected_model == "Select Model":
        st.info("👆 Select a model to view and edit budget impact parameters.")
        return
    
    model_id = selected_model.split(":")[0]
    model_data = budget_models[model_id]
    
    # Budget impact form
    with st.form("budget_impact_form"):
        st.markdown("### 💰 Budget Impact Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Population & Market:**")
            target_population = st.number_input(
                "Target Population Size", 
                value=model_data.get('budget_impact', {}).get('target_population', 100000),
                min_value=0
            )
            market_share_year1 = st.slider(
                "Market Share Year 1 (%)", 
                0.0, 100.0, 
                model_data.get('budget_impact', {}).get('market_share_year1', 5.0)
            )
            market_share_year5 = st.slider(
                "Market Share Year 5 (%)", 
                0.0, 100.0,
                model_data.get('budget_impact', {}).get('market_share_year5', 15.0)
            )
        
        with col2:
            st.markdown("**Treatment Costs:**")
            drug_cost_annual = st.number_input(
                "Annual Drug Cost ($)", 
                value=model_data.get('budget_impact', {}).get('drug_cost_annual', 50000),
                min_value=0
            )
            admin_cost_annual = st.number_input(
                "Annual Administration Cost ($)", 
                value=model_data.get('budget_impact', {}).get('admin_cost_annual', 5000),
                min_value=0
            )
            monitoring_cost_annual = st.number_input(
                "Annual Monitoring Cost ($)", 
                value=model_data.get('budget_impact', {}).get('monitoring_cost_annual', 2000),
                min_value=0
            )
        
        # Comparator costs
        st.markdown("**Comparator Costs:**")
        col1, col2 = st.columns(2)
        
        with col1:
            comparator_drug_cost = st.number_input(
                "Comparator Annual Drug Cost ($)", 
                value=model_data.get('budget_impact', {}).get('comparator_drug_cost', 30000),
                min_value=0
            )
        
        with col2:
            comparator_total_cost = st.number_input(
                "Comparator Total Annual Cost ($)", 
                value=model_data.get('budget_impact', {}).get('comparator_total_cost', 35000),
                min_value=0
            )
        
        # Form submission
        if st.form_submit_button("💾 Update Budget Impact Model", use_container_width=True):
            update_budget_impact_model(model_id, {
                'target_population': target_population,
                'market_share_year1': market_share_year1,
                'market_share_year5': market_share_year5,
                'drug_cost_annual': drug_cost_annual,
                'admin_cost_annual': admin_cost_annual,
                'monitoring_cost_annual': monitoring_cost_annual,
                'comparator_drug_cost': comparator_drug_cost,
                'comparator_total_cost': comparator_total_cost
            })
    
    # Budget impact calculations and visualization
    st.markdown("---")
    render_budget_impact_results(model_data.get('budget_impact', {}))


def render_cost_effectiveness() -> None:
    """Render cost-effectiveness analysis interface."""
    
    st.subheader("⚖️ Cost-Effectiveness Analysis")
    
    economics_data = get_session_data("economics_data", {})
    dossiers = get_session_data("dossiers", {})
    
    # Model selection
    ce_models = {k: v for k, v in economics_data.items() if v.get('cost_effectiveness')}
    
    if not ce_models:
        st.info("💼 No cost-effectiveness models exist. Create one from the Economic Models tab.")
        return
    
    # Model selector
    model_options = ["Select Model"] + [f"{mid}: {get_model_title(mid, m, dossiers)}" for mid, m in ce_models.items()]
    selected_model = st.selectbox("Select Cost-Effectiveness Model", model_options)
    
    if selected_model == "Select Model":
        st.info("👆 Select a model to view and edit cost-effectiveness parameters.")
        return
    
    model_id = selected_model.split(":")[0]
    model_data = ce_models[model_id]
    
    # Cost-effectiveness form
    with st.form("cost_effectiveness_form"):
        st.markdown("### 📊 Cost-Effectiveness Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Clinical Outcomes:**")
            life_years_gained = st.number_input(
                "Life Years Gained", 
                value=model_data.get('cost_effectiveness', {}).get('life_years_gained', 2.5),
                min_value=0.0, 
                step=0.1
            )
            quality_adjusted_ly = st.number_input(
                "Quality Adjusted Life Years (QALYs)", 
                value=model_data.get('cost_effectiveness', {}).get('quality_adjusted_ly', 2.0),
                min_value=0.0, 
                step=0.1
            )
            response_rate = st.slider(
                "Response Rate (%)", 
                0.0, 100.0,
                model_data.get('cost_effectiveness', {}).get('response_rate', 65.0)
            )
        
        with col2:
            st.markdown("**Economic Parameters:**")
            total_treatment_cost = st.number_input(
                "Total Treatment Cost ($)", 
                value=model_data.get('cost_effectiveness', {}).get('total_treatment_cost', 150000),
                min_value=0
            )
            comparator_total_cost = st.number_input(
                "Comparator Total Cost ($)", 
                value=model_data.get('cost_effectiveness', {}).get('comparator_total_cost', 100000),
                min_value=0
            )
            willingness_to_pay = st.number_input(
                "Willingness to Pay Threshold ($/QALY)", 
                value=model_data.get('cost_effectiveness', {}).get('willingness_to_pay', 100000),
                min_value=0
            )
        
        # Sensitivity parameters
        st.markdown("**Sensitivity Analysis:**")
        col1, col2 = st.columns(2)
        
        with col1:
            discount_rate = st.slider(
                "Discount Rate (%)", 
                0.0, 10.0,
                model_data.get('cost_effectiveness', {}).get('discount_rate', 3.5)
            )
        
        with col2:
            time_horizon = st.number_input(
                "Time Horizon (years)", 
                value=model_data.get('cost_effectiveness', {}).get('time_horizon', 10),
                min_value=1,
                max_value=50
            )
        
        # Form submission
        if st.form_submit_button("💾 Update Cost-Effectiveness Model", use_container_width=True):
            update_cost_effectiveness_model(model_id, {
                'life_years_gained': life_years_gained,
                'quality_adjusted_ly': quality_adjusted_ly,
                'response_rate': response_rate,
                'total_treatment_cost': total_treatment_cost,
                'comparator_total_cost': comparator_total_cost,
                'willingness_to_pay': willingness_to_pay,
                'discount_rate': discount_rate,
                'time_horizon': time_horizon
            })
    
    # Cost-effectiveness calculations and visualization
    st.markdown("---")
    render_cost_effectiveness_results(model_data.get('cost_effectiveness', {}))


def render_economics_analytics() -> None:
    """Render economics analytics and insights."""
    
    economics_data = get_session_data("economics_data", {})
    
    if not economics_data:
        st.info("📊 No economic data to analyze yet. Create some economic models first!")
        return
    
    st.subheader("📈 Economics Analytics")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Models", len(economics_data))
    
    with col2:
        budget_models = sum(1 for e in economics_data.values() if e.get('budget_impact'))
        st.metric("Budget Impact Models", budget_models)
    
    with col3:
        ce_models = sum(1 for e in economics_data.values() if e.get('cost_effectiveness'))
        st.metric("Cost-Effectiveness Models", ce_models)
    
    with col4:
        # Calculate average ICER across models
        icers = []
        for model in economics_data.values():
            ce_data = model.get('cost_effectiveness', {})
            if ce_data and ce_data.get('icer'):
                icers.append(ce_data['icer'])
        
        avg_icer = sum(icers) / len(icers) if icers else 0
        st.metric("Avg ICER ($/QALY)", f"${avg_icer:,.0f}")
    
    # Economic model performance
    st.subheader("💰 Model Performance Summary")
    
    # Create summary table
    model_summary = []
    dossiers = get_session_data("dossiers", {})
    
    for model_id, model in economics_data.items():
        dossier_id = model.get('associated_dossier')
        dossier_title = dossiers.get(dossier_id, {}).get('title', 'Unknown') if dossier_id else 'Not Associated'
        
        # Budget impact summary
        bi_data = model.get('budget_impact', {})
        budget_impact_y1 = bi_data.get('budget_impact_year1', 0)
        
        # Cost-effectiveness summary
        ce_data = model.get('cost_effectiveness', {})
        icer = ce_data.get('icer', 0)
        cost_effective = icer <= ce_data.get('willingness_to_pay', 100000) if icer > 0 else False
        
        model_summary.append({
            'Model ID': model_id[:8],
            'Associated Dossier': dossier_title,
            'Budget Impact Y1 ($M)': f"${budget_impact_y1/1000000:.1f}M" if budget_impact_y1 else "N/A",
            'ICER ($/QALY)': f"${icer:,.0f}" if icer else "N/A",
            'Cost-Effective': "✅" if cost_effective else "❌" if icer > 0 else "N/A"
        })
    
    if model_summary:
        df = pd.DataFrame(model_summary)
        st.dataframe(df, use_container_width=True)
    
    # Charts
    if len(economics_data) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            # ICER distribution
            icers = []
            labels = []
            for model_id, model in economics_data.items():
                ce_data = model.get('cost_effectiveness', {})
                if ce_data and ce_data.get('icer'):
                    icers.append(ce_data['icer'])
                    labels.append(model_id[:8])
            
            if icers:
                st.subheader("ICER Comparison")
                icer_df = pd.DataFrame({'Model': labels, 'ICER': icers})
                st.bar_chart(icer_df.set_index('Model'))
        
        with col2:
            # Budget impact comparison
            budget_impacts = []
            labels = []
            for model_id, model in economics_data.items():
                bi_data = model.get('budget_impact', {})
                if bi_data and bi_data.get('budget_impact_year1'):
                    budget_impacts.append(bi_data['budget_impact_year1'] / 1000000)  # Convert to millions
                    labels.append(model_id[:8])
            
            if budget_impacts:
                st.subheader("Budget Impact Y1 ($M)")
                bi_df = pd.DataFrame({'Model': labels, 'Budget Impact': budget_impacts})
                st.bar_chart(bi_df.set_index('Model'))


def render_budget_impact_results(budget_data: Dict[str, Any]) -> None:
    """Render budget impact calculation results.
    
    Args:
        budget_data: Budget impact model data
    """
    
    if not budget_data:
        return
    
    st.subheader("📊 Budget Impact Results")
    
    # Calculate key metrics
    target_pop = budget_data.get('target_population', 0)
    ms_y1 = budget_data.get('market_share_year1', 0) / 100
    ms_y5 = budget_data.get('market_share_year5', 0) / 100
    
    drug_cost = budget_data.get('drug_cost_annual', 0)
    admin_cost = budget_data.get('admin_cost_annual', 0)
    monitoring_cost = budget_data.get('monitoring_cost_annual', 0)
    total_treatment_cost = drug_cost + admin_cost + monitoring_cost
    
    comparator_cost = budget_data.get('comparator_total_cost', 0)
    
    # Calculate patient numbers and costs over 5 years
    years = list(range(1, 6))
    patients_treated = []
    budget_impacts = []
    
    for year in years:
        # Linear interpolation of market share
        if year == 1:
            market_share = ms_y1
        else:
            market_share = ms_y1 + (ms_y5 - ms_y1) * (year - 1) / 4
        
        patients = int(target_pop * market_share)
        patients_treated.append(patients)
        
        # Budget impact = (New treatment cost - Comparator cost) * Patients
        impact = (total_treatment_cost - comparator_cost) * patients
        budget_impacts.append(impact)
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Year 1 Patients", f"{patients_treated[0]:,}")
        st.metric("Year 5 Patients", f"{patients_treated[4]:,}")
    
    with col2:
        st.metric("Year 1 Budget Impact", f"${budget_impacts[0]:,.0f}")
        st.metric("5-Year Cumulative", f"${sum(budget_impacts):,.0f}")
    
    with col3:
        annual_savings = comparator_cost - total_treatment_cost if comparator_cost > total_treatment_cost else 0
        st.metric("Cost per Patient vs Comparator", f"${total_treatment_cost - comparator_cost:,.0f}")
        st.metric("Net Budget Impact Y1", f"${budget_impacts[0]:,.0f}")
    
    # Chart
    st.subheader("📈 Budget Impact Over Time")
    
    chart_data = pd.DataFrame({
        'Year': years,
        'Patients Treated': patients_treated,
        'Budget Impact ($M)': [bi/1000000 for bi in budget_impacts]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.line_chart(chart_data.set_index('Year')['Patients Treated'])
    
    with col2:
        st.line_chart(chart_data.set_index('Year')['Budget Impact ($M)'])
    
    # Update model with calculated results
    budget_data.update({
        'patients_year1': patients_treated[0],
        'patients_year5': patients_treated[4],
        'budget_impact_year1': budget_impacts[0],
        'budget_impact_cumulative': sum(budget_impacts)
    })


def render_cost_effectiveness_results(ce_data: Dict[str, Any]) -> None:
    """Render cost-effectiveness calculation results.
    
    Args:
        ce_data: Cost-effectiveness model data
    """
    
    if not ce_data:
        return
    
    st.subheader("⚖️ Cost-Effectiveness Results")
    
    # Calculate ICER and other metrics
    total_cost = ce_data.get('total_treatment_cost', 0)
    comparator_cost = ce_data.get('comparator_total_cost', 0)
    qalys = ce_data.get('quality_adjusted_ly', 0)
    wtp_threshold = ce_data.get('willingness_to_pay', 100000)
    
    incremental_cost = total_cost - comparator_cost
    incremental_qalys = qalys  # Assuming comparator has 0 additional QALYs for simplicity
    
    icer = incremental_cost / incremental_qalys if incremental_qalys > 0 else float('inf')
    cost_effective = icer <= wtp_threshold
    
    # Display key results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Incremental Cost", f"${incremental_cost:,.0f}")
    
    with col2:
        st.metric("Incremental QALYs", f"{incremental_qalys:.2f}")
    
    with col3:
        st.metric("ICER ($/QALY)", f"${icer:,.0f}" if icer != float('inf') else "Dominated")
    
    with col4:
        st.metric("Cost-Effective", "✅ Yes" if cost_effective else "❌ No")
    
    # Cost-effectiveness plane visualization
    st.subheader("📊 Cost-Effectiveness Analysis")
    
    # Simple visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Economic Evaluation:**")
        
        if cost_effective:
            st.success(f"✅ Cost-effective at ${wtp_threshold:,}/QALY threshold")
        else:
            st.error(f"❌ Not cost-effective at ${wtp_threshold:,}/QALY threshold")
        
        st.write(f"• **ICER:** ${icer:,.0f} per QALY gained")
        st.write(f"• **Net Monetary Benefit:** ${(incremental_qalys * wtp_threshold) - incremental_cost:,.0f}")
        
        # Probability of cost-effectiveness (simplified)
        prob_ce = min(100, max(0, 100 - (icer - wtp_threshold) / wtp_threshold * 50)) if icer != float('inf') else 0
        st.write(f"• **Probability Cost-Effective:** {prob_ce:.1f}%")
    
    with col2:
        st.markdown("**Sensitivity Factors:**")
        
        # Simple sensitivity analysis display
        discount_rate = ce_data.get('discount_rate', 3.5)
        time_horizon = ce_data.get('time_horizon', 10)
        response_rate = ce_data.get('response_rate', 65)
        
        st.write(f"• **Discount Rate:** {discount_rate}%")
        st.write(f"• **Time Horizon:** {time_horizon} years")
        st.write(f"• **Response Rate:** {response_rate}%")
        
        # Impact of key parameters
        st.markdown("**Parameter Impact:**")
        if discount_rate > 5:
            st.write("⚠️ High discount rate may reduce cost-effectiveness")
        if time_horizon < 5:
            st.write("⚠️ Short time horizon may underestimate benefits")
        if response_rate < 50:
            st.write("⚠️ Low response rate may impact cost-effectiveness")
    
    # Update model with calculated results
    ce_data.update({
        'incremental_cost': incremental_cost,
        'incremental_qalys': incremental_qalys,
        'icer': icer,
        'cost_effective': cost_effective,
        'net_monetary_benefit': (incremental_qalys * wtp_threshold) - incremental_cost
    })


def create_economic_model(dossier_id: str, model_type: str) -> None:
    """Create a new economic model.
    
    Args:
        dossier_id: Associated dossier ID
        model_type: Type of model ('budget_impact' or 'cost_effectiveness')
    """
    
    model_id = str(uuid.uuid4())
    
    model_data = {
        'created_date': datetime.now().isoformat(),
        'last_modified': datetime.now().isoformat(),
        'associated_dossier': dossier_id,
        'model_type': model_type
    }
    
    if model_type == 'budget_impact':
        model_data['budget_impact'] = {
            'target_population': 100000,
            'market_share_year1': 5.0,
            'market_share_year5': 15.0,
            'drug_cost_annual': 50000,
            'admin_cost_annual': 5000,
            'monitoring_cost_annual': 2000,
            'comparator_drug_cost': 30000,
            'comparator_total_cost': 35000
        }
    elif model_type == 'cost_effectiveness':
        model_data['cost_effectiveness'] = {
            'life_years_gained': 2.5,
            'quality_adjusted_ly': 2.0,
            'response_rate': 65.0,
            'total_treatment_cost': 150000,
            'comparator_total_cost': 100000,
            'willingness_to_pay': 100000,
            'discount_rate': 3.5,
            'time_horizon': 10
        }
    
    # Save to session state
    economics_data = get_session_data("economics_data", {})
    economics_data[model_id] = model_data
    set_session_data("economics_data", economics_data)
    
    show_success_message(f"✅ {model_type.replace('_', ' ').title()} model created successfully!")
    st.rerun()


def update_budget_impact_model(model_id: str, budget_data: Dict[str, Any]) -> None:
    """Update a budget impact model.
    
    Args:
        model_id: Model ID to update
        budget_data: Updated budget impact data
    """
    
    economics_data = get_session_data("economics_data", {})
    
    if model_id in economics_data:
        economics_data[model_id]['budget_impact'].update(budget_data)
        economics_data[model_id]['last_modified'] = datetime.now().isoformat()
        set_session_data("economics_data", economics_data)
        
        show_success_message("✅ Budget impact model updated successfully!")
    else:
        st.error("❌ Model not found.")


def update_cost_effectiveness_model(model_id: str, ce_data: Dict[str, Any]) -> None:
    """Update a cost-effectiveness model.
    
    Args:
        model_id: Model ID to update
        ce_data: Updated cost-effectiveness data
    """
    
    economics_data = get_session_data("economics_data", {})
    
    if model_id in economics_data:
        economics_data[model_id]['cost_effectiveness'].update(ce_data)
        economics_data[model_id]['last_modified'] = datetime.now().isoformat()
        set_session_data("economics_data", economics_data)
        
        show_success_message("✅ Cost-effectiveness model updated successfully!")
    else:
        st.error("❌ Model not found.")


def get_model_title(model_id: str, model_data: Dict[str, Any], dossiers: Dict[str, Any]) -> str:
    """Get a readable title for a model.
    
    Args:
        model_id: Model ID
        model_data: Model data
        dossiers: Available dossiers
        
    Returns:
        Model title string
    """
    
    dossier_id = model_data.get('associated_dossier')
    dossier_title = dossiers.get(dossier_id, {}).get('title', 'Unknown Dossier') if dossier_id else 'Unassociated'
    
    model_type = model_data.get('model_type', 'unknown').replace('_', ' ').title()
    
    return f"{dossier_title} - {model_type}"
