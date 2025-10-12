from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Category
from .forms import TaskForm, CustomRegisterForm, CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from datetime import timedelta, datetime
from django.utils.text import slugify
import json
import requests
@login_required
def task_list(request):
    today = timezone.now().date()
    today_plus_2 = today + timedelta(days=2)

    # All tasks for user
    tasks = Task.objects.filter(user=request.user)

    # --- Status filter ---
    status = request.GET.get('status')

    if status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'pending':
        tasks = tasks.filter(completed=False)
    elif status == 'due_soon':
        tasks = tasks.filter(completed=False, due_date__gte=today, due_date__lte=today_plus_2)
    elif status == 'overdue':
        tasks = tasks.filter(completed=False, due_date__lt=today)
    elif not status:
        # default: pending if no filter chosen
        tasks = tasks.filter(completed=False)

    # --- Search filter ---ƒ
    query = request.GET.get('q', '').strip()
    if query:
        tasks = tasks.filter(title__icontains=query)

    # --- Category filter ---
    category_id = request.GET.get('category')
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    # Get user's categories for the dropdown
    categories = Category.objects.filter(user=request.user)

    # Strip leading/trailing whitespace & blank lines from descriptions
    for task in tasks:
        if task.description:
            task.description = task.description.strip()

    # Map categories to specific badge color classes
    category_color_classes = {
        'shopping': 'badge-category-shopping',
        'work': 'badge-category-work',
        'personal': 'badge-category-personal',
        'house-shopping': 'badge-category-house-shopping',
        'pets': 'badge-category-pets',
        'health-fitness': 'badge-category-health-fitness',
        'finance-bills': 'badge-category-finance-bills',
        'travel': 'badge-category-travel',
    }

    for cat in categories:
        slug_name = slugify(cat.name)
        if slug_name not in category_color_classes:
            category_color_classes[slug_name] = 'badge-category-other'

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'today': today,
        'today_plus_2': today_plus_2,
        'categories': categories,
        'category_color_classes': category_color_classes,
        'request': request
    })
@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect('task_list')
    else:
        form = TaskForm()
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'tasks/create_task.html', {'form': form})


@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
    return render(request, 'tasks/update_task.html', {'form': form})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect('task_list')
    return render(request, 'tasks/delete_task.html', {'task': task})

@login_required
def manage_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(user=request.user, name=name)
            messages.success(request, f"Category '{name}' created successfully.")
            return redirect('manage_categories')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'tasks/manage_categories.html', {'categories': categories})


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f"Category '{category.name}' deleted.")
        return redirect('manage_categories')
    return render(request, 'tasks/delete_category.html', {'category': category})


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            messages.success(request, f"Category '{name}' updated.")
            return redirect('manage_categories')
    return render(request, 'tasks/edit_category.html', {'category': category})
def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect('task_list')
    else:
        form = CustomRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Logged in successfully.")
            return redirect('task_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'tasks/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('login')


@login_required
def toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')


@login_required
def update_due_date(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        due_date_str = request.POST.get('due_date')
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            task.due_date = None
        task.save()
    return redirect('task_list')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Password changed successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'tasks/profile.html', {
        'form': form,
        'user': request.user
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect('register')
    return render(request, 'tasks/delete_account.html')

@login_required
def dashboard(request):
    today = timezone.now().date()
    user_tasks = Task.objects.filter(user=request.user)

    # --- Daily stats ---
    daily_tasks = user_tasks.filter(due_date=today)
    daily_total = daily_tasks.count()
    daily_completed = daily_tasks.filter(completed=True).count()
    daily_completion_rate = round((daily_completed / daily_total) * 100, 1) if daily_total > 0 else 0

    # --- Other stats ---
    total = user_tasks.count()
    completed = user_tasks.filter(completed=True).count()
    pending = user_tasks.filter(completed=False).count()
    overdue = user_tasks.filter(completed=False, due_date__lt=today).count()
    due_today = daily_total - daily_completed

    # --- Category Breakdown ---
    categories = Category.objects.filter(user=request.user)
    category_counts = [
        {"name": cat.name, "count": user_tasks.filter(category=cat).count()}
        for cat in categories
    ]
    category_labels = [c["name"] for c in category_counts]
    category_values = [c["count"] for c in category_counts]

    # --- Upcoming Deadlines ---
    upcoming_deadlines = (
        user_tasks.filter(completed=False, due_date__gte=today)
        .order_by("due_date")[:3]
    )

    # --- Motivational Quote (cached per user/day) ---
    session_key = f"daily_quote_{request.user.id}_{today}"
    if session_key not in request.session:
        try:
            response = requests.get("https://zenquotes.io/api/random", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    quote_text = data[0].get("q", "Stay motivated!")
                    author = data[0].get("a", "Unknown")
                    request.session[session_key] = f"{quote_text} — {author}"
                else:
                    request.session[session_key] = "Stay motivated!"
            else:
                request.session[session_key] = "Stay motivated!"
        except Exception:
            request.session[session_key] = "Stay motivated!"

    quote = request.session[session_key]

    # --- Battery = Today’s Completion Rate ---
    battery_level = daily_completion_rate

    stats = {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "due_today": due_today,
        "daily_total": daily_total,
        "daily_completed": daily_completed,
        "daily_completion_rate": daily_completion_rate,
    }

    return render(request, "tasks/dashboard.html", {
        "stats": stats,
        "upcoming_deadlines": upcoming_deadlines,
        "quote": quote,
        "battery_level": battery_level,
        "category_labels": json.dumps(category_labels),
        "category_values": json.dumps(category_values),
    })
@login_required
def toggle_theme(request):
    current = request.session.get('dark_mode', False)
    request.session['dark_mode'] = not current
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))

@login_required
def clear_due_date(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.due_date = None
    task.save()
    return redirect('task_list')
