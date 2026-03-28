# ⚡ Quick Start Guide

Get the Autonomous AI Developer System up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Git
- pip (Python package manager)

## 🚀 Installation (5 minutes)

### Step 1: Clone & Navigate
```bash
cd Autonomous-AI-Developer-System-AADS-
```

### Step 2: Create Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate venv
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy template
cp .env .env.local

# Edit with your settings (optional for basic usage)
nano .env.local
```

### Step 5: Run the System
```bash
streamlit run app.py
```

✅ **Done!** Open http://localhost:8501 in your browser

---

## 📋 First Task

Try this simple example:

1. **Input:** "Create a function that calculates factorial of a number with error handling"

2. **Watch it:**
   - ✓ Plan the implementation
   - ✓ Generate Python code
   - ✓ Validate syntax
   - ✓ Review code quality
   - ✓ Request approval

3. **Approve and commit** to your git branch

---

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_validator.py -v

# Run with coverage
pytest tests/ --cov=core --cov=agents
```

---

## 🔍 Verify Installation

Check that all files are present:

```bash
ls -la
# Should show:
# ├── app.py
# ├── requirements.txt
# ├── .env
# ├── agents/
# ├── core/
# ├── tests/
# └── README_SYSTEM.md
```

---

## 🐛 Common Issues

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Git Command Not Found
```bash
# On Ubuntu/Debian:
sudo apt-get install git

# On macOS:
brew install git
```

---

## 📚 Next Steps

1. **Read** [README_SYSTEM.md](README_SYSTEM.md) for full documentation
2. **Explore** the code in `core/` and `agents/` directories
3. **Run tests** to verify everything works
4. **Create tasks** in the UI and approve commits
5. **Customize** agents and validators as needed

---

## 🎯 System Capabilities

✓ Task planning and breakdown
✓ Python code generation
✓ Syntax validation (AST)
✓ Code quality scoring
✓ Security checking
✓ Safe git workflows
✓ Interactive UI dashboard
✓ Comprehensive testing

---

## 💡 Example Tasks

### Example 1: Simple Function
```
Create a function to check if a string is a palindrome
```

### Example 2: Data Class
```
Create a class to represent a Person with name, age, email
Include validation and string representation
```

### Example 3: Error Handling
```
Create a function that reads a JSON file safely
Handle missing files, invalid JSON, and other errors
```

---

## 📞 Need Help?

1. Check logs in terminal where you ran `streamlit run app.py`
2. Review the [full documentation](README_SYSTEM.md)
3. Check existing code in `agents/` and `core/` directories
4. Run tests to verify installation

---

**Happy coding! 🚀**
