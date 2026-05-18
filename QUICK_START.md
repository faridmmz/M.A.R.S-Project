# 🚀 Quick Start Guide

## 🐳 Option 1: Docker - NO Dependencies Needed! (BEST)

**Works on Windows, Mac, and Linux!**

✅ No Python installation needed  
✅ No Node.js installation needed  
✅ Perfect for sharing with others!

### Windows:
1. Install Docker Desktop (if not already installed)
   - Download from: https://www.docker.com/products/docker-desktop/
2. Make sure Docker Desktop is RUNNING
3. Double-click `start-docker.bat` or run `docker-compose up`
4. Open browser to `http://localhost:3000`

### Mac/Linux:
1. Install Docker Desktop (if not already installed)
   - **Mac:** Download from https://www.docker.com/products/docker-desktop/
   - **Linux:** Install Docker Engine - see https://docs.docker.com/engine/install/
2. Make sure Docker is RUNNING
3. Run:
   ```bash
   chmod +x start-docker.sh
   ./start-docker.sh
   ```
   Or simply: `docker-compose up`
4. Open browser to `http://localhost:3000`

That's it! 🎉

---

## 🪟 Option 2: Windows Script (Requires Python & Node.js)

**Check your dependencies first:** Run `check-dependencies.bat`

1. **Double-click `start.bat`**
2. Wait for both servers to start
3. Open your browser to `http://localhost:3000`

**Note:** This requires Python 3.11+ and Node.js 18+ to be installed.

---

## 🍎 Option 3: Mac/Linux Script (Requires Python & Node.js)

1. **Make the script executable and run it:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
2. Wait for both servers to start
3. Open your browser to `http://localhost:3000`

**Note:** This requires Python 3.11+ and Node.js 18+ to be installed.

**Don't have Python/Node.js?** Use Docker instead (Option 1) - it's much easier!

---

## 🐳 Option 4: Docker (Command Line)

**Prerequisites:** Docker Desktop installed

1. Open terminal in the project folder
2. Run:
   ```bash
   docker-compose up
   ```
3. Open browser to `http://localhost:3000`

**To stop:**
```bash
docker-compose down
```

**Why Docker?**
- No need to install Python or Node.js
- Works the same on Windows, Mac, and Linux
- Easy to share with others - just send the folder!

---

## 💻 Option 5: Manual Setup (For Developers)

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 2: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 3: Open Browser

Navigate to the URL shown in the frontend terminal (usually `http://localhost:3000`)

---

## Troubleshooting

**Port already in use?**
- Backend uses port 8000
- Frontend uses port 3000
- Change ports in the commands if needed

**Python not found?**
- Make sure Python 3.11+ is installed
- Try `python3` instead of `python`

**npm not found?**
- Install Node.js 18+ from nodejs.org
- Restart your terminal after installing

**Docker issues?**
- Make sure Docker Desktop is running
- Try `docker-compose up --build` to rebuild

---

## Need Help?

Check the main [README.md](README.md) for detailed documentation.

