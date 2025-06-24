# 🔧 Configuration Guide

Comprehensive guide for configuring the Documents Processor with structured extraction capabilities for optimal performance and business integration.

## 📋 Table of Contents
1. [Overview](#overview)
2. [Settings Configuration](#settings-configuration)
3. [Schema System](#schema-system)
4. [Prompt Engineering](#prompt-engineering)
5. [Environment Setup](#environment-setup)
6. [Performance Optimization](#performance-optimization)
7. [Security Configuration](#security-configuration)
8. [Integration Settings](#integration-settings)
9. [Troubleshooting](#troubleshooting)

---

## 🔍 Overview

The Documents Processor uses a hierarchical configuration system that supports:

- **Flexible Configuration**: JSON-based settings with environment variable overrides
- **Modular Architecture**: Separate configuration for different components
- **Business Adaptation**: Industry-specific schemas and prompts
- **Performance Tuning**: Caching, API optimization, and resource management
- **Security Controls**: API key management and data protection settings

### Configuration Hierarchy

```mermaid
graph TD
    A[Environment Variables] --> B[config/settings.json]
    B --> C[Schema Files]
    B --> D[Prompt Files]
    C --> E[base_types.json]
    C --> F[Business Schemas]
    D --> G[System Prompts]
    
    style A fill:#ff6b6b,stroke:#ff5252,color:white
    style B fill:#4ecdc4,stroke:#26a69a,color:white
    style C fill:#45b7d1,stroke:#2196f3,color:white
    style D fill:#96ceb4,stroke:#4caf50,color:white
```

---

## ⚙️ Settings Configuration

### Main Configuration File: `config/settings.json`

The primary configuration file controls all aspects of document processing and structured extraction.

#### Complete Configuration Example

```json
{
  "processing": {
    "default_model": "gpt-4o-mini",
    "fallback_model": "gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 4000,
    "timeout_seconds": 120,
    "retry_attempts": 3,
    "retry_delay": 2
  },
  "schemas": {
    "default_schema": "default_schema.json",
    "schema_directory": "config/schemas",
    "validation_enabled": true,
    "auto_fallback": true
  },
  "prompts": {
    "default_prompt": "default_prompt",
    "prompt_directory": "config/prompts",
    "template_variables": {
      "organization_name": "Your Company",
      "processing_date": "auto",
      "business_context": "general"
    }
  },
  "caching": {
    "enabled": true,
    "memory_slots": 100,
    "disk_max_size_mb": 500,
    "default_ttl_hours": 24,
    "cleanup_interval_hours": 6,
    "cache_directory": ".cache/structured_processing"
  },
  "input_processing": {
    "default_input_file": "processed_documents/complete_processing_report.md",
    "max_input_size_mb": 50,
    "encoding": "utf-8",
    "chunk_size": 50000,
    "overlap_size": 1000
  },
  "output_settings": {
    "output_directory": "processed_documents",
    "filename_template": "structured_results_{timestamp}.json",
    "pretty_print": true,
    "backup_originals": true,
    "include_metadata": true
  },
  "logging": {
    "level": "INFO",
    "log_file": "logs/structured_processing.log",
    "log_api_calls": true,
    "log_cache_operations": true,
    "detailed_errors": true,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "cost_management": {
    "daily_budget_usd": 50.0,
    "cost_estimation": {
      "gpt-4o-mini": {
        "input_per_1k_tokens": 0.150,
        "output_per_1k_tokens": 0.600
      },
      "gpt-4o": {
        "input_per_1k_tokens": 5.0,
        "output_per_1k_tokens": 15.0
      },
      "gpt-4": {
        "input_per_1k_tokens": 30.0,
        "output_per_1k_tokens": 60.0
      }
    },
    "budget_warnings": true,
    "auto_stop_on_budget": false
  },
  "performance": {
    "parallel_processing": true,
    "max_workers": 4,
    "batch_size": 10,
    "memory_limit_mb": 1000,
    "processing_timeout": 300
  },
  "business_settings": {
    "organization_name": "Your Organization",
    "industry": "general",
    "compliance_requirements": ["data_privacy", "audit_trail"],
    "custom_entity_types": [],
    "business_rules": {}
  }
}
```

### Configuration Sections Explained

#### Processing Settings
```json
{
  "processing": {
    "default_model": "gpt-4o-mini",      // Primary OpenAI model
    "fallback_model": "gpt-4o-mini",     // Backup model if primary fails
    "temperature": 0.1,                  // Control randomness (0.0-1.0)
    "max_tokens": 4000,                  // Maximum response length
    "timeout_seconds": 120,              // API call timeout
    "retry_attempts": 3,                 // Number of retries on failure
    "retry_delay": 2                     // Seconds between retries
  }
}
```

**Best Practices:**
- Use `gpt-4o-mini` for cost-effective processing
- Set `temperature` to 0.1 for consistent extraction
- Adjust `max_tokens` based on schema complexity
- Configure retries for reliability

#### Schema Configuration
```json
{
  "schemas": {
    "default_schema": "default_schema.json",    // Default extraction schema
    "schema_directory": "config/schemas",       // Schema files location
    "validation_enabled": true,                 // Validate against schema
    "auto_fallback": true                       // Use simpler schema on failure
  }
}
```

#### Caching System
```json
{
  "caching": {
    "enabled": true,                    // Enable/disable caching
    "memory_slots": 100,               // In-memory cache size
    "disk_max_size_mb": 500,           // Disk cache limit
    "default_ttl_hours": 24,           // Cache expiration time
    "cleanup_interval_hours": 6,       // Automatic cleanup frequency
    "cache_directory": ".cache/"       // Cache storage location
  }
}
```

**Cache Optimization:**
- Enable caching to reduce API costs
- Adjust TTL based on data freshness needs
- Monitor disk usage for large document volumes
- Use cleanup intervals to prevent cache bloat

---

## 📋 Schema System

### Schema Architecture Overview

The schema system uses a modular approach with base types and specialized schemas for different use cases.

```
config/schemas/
├── base_types.json                 # Reusable type definitions
├── default_schema.json             # General purpose extraction
├── document_analysis_schema.json   # Comprehensive analysis
└── [Custom business schemas]       # Industry-specific schemas
```

### Base Types Reference: `config/schemas/base_types.json`

Foundation types used across all schemas:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Base Types for Document Processing",
  "definitions": {
    "ReportMetadata": {
      "type": "object",
      "description": "Standard metadata for all processing reports",
      "properties": {
        "processor_version": {"type": "string"},
        "processing_timestamp": {"type": "string", "format": "date-time"},
        "input_file": {"type": "string"},
        "schema_name": {"type": "string"},
        "model_used": {"type": "string"},
        "processing_duration_seconds": {"type": "number"}
      },
      "required": ["processor_version", "processing_timestamp", "input_file"]
    },
    "ExtractionInfo": {
      "type": "object",
      "description": "Performance and cost information",
      "properties": {
        "total_characters_processed": {"type": "integer"},
        "extraction_method": {"type": "string"},
        "cache_hit": {"type": "boolean"},
        "processing_time_seconds": {"type": "number"},
        "api_cost_estimate_usd": {"type": "number"},
        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "BaseEntity": {
      "type": "object",
      "description": "Foundation for extracted entities",
      "properties": {
        "type": {"type": "string"},
        "name": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "source_location": {"type": "string"},
        "metadata": {"type": "object"}
      },
      "required": ["type", "name"]
    },
    "ContactInfo": {
      "type": "object",
      "description": "Structured contact information",
      "properties": {
        "email": {"type": "string", "format": "email"},
        "phone": {"type": "string"},
        "address": {"type": "string"},
        "website": {"type": "string", "format": "uri"},
        "social_media": {"type": "object"}
      }
    },
    "MonetaryValue": {
      "type": "object",
      "description": "Currency-aware monetary values",
      "properties": {
        "amount": {"type": "number"},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "exchange_rate": {"type": "number"},
        "base_currency_amount": {"type": "number"}
      },
      "required": ["amount", "currency"]
    },
    "DateRange": {
      "type": "object",
      "description": "Date intervals and periods",
      "properties": {
        "start_date": {"type": "string", "format": "date"},
        "end_date": {"type": "string", "format": "date"},
        "duration_days": {"type": "integer"},
        "timezone": {"type": "string"}
      },
      "required": ["start_date"]
    },
    "GeographicLocation": {
      "type": "object",
      "description": "Location information",
      "properties": {
        "address": {"type": "string"},
        "city": {"type": "string"},
        "state_province": {"type": "string"},
        "country": {"type": "string"},
        "postal_code": {"type": "string"},
        "coordinates": {
          "type": "object",
          "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
          }
        }
      }
    }
  }
}
```

### Creating Custom Schemas

#### Business-Specific Schema Example

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Custom Business Schema",
  "description": "Schema tailored for specific business requirements",
  "type": "object",
  "properties": {
    "metadata": {
      "$ref": "base_types.json#/definitions/ReportMetadata"
    },
    "extraction_info": {
      "$ref": "base_types.json#/definitions/ExtractionInfo"
    },
    "business_data": {
      "type": "object",
      "properties": {
        "summary": {
          "type": "object",
          "properties": {
            "total_documents": {"type": "integer"},
            "document_types": {"type": "object"},
            "processing_status": {"type": "string"},
            "key_findings": {"type": "array", "items": {"type": "string"}}
          }
        },
        "entities": {
          "type": "array",
          "items": {
            "$ref": "base_types.json#/definitions/BaseEntity"
          }
        },
        "financial_data": {
          "type": "array",
          "items": {
            "allOf": [
              {"$ref": "base_types.json#/definitions/MonetaryValue"},
              {
                "properties": {
                  "category": {"type": "string"},
                  "description": {"type": "string"},
                  "date": {"type": "string", "format": "date"}
                }
              }
            ]
          }
        },
        "temporal_data": {
          "type": "array",
          "items": {
            "$ref": "base_types.json#/definitions/DateRange"
          }
        }
      }
    }
  },
  "required": ["metadata", "extraction_info", "business_data"]
}
```

#### Schema Validation Commands

```bash
# Validate schema syntax
python structured_report_processor.py --validate-schema custom_business_schema.json

# Test schema with sample data
python structured_report_processor.py \
  --schema custom_business_schema.json \
  --input sample_data.md \
  --preview

# Show schema documentation
python structured_report_processor.py --schema-info custom_business_schema.json
```

---

## 🤖 Prompt Engineering

### Default Prompt: `config/prompts/default_prompt.txt`

The default system prompt is optimized for accurate, consistent extraction:

```
You are an extraction assistant. From arbitrary text, extract information and form **one** JSON object strictly according to the approved schema.

━━━━━━━━━━ 1 · ENTITY TYPES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extract these entity types:
- Organizations: Companies, institutions, agencies, government bodies
- People: Names, roles, titles, contact information
- Financial: Monetary amounts, budgets, costs, revenues, transactions
- Temporal: Dates, deadlines, timelines, schedules, durations
- Documents: Reports, contracts, invoices, receipts, certificates
- Locations: Addresses, cities, countries, facilities, venues

━━━━━━━━━━ 2 · CLASSIFICATION RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Entity Classification:
- Organizations: Use official names, include industry/type
- People: Full names with roles/titles when available
- Financial: Include currency, specify amounts clearly
- Temporal: Use ISO 8601 format (YYYY-MM-DD)
- Documents: Include document types and reference numbers
- Locations: Be specific about geographic hierarchy

━━━━━━━━━━ 3 · OUTPUT STRUCTURE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required JSON structure:
{
  "metadata": { /* Processing information */ },
  "extraction_info": { /* Performance metrics */ },
  "extracted_data": { /* Main extraction results */ }
}

━━━━━━━━━━ 4 · QUALITY STANDARDS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Data Quality Requirements:
- Accuracy: Extract only factual information from the text
- Completeness: Include all relevant entities found
- Consistency: Use standardized formats and terminology
- Confidence: Assign confidence scores based on source clarity
- Source Attribution: Note location of extracted information

━━━━━━━━━━ 5 · FIELD COMPLETION ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Field Completion Rules:
- Required fields: Must be completed if information exists
- Optional fields: Complete only if clearly stated
- Confidence scores: 0.9+ for explicit, 0.7+ for inferred, 0.5+ for uncertain
- Missing data: Use null values, never guess or fabricate
- Array fields: Include all relevant items found

━━━━━━━━━━ 6 · EXTRACTION PROCESS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step-by-step extraction:
1. Read through entire text to understand context
2. Identify entity types present in the document
3. Extract entities with location references
4. Classify entities according to schema requirements
5. Assign appropriate confidence scores
6. Structure data according to JSON schema
7. Validate completeness and accuracy
```

### Custom Prompt Development

#### Template Structure for Business Prompts

```
You are a {DOMAIN} extraction specialist. From {DOCUMENT_TYPES}, extract structured information for {BUSINESS_PURPOSE}.

━━━━━━━━━━ 1 · BUSINESS CONTEXT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{BUSINESS_CONTEXT}

━━━━━━━━━━ 2 · DOMAIN ENTITIES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{DOMAIN_SPECIFIC_ENTITIES}

━━━━━━━━━━ 3 · BUSINESS RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{BUSINESS_RULES}

━━━━━━━━━━ 4 · OUTPUT SCHEMA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{JSON_SCHEMA}

━━━━━━━━━━ 5 · VALIDATION RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{VALIDATION_REQUIREMENTS}

━━━━━━━━━━ 6 · EXTRACTION METHODOLOGY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{STEP_BY_STEP_PROCESS}
```

#### Example: Financial Domain Prompt

```
You are a financial document extraction specialist. From financial reports, invoices, and expense documents, extract structured information for accounting and compliance purposes.

━━━━━━━━━━ 1 · BUSINESS CONTEXT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Automate accounts payable and expense reporting
Requirements: GAAP compliance, audit trail preservation
Accuracy: 99%+ required for financial data

━━━━━━━━━━ 2 · DOMAIN ENTITIES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Monetary amounts (always include currency)
- Vendor information (legal names, tax IDs)
- Transaction dates (invoice, due, payment dates)
- GL codes and cost centers
- Tax information (rates, amounts, exemptions)
- Payment terms and methods

━━━━━━━━━━ 3 · BUSINESS RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Amounts must balance (line items = total)
- Dates must be valid and logical sequence
- Tax calculations must be verifiable
- Vendor names must match official records
- GL codes must follow company chart of accounts

━━━━━━━━━━ 4 · OUTPUT SCHEMA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "invoice_header": {...},
  "line_items": [...],
  "financial_totals": {...},
  "tax_details": {...}
}

━━━━━━━━━━ 5 · VALIDATION RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Verify mathematical accuracy
- Check date logical sequence
- Validate currency consistency
- Confirm required field completion
- Flag unusual patterns for review

━━━━━━━━━━ 6 · EXTRACTION METHODOLOGY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Identify document type (invoice, receipt, statement)
2. Extract header information (vendor, dates, numbers)
3. Process line items with quantities and amounts
4. Calculate and verify totals
5. Extract tax information and calculations
6. Validate against business rules
7. Format according to JSON schema
```

### Prompt Testing and Optimization

#### A/B Testing Framework

```python
# Test different prompt versions
def test_prompt_versions():
    test_cases = [
        {
            "input": "sample_invoice.md",
            "prompts": ["prompt_v1.txt", "prompt_v2.txt", "prompt_v3.txt"],
            "expected_schema": "invoice_schema.json"
        }
    ]
    
    results = {}
    for test_case in test_cases:
        for prompt in test_case["prompts"]:
            result = run_extraction(
                input_file=test_case["input"],
                prompt=prompt,
                schema=test_case["expected_schema"]
            )
            results[prompt] = evaluate_accuracy(result, test_case["expected"])
    
    return results
```

#### Performance Metrics

```python
def evaluate_prompt_performance(results):
    metrics = {
        "accuracy": calculate_field_accuracy(results),
        "completeness": calculate_field_completeness(results),
        "consistency": calculate_consistency_score(results),
        "processing_time": results["extraction_info"]["processing_time_seconds"],
        "api_cost": results["extraction_info"]["api_cost_estimate_usd"]
    }
    return metrics
```

---

## 🌍 Environment Setup

### Environment Variables Configuration

Create a `.env` file in the project root:

```bash
# Required: OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_ORG_ID=your_org_id_here  # Optional

# Optional: Model Preferences
STRUCTURED_PROCESSING_MODEL=gpt-4o-mini
STRUCTURED_PROCESSING_FALLBACK_MODEL=gpt-4o-mini
STRUCTURED_PROCESSING_TEMPERATURE=0.1

# Optional: Processing Limits
STRUCTURED_PROCESSING_TIMEOUT=120
STRUCTURED_PROCESSING_MAX_TOKENS=4000
STRUCTURED_PROCESSING_DAILY_BUDGET=50.0

# Optional: Caching Configuration
STRUCTURED_PROCESSING_CACHE_ENABLED=true
STRUCTURED_PROCESSING_CACHE_TTL=86400  # 24 hours in seconds
STRUCTURED_PROCESSING_CACHE_DIR=.cache/structured_processing

# Optional: Logging Configuration
STRUCTURED_PROCESSING_LOG_LEVEL=INFO
STRUCTURED_PROCESSING_LOG_FILE=logs/structured_processing.log
STRUCTURED_PROCESSING_DETAILED_ERRORS=true

# Optional: Business Configuration
ORGANIZATION_NAME="Your Organization"
INDUSTRY_TYPE="general"
BUSINESS_CONTEXT="document_processing"

# Optional: Security Settings
DATA_ENCRYPTION_ENABLED=false
AUDIT_TRAIL_ENABLED=true
COMPLIANCE_MODE=standard

# Optional: Integration Settings
WEBHOOK_URL=""
API_CALLBACK_URL=""
EXPORT_FORMAT=json
```

### Environment-Specific Configurations

#### Development Environment
```bash
# .env.development
STRUCTURED_PROCESSING_MODEL=gpt-4o-mini
STRUCTURED_PROCESSING_CACHE_TTL=3600  # 1 hour for rapid testing
STRUCTURED_PROCESSING_LOG_LEVEL=DEBUG
STRUCTURED_PROCESSING_DAILY_BUDGET=10.0
```

#### Production Environment
```bash
# .env.production
STRUCTURED_PROCESSING_MODEL=gpt-4o-mini
STRUCTURED_PROCESSING_FALLBACK_MODEL=gpt-4o-mini
STRUCTURED_PROCESSING_CACHE_TTL=86400  # 24 hours
STRUCTURED_PROCESSING_LOG_LEVEL=INFO
STRUCTURED_PROCESSING_DAILY_BUDGET=200.0
AUDIT_TRAIL_ENABLED=true
DATA_ENCRYPTION_ENABLED=true
```

### Configuration Validation

```python
def validate_environment():
    """Validate environment configuration"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ConfigurationError(f"Missing required environment variables: {missing_vars}")
    
    # Validate API key format
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key.startswith("sk-"):
        raise ConfigurationError("Invalid OpenAI API key format")
    
    # Validate budget settings
    daily_budget = float(os.getenv("STRUCTURED_PROCESSING_DAILY_BUDGET", 50.0))
    if daily_budget <= 0:
        raise ConfigurationError("Daily budget must be positive")
    
    return True
```

---

## 🚀 Performance Optimization

### Caching Strategies

#### Multi-Tier Cache Configuration

```json
{
  "caching": {
    "enabled": true,
    "tiers": {
      "memory": {
        "enabled": true,
        "max_size": 100,
        "ttl_seconds": 3600
      },
      "disk": {
        "enabled": true,
        "max_size_mb": 500,
        "ttl_seconds": 86400,
        "compression": true
      },
      "redis": {
        "enabled": false,
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "ttl_seconds": 604800
      }
    },
    "cache_keys": {
      "include_schema": true,
      "include_prompt": true,
      "include_model": true,
      "hash_algorithm": "sha256"
    }
  }
}
```

#### Cache Performance Monitoring

```python
class CacheMonitor:
    def __init__(self):
        self.stats = {
            "hits": 0,
            "misses": 0,
            "size": 0,
            "evictions": 0
        }
    
    def record_hit(self):
        self.stats["hits"] += 1
    
    def record_miss(self):
        self.stats["misses"] += 1
    
    def get_hit_ratio(self):
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total > 0 else 0
    
    def generate_report(self):
        return {
            "hit_ratio": self.get_hit_ratio(),
            "total_requests": self.stats["hits"] + self.stats["misses"],
            "cache_efficiency": "excellent" if self.get_hit_ratio() > 0.8 else "good" if self.get_hit_ratio() > 0.6 else "needs_improvement"
        }
```

### API Optimization

#### Rate Limiting and Retry Configuration

```json
{
  "api_optimization": {
    "rate_limiting": {
      "requests_per_minute": 60,
      "tokens_per_minute": 150000,
      "concurrent_requests": 5
    },
    "retry_strategy": {
      "max_attempts": 3,
      "base_delay": 1,
      "exponential_backoff": true,
      "jitter": true,
      "timeout_seconds": 120
    },
    "request_batching": {
      "enabled": true,
      "batch_size": 5,
      "batch_timeout": 30
    }
  }
}
```

#### Cost Optimization

```python
class CostOptimizer:
    def __init__(self, daily_budget=50.0):
        self.daily_budget = daily_budget
        self.daily_usage = 0.0
        self.cost_per_model = {
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},
            "gpt-4o": {"input": 5.0, "output": 15.0}
        }
    
    def estimate_cost(self, text, model="gpt-4o-mini"):
        tokens = self.estimate_tokens(text)
        input_cost = (tokens / 1000) * self.cost_per_model[model]["input"]
        output_cost = (tokens * 0.3 / 1000) * self.cost_per_model[model]["output"]  # Estimate output as 30% of input
        return input_cost + output_cost
    
    def check_budget(self, estimated_cost):
        if self.daily_usage + estimated_cost > self.daily_budget:
            raise BudgetExceededException(f"Operation would exceed daily budget")
        return True
    
    def recommend_model(self, text, quality_requirement="standard"):
        if quality_requirement == "high" or len(text) > 100000:
            return "gpt-4o"
        else:
            return "gpt-4o-mini"
```

---

## 🔒 Security Configuration

### Data Protection Settings

```json
{
  "security": {
    "data_protection": {
      "encrypt_at_rest": true,
      "encrypt_in_transit": true,
      "anonymize_output": false,
      "redact_pii": true,
      "audit_trail": true
    },
    "api_security": {
      "key_rotation_days": 90,
      "secure_storage": true,
      "environment_isolation": true
    },
    "access_control": {
      "user_authentication": false,
      "role_based_access": false,
      "ip_whitelisting": false
    },
    "compliance": {
      "gdpr_compliance": true,
      "hipaa_compliance": false,
      "sox_compliance": false,
      "data_retention_days": 365
    }
  }
}
```

### PII Redaction Configuration

```python
class PIIRedactor:
    def __init__(self):
        self.patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
        }
    
    def redact_text(self, text, redaction_char="*"):
        for pii_type, pattern in self.patterns.items():
            text = re.sub(pattern, lambda m: redaction_char * len(m.group()), text)
        return text
    
    def redact_json(self, data, fields_to_redact=None):
        if fields_to_redact is None:
            fields_to_redact = ["email", "phone", "ssn", "address"]
        
        def redact_value(obj):
            if isinstance(obj, dict):
                return {k: redact_value(v) if k not in fields_to_redact else "***REDACTED***" for k, v in obj.items()}
            elif isinstance(obj, list):
                return [redact_value(item) for item in obj]
            else:
                return obj
        
        return redact_value(data)
```

---

## 🔗 Integration Settings

### Webhook Configuration

```json
{
  "integrations": {
    "webhooks": {
      "enabled": false,
      "endpoints": [
        {
          "name": "processing_complete",
          "url": "https://your-api.com/webhooks/processing-complete",
          "method": "POST",
          "headers": {
            "Authorization": "Bearer your_token",
            "Content-Type": "application/json"
          },
          "timeout_seconds": 30,
          "retry_attempts": 3
        }
      ]
    },
    "database": {
      "enabled": false,
      "type": "postgresql",
      "connection_string": "postgresql://user:pass@localhost/db",
      "table_prefix": "doc_processor_"
    },
    "file_export": {
      "enabled": true,
      "formats": ["json", "csv", "xlsx"],
      "destinations": [
        {
          "type": "local",
          "path": "exports/"
        },
        {
          "type": "s3",
          "bucket": "your-bucket",
          "prefix": "processed-documents/"
        }
      ]
    }
  }
}
```

### API Integration Example

```python
class BusinessSystemIntegration:
    def __init__(self, config):
        self.config = config
        self.processor = StructuredReportProcessor()
    
    def process_and_integrate(self, document_path):
        # Process document
        results = self.processor.process_report(document_path)
        
        # Transform for business system
        transformed_data = self.transform_for_business_system(results)
        
        # Send to multiple systems
        if self.config["integrations"]["erp"]["enabled"]:
            self.send_to_erp(transformed_data)
        
        if self.config["integrations"]["crm"]["enabled"]:
            self.send_to_crm(transformed_data)
        
        if self.config["integrations"]["webhooks"]["enabled"]:
            self.send_webhooks(results)
        
        return results
    
    def transform_for_business_system(self, data):
        # Business-specific transformation logic
        return {
            "entities": data.get("extracted_data", {}).get("entities", []),
            "financial_data": data.get("extracted_data", {}).get("financial_data", []),
            "metadata": data.get("metadata", {})
        }
```

---

## 🔧 Troubleshooting

### Common Configuration Issues

#### 1. API Key Problems
```bash
# Test API connectivity
python structured_report_processor.py --test-connection

# Check API key permissions
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### 2. Schema Validation Errors
```python
def debug_schema_issues():
    try:
        with open("config/schemas/your_schema.json") as f:
            schema = json.load(f)
        jsonschema.validate({}, schema)  # Test with empty object
    except jsonschema.ValidationError as e:
        print(f"Schema validation error: {e.message}")
        print(f"Failed at path: {' -> '.join(str(p) for p in e.path)}")
    except json.JSONDecodeError as e:
        print(f"JSON syntax error: {e}")
```

#### 3. Performance Issues
```python
def diagnose_performance():
    import cProfile
    import pstats
    
    # Profile processing
    pr = cProfile.Profile()
    pr.enable()
    
    # Your processing code here
    processor = StructuredReportProcessor()
    results = processor.process_report("test_document.md")
    
    pr.disable()
    
    # Analyze results
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 time-consuming functions
```

### Configuration Validation

```python
def validate_configuration():
    """Comprehensive configuration validation"""
    issues = []
    
    # Check required files
    required_files = [
        "config/settings.json",
        "config/schemas/base_types.json",
        "config/schemas/default_schema.json",
        "config/prompts/default_prompt.txt"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing required file: {file_path}")
    
    # Validate settings.json
    try:
        with open("config/settings.json") as f:
            settings = json.load(f)
    except Exception as e:
        issues.append(f"Invalid settings.json: {e}")
        return issues
    
    # Check cache directory
    cache_dir = settings.get("caching", {}).get("cache_directory", ".cache")
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except Exception as e:
            issues.append(f"Cannot create cache directory: {e}")
    
    # Validate budget settings
    daily_budget = settings.get("cost_management", {}).get("daily_budget_usd", 0)
    if daily_budget <= 0:
        issues.append("Daily budget must be greater than 0")
    
    return issues

def fix_common_issues():
    """Automatically fix common configuration issues"""
    # Create missing directories
    os.makedirs("config/schemas", exist_ok=True)
    os.makedirs("config/prompts", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(".cache/structured_processing", exist_ok=True)
    
    # Set file permissions
    if os.name != 'nt':  # Not Windows
        os.chmod("config/settings.json", 0o600)  # Read/write for owner only
```

### Logging and Monitoring

```python
import logging
from datetime import datetime

def setup_comprehensive_logging():
    """Setup detailed logging for troubleshooting"""
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/structured_processing.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create specialized loggers
    api_logger = logging.getLogger('api_calls')
    cache_logger = logging.getLogger('cache_operations')
    performance_logger = logging.getLogger('performance')
    
    # API call logging
    def log_api_call(model, tokens, cost, duration):
        api_logger.info(f"API call: model={model}, tokens={tokens}, cost=${cost:.4f}, duration={duration:.2f}s")
    
    # Cache operation logging
    def log_cache_operation(operation, key, hit=None):
        if hit is not None:
            cache_logger.info(f"Cache {operation}: key={key[:20]}..., hit={hit}")
        else:
            cache_logger.info(f"Cache {operation}: key={key[:20]}...")
    
    # Performance logging
    def log_performance_metrics(metrics):
        performance_logger.info(f"Performance: {metrics}")
    
    return {
        "api": log_api_call,
        "cache": log_cache_operation,
        "performance": log_performance_metrics
    }
```

---

*This configuration guide provides comprehensive coverage of all configuration aspects for the Documents Processor. Regular review and optimization of these settings will ensure optimal performance and business value.*