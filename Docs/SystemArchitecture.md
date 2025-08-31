# CortexAI System Architecture

## Overview

This document provides a comprehensive view of the CortexAI system architecture, showing how all components interact to deliver an AI-powered mental health and wellness platform.

## Architecture Layers

### 1. Client Layer
- **Unity Client (C#/.NET)**
  - Cross-platform mobile/desktop application
  - Voice input/output capabilities
  - Local encrypted caching for offline functionality
  - Offline queue for data synchronization
  - Real-time UI/UX components

- **Analytics Dashboard (React + TypeScript)**
  - Web-based admin and analytics interface
  - Data visualization and reporting
  - Clinical portal for healthcare providers
  - Built with Vite for fast development

### 2. API Gateway Layer
- **Azure API Management**
  - Web Application Firewall (WAF) protection
  - Rate limiting and throttling
  - Request routing and load balancing
  - CORS handling for web clients
  - API versioning and documentation

### 3. Backend Services Layer
- **Main Backend API (FastAPI + Python)**
  - User management and authentication
  - Session tracking and analytics
  - Business logic orchestration
  - Data validation and sanitization
  - Integration hub for all services

- **Emotion Analysis Service (FastAPI + Python)**
  - Text processing and NLP
  - Emotion detection algorithms
  - Confidence scoring
  - Keyword-based analysis with extensible ML models

- **Recommendation Service (FastAPI + Python)**
  - Mood-based recommendation logic
  - Therapy module selection
  - Difficulty level assignment
  - Personalization algorithms

### 4. External AI Services
- **Azure OpenAI**
  - Large Language Model processing
  - Context-aware response generation
  - Safety filtering and content moderation
  - Prompt optimization

- **Speech Services**
  - Automatic Speech Recognition (ASR)
  - Text-to-Speech (TTS) synthesis
  - Audio processing and enhancement
  - Multiple voice options

### 5. Data Storage Layer
- **Azure SQL Database**
  - User data with PII/PHI protection
  - Consent and compliance records
  - Session metadata and relationships
  - RBAC and audit controls

- **Cosmos DB (NoSQL)**
  - Telemetry and event data
  - Pseudonymous analytics data
  - Configuration and feature flags
  - High-throughput analytics aggregates

- **Blob Storage**
  - Audio artifacts and recordings
  - File uploads and temporary data
  - Backup and archival storage
  - Content delivery optimization

- **Azure Key Vault**
  - API keys and secrets management
  - Database connection strings
  - SSL certificates
  - Encryption key rotation

### 6. Identity & Security Layer
- **Azure AD B2C**
  - OpenID Connect (OIDC) authentication
  - User identity management
  - JWT token generation and validation
  - Social login integration

- **Log Analytics**
  - Security monitoring and SIEM
  - Audit trail management
  - Real-time alerting
  - Compliance reporting

### 7. Messaging & Analytics
- **Service Bus / Message Queue**
  - Asynchronous event processing
  - Retry logic and dead letter handling
  - Inter-service communication
  - Load balancing and scaling

- **Data Warehouse**
  - Analytics data processing
  - Historical data storage
  - ETL pipeline management
  - Reporting and business intelligence

## Communication Patterns

### Synchronous Communication
- **Client ↔ API Gateway**: HTTPS/REST for real-time interactions
- **API Gateway ↔ Backend Services**: HTTP/Internal network
- **Backend ↔ AI Services**: REST API calls with timeout handling

### Asynchronous Communication
- **Backend → Message Queue**: Event publishing for analytics
- **Message Queue → Data Warehouse**: ETL processing
- **Backend → Log Analytics**: Audit and monitoring events

## Technology Stack

### Frontend Technologies
- **Unity 2022.3+**: Cross-platform client development
- **React 18**: Modern web dashboard framework
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server

### Backend Technologies
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Object-Relational Mapping (ORM)
- **Pydantic**: Data validation and serialization
- **JWT**: Stateless authentication tokens

### Infrastructure & Cloud
- **Azure Cloud Platform**: Primary cloud provider
- **Docker**: Containerization for all services
- **Azure API Management**: Gateway and security
- **Virtual Networks**: Private connectivity

### AI & Machine Learning
- **Azure OpenAI**: GPT models for conversational AI
- **Azure Speech Services**: ASR and TTS capabilities
- **Custom NLP Models**: Emotion analysis and recommendations

## Security Architecture

### Data Protection
- **Encryption at Rest**: All databases and storage
- **Encryption in Transit**: TLS 1.2+ for all communications
- **Data Classification**: PII/PHI in SQL, pseudonymous in Cosmos
- **Key Management**: Azure Key Vault for all secrets

### Access Control
- **Authentication**: Azure AD B2C with OIDC
- **Authorization**: JWT tokens with role-based access
- **Network Security**: Private endpoints and VNet isolation
- **API Security**: WAF, rate limiting, and CORS protection

## Deployment Architecture

### Container Strategy
- Each service runs in its own Docker container
- Health check endpoints for monitoring
- Auto-scaling based on demand
- Blue-green deployment for zero downtime

### Service Ports
- Main API: 8000
- Emotion Analysis: 8001
- Recommendation: 8002
- Unity Client: Variable (client-side)
- Analytics Dashboard: 5173

### Monitoring & Observability
- Application Insights for performance monitoring
- Log Analytics for centralized logging
- Health check endpoints for service status
- Real-time alerting for critical issues

## Scalability Considerations

### Horizontal Scaling
- Stateless service design for easy scaling
- Load balancing across multiple instances
- Database connection pooling
- Caching strategies for frequently accessed data

### Performance Optimization
- Async processing for heavy operations
- Message queues for decoupling services
- CDN for static content delivery
- Database indexing and query optimization

## Compliance & Privacy

### Data Handling
- GDPR compliance with right to erasure
- HIPAA compliance for health data
- Data minimization principles
- Pseudonymization for analytics

### Audit & Compliance
- Complete audit trails in Log Analytics
- Data retention policies
- Regular security assessments
- Compliance reporting automation