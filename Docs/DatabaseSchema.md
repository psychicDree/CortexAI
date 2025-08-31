# CortexAI Database Schema Documentation

## Overview

The CortexAI platform uses a multi-database architecture designed for security, compliance, and performance. This document details the database schema, relationships, and data management strategies.

## Database Architecture

### Azure SQL Database (Relational Data)
Primary database for structured data requiring ACID compliance and complex relationships.

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY IDENTITY(1,1),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE(),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    consent_given BIT DEFAULT 0,
    consent_date DATETIME2,
    timezone VARCHAR(50) DEFAULT 'UTC',
    healthcare_provider_id VARCHAR(100),
    
    INDEX IX_users_email (email),
    INDEX IX_users_created_at (created_at)
);
```

**Data Classification**: Contains PII (email, name, phone) and PHI (healthcare provider)
**Security**: Column-level encryption, row-level security
**Compliance**: GDPR Article 17 (right to erasure) support

#### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY IDENTITY(1,1),
    user_id INTEGER NOT NULL,
    mood VARCHAR(50),
    started_at DATETIME2 DEFAULT GETUTCDATE(),
    ended_at DATETIME2,
    duration_seconds INTEGER DEFAULT 0,
    session_type VARCHAR(50) DEFAULT 'general',
    notes NVARCHAR(MAX),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    completed BIT DEFAULT 0,
    tags NVARCHAR(MAX), -- JSON array
    metrics NVARCHAR(MAX), -- JSON object
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX IX_sessions_user_started (user_id, started_at),
    INDEX IX_sessions_mood (mood),
    INDEX IX_sessions_type (session_type)
);
```

**Data Classification**: Contains PHI (therapy notes, ratings)
**Relationships**: Many-to-one with users
**Performance**: Composite index on user_id + started_at for efficient queries

#### User Profiles Table
```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY IDENTITY(1,1),
    user_id INTEGER UNIQUE NOT NULL,
    goals NVARCHAR(MAX), -- JSON array
    conditions NVARCHAR(MAX), -- JSON array
    medications NVARCHAR(MAX), -- JSON array
    emergency_contact VARCHAR(255),
    therapist_id VARCHAR(100),
    assessment_data NVARCHAR(MAX), -- JSON object
    privacy_settings NVARCHAR(MAX), -- JSON object
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX IX_profiles_therapist (therapist_id)
);
```

**Data Classification**: Contains PHI (medical conditions, medications)
**Relationships**: One-to-one with users
**Security**: Encrypted JSON fields for sensitive medical data

#### Session Activities Table
```sql
CREATE TABLE session_activities (
    id INTEGER PRIMARY KEY IDENTITY(1,1),
    session_id INTEGER NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_data NVARCHAR(MAX), -- JSON object
    started_at DATETIME2 DEFAULT GETUTCDATE(),
    completed_at DATETIME2,
    duration_seconds INTEGER,
    outcome_score DECIMAL(3,2),
    user_feedback NVARCHAR(MAX),
    ai_analysis NVARCHAR(MAX), -- JSON object
    
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX IX_activities_session_started (session_id, started_at),
    INDEX IX_activities_type (activity_type)
);
```

**Data Classification**: Contains PHI (therapy activities, outcomes)
**Relationships**: Many-to-one with sessions
**Analytics**: Outcome scoring for effectiveness measurement

### Cosmos DB (NoSQL Analytics Data)

#### Telemetry Events Collection
```json
{
  "id": "unique-event-id",
  "partitionKey": "user_id_hash",
  "timestamp": "2024-01-27T10:30:00Z",
  "session_id": "pseudonymous-session-id",
  "user_id_hash": "sha256-hashed-user-id",
  "event_type": "session_start|voice_input|emotion_detected|recommendation_shown",
  "event_data": {
    "emotion": "joy",
    "confidence": 0.85,
    "duration_ms": 1500,
    "interaction_type": "voice"
  },
  "geo_region": "us-east",
  "device_type": "mobile|desktop",
  "app_version": "1.2.3",
  "performance_metrics": {
    "response_time_ms": 250,
    "memory_usage_mb": 45,
    "cpu_usage_percent": 12
  },
  "error_data": {
    "error_code": null,
    "error_message": null,
    "stack_trace": null
  },
  "tags": ["mindfulness", "breathing", "beginner"]
}
```

