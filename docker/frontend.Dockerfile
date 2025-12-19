# Multi-stage build for React frontend

# Stage 1: Build
FROM node:20-alpine AS builder

# Add build arg with default value
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build the application with increased memory limit
ENV NODE_OPTIONS="--max-old-space-size=768"
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
