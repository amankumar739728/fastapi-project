from fastapi import FastAPI, Form, Request, UploadFile, File,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import json
import base64
from typing import Union, List

app = FastAPI()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")


#for '/' handler it will redirect to '/create_resume_form/' endpoint
@app.get("/", include_in_schema=False)  # Set include_in_schema=False to hide it in docs
async def redirect_to_form():
    response = RedirectResponse(url='/create_resume_form/')
    return response

# Create a route for the resume creation form
@app.post("/create_resume/")
async def create_resume(request: Request,
                        professional_summary: str = Form(...),
                        technical_skills: str = Form(...),
                        work_history: str = Form(...),  # Required field
                        education: str = Form(...),
                        full_name: str = Form(...),
                        company_logo: UploadFile = File(...),
                        designation: str = Form(...)):

    # Deserialize the JSON data from the work_history field
    try:
        work_history_data = json.loads(work_history)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid work history JSON")

    # Set the value of 'client' to be the same as 'company' if it's missing
    for entry in work_history_data:
        if "client" not in entry:
            entry["client"] = entry["company"]

    # Inside the loop that processes work history
    for entry in work_history_data:
        entry["client"] = entry.get("client", entry["company"])
        entry["role"] = entry.get("role", "")
        entry["responsibilities"] = entry.get("responsibilities", [])

    # Process the professional_summary to create bullet points
    professional_summary_bullets = professional_summary.split('\n')
    technical_skills_bullets = technical_skills.split('\n')

    # Encode the company logo as base64
    company_logo_data = company_logo.file.read()
    company_logo_base64 = base64.b64encode(company_logo_data).decode("utf-8")

    context = {
        "professional_summary": professional_summary_bullets,
        "technical_skills": technical_skills_bullets,
        "work_history": work_history_data,
        "education": education,
        "full_name": full_name,
        "company_logo_base64": company_logo_base64,
        "designation": designation,
    }
    
    return templates.TemplateResponse("resume_template1.html", {"request": request, "context": context})

# Route to render the create resume form
@app.get("/create_resume_form/")
async def create_resume_form(request: Request):
    return templates.TemplateResponse("resume_form.html", {"request": request})
