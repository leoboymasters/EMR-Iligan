import streamlit as st
import re

def extract_info(text):
    """Extract information from medical notes"""
    info = {
        'name': '',
        'age': '',
        'gender': '',
        'address': '',
        'chief_complaint': '',
        'vital_signs': {
            'bp': '',
            'hr': '',
            'temp': '',
            'spo2': ''
        },
        'history': '',
        'physical_exam': '',
        'impression': '',
        'plan': ''
    }
    
    # Extract basic info using simple pattern matching
    name_match = re.search(r'Patient is ([^,]+)', text)
    if name_match:
        info['name'] = name_match.group(1).strip()
    
    age_match = re.search(r'(\d+)\s*year[s]?\s*old', text)
    if age_match:
        info['age'] = age_match.group(1)
    
    gender_match = re.search(r'(male|female)', text, re.IGNORECASE)
    if gender_match:
        info['gender'] = gender_match.group(1)
    
    address_match = re.search(r'from ([^,]+(?:,[^,]+)*)', text)
    if address_match:
        info['address'] = address_match.group(1).strip()
    
    # Extract chief complaint
    cc_match = re.search(r'chief[^\n]*of ([^\n]+)', text, re.IGNORECASE)
    if cc_match:
        info['chief_complaint'] = cc_match.group(1).strip()
    
    # Extract vital signs
    bp_match = re.search(r'BP (\d+/\d+)', text)
    if bp_match:
        info['vital_signs']['bp'] = bp_match.group(1)
    
    hr_match = re.search(r'HR (\d+)', text)
    if hr_match:
        info['vital_signs']['hr'] = hr_match.group(1)
    
    temp_match = re.search(r'Temp (\d+\.?\d*)', text)
    if temp_match:
        info['vital_signs']['temp'] = temp_match.group(1)
    
    spo2_match = re.search(r'SPO2 (\d+)', text)
    if spo2_match:
        info['vital_signs']['spo2'] = spo2_match.group(1)

    # Extract impression
    impression_match = re.search(r'Impression[,:]?\s*([^\n]+)', text)
    if impression_match:
        info['impression'] = impression_match.group(1).strip()

    # Extract plan
    plan_match = re.search(r'Plan:([^I]+)', text)
    if plan_match:
        info['plan'] = plan_match.group(1).strip()
        
    return info

def main():
    st.set_page_config(layout="wide", page_title="EMR System")
    
    st.title("EMR System")
    
    # Create two columns
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("Medical Notes")
        notes = st.text_area("Enter medical notes", height=400)
        
        if st.button("Generate EMR", type="primary"):
            if notes:
                # Extract information from notes
                info = extract_info(notes)
                # Store in session state
                st.session_state.info = info
                st.success("EMR generated! Please verify the information on the right.")
            else:
                st.warning("Please enter medical notes first.")
    
    with right_col:
        st.subheader("EMR Form")
        if 'info' in st.session_state:
            info = st.session_state.info
            
            # Demographics
            st.markdown("### Patient Information")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", value=info['name'])
                age = st.text_input("Age", value=info['age'])
            with col2:
                gender = st.selectbox("Gender", 
                                    ["Male", "Female"], 
                                    index=0 if info['gender'].lower() == 'male' else 1)
                address = st.text_input("Address", value=info['address'])
            
            # Chief Complaint
            st.markdown("### Chief Complaint")
            chief_complaint = st.text_area("Chief Complaint", value=info['chief_complaint'])
            
            # Vital Signs
            st.markdown("### Vital Signs")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                bp = st.text_input("Blood Pressure", value=info['vital_signs']['bp'])
            with col2:
                hr = st.text_input("Heart Rate", value=info['vital_signs']['hr'])
            with col3:
                temp = st.text_input("Temperature", value=info['vital_signs']['temp'])
            with col4:
                spo2 = st.text_input("SpO2", value=info['vital_signs']['spo2'])
            
            # Impression
            st.markdown("### Assessment")
            impression = st.text_area("Impression", value=info['impression'])
            
            # Plan
            st.markdown("### Plan")
            plan = st.text_area("Plan", value=info['plan'])
            
            # Save button
            if st.button("Save EMR"):
                st.success("EMR saved successfully!")
                # Here you would typically save to a database
        
        else:
            st.info("Enter notes and click 'Generate EMR' to see the form.")

if __name__ == "__main__":
    main()