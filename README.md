# LLM-Powered Intelligent Query Retrieval System

A comprehensive system for processing real-world documents in domains like insurance, legal, HR, and compliance. The system uses advanced LLM parsing, semantic embeddings, and intelligent clause matching to provide accurate, explainable results.

## 🚀 Features

- **Multi-format Document Processing**: Supports PDF, DOCX, and email content
- **LLM-Powered Query Parsing**: Uses GPT-4 to understand and structure user queries
- **Semantic Embeddings**: OpenAI embeddings with FAISS for efficient retrieval
- **Intelligent Clause Matching**: Multi-factor scoring with confidence assessment
- **Explainable Results**: Detailed rationale for each matched clause
- **FastAPI Backend**: Modern, async API with comprehensive documentation
- **PostgreSQL Integration**: Robust data storage and analytics
- **Authentication**: Secure Bearer token authentication
- **Low Latency**: Optimized for <2 second response times

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Document Proc  │    │   LLM Parser    │
│                 │    │                 │    │                 │
│  POST /hackrx/  │───▶│  PDF/DOCX/TXT   │───▶│  Query Analysis │
│      /run       │    │   Processing    │    │   & Intent      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │ Embedding Svc   │    │ Clause Matcher  │
│                 │    │                 │    │                 │
│ Token Validation│    │ OpenAI + FAISS  │    │ Semantic Match  │
│                 │    │ Vector Storage  │    │ Confidence Score│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Database Service│    │ Response Format │    │ JSON Output     │
│                 │    │                 │    │                 │
│ PostgreSQL Logs │    │ Structured Data │    │ Matched Clause  │
│ Analytics       │    │ Metadata        │    │ Rationale       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Requirements

- Python 3.8+
- PostgreSQL (optional, falls back to SQLite)
- OpenAI API key
- 4GB+ RAM for embedding operations

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd bajaj
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your configuration
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=postgresql://user:password@localhost/hackrx_db
```

4. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DATABASE_URL` | PostgreSQL connection string | SQLite fallback |
| `LLM_MODEL` | GPT model to use | `gpt-4` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-ada-002` |
| `CONFIDENCE_THRESHOLD` | Minimum confidence score | `0.7` |
| `SEGMENT_SIZE` | Document chunk size | `1000` |

### Authentication

The system uses Bearer token authentication:
```
Authorization: Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355
```

## 📡 API Usage

### Main Endpoint

**POST** `/hackrx/run`

Process a document query and return matched clauses.

**Request Body:**
```json
{
  "document_url": "https://example.com/contract.pdf",
  "user_query": "What is the termination clause?"
}
```

**Response:**
```json
{
  "query": "What is the termination clause?",
  "matched_clause": {
    "text": "Either party may terminate this agreement with 30 days written notice...",
    "location": "Page 3, Clause 2.4",
    "confidence": 0.91,
    "scoring_factors": {
      "intent_match": 0.95,
      "keyword_density": 0.88,
      "clause_type_match": 1.0,
      "text_relevance": 0.92
    }
  },
  "decision_rationale": "Clause 2.4 defines policy termination conditions clearly, matching the user's query about termination clauses. The clause specifies notice periods and termination procedures.",
  "metadata": {
    "source_document": "https://example.com/contract.pdf",
    "processed_at": "2025-01-28T12:00:00Z",
    "token_usage": {
      "prompt_tokens": 150,
      "completion_tokens": 75,
      "total_tokens": 225
    },
    "processing_time_ms": 1250
  }
}
```

### Health Check

**GET** `/health`

Returns system health status.

### Statistics

**GET** `/stats`

Returns system usage statistics (requires authentication).

## 🔍 Supported Query Types

The system can handle various types of queries:

- **Termination clauses**: "What is the termination clause?"
- **Payment terms**: "What are the payment terms?"
- **Liability limits**: "What are the liability limits?"
- **Confidentiality**: "What does the confidentiality clause say?"
- **Non-compete**: "What are the non-compete restrictions?"
- **Intellectual property**: "What are the IP rights?"
- **Governing law**: "What law governs this contract?"
- **Dispute resolution**: "How are disputes resolved?"
- **Force majeure**: "What are the force majeure provisions?"

## 🎯 Evaluation Metrics

The system is optimized for:

- **Accuracy**: High precision in clause matching
- **Token Efficiency**: Minimized LLM API costs
- **Low Latency**: <2 second response times
- **Explainability**: Clear rationale for matches
- **Modularity**: Reusable components

## 🏃‍♂️ Performance

- **Processing Time**: <2 seconds average
- **Token Usage**: ~200-300 tokens per query
- **Memory Usage**: ~500MB for typical documents
- **Concurrent Requests**: 10+ simultaneous queries

## 🔧 Development

### Project Structure

```
bajaj/
├── app.py                 # Main FastAPI application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── services/            # Core service modules
│   ├── __init__.py
│   ├── document_processor.py
│   ├── llm_parser.py
│   ├── embedding_service.py
│   ├── clause_matcher.py
│   ├── database.py
│   └── auth_service.py
└── README.md
```

### Adding New Features

1. **New Document Format**: Extend `DocumentProcessor`
2. **New Query Type**: Update `LLMParser` intent mapping
3. **New Scoring Factor**: Modify `ClauseMatcher`
4. **New Database Field**: Update `DatabaseService`

## 🧪 Testing

### Example Queries

```bash
# Test termination clause query
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355" \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://example.com/contract.pdf",
    "user_query": "What is the termination clause?"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 📊 Monitoring

The system provides comprehensive logging and metrics:

- **Query Processing**: Detailed logs for each request
- **Performance Metrics**: Processing time and token usage
- **Error Tracking**: Comprehensive error handling
- **Analytics**: Query patterns and confidence scores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the logs for detailed error information
- Verify your OpenAI API key is valid
- Ensure document URLs are accessible
- Check authentication token format

---

**Built with FastAPI, OpenAI, FAISS, and PostgreSQL** 