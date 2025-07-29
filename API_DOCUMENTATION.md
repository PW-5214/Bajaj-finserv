# RETRIEVAL SYSTEM API DOCUMENTATION

## Base URL (Local Development)
```
http://localhost:8000/api/v1
```

## Authentication
```
Authorization: Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355
```
✅ Team token loaded successfully

## API Endpoints Overview

### POST `/api/v1/hackrx/run`
**Run Submissions**

#### Sample Upload Request:
```http
POST /api/v1/hackrx/run
Content-Type: application/json
Accept: application/json
Authorization: Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355
```

#### Request Body:
```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}
```

#### Sample Response:
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
        "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
    ]
}
```

### GET `/api/v1/health`
**Health Check Endpoint**

#### Response:
```json
{
    "status": "healthy",
    "timestamp": "2025-07-29T00:09:43.691222"
}
```

### GET `/api/v1/stats`
**System Statistics** (requires authentication)

#### Response:
```json
{
    "total_queries": 0,
    "average_confidence": 0.0,
    "most_common_queries": [],
    "system_uptime": "active"
}
```

## Webhook Endpoint

### POST /api/v1/webhook

**Description**: Webhook endpoint to receive external data and process queries automatically.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment?",
    "What is the waiting period for pre-existing diseases?",
    "Does this policy cover maternity expenses?"
  ],
  "source": "external_system",
  "timestamp": "2025-07-29T00:18:27.704349"
}
```

**Response**:
```json
{
  "status": "success",
  "processed_questions": 3,
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period."
  ],
  "webhook_received_at": "2025-07-29T00:18:27.704349"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "No questions provided in webhook payload"
}
```

**Use Cases**:
- External system integration
- Automated document processing
- Batch query processing
- Real-time notifications

## Testing the API

### Using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
}'
```

### Using Python:
```python
import requests

url = "http://localhost:8000/api/v1/hackrx/run"
headers = {
    "Authorization": "Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

## Running the System

### Start the server:
```bash
python simple_app.py
```

### Test the API:
```bash
python test_new_api.py
```

## System Status

✅ **Server Running**: http://localhost:8000  
✅ **API Documentation**: http://localhost:8000/docs  
✅ **Health Check**: http://localhost:8000/api/v1/health  
✅ **Authentication**: Bearer token working  
✅ **Query Processing**: Multiple questions supported  
✅ **Response Format**: Matches documentation requirements  

## Supported Question Types

The system can handle various types of insurance policy questions:

- **Grace Period**: Premium payment grace periods
- **Pre-existing Diseases**: Waiting periods and coverage
- **Maternity Expenses**: Coverage conditions and limitations
- **Cataract Surgery**: Specific waiting periods
- **Organ Donor Expenses**: Coverage for donor medical expenses
- **No Claim Discount**: NCD benefits and conditions
- **Preventive Health**: Health check-up benefits
- **Hospital Definition**: Policy hospital criteria
- **AYUSH Treatments**: Alternative medicine coverage
- **Room Rent & ICU**: Sub-limits and coverage caps

## Error Handling

- **401 Unauthorized**: Invalid or missing authentication token
- **422 Validation Error**: Invalid request format
- **500 Internal Server Error**: Server processing error

## Performance

- **Response Time**: <2 seconds for typical queries
- **Concurrent Requests**: Supported
- **Memory Usage**: Optimized for document processing
- **Scalability**: Ready for production deployment 