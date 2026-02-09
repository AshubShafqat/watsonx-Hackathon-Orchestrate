import os
import arxiv
from fastapi import FastAPI
from pydantic import BaseModel
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

API_KEY = "#"
PROJECT_ID = "83813b90-bd70-4fbb-86b6-3de299cad5f8"
IBM_URL = "https://us-south.ml.cloud.ibm.com"

PUBLIC_URL = "https://5681986d3d74.ngrok-free.app"

def analyze_abstract_with_ibm(text):
    creds = Credentials(url=IBM_URL, api_key=API_KEY)
    
    model = ModelInference(
        model_id="ibm/granite-3-8b-instruct",
        params={
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 400,
            GenParams.MIN_NEW_TOKENS: 10
        },
        credentials=creds,
        project_id=PROJECT_ID
    )
    
    prompt = f"""[INST] You are an expert AI Researcher. Analyze this abstract and extract 3 specific details.

    Abstract: {text}
    
    Format the output exactly like this:
    **Problem:** [What is the specific gap or issue?]
    **Method:** [What architecture or technique is proposed?]
    **Result:** [What is the main performance metric or finding?]
    [/INST]"""
    
    try:
        response = model.generate(prompt)
        return response['results'][0]['generated_text'].strip()
    except Exception as e:
        return "Could not analyze paper."

# --- 4. FASTAPI APP ---
app = FastAPI(
    title="Deep Research Agent",
    description="An AI agent that performs literature reviews.",
    version="1.0.0",
    servers=[{"url": PUBLIC_URL}] 
)

class PaperResult(BaseModel):
    title: str
    pdf_url: str
    analysis: str

@app.get("/research_topic", response_model=list[PaperResult])
def research_topic(topic: str):
   
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=3,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    results = []
    for r in client.results(search):
        analysis_text = analyze_abstract_with_ibm(r.summary)
        
        results.append({
            "title": r.title,
            "pdf_url": r.pdf_url,
            "analysis": analysis_text
        })
    
   
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
