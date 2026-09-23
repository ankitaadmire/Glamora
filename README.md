# 💄 Glamora — Beauty Service Marketplace

Glamora is a Django-based beauty service marketplace that connects customers with service providers through a centralized platform.

The project includes a custom admin panel for managing customers, service providers, categories, services, bookings, payments, reviews, offers, notifications, reports, and other platform operations.

---

## ✨ Features

### 👩‍💼 Custom Admin Panel

- Admin dashboard with dynamic statistics
- Customer management
- Service provider management
- Provider approval and rejection
- Category management
- Service management
- Provider-service assignment
- Booking management
- Reviews and ratings management
- Offers and discounts management
- Availability management
- Payment management
- Revenue tracking
- Reports
- Support query management
- Notification management
- Admin profile and settings

### 👤 Customer

- Customer registration and authentication
- Browse available beauty services
- View service details
- Book services
- View bookings
- Reviews and ratings

### 💇 Service Provider

- Provider registration
- Provider approval workflow
- Service assignment
- Availability management
- Booking-related functionality

### 🔔 Notifications

The admin panel includes notifications for important activities such as:

- New provider registration
- New booking
- New service requests
- Other platform activities

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Django | Web framework |
| Django REST Framework | API development |
| MySQL | Database |
| HTML5 | Frontend structure |
| CSS3 | Styling |
| Bootstrap | Responsive UI |
| JavaScript | Frontend interactions |
| XAMPP | Local MySQL server |

---

## 📁 Project Structure

```text
Glamora/
│
├── accounts/              # Custom user authentication and roles
├── adminpanel/            # Custom admin panel
├── api/                   # REST API
├── glamora/               # Django project configuration
├── services/              # Categories, services, bookings, etc.
├── static/                # CSS and static assets
├── templates/             # HTML templates
├── screenshots/           # Project screenshots
├── manage.py               # Django management file
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignored files
└── README.md               # Project documentation
