# Production Deployment Checklist

Use this checklist to ensure all steps are completed before and after deployment.

## Pre-Deployment

### Infrastructure

- [ ] Server provisioned with minimum requirements (2 CPU, 4GB RAM, 20GB disk)
- [ ] Docker and Docker Compose installed
- [ ] Domain name configured and DNS pointed to server
- [ ] Firewall configured (ports 80, 443, SSH only)
- [ ] SSH key-based authentication enabled
- [ ] SSL certificate obtained (Let's Encrypt recommended)

### Configuration

- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` generated using `secrets.token_hex(32)`
- [ ] Strong database password set (16+ characters)
- [ ] `CORS_ORIGINS` set to production domain only
- [ ] `FLASK_ENV` set to `production`
- [ ] SSL certificate files copied to `./ssl/` directory
- [ ] `.env` file permissions set to 600 (`chmod 600 .env`)

### Code & Dependencies

- [ ] Latest code pulled from main branch
- [ ] No uncommitted changes in repository
- [ ] Docker images built successfully
- [ ] Frontend build completes without errors
- [ ] Backend dependencies resolved

## Deployment

### Database

- [ ] PostgreSQL container started and healthy
- [ ] Database migrations run successfully
- [ ] Database connection verified from backend
- [ ] Initial backup created

### Application

- [ ] All containers started successfully
- [ ] Health checks passing for all services
- [ ] Backend API responding at `/health`
- [ ] Frontend loading correctly
- [ ] No errors in container logs

### Security

- [ ] HTTPS working correctly (no certificate warnings)
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header present in responses
- [ ] Security headers configured (X-Frame-Options, etc.)
- [ ] Rate limiting enabled and tested
- [ ] CORS configured correctly (no wildcard in production)
- [ ] File upload size limits enforced

## Post-Deployment Verification

### Functional Testing

- [ ] Can create a new warehouse
- [ ] Can add zones to warehouse
- [ ] Can upload inventory file
- [ ] Can run allocation analysis
- [ ] Can export reports (HTML, CSV)
- [ ] Can delete resources

### Performance

- [ ] Page load time acceptable (< 3 seconds)
- [ ] API response times acceptable (< 1 second)
- [ ] File upload working for 10MB files
- [ ] No memory leaks observed
- [ ] Database queries optimized

### Monitoring

- [ ] Uptime monitoring configured and alerting
- [ ] Error tracking (Sentry) configured
- [ ] Log aggregation set up
- [ ] Backup automation configured and tested
- [ ] SSL certificate renewal automated

## Operational Readiness

### Documentation

- [ ] Deployment documentation reviewed
- [ ] Runbooks created for common operations
- [ ] Emergency contacts documented
- [ ] Rollback procedure tested

### Backup & Recovery

- [ ] Automated backup script tested
- [ ] Backup restoration tested
- [ ] Backup retention policy configured (30 days minimum)
- [ ] Offsite backup storage configured

### Maintenance

- [ ] Update schedule defined
- [ ] Maintenance window communicated
- [ ] Scaling plan documented
- [ ] Monitoring dashboards configured

## Sign-off

- [ ] Technical lead approval
- [ ] Security review completed
- [ ] Load testing performed (if required)
- [ ] Deployment window scheduled
- [ ] Stakeholders notified

---

**Deployment Date**: _______________

**Deployed By**: _______________

**Verified By**: _______________
