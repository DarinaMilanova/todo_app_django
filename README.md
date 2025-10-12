# 📝 My To-Do App

A Django-based To-Do application with user authentication, dark mode, dashboards, and password reset functionality.

---

## 🚀 Features

- ✅ Create, update, delete, and manage personal tasks
- 📅 Due date tracking and automatic overdue highlighting
- 🗂️ Custom categories per user
- 📊 Dashboard with statistics and motivational quotes
- 🌗 Dark/Light mode toggle (saved per session)
- 🔐 Full authentication (register, login, logout, password reset)
- 🧩 Responsive Bootstrap 5 design

---

## 🧱 Project Structure

```
todo-app/
│
├── config/               # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── tasks/                # Main Django app
│   ├── static/tasks/     # CSS, JS, images
│   │   └── style.css
│   ├── templates/
│   │   ├── tasks/        # App UI templates
│   │   └── registration/ # Auth & password reset templates
│   ├── views.py
│   ├── forms.py
│   ├── models.py
│   └── urls.py
│
├── staticfiles/          # Collectstatic output (ignored in git)
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/todo-app.git
   cd todo-app
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the app**
   Visit: `http://127.0.0.1:8000`

---

## 🔑 Admin Access

Create a superuser to access the Django admin panel:

```bash
python manage.py createsuperuser
```
Then visit: `http://127.0.0.1:8000/admin/`

---

## 👩🏻‍💻Author

**Darina Milanova**  
Built with ❤️ using Django & Bootstrap  
📧 Contact: darinakmilanova@gmail.com