**Data Classification**: Pseudonymous (no direct PII linkage)
**Partition Strategy**: Hash of user ID for even distribution
**TTL**: 2 years for analytics retention

#### Analytics Aggregates Collection
```json
{
  "id": "daily-mood-2024-01-27-us-east",
  "partitionKey": "2024-01-27",
  "date": "2024-01-27",
  "metric_type": "mood_distribution",
  "metric_value": 0.35,
  "aggregation_level": "daily",
  "region": "us-east",
  "user_cohort": "new_users",
  "platform": "mobile",
  "time_bucket": "morning",
  "additional_dimensions": {
    "age_group": "25-34",
    "session_count": 1250,
    "avg_duration": 420
  }
}
```

**Data Classification**: Aggregated analytics (no individual user data)
**Partition Strategy**: Date-based for time-series queries
**Use Case**: Real-time dashboards and reporting

#### Configuration Collection
```json
{
  "id": "emotion-analysis-config",
  "partitionKey": "emotion_analysis",
  "config_type": "service_config",
  "config_data": {
    "confidence_threshold": 0.7,
    "supported_emotions": ["joy", "sadness", "anger", "fear", "neutral"],
    "keyword_weights": {
      "happy": 1.0,
      "great": 0.8,
      "good": 0.6
    }
  },
  "created_at": "2024-01-27T10:00:00Z",
  "updated_at": "2024-01-27T10:00:00Z",
  "active": true,
  "version": 1
}
```

**Data Classification**: System configuration (public)
**Partition Strategy**: Configuration type
**Use Case**: Dynamic service configuration without deployment

#### Feature Flags Collection
```json
{
  "id": "voice-emotion-analysis",
  "partitionKey": "voice_emotion_analysis",
  "flag_name": "voice_emotion_analysis",
  "enabled": true,
  "target_users": ["beta-testers", "premium-users"],
  "target_regions": ["us-east", "eu-west"],
  "start_date": "2024-01-27T00:00:00Z",
  "end_date": "2024-02-27T00:00:00Z",
  "rollout_percentage": 25
}
```

**Data Classification**: System configuration (public)
**Partition Strategy**: Feature flag name
**Use Case**: Gradual feature rollouts and A/B testing

### Azure Blob Storage (File Data)

#### Audio Artifacts Container
- **Purpose**: Temporary storage for voice recordings and audio analysis
- **Structure**: `/{user_id_hash}/{session_id}/{timestamp}-{type}.{ext}`
- **Retention**: 30 days with auto-deletion
- **Security**: Private access with SAS tokens

#### User Data Container
- **Purpose**: User-uploaded files and exported data
- **Structure**: `/{user_id}/{category}/{filename}`
- **Retention**: User-controlled with compliance override
- **Security**: User-scoped access control

#### System Data Container
- **Purpose**: Application logs, error reports, diagnostic data
- **Structure**: `/{service}/{date}/{log-type}-{timestamp}.json`
- **Retention**: 90 days for security logs, 30 days for performance
- **Security**: Admin-only access

### Azure Key Vault (Secrets Management)

#### Stored Secrets
- Database connection strings (SQL, Cosmos)
- API keys (OpenAI, Speech Services)
- JWT signing keys with rotation
- SSL certificates
- Service principal credentials
- Encryption keys for sensitive data

#### Security Features
- Hardware Security Module (HSM) backing
- Access policies with least privilege
- Audit logging for all access
- Automatic key rotation
- Network access restrictions

## Relationships and Constraints

### Primary Relationships
1. **Users ↔ Sessions** (1:N)
   - One user can have multiple therapy sessions
   - Cascade delete for data privacy compliance
   - Foreign key constraint ensures data integrity

2. **Users ↔ User Profiles** (1:1)
   - Each user has exactly one profile
   - Contains sensitive medical information
   - Separate table for better security and performance

3. **Sessions ↔ Session Activities** (1:N)
   - Each session contains multiple activities
   - Tracks individual exercises and interactions
   - Enables detailed progress monitoring

