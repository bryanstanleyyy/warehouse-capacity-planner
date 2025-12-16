# Environment Variables Reference

Complete reference for all environment variables used in the Warehouse Capacity Planner application.

## Database Configuration

### POSTGRES_USER
- **Required**: Yes
- **Default**: None
- **Description**: PostgreSQL database username
- **Example**: `warehouse_prod_user`
- **Security**: Use a dedicated user, not `postgres` root user
- **Notes**: Must match between `.env` and database configuration

### POSTGRES_PASSWORD
- **Required**: Yes
- **Default**: None
- **Description**: PostgreSQL database password
- **Example**: Generate with `openssl rand -base64 32`
- **Security**: Must be strong (16+ chars, mixed case, numbers, symbols)
- **Notes**: Never use default or development passwords in production

### POSTGRES_DB
- **Required**: Yes
- **Default**: None
- **Description**: PostgreSQL database name
- **Example**: `warehouse_planner_prod`
- **Notes**: Use descriptive name, consider environment suffix

### DATABASE_URL
- **Required**: Yes (auto-generated or manual)
- **Default**: Generated from POSTGRES_* variables
- **Description**: Full PostgreSQL connection string
- **Format**: `postgresql://user:password@host:port/database`
- **Example**: `postgresql://user:pass@db:5432/warehouse_planner_prod`
- **Notes**: Overrides individual POSTGRES_* variables if set

## Backend Configuration

### SECRET_KEY
- **Required**: Yes
- **Default**: None (unsafe default in development)
- **Description**: Flask secret key for session encryption and CSRF protection
- **Generation**: `python -c "import secrets; print(secrets.token_hex(32))"`
- **Security**: CRITICAL - Must be random and kept secret
- **Length**: 64 characters (32 bytes hex-encoded)
- **Notes**: Changing this invalidates all existing sessions

### FLASK_ENV
- **Required**: Yes
- **Default**: `development`
- **Valid Values**: `development`, `production`, `testing`
- **Description**: Flask environment mode
- **Production Value**: Must be set to `production`
- **Notes**: Affects debug mode, logging, and security settings

### CORS_ORIGINS
- **Required**: Yes
- **Default**: `http://localhost:3000`
- **Description**: Comma-separated list of allowed CORS origins
- **Format**: `https://domain1.com,https://domain2.com`
- **Example**: `https://warehouse.example.com`
- **Security**: Never use `*` wildcard in production
- **Notes**: No trailing slashes, must include protocol (https://)

### MAX_UPLOAD_SIZE
- **Required**: No
- **Default**: `10485760` (10MB)
- **Description**: Maximum file upload size in bytes
- **Units**: Bytes
- **Example**: `20971520` for 20MB
- **Notes**: Must also be configured in nginx `client_max_body_size`

### LOG_LEVEL
- **Required**: No
- **Default**: `INFO`
- **Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description**: Application logging level
- **Production Value**: `INFO` or `WARNING`
- **Notes**: `DEBUG` should never be used in production (performance impact)

### UPLOAD_FOLDER
- **Required**: No
- **Default**: `/tmp/uploads`
- **Description**: Directory path for uploaded files
- **Example**: `/app/uploads`
- **Notes**: Must be writable by application, should be in a persistent volume

## Frontend Configuration

### VITE_API_URL
- **Required**: No
- **Default**: `/api/v1`
- **Description**: Base URL for API requests from frontend
- **Format**: Relative path or full URL
- **Examples**:
  - Relative (recommended): `/api/v1`
  - Absolute: `https://api.example.com/api/v1`
- **Notes**: Build-time variable (requires rebuild to change)

## Optional Configuration

### SENTRY_DSN
- **Required**: No
- **Default**: None
- **Description**: Sentry error tracking Data Source Name
- **Format**: `https://key@o0.ingest.sentry.io/project-id`
- **Example**: Get from Sentry.io project settings
- **Notes**: Highly recommended for production error tracking

### REDIS_URL
- **Required**: No
- **Default**: None
- **Description**: Redis connection string for caching
- **Format**: `redis://host:port/db`
- **Example**: `redis://redis:6379/0`
- **Notes**: Optional performance improvement, requires Redis service

### CACHE_TYPE
- **Required**: No
- **Default**: `SimpleCache` (dev), `FileSystemCache` (prod)
- **Description**: Type of caching backend
- **Valid Values**: `SimpleCache`, `FileSystemCache`, `RedisCache`
- **Notes**: Automatically set based on FLASK_ENV

### CACHE_DEFAULT_TIMEOUT
- **Required**: No
- **Default**: `300` (5 minutes)
- **Description**: Default cache timeout in seconds
- **Example**: `600` for 10 minutes
- **Notes**: Adjust based on data volatility

## Docker-Specific Variables

These variables are used in Docker Compose but not directly by the application:

### Container Names
- `warehouse-planner-db-prod`
- `warehouse-planner-backend-prod`
- `warehouse-planner-frontend-prod`
- `warehouse-planner-nginx`

## Variable Precedence

1. Environment variables (highest priority)
2. `.env` file
3. Application defaults (lowest priority)

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use `.env.example`** as a template (with placeholder values)
3. **Generate unique values** for each environment (dev, staging, prod)
4. **Rotate secrets regularly** (quarterly recommended)
5. **Use strong passwords** (16+ characters minimum)
6. **Limit access** to `.env` files (`chmod 600`)
7. **Audit access** to production secrets regularly
8. **Use secret management** tools for enterprise deployments (Vault, AWS Secrets Manager)

## Validation

Before deployment, verify all required variables:

```bash
# Check if all required variables are set
grep -v '^#' .env | grep -E 'POSTGRES_|SECRET_KEY|CORS_ORIGINS' | wc -l
# Should return at least 5
```

## Troubleshooting

**Issue**: Application fails to start
**Check**: All required variables are set and valid

**Issue**: Database connection errors
**Check**: DATABASE_URL or POSTGRES_* variables are correct

**Issue**: CORS errors in browser
**Check**: CORS_ORIGINS includes your frontend domain with correct protocol

**Issue**: File uploads fail
**Check**: MAX_UPLOAD_SIZE and nginx client_max_body_size match
