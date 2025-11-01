# Documentation Index

## 📘 Main Documentation

**Start here**: [README.md](README.md)
- Quick start guide
- Configuration options (local, cloud, company API)
- Service usage and debugging
- Troubleshooting

## 📗 Supplementary Guides

### For New Machine Setup
**[SETUP_WORK_MACHINE.md](SETUP_WORK_MACHINE.md)**
- Detailed setup instructions for work machines
- Configuration examples for different scenarios
- Troubleshooting tips for new environments

### For Company API (Basic Auth)
**[COMPANY_API_GUIDE.md](COMPANY_API_GUIDE.md)**
- Technical details on company API integration
- Architecture and design decisions
- Debugging authentication issues
- Direct client usage examples

## 🗂️ File Structure

```
rag_api/
├── README.md              ← START HERE - Main documentation
├── SETUP_WORK_MACHINE.md  ← For new machine setup
├── COMPANY_API_GUIDE.md   ← For company API details
├── DOCUMENTATION.md       ← This file (index)
├── env.example            ← Configuration template
└── check_setup.py         ← Setup validation script
```

## 🚀 Quick Navigation

**I want to...**
- **Get started quickly** → [README.md#quick-start](README.md#quick-start)
- **Set up on a new machine** → [SETUP_WORK_MACHINE.md](SETUP_WORK_MACHINE.md)
- **Use company API** → [README.md#company-api-configuration](README.md#company-api-configuration)
- **Debug authentication** → [COMPANY_API_GUIDE.md#debugging](COMPANY_API_GUIDE.md#debugging)
- **See all config options** → `env.example`

## 💡 Pro Tips

1. **Always start with README.md** - it has 90% of what you need
2. **Use `env.example`** as your `.env` template
3. **Run `check_setup.py`** to validate your configuration
4. **Check service status** at `/status` endpoint or debug UI