### Data Integrity Constraints
- **Email Uniqueness**: Prevents duplicate user accounts
- **Rating Validation**: Check constraint for 1-5 rating scale
- **Cascade Deletes**: Maintains referential integrity during user deletion
- **Non-null Constraints**: Ensures required fields are always populated

## Performance Optimization

### Indexing Strategy
- **Primary Keys**: Clustered indexes for fast row access
- **Foreign Keys**: Non-clustered indexes for join performance
- **Composite Indexes**: user_id + timestamp for session queries
- **Covering Indexes**: Include frequently accessed columns

### Query Optimization
- **Parameterized Queries**: Prevent SQL injection and improve plan reuse
- **Connection Pooling**: Reduce connection overhead
- **Read Replicas**: Offload analytics queries from primary database
- **Caching Layer**: Redis for frequently accessed configuration

### Cosmos DB Optimization
- **Partition Key Strategy**: Even distribution based on user hash
- **Request Unit (RU) Management**: Monitor and scale based on usage
- **Indexing Policy**: Custom indexes for specific query patterns
- **Time-to-Live (TTL)**: Automatic cleanup of old telemetry data

## Data Classification and Compliance

### PII (Personally Identifiable Information)
- **Location**: Azure SQL Database
- **Examples**: Email, name, phone number, date of birth
- **Protection**: Column-level encryption, access logging
- **Compliance**: GDPR, CCPA, state privacy laws

### PHI (Protected Health Information)
- **Location**: Azure SQL Database
- **Examples**: Medical conditions, therapy notes, assessments
- **Protection**: HIPAA-compliant encryption and access controls
- **Compliance**: HIPAA, HITECH Act

### Pseudonymous Data
- **Location**: Cosmos DB
- **Examples**: Hashed user IDs, aggregated metrics
- **Protection**: No direct linkage to PII
- **Use Case**: Analytics and machine learning

### Public/System Data
- **Location**: Cosmos DB, Key Vault
- **Examples**: Configuration, feature flags, system metadata
- **Protection**: Standard encryption and access controls
- **Use Case**: Application functionality and monitoring

## Backup and Recovery

### Backup Strategy
- **Azure SQL**: Automated daily backups with 7-day retention
- **Cosmos DB**: Continuous backup with point-in-time recovery
- **Blob Storage**: Geo-redundant storage with versioning
- **Key Vault**: Automatic backup with Microsoft-managed recovery

### Disaster Recovery
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Geo-Replication**: Secondary region for failover
- **Testing**: Monthly disaster recovery drills

## Migration and Evolution

### Schema Versioning
- **Database Migrations**: Alembic for SQL schema changes
- **Cosmos DB Evolution**: Schema-less design allows gradual migration
- **Backward Compatibility**: Maintain for at least 2 versions
- **Rollback Strategy**: Database snapshots before major changes

### Future Extensions
The schema is designed to accommodate future features:

1. **Therapists Table**: Healthcare provider management
2. **Assessments Table**: Standardized mental health assessments
3. **Notifications Table**: Push notification management
4. **User Goals Table**: Goal setting and tracking
5. **Appointments Table**: Scheduling integration
6. **Billing Table**: Payment and subscription management

### Scalability Considerations
- **Horizontal Partitioning**: User-based sharding for large datasets
- **Read Replicas**: Geographic distribution for global users
- **Caching Strategy**: Multi-level caching (application, database, CDN)
- **Archive Strategy**: Move old data to cheaper storage tiers

## Monitoring and Maintenance

### Performance Monitoring
- **Query Performance**: Identify slow queries and missing indexes
- **Resource Usage**: CPU, memory, and storage utilization
- **Connection Pooling**: Monitor connection health and usage
- **Deadlock Detection**: Identify and resolve blocking queries

### Data Quality
- **Validation Rules**: Enforce data integrity at application and database levels
- **Anomaly Detection**: Identify unusual patterns in data
- **Data Profiling**: Regular analysis of data quality metrics
- **Cleanup Jobs**: Remove orphaned or expired data

### Security Monitoring
- **Access Auditing**: Log all data access and modifications
- **Privilege Escalation**: Monitor for unauthorized access attempts
- **Data Exfiltration**: Detect unusual data access patterns
- **Compliance Reporting**: Automated compliance status reports