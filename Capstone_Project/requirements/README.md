# Smart Warranty and Product Service Tracker

## Problem Statement

Managing warranties, product ownership records, and service requests manually often results in missed warranty claims, delayed servicing, lost invoices, and poor customer experience. Individuals and organizations frequently struggle to keep track of multiple products purchased from different vendors.

The **Smart Warranty and Product Service Tracker** provides a centralized platform to store product information, monitor warranty status, raise service requests, and receive AI-powered assistance for warranty-related queries. The system also visualizes product and service data to help users monitor their assets efficiently.

### Objectives

- Digitize warranty and product records.
- Track warranty expiration dates.
- Simplify service request management.
- Provide AI-assisted warranty support.
- Offer an interactive dashboard for monitoring products and services.

---

# Dataset / Reference Source

The project uses structured CSV datasets along with a MySQL database.

| Source / File | Description | Format | Notes |
| --- | --- | --- | --- |
| `data/products.csv` | Product inventory with purchase and warranty details | CSV | Imported into MySQL |
| `data/warranties.csv` | Warranty information for products | CSV | Used for warranty tracking |
| `data/service_requests.csv` | Customer service request records | CSV | Displays request status |
| `data/documents.csv` | Product document metadata | CSV | Invoice and warranty document references |
| `smart_warranty_database.sql` | Database schema | SQL | Creates database tables |
| `setup_database.sql` | Database initialization | SQL | Initial database setup |

---

# Tools Used

- **Programming Language:** Python 3
- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** MySQL
- **ORM / Database Connector:** SQLAlchemy
- **Data Processing:** Pandas
- **Visualization:** Plotly Express
- **Authentication:** Firebase Authentication (Pyrebase)
- **AI Integration:** Google Gemini API
- **Document Processing:** PyMuPDF
- **Speech Input:** streamlit-mic-recorder
- **Image Processing:** Pillow (PIL)
- **Version Control:** Git & GitHub

---

# Project Workflow

### 1. Data Collection

Product, warranty, document, and service request information is maintained using CSV files and imported into the MySQL database.

### 2. Database Initialization

SQL scripts create the required database tables before application startup.

### 3. User Authentication

Firebase Authentication provides secure login and signup functionality.

### 4. Dashboard

After authentication, users access a dashboard displaying:

- Product inventory
- Warranty statistics
- Service request analytics
- Warranty expiry visualization

### 5. Service Request Management

Users can submit and track service requests for registered products.

### 6. AI Warranty Assistant

The integrated Gemini AI assistant answers warranty-related questions and assists users in understanding product coverage and servicing information.

### 7. Data Visualization

Interactive Plotly charts provide insights into:

- Warranty expiry timeline
- Service request status
- Product inventory overview

---

# AI / Software Component

### Component Name

Gemini AI Warranty Assistant

### Purpose

Provide intelligent responses related to product warranties, servicing, and maintenance.

### Inputs

- User questions
- Product information
- Warranty details

### Outputs

- Warranty guidance
- Product support suggestions
- AI-generated assistance

### Technologies Used

- Google Gemini API
- Prompt-based Generative AI
- Streamlit Chat Interface

### Key Features

- AI-powered warranty assistance
- Natural language interaction
- Product information guidance
- Customer support enhancement

---

# Features

- Secure Login & Registration
- Product Inventory Management
- Warranty Tracking
- Service Request Submission
- Interactive Dashboard
- Warranty Expiry Monitoring
- AI Warranty Assistant
- CSV to Database Synchronization
- Data Visualization
- Responsive Streamlit Interface

---

# Project Structure

```
Capstone_Project/
│
├── app/
│   ├── app.py
│   ├── auth.py
│   └── database_initialise.py
│
├── data/
│   ├── products.csv
│   ├── warranties.csv
│   ├── service_requests.csv
│   └── documents.csv
│
├── requirements/
│   └── README.md
│
├── setup_database.sql
├── smart_warranty_database.sql
└── import_csv.py
```

---

# How To Run The Project

## Prerequisites

Install:

- Python 3.10+
- MySQL Server
- Git
- Streamlit

Configure:

- Firebase credentials
- Google Gemini API Key
- MySQL database

---

## Installation

```bash
git clone <repository-url>

cd Capstone_Project

pip install -r requirements.txt
```

---

## Database Setup

Create the database using:

```sql
setup_database.sql
```

or

```sql
smart_warranty_database.sql
```

---

## Run the Application

```bash
cd app

streamlit run app.py
```

---

## Expected Output

After launching the application:

- Login / Signup page
- Interactive dashboard
- Product inventory
- Warranty analytics
- Service request management
- AI warranty assistant
- Live product tracking interface

---

# Demo Screenshots

| Screen | Description | Screenshot |
| --- | --- | --- |
| Login Page | User Authentication | Add Screenshot |
| Dashboard | Warranty Overview | Add Screenshot |
| Product Inventory | Product Details | Add Screenshot |
| Service Request | Submit Service Request | Add Screenshot |
| AI Assistant | Gemini Chat Interface | Add Screenshot |

---

# Results and Insights

- Successfully centralizes warranty and product management.
- Reduces manual tracking of warranties and service requests.
- AI-powered assistance improves user experience.
- Interactive dashboards simplify product monitoring.
- Database-backed architecture enables scalable record management.

---

# Limitations

- Requires MySQL database configuration.
- Gemini API key and Firebase credentials must be configured manually.
- Limited document management features in the current version.
- Currently designed for desktop web usage through Streamlit.

---

# Future Improvements

- Email and SMS warranty expiry notifications.
- OCR-based invoice upload.
- QR code product registration.
- Mobile application support.
- Multi-user organization management.
- Predictive maintenance using machine learning.
- Cloud deployment with Docker and CI/CD.
- Integration with manufacturer APIs.

---

# Team Members

| Name | Role |
| --- | --- |
| Tulika | Project Development |
| Tisya | Backend & Database |
| Ritvik | AI Integration |
| Bhavya | Frontend & Testing |

---

# Conclusion

The **Smart Warranty and Product Service Tracker** is a comprehensive warranty management solution that combines secure authentication, centralized product storage, AI-powered assistance, service request management, and interactive analytics. The project demonstrates the practical integration of modern web technologies, databases, visualization tools, and Generative AI to improve product lifecycle management and customer support.
