import google.generativeai as genai
import os

def generate_prd(transcript):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert Product Manager. Based on the following interview transcript, generate a comprehensive Product Requirements Document (PRD) in Markdown format.
    
    Transcript:
    {transcript}
    
    The PRD should include:
    1. **Problem Statement**: What is the core problem?
    2. **Jobs to be Done (JTBD)**: The main job and related functional/emotional/social jobs.
    3. **Target Audience**: Who is this for?
    4. **Key Features & Requirements**: What must the solution do?
    5. **Success Metrics**: How will we measure success?
    6. **Risks & Mitigation**: What could go wrong?
    
    Output strictly Markdown.
    """
    
    response = model.generate_content(prompt)
    return response.text
