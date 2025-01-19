import streamlit as st
import replicate
import os
import json

def analyze_with_llama(text):
    """Use LLAMA to analyze the medical text"""
    prompt = f"""Extract the medical information from this note. Return ONLY a JSON object with this structure:
{{
    "patient_demographics": {{
        "name": "",
        "age": "",
        "gender": "",
        "address": ""
    }},
    "vitals": {{
        "blood_pressure": "",
        "heart_rate": "",
        "temperature": "",
        "spo2": ""
    }},
    "chief_complaint": "",
    "physical_exam": "",
    "diagnosis": "",
    "plan": ""
}}

Medical Note:
{text}"""

    # LLAMA model config
    llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    
    try:
        # Run LLAMA analysis
        output = replicate.run(
            llm,
            input={
                "prompt": prompt,
                "temperature": 0.1,
                "max_length": 500,
                "top_p": 0.9
            }
        )
        
        # Combine the streaming output
        response = ""
        for item in output:
            response += item
            
        # Find JSON in response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Could not parse LLAMA output")
                st.code(json_str)  # Show the problematic JSON
                return None
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    st.title("Medical Notes Analysis")

    # API token handling
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter valid Replicate API token!')
            return
    
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    # Create two columns
    left_col, right_col = st.columns([1, 1])
    
    # Left column for note input
    with left_col:
        st.subheader("Medical Notes")
        notes = st.text_area("Enter medical notes", height=400)
        
        if st.button("Generate EMR", type="primary"):
            if notes:
                with st.spinner("Analyzing with LLAMA..."):
                    result = analyze_with_llama(notes)
                    if result:
                        st.session_state.emr_data = result
                        st.success("Analysis complete!")
            else:
                st.warning("Please enter notes first")
    
    # Right column for form display
    with right_col:
        st.subheader("EMR Form")
        if 'emr_data' in st.session_state:
            data = st.session_state.emr_data
            
            # Patient Demographics
            st.markdown("### Patient Information")
            demographics = data.get('patient_demographics', {})
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Name", value=demographics.get('name', ''))
                st.text_input("Age", value=demographics.get('age', ''))
            with col2:
                st.text_input("Gender", value=demographics.get('gender', ''))
                st.text_input("Address", value=demographics.get('address', ''))
            
            # Vital Signs
            st.markdown("### Vital Signs")
            vitals = data.get('vitals', {})
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Blood Pressure", value=vitals.get('blood_pressure', ''))
                st.text_input("Heart Rate", value=vitals.get('heart_rate', ''))
            with col2:
                st.text_input("Temperature", value=vitals.get('temperature', ''))
                st.text_input("SpO2", value=vitals.get('spo2', ''))
            
            # Other Information
            st.markdown("### Clinical Information")
            st.text_area("Chief Complaint", value=data.get('chief_complaint', ''))
            st.text_area("Physical Examination", value=data.get('physical_exam', ''))
            st.text_area("Diagnosis", value=data.get('diagnosis', ''))
            st.text_area("Plan", value=data.get('plan', ''))
            
            # Save Button
            if st.button("Save EMR"):
                st.success("EMR saved successfully!")
                # Here you would typically save to a database
                
        else:
            st.info("Enter notes and click 'Generate EMR' to see the form")

if __name__ == "__main__":
    main()