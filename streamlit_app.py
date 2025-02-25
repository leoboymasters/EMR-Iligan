import streamlit as st
import replicate
import os
import json

def analyze_with_llama(text):
    """Use LLAMA to analyze the medical text"""
    prompt = f"""Extract medical information from this note. Format each finding and plan item with a bullet point. Return the data in this exact format:
{{
    "patient_demographics": {{
        "name": "patient name here",
        "age": "age here",
        "gender": "gender here",
        "address": "address here"
    }},
    "vitals": {{
        "blood_pressure": "BP here",
        "heart_rate": "HR here",
        "temperature": "temp here",
        "spo2": "spo2 here"
    }},
    "chief_complaint": "main complaint here",
    "physical_exam": [
        "• HEENT: unremarkable",
        "• Skin: cold and clammy",
        "• Chest: clear to auscultation"
    ],
    "diagnosis": "diagnosis/impression here",
    "plan": [
        "• Medication 1 with dose and frequency",
        "• Medication 2 with dose and frequency",
        "• Test or procedure 1",
        "• Instructions 1"
    ]
}}

For the physical_exam and plan sections:
1. Start each line with a bullet point (•)
2. Include proper section labels in physical exam
3. Include complete medication instructions in plan
4. Keep the format exactly as shown

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
        
        # Combine streaming output
        response = ""
        for item in output:
            response += item
        
        # Extract JSON
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Error processing the note. Please try again.")
                return None
        return None
    except Exception as e:
        st.error("An error occurred. Please try again.")
        return None

def main():
    st.set_page_config(
        page_title="EMR System",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("EMR System")
    
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
        notes = st.text_area("Enter medical notes", height=400, placeholder="Enter patient notes here...")
        
        if st.button("Generate EMR", type="primary"):
            if notes:
                with st.spinner("Processing medical notes..."):
                    result = analyze_with_llama(notes)
                    if result:
                        st.session_state.emr_data = result
                        st.success("EMR generated successfully!")
            else:
                st.warning("Please enter medical notes first.")
    
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
                st.text_input("Name", value=demographics.get('name', ''), key="name")
                st.text_input("Age", value=demographics.get('age', ''), key="age")
            with col2:
                st.text_input("Gender", value=demographics.get('gender', ''), key="gender")
                st.text_input("Address", value=demographics.get('address', ''), key="address")
            
            # Vital Signs
            st.markdown("### Vital Signs")
            vitals = data.get('vitals', {})
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Blood Pressure", value=vitals.get('blood_pressure', ''), key="bp")
                st.text_input("Heart Rate", value=vitals.get('heart_rate', ''), key="hr")
            with col2:
                st.text_input("Temperature", value=vitals.get('temperature', ''), key="temp")
                st.text_input("SpO2", value=vitals.get('spo2', ''), key="spo2")
            
            # Clinical Information
            st.markdown("### Clinical Information")
            st.text_area("Chief Complaint", value=data.get('chief_complaint', ''), 
                        height=100, key="chief_complaint")
            
            # Physical Examination
            st.markdown("### Physical Examination")
            physical_exam_text = "\n".join(data.get('physical_exam', []))
            st.text_area("Physical Exam Findings", value=physical_exam_text, 
                        height=200, key="physical_exam")
            
            # Diagnosis
            st.markdown("### Assessment")
            st.text_area("Impression", value=data.get('diagnosis', ''), 
                        height=100, key="diagnosis")
            
            # Plan
            st.markdown("### Plan")
            plan_text = "\n".join(data.get('plan', []))
            st.text_area("Orders", value=plan_text, height=200, key="plan")
            
            # Save button in a container for better spacing
            with st.container():
                st.write("")  # Add some space
                if st.button("Save EMR", type="primary", key="save"):
                    st.success("EMR saved successfully!")
        else:
            st.info("Enter notes and click 'Generate EMR' to see the form")

if __name__ == "__main__":
    main()