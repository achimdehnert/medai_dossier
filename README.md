# 📘 MedAI Dossier - Value Dossier Management System
**Version 0.1** - Streamlit MVP ✅ **COMPLETED & RUNNING**

## 🚀 Project Overview

MedAI Dossier is a **Value Dossier Management System** designed for pharmaceutical companies to streamline **Health Technology Assessment (HTA)** dossier creation and management. 

**Current Status: V0.1 Streamlit MVP Complete** - Fully functional application ready for testing and use.

## ⚡ Quick Start

```bash
# Clone and run the MVP
git clone https://github.com/achimdehnert/medai_dossier.git
cd medai_dossier/streamlit_pilot
python -m streamlit run app.py --server.port 8501
```

**Access at:** <http://localhost:8501>

## 🎯 V0.1 Features (Streamlit MVP)

### Core Functionality

- **📋 Dossier Management**: Create, edit, and track value dossiers
- **🧪 Evidence Tracking**: Add and manage clinical evidence
- **💰 Simple Economics**: Basic cost calculations and parameter management
- **📊 Dashboard**: Status overview with key metrics
- **📱 Responsive UI**: Modern Streamlit interface

### Supported Use Cases

- Create new pharmaceutical dossiers
- Track clinical evidence and studies
- Manage basic economic parameters
- Monitor dossier completion status
- Export basic reports

## 🔧 Latest Updates (2025-07-07)

### ✅ Critical Fixes Completed

- **Import Errors Fixed**: Resolved all module import issues across 4 files
- **Streamlit Compatibility**: Updated 13 deprecated function calls (`st.experimental_rerun()` → `st.rerun()`)
- **UI Enhancement**: Removed non-functional upper sidebar by restructuring file organization
- **File Structure**: Renamed `pages/` to `components/` to prevent Streamlit navigation conflicts
- **Documentation**: Updated project memory and user guides for smooth restarts

### 🚀 Application Status

- **✅ Fully Functional**: All features working without errors
- **✅ Production Ready**: Safe for local testing and use
- **✅ Well Documented**: Complete restart instructions and troubleshooting guides

## 👥 Target Users (V0.1)

- **Market Access Teams**: Early-stage dossier planning
- **HEOR Analysts**: Evidence organization and tracking
- **Medical Affairs**: Clinical data management
- **Project Managers**: Status tracking and reporting

## 🏗️ Architecture (V0.1)

### Current Tech Stack
- **Frontend**: Streamlit (Python)
- **Backend**: Integrated Streamlit + Python services
- **Data Storage**: Local JSON/CSV files
- **Testing**: Pytest with comprehensive unit tests

### Planned Evolution
```
V0.1 (Streamlit Pilot) → V0.2 (Database) → V1.0 (FastAPI + UI)
```

### Service Architecture
- **DossierService**: Core dossier CRUD operations
- **EvidenceService**: Clinical evidence management
- **EconomicsService**: Economic modeling and calculations
- **HTAService**: HTA framework and submission management

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend dependencies)
- PostgreSQL 12+

### Installation

```bash
# Clone repository
git clone https://github.com/achimdehnert/medai_dossier.git
cd medai_dossier

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_database.py

# Start development servers
python -m uvicorn src.api.main:app --reload --port 8000  # Backend
cd flask_ui && python app.py  # Frontend
```

### Access
- **API Documentation**: http://localhost:8000/docs
- **Web Interface**: http://localhost:5000

## Project Structure

```
medai_dossier/
├── src/
│   ├── api/                    # FastAPI Backend
│   │   ├── main.py            # Application entry point
│   │   ├── routers/           # API endpoints
│   │   ├── models/            # Pydantic data models
│   │   └── services/          # Business logic
│   ├── core/
│   │   ├── dossier/           # Value dossier management
│   │   ├── evidence/          # Clinical evidence handling
│   │   ├── economics/         # Health economic models
│   │   └── hta/               # HTA-specific functionality
│   └── templates/             # Dossier templates
├── flask_ui/                  # Web interface
│   ├── app.py                # Flask application
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, assets
├── tests/
│   ├── robot/                # Robot Framework tests
│   └── unit/                 # Unit tests
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── data/                     # Sample data and templates
```

## Development Standards

### Code Quality
- **Maximum file length**: 500 lines
- **Maximum function length**: 50 lines
- **Type hints**: Required for all functions
- **Documentation**: Google-style docstrings
- **Testing**: Minimum 80% coverage

### Naming Conventions
- **Classes**: PascalCase (e.g., `DossierManager`)
- **Functions**: snake_case (e.g., `create_value_dossier`)
- **Variables**: snake_case (e.g., `clinical_data`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `HTA_FRAMEWORKS`)

## Standards & Compliance

### Supported HTA Frameworks
- **AMCP Format** (USA)
- **EUnetHTA Core Model** (EU)
- **G-BA Requirements** (Germany)
- **NICE Templates** (UK)
- **HAS Guidelines** (France)

### Data Standards
- **HL7 FHIR**: Clinical data exchange
- **CDISC Standards**: Clinical trial data
- **ISPOR Guidelines**: Health economics reporting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Project Wiki](docs/)
- **Issues**: [GitHub Issues](https://github.com/achimdehnert/medai_dossier/issues)
- **Discussions**: [GitHub Discussions](https://github.com/achimdehnert/medai_dossier/discussions)

## Version

**Current Version**: 0.1.0  
**Release Date**: 2025-07-07  
**Status**: Initial Development

---

*Built with ❤️ for advancing healthcare access through better evidence communication*
