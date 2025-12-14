# Troubleshooting Guide

## White Screen Issue - Quick Fixes

### 1. Check if Backend is Running

The frontend needs the backend API to be running. Open a terminal and start the backend:

```bash
cd backend
python run.py
```

Expected output:
```
* Running on http://localhost:5000
```

### 2. Start the Frontend Development Server

In a **separate terminal**, start the frontend:

```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v7.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### 3. Open the Application

Navigate to: http://localhost:5173/

### 4. Check Browser Console for Errors

1. Open browser developer tools (Press F12)
2. Go to the "Console" tab
3. Look for any red error messages

Common errors and solutions:

#### "Failed to fetch" or "Network Error"
**Problem:** Backend is not running
**Solution:** Start the backend server (see step 1)

#### "Cannot read property of undefined"
**Problem:** Missing data or API response issue
**Solution:** Check backend logs and ensure database is initialized

#### Import errors or module not found
**Problem:** Missing dependencies
**Solution:**
```bash
cd frontend
npm install
```

### 5. Verify Setup

Run the diagnostic page to check connectivity:
http://localhost:5173/diagnostic.html

This will test:
- ✓ Frontend HTML loading
- ✓ JavaScript execution
- ✓ Backend API connectivity

### 6. Clear Cache and Rebuild

If issues persist:

```bash
# Frontend
cd frontend
rm -rf node_modules dist .vite
npm install
npm run dev

# Backend
cd backend
rm -rf __pycache__
```

### 7. Check Environment Variables

Verify [frontend/.env](frontend/.env):
```
VITE_API_URL=http://localhost:5000/api/v1
```

### 8. Error Boundary

The app now includes an error boundary that will show you detailed error information if React crashes. If you see an error screen with details, check:

1. The error message (shows what went wrong)
2. The component stack (shows where it happened)
3. Browser console for additional details

## Common Issues

### Port Already in Use

**Frontend (5173):**
```bash
# Find and kill process using port 5173
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5173 | xargs kill -9
```

**Backend (5000):**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Database Not Initialized

```bash
cd backend
flask db upgrade
flask seed-data  # Optional: load sample data
```

### Still Seeing White Screen?

1. **Hard refresh:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Clear browser cache:** Browser settings → Clear browsing data
3. **Try a different browser:** Chrome, Firefox, or Edge
4. **Check firewall:** Ensure localhost connections are allowed
5. **Review the terminal output:** Look for error messages in both frontend and backend terminals

## Getting Help

If you're still experiencing issues:

1. Check browser console (F12 → Console tab)
2. Check backend terminal for error messages
3. Check frontend terminal for build errors
4. Copy any error messages and search for solutions

## Quick Start Script

Create a file `start.sh` (Linux/Mac) or `start.bat` (Windows):

**start.sh:**
```bash
#!/bin/bash
# Start backend
cd backend
source venv/bin/activate
python run.py &

# Wait for backend
sleep 3

# Start frontend
cd ../frontend
npm run dev
```

**start.bat:**
```batch
@echo off
start cmd /k "cd backend && venv\Scripts\activate && python run.py"
timeout /t 3
start cmd /k "cd frontend && npm run dev"
```
