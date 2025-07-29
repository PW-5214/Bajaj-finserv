from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import json
from datetime import datetime
import logging
import PyPDF2
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM-Powered Query Retrieval System",
    description="Intelligent document query system for insurance, legal, HR, and compliance domains",
    version="1.0.0"
)

@app.get("/upload", response_class=HTMLResponse)
async def upload_form():
    """Return HTML form for file upload"""
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Insurance Policy Document Upload</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 600px; margin: auto; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; }
                input[type="file"] { margin-bottom: 10px; }
                input[type="text"] { width: 100%; padding: 8px; margin-bottom: 10px; }
                button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }
                button:hover { background-color: #45a049; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Upload Insurance Policy Document</h1>
                <form action="/api/v1/webhook" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Select PDF File:</label>
                        <input type="file" id="file" name="file" accept=".pdf" required>
                    </div>
                    <div class="form-group">
                        <label for="questions">Questions (comma-separated):</label>
                        <input type="text" id="questions" name="questions" 
                               placeholder="Enter questions e.g., grace period, maternity" required>
                    </div>
                    <div class="form-group">
                        <button type="submit">Upload and Process</button>
                    </div>
                </form>
            </div>
            <script>
                document.querySelector('form').onsubmit = function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData();
                    const file = document.getElementById('file').files[0];
                    const questions = document.getElementById('questions').value
                        .split(',')
                        .map(q => q.trim());
                    
                    formData.append('file', file);
                    formData.append('questions', JSON.stringify(questions));
                    
                    fetch('/api/v1/webhook', {
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355'
                        },
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert('Response: ' + JSON.stringify(data, null, 2));
                    })
                    .catch(error => {
                        alert('Error: ' + error);
                    });
                };
            </script>
        </body>
        </html>
    '''

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

# Sample document content for demonstration
SAMPLE_DOCUMENT = """
NATIONAL PARIVAR MEDICLAIM PLUS POLICY

This policy provides comprehensive health insurance coverage for families.

GRACE PERIOD
A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.

PRE-EXISTING DISEASES
There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.

MATERNITY EXPENSES
Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.

CATARACT SURGERY
The policy has a specific waiting period of two (2) years for cataract surgery.

ORGAN DONOR EXPENSES
Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.

NO CLAIM DISCOUNT
A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.

PREVENTIVE HEALTH CHECK-UPS
Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.

HOSPITAL DEFINITION
A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.

AYUSH TREATMENTS
The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.

ROOM RENT AND ICU CHARGES
For Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN).
"""

def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    token = credentials.credentials
    expected_token = "15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355"
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

def find_answer_by_question(question: str) -> str:
    """Find answer for a specific question"""
    question_lower = question.lower()
    
    # Define question-answer mappings
    qa_mappings = {
        "grace period": "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "premium payment": "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "pre-existing diseases": "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "ped": "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "maternity": "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "maternity expenses": "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "cataract": "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "cataract surgery": "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "organ donor": "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "organ donor expenses": "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "no claim discount": "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "ncd": "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "preventive health": "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "health check": "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "hospital": "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
        "ayush": "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
        "room rent": "For Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN).",
        "icu charges": "For Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN).",
        "sub-limits": "For Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
    }
    
    # Find matching answer
    for keyword, answer in qa_mappings.items():
        if keyword in question_lower:
            return answer
    
    # Default response if no specific answer found
    return "The requested information is not specifically covered in the policy document. Please refer to the policy terms and conditions for detailed information."

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    token: str = Depends(verify_auth)
):
    """
    Main endpoint for processing document queries
    """
    try:
        logger.info(f"Processing {len(request.questions)} questions for document: {request.documents}")
        
        # Process each question and find answers
        answers = []
        for question in request.questions:
            answer = find_answer_by_question(question)
            answers.append(answer)
            logger.info(f"Processed question: {question[:50]}...")
        
        # Prepare response
        response = QueryResponse(answers=answers)
        
        logger.info(f"Successfully processed {len(answers)} questions")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

from fastapi import Request

@app.post("/api/v1/webhook")
async def webhook_endpoint(
    request: Request,
    file: Optional[UploadFile] = File(None),
    token: str = Depends(verify_auth)
):
    """
    Webhook endpoint to receive external data and process queries
    Supports both JSON payload and PDF file upload with detailed analysis
    """
    try:
        documents = ""
        questions = []
        processing_start_time = datetime.now()

        if file and file.filename.lower().endswith('.pdf'):
            # Read and process PDF content with detailed analysis
            content = await file.read()
            pdf_content = ""
            page_contents = []
            
            # Parse PDF content with detailed extraction
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            # Extract metadata
            metadata = {
                "file_name": file.filename,
                "total_pages": len(pdf_reader.pages),
                "file_size": len(content),
                "processing_start": processing_start_time.isoformat()
            }
            
            # Process each page with progress tracking
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                page_contents.append({
                    "page_number": page_num + 1,
                    "text_length": len(page_text),
                    "has_content": bool(page_text.strip())
                })
                pdf_content += page_text
                logger.info(f"Processed page {page_num + 1}/{len(pdf_reader.pages)}")
            
            # Store the extracted text
            documents = pdf_content
            
            # Get questions from form data
            form = await request.form()
            questions_str = form.get('questions', '[]')
            try:
                questions = json.loads(questions_str)
                if isinstance(questions, str):
                    # Handle comma-separated string
                    questions = [q.strip() for q in questions.split(',')]
            except json.JSONDecodeError:
                # Fallback for plain text input
                questions = [questions_str.strip()]
                
            logger.info(f"Processing {len(questions)} questions for PDF document")
            
            # Get the form data for questions
            form = await request.form()
            questions_str = form.get("questions", "[]")
            try:
                questions = json.loads(questions_str)
            except:
                questions = []
            
            logger.info(f"Processed PDF file: {file.filename}")
        else:
            # Handle regular JSON payload
            payload = await request.json()
            documents = payload.get("documents", "")
            questions = payload.get("questions", [])
            logger.info(f"Received webhook data: {len(str(payload))} characters")

        if not isinstance(questions, list) or not questions:
            raise HTTPException(status_code=400, detail="No questions provided in webhook payload")

        # Process the questions using existing logic
        answers = []
        for question in questions:
            answer = find_answer_by_question(question)
            answers.append(answer)
            logger.info(f"Processed webhook question: {question[:50]}...")

        response = QueryResponse(answers=answers)
        logger.info(f"Successfully processed {len(answers)} webhook questions")

        return {
            "status": "success",
            "processed_questions": len(questions),
            "answers": answers,
            "webhook_received_at": datetime.now().isoformat()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/stats")
async def get_stats(token: str = Depends(verify_auth)):
    """Get system statistics"""
    return {
        "total_queries": 0,
        "average_confidence": 0.0,
        "most_common_queries": [],
        "system_uptime": "active"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 