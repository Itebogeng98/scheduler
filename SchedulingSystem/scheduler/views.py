from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required 
from django.urls import reverse
from django.contrib import messages
from .utils import host_url
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course,  Vendor,CostSheet,Sale,CustomUser,Role
from .forms import CourseForm,VendorForm
import pandas as pd
from django.db.models import Count, Q
import json, requests
from .calculation import calculate_sale_cost_and_revenue,calculate_sale_cost_revenue_gp
from decimal import Decimal
from django.contrib.sessions.models import Session
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth






#Please note that I have used form.py for most of the updates function for certain models in views.py
#The reason I did that it was because of time constraint and I wanted to make sure that the project is completed on time.
#I will refactor the code to use requests and API in the future.
#ref IE Sebapu


def landing_page(request):
    return render(request, 'system_management/landing_page.html')


import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    api_url = f"{request.scheme}://{request.get_host()}{reverse('obtain_token')}"  # your token API URL

    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        try:
            # Call your token API
            response = requests.post(api_url, json={
                'username': username,
                'password': password
            })

            if response.status_code == 200:
                data = response.json()
                required_keys = ['token', 'user_id', 'user_role']
                if not all(key in data for key in required_keys):
                    return JsonResponse({"error": "Invalid response from authentication server"}, status=500)

                # Authenticate in Django session
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)  # Django session

                return JsonResponse({
                    'status': 'success',
                    'token': data['token'],
                    'user_id': data['user_id'],
                    'user_role': data['user_role'],
                    'message': data.get("message", "Login successful!"),
                    'redirect_url': reverse('dashboard'),
                }, status=200)
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Login failed.")
                except:
                    error_msg = "Login failed. Please try again."
                return JsonResponse({"error": error_msg}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"API connection error: {str(e)}"}, status=500)

    return render(request, 'system_management/login.html')


def sign_up_view(request):
    api_url = f"{host_url(request)}{reverse('signup_api')}"

    if request.method == 'GET':
        # Fetch roles from API to populate dropdown
        try:
            roles_response = requests.get(api_url, timeout=10)
            roles_data = roles_response.json().get("data", []) if roles_response.status_code == 200 else []
        except requests.exceptions.RequestException:
            roles_data = []

        return render(request, 'system_management/sign_up.html', {"roles": roles_data})

    if request.method == 'POST':
        headers = {"Content-Type": "application/json"}

        try:
            # Read JSON data from request body
            data = json.loads(request.body)

            # Check for required fields
            required_fields = ["work_email", "first_name", "last_name", "password", "role"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return JsonResponse({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            payload = {
                "work_email": data.get("work_email"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "password": data.get("password"),
                "role": data.get("role"),  # expects role ID
                "phone_number": data.get("phone_number", "")
            }

            # Call signup API
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=15)
            api_response = response.json()

            if response.status_code == 201:
                return JsonResponse({
                    "status": "success",
                    "message": "User registered successfully",
                    "data": api_response.get("data")
                }, status=201)

            # Return API errors if signup failed
            return JsonResponse({
                "status": "error",
                "message": api_response.get("message", "Signup failed"),
                "errors": api_response.get("errors", {})
            }, status=response.status_code)

        except ValueError as e:
            return JsonResponse({"status": "error", "message": f"Invalid JSON: {str(e)}"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"status": "error", "message": f"API connection failed: {str(e)}"}, status=502)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Unexpected error: {str(e)}"}, status=500)

    # fallback
    return render(request, 'system_management/sign_up.html')



@login_required
def dashboard(request):
    # 🔹 Total Students
    total_students = Sale.objects.aggregate(total=Sum('number_of_students'))['total'] or 0

    # 🔹 Confirmed Trainings
    confirmed_trainings = Sale.objects.filter(confirmed_training=True).count()

    # 🔹 Pending Confirmations
    pending_confirmations = Sale.objects.filter(confirmed_training=False).count()

    # 🔹 Pending count unapproved users

    pending_count = CustomUser.objects.filter(is_approved=False, is_superuser=False).count()


    # 🔹 Total Companies
    total_companies = (
        Sale.objects
        .exclude(company__isnull=True)
        .exclude(company__exact='')
        .values('company')
        .distinct()
        .count()
    )

    # 🔹 Client Type Distribution
    # 🔹 Count sales grouped by client_type name
    client_type_counts = (
            Sale.objects
            .values('client_type__client_name')  # ✅ get actual name from related table
            .annotate(total_sales=Count('id'))
            .order_by('client_type__client_name')
        )

    # 🔹 Convert to lists for Chart.js
    client_type_labels = [
            entry['client_type__client_name'] if entry['client_type__client_name'] else "Unknown"
            for entry in client_type_counts
        ]
    client_type_data = [entry['total_sales'] for entry in client_type_counts]


    # 🔹 Monthly Training Volume
    monthly_counts = (
        Sale.objects
        .annotate(month=ExtractMonth('proposed_date'))
        .values('month')
        .annotate(total_trainings=Count('id'))
        .order_by('month')
    )

    # Format data for Chart.js
    month_labels = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    month_data = [0] * 12  # start with zeros for all 12 months

    for entry in monthly_counts:
        month_index = entry['month'] - 1  # month 1 → index 0
        month_data[month_index] = entry['total_trainings']

    context = {
        'total_students': total_students,
        'confirmed_trainings': confirmed_trainings,
        'pending_confirmations': pending_confirmations,
        'total_companies': total_companies,
        'client_type_labels': client_type_labels,
        'client_type_data': client_type_data,
        'month_labels': month_labels,
        'month_data': month_data,
        'pending_count': pending_count,
    }

    return render(request, 'system_management/dashboard.html', context)



@login_required
def sales_view(request):
    api_url = f"{host_url(request)}{reverse('sale_list_api')}"
    sales = []
    error = None

    try:
        response = requests.get(api_url, timeout=10, headers={
            'Authorization': f'Token {request.user.auth_token.key}' if hasattr(request.user, 'auth_token') else ''
        })
        if response.status_code == 200:
            data = response.json()
            # Extract only the "data" list
            sales = data.get("data", [])
        else:
            error = f"Failed to fetch sales: {response.status_code}"
    except requests.exceptions.RequestException as e:
        error = f"Connection error: {str(e)}"

    # Pass sales and error to template
    context = {
        "sales": sales,
        "error": error
    }
    return render(request, 'system_management/sales/sales.html', context)

@login_required
@csrf_exempt
def vendors_create(request):
    api_url = f"{host_url(request)}{reverse('vendor_list_create_api')}"


    if request.method == "GET":
       
        return render(request, "system_management/vendors/create_vendor.html")
    
    if request.method == "POST":
        headers = {"Content-Type": "application/json"}

        try:
            data = json.loads(request.body)

            # Required fields
            required_fields = ["name"]
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return JsonResponse({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            payload = {
                "name": data.get("name"),
                "user": data.get("user"),       # expects user_id (FK)
                "is_active": data.get("is_active", False)
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=15)

            if response.status_code == 201:
                vendor_data = response.json()
                return JsonResponse({
                    "status": "success",
                    "data": vendor_data,
                    "message": "Vendor created successfully"
                }, status=201)

            # Pass through API error if creation failed
            return JsonResponse(response.json(), status=response.status_code)

        except ValueError as e:
            return JsonResponse({"error": f"Invalid data: {str(e)}"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"API connection failed: {str(e)}"}, status=502)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    # Fallback (should rarely reach here)
    return render(request, "system_management/vendors/create_vendor.html")


@login_required
@csrf_exempt
def vendors_view(request):
    # Annotate each vendor with course counts
    vendors = Vendor.objects.annotate(
        course_count=Count("course"),
        active_course_count=Count("course", filter=Q(course__is_active=True))
    )

    # ✅ Counts for the stats cards
    total_vendors = vendors.count()
    active_vendors_count = vendors.filter(is_active=True).count()
    courses_count = Course.objects.count()

    # Combine all courses across all vendors (optional, for global listing)
    all_courses = Course.objects.all()

    return render(request, "system_management/vendors/vendors.html", {
        "vendors": vendors,
        "all_courses": all_courses,
        "total_vendors": total_vendors,
        "active_vendors_count": active_vendors_count,
        "courses_count": courses_count
    })


@login_required
@csrf_exempt
def create_course_view(request, vendor_id):
    api_url = f"{host_url(request)}{reverse('create_course_api', args=[vendor_id])}"

    if request.method == "GET":
        return render(request, "system_management/vendors/create_course.html", {"vendor_id": vendor_id})

    if request.method == "POST":
        headers = {"Content-Type": "application/json"}

        try:
            data = json.loads(request.body)

            # Required fields
            required_fields = ["name", "code"]
            missing_fields = [field for field in required_fields if not data.get(field)]

            if missing_fields:
                return JsonResponse({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            payload = {
                "name": data.get("name"),
                "code": data.get("code"),
                "description": data.get("description", ""),
                # "vendor" will be set by the API based on the URL parameter
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=15)

            if response.status_code == 201:
                course_data = response.json()
                return JsonResponse({
                    "status": "success",
                    "data": course_data,
                    "message": "Course created successfully"
                }, status=201)

            # Pass through API error if creation failed
            return JsonResponse(response.json(), status=response.status_code)

        except ValueError as e:
            return JsonResponse({"error": f"Invalid data: {str(e)}"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"API connection failed: {str(e)}"}, status=502)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    # Fallback (should rarely reach here)
    return render(request, "system_management/vendors/create_course.html", {"vendor_id": vendor_id})


@login_required
@csrf_exempt
def courses_view(request, vendor_id):
    api_url = f"{host_url(request)}{reverse('create_course_api', args=[vendor_id])}"

    courses = []
    error = None

    if request.method == "GET":
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # ✅ Extract only the "data" list
                courses = data.get("data", [])
               
            else:
                error = f"Failed to fetch courses: {response.status_code}"
        except requests.exceptions.RequestException as e:
            error = f"Connection error: {str(e)}"

        return render(request, "system_management/vendors/courses_view.html", {
            "courses": courses,
            "vendor_id": vendor_id,
            "error": error
        })
    

@login_required
def import_courses(request, vendor_id):
    if request.method == "POST":
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            return JsonResponse({"message": "No file selected!"}, status=400)

        try:
            df = pd.read_excel(excel_file)
            # normalize headers
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

            for _, row in df.iterrows():
                Course.objects.update_or_create(
                    course_code=row.get('course_code'),
                    vendor_id=vendor_id,
                    defaults={
                        'course_description': row.get('course_description', ''),
                        'exam': row.get('exam', 'NA'),
                        'duration': row.get('duration', ''),
                        'price': row.get('price', 0),
                        'is_active': True
                    }
                )

            return JsonResponse({"message": "Courses imported successfully!"})
        except Exception as e:
            return JsonResponse({"message": f"Error importing courses: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request."}, status=400)



#I used forms.py to develop this function
@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('courses_view', vendor_id=course.vendor.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'system_management/vendors/edit_course.html', {'form': form, 'course': course})

# Activate / Deactivate Course
@login_required
def toggle_course_status(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.is_active = not course.is_active
    course.save()
    action = "activated" if course.is_active else "deactivated"
    messages.success(request, f"Course {action} successfully!")
    return redirect('courses_view', vendor_id=course.vendor.id)



# Edit Vendor
@login_required
def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == "POST":
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor updated successfully!")
            return redirect('vendors_view')
    else:
        form = VendorForm(instance=vendor)

    return render(request, 'system_management/vendors/edit_vendor.html', {'form': form, 'vendor': vendor})

# Activate / Deactivate Vendor
@login_required
def toggle_vendor_status(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_active = not vendor.is_active
    vendor.save()
    action = "activated" if vendor.is_active else "deactivated"
    messages.success(request, f"Vendor {action} successfully!")
    return redirect('vendors_view')



@login_required
@csrf_exempt
def create_sales(request):
    """
    Render the Sales creation page.
    Fetch populaters (client types, vendors, courses) from API 
    and pass them to the template.
    """
    api_url = f"{host_url(request)}{reverse('create_sale_api')}"
    client_types, vendors, courses = [], [], []
    error = None

    try:
        # Call the API to get populaters
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                client_types = data["populaters"]["client_types"]
                vendors = data["populaters"]["vendors"]
                courses = data["populaters"]["courses"]
                sales_people = data["populaters"]["sales_people"]
            else:
                error = data.get("message", "Failed to fetch populaters")
        else:
            error = f"API error: {response.status_code}"
    except requests.RequestException as e:
        error = f"Request failed: {e}"

    return render(request, "system_management/sales/create_sales.html", {
        "api_url": api_url,
        "client_types": client_types,
        "vendors": vendors,
        "courses": courses,
        "sales_people":sales_people,
        "error": error,
        "user_email": request.user.work_email,
        "sales_person": f"{request.user.first_name} {request.user.last_name}",
    })


@login_required
def client_type_cost_sheet_view(request):
    api_url = f"{host_url(request)}{reverse('request_client_type_api')}"
    client_types = []
    error = None

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            client_types = data.get("data", [])
        else:
            error = f"Failed to fetch client types. Status code: {response.status_code}"
    except Exception as e:
        error = str(e)

    return render(request, "system_management/cost_sheet/cost_client_type.html", {
        "client_types": client_types,
        "error": error,
        "api_url": api_url
    })


@login_required
@csrf_exempt
def client_type_cost_sheet(request, client_id):
    api_url = f"{request.scheme}://{request.get_host()}{reverse('cost_sheet_api', args=[client_id])}"

    # Field mapping based on client_id (same as in serializer)
    client_field_map = {
            1: ["instructor_cost","courseware","exam","lab_fees", "lms_license","data","project_man_fee","corporate_cost_content_dev","admin_cost","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware"],
            2: ["instructor_cost","courseware","exam","lab_fees","lms_license","data","project_man_fee","corporate_cost_content_dev","admin_cost","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware","daily_venue_cost","refreshment","consumables"],
            3: ["instructor_cost","courseware","exam","lab_fees","lms_license","data","project_man_fee","daily_venue_cost","refreshment"," consumables","qcto_seta_consumables","assessor_fees","sme_hour","sme_hour","labs","welcome_packs","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware","consumables"],
            4: ["instructor_cost","courseware","exam","lab_fees","lms_license","data","project_man_fee","daily_venue_cost","refreshment"," consumables","qcto_seta_consumables","assessor_fees","sme_hour","sme_hour","labs","welcome_packs","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware","consumables","recruitment"],
            5: ["instructor_cost","exam","lab_fees","consumables","sme_hour","travel_flights","accomodation","per_diem","international","driving_travel","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware"],
            6: ["instructor_cost","exam","lab_fees","total_cost","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware","marketing_fee"],
            7: ["instructor_cost","exam","lab_fees","daily_venue_cost","refreshment","consumables","set_up_fee","license_fee","per_user_fee","consulting","analysis","design","development","implementation","evaluation","e_learning_courseware","marketing_fee"],

        }

    if request.method == "GET":
        return render(request, "system_management/cost_sheet/client_cost_sheet_form.html", {
            "client_id": client_id,
            "allowed_fields": client_field_map.get(client_id, [])
        })

    if request.method == "POST":
        headers = {"Content-Type": "application/json"}

        try:
            data = json.loads(request.body)

            # Remove the missing fields check
            # Just forward whatever fields are sent
            response = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=15)

            if response.status_code == 201:
                return JsonResponse({
                    "status": "success",
                    "data": response.json(),
                    "message": "Cost sheet created successfully"
                }, status=201)

            return JsonResponse(response.json(), status=response.status_code)

        except ValueError as e:
            return JsonResponse({"error": f"Invalid JSON data: {str(e)}"}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"API connection failed: {str(e)}"}, status=502)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return render(request, "system_management/cost_sheet/client_cost_sheet_form.html", {
        "client_id": client_id,
        "allowed_fields": client_field_map.get(client_id, [])
    })


@login_required
def get_costsheet(request, client_type_id, course_id):
    gp_percent = Decimal("0.00")  # default in case of error

    try:
        cs = CostSheet.objects.filter(client_type_id=client_type_id).first()
        course = Course.objects.filter(id=course_id).first()
        num_students = int(request.GET.get("num_students", 0))

        if cs and course and num_students > 0:
            # Only call the GP function, it returns total_cost, revenue, gp_percent
            total_cost, revenue, gp_percent = calculate_sale_cost_revenue_gp(cs, course, num_students)

            return JsonResponse({
                "total_cost": float(total_cost),
                "revenue": float(revenue),
                "course_price": float(course.price) if course.price else 0,
                "gp_percent": float(gp_percent)
            })

        return JsonResponse({
            "total_cost": 0,
            "revenue": 0,
            "course_price": 0,
            "gp_percent": 0
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "total_cost": 0,
            "revenue": 0,
            "course_price": 0,
            "gp_percent": float(gp_percent),
        })


@login_required
def logout_view(request):
    try:
        # Clear the session safely
        session_key = request.session.session_key
        if session_key:
            Session.objects.filter(session_key=session_key).delete()
        request.session.flush()
        
        # Redirect directly to landing page
        return HttpResponseRedirect(reverse('landing_page'))
    
    except Exception:
        # Even if something goes wrong, redirect anyway
        return HttpResponseRedirect(reverse('landing_page'))


@login_required
def approve_sale_view(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    # Get the "Trainer" role
    trainer_role = Role.objects.filter(role="Trainer").first()

    # Fetch all users who have the Trainer role
    trainers = CustomUser.objects.filter(role=trainer_role) if trainer_role else []

    if request.method == "POST":
        # Update sale fields from POST data
        sale.company = request.POST.get("company")
        sale.course_name = request.POST.get("course_name")
        sale.number_of_students = request.POST.get("number_of_students")
        sale.proposed_date = request.POST.get("proposed_date")
        sale.training_end_date = request.POST.get("training_end_date")
        sale.pricing_approved_by = request.POST.get("pricing_approved_by")
        sale.sales_person = request.POST.get("sales_person")
        sale.branch = request.POST.get("branch")
        sale.notes = request.POST.get("notes")
        sale.revenue = request.POST.get("revenue")

        # Assign trainer if selected
        trainer_id = request.POST.get("trainer")
        if trainer_id:
            sale.user_id = int(trainer_id)

        # Handle approvals
        user_role = getattr(request.user.role, "role", "")
        if user_role == "Training Manager":
            sale.training_manager_approved = True

        # Update status based on approvals
        sale.update_status()
        sale.save()

        return JsonResponse({
            "status": "success",
            "message": "Sale updated and approved successfully"
        }, status=200)

    # GET request → render the template
    return render(request, "system_management/sales/sales_details.html", {
        "sale": sale,
        "trainers": trainers
    })


@login_required
def list_sales_for_approval(request):
    api_url = f"{host_url(request)}{reverse('sale_list_api')}"
    sales = []
    error = None
    pending_sales_count = 0

    try:
        response = requests.get(api_url, timeout=10, headers={
            'Authorization': f'Token {request.user.auth_token.key}' if hasattr(request.user, 'auth_token') else ''
        })
        if response.status_code == 200:
            data = response.json()
            # Extract only the "data" list
            sales = data.get("data", [])
            
            # Count only pending + partially approved sales
            pending_sales_count = sum(1 for sale in sales if sale['status'] in ['pending', 'partially_approved'])
        else:
            error = f"Failed to fetch sales: {response.status_code}"
    except requests.exceptions.RequestException as e:
        error = f"Connection error: {str(e)}"

    # Pass sales, error, and count to template
    context = {
        "sales": sales,
        "error": error,
        "pending_sales_count": pending_sales_count
    }
    return render(request, 'system_management/sales/list_sales.html', context)


@login_required
def approve_or_reject_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    user_role = getattr(request.user.role, 'role', None)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve":
            if user_role == "Training Manager":
                sale.training_manager_approved = True
                messages.success(request, "Sale approved by Training Manager.")
            else:
                messages.error(request, "You are not authorized to approve this sale.")

        elif action == "reject":
            if user_role in ["Training Manager"]:
                sale.status = "rejected"
                sale.training_manager_approved = False
                messages.warning(request, "Sale rejected.")
            else:
                messages.error(request, "You are not authorized to reject this sale.")

        # Automatically update the status
        sale.update_status()
        sale.save()

        # **Redirect to correct list view**
        return redirect("list_sales_for_approval")  # <- Updated here

    return render(request, "system_management/sales/sale_detail.html", {"sale": sale})



def cost_sheet_view(request):
    api_url = f"{host_url(request)}{reverse('cost_sheet_list_view_api')}"

    costsheet_data = []
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            costsheet_data = json_data.get("data", [])
    except requests.exceptions.RequestException as e:
        print("API request failed:", e)

    return render(request, 'system_management/cost_sheet/cost_client_type_view.html', {
        "costdata": costsheet_data,
        "count": len(costsheet_data)
    })



@login_required
@csrf_exempt
def ceo_approval_cost_sheet(request, sheet_id):
    api_url = f"{request.scheme}://{request.get_host()}{reverse('ceo_approval_cost_sheet_api', args=[sheet_id])}"

    # Determine if current user is CEO
    is_ceo = False
    try:
        is_ceo = getattr(request.user.role, "role", "").strip().lower() == "ceo"
    except Exception:
        is_ceo = False

    # Field map
    client_field_map = {
        1: ["instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data", "project_man_fee",
            "corporate_cost_content_dev", "admin_cost", "set_up_fee", "license_fee", "per_user_fee",
            "consulting", "analysis", "design", "development", "implementation", "evaluation",
            "e_learning_courseware"],
        2: ["instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data", "project_man_fee",
            "corporate_cost_content_dev", "admin_cost", "set_up_fee", "license_fee", "per_user_fee",
            "consulting", "analysis", "design", "development", "implementation", "evaluation",
            "e_learning_courseware", "daily_venue_cost", "refreshment", "consumables"],
        3: ["instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data", "project_man_fee",
            "daily_venue_cost", "refreshment", "consumables", "qcto_seta_consumables", "assessor_fees",
            "sme_hour", "labs", "welcome_packs", "set_up_fee", "license_fee", "per_user_fee", "consulting",
            "analysis", "design", "development", "implementation", "evaluation", "e_learning_courseware"],
        4: ["instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data", "project_man_fee",
            "daily_venue_cost", "refreshment", "consumables", "qcto_seta_consumables", "assessor_fees",
            "sme_hour", "labs", "welcome_packs", "set_up_fee", "license_fee", "per_user_fee", "consulting",
            "analysis", "design", "development", "implementation", "evaluation", "e_learning_courseware",
            "recruitment"],
        5: ["instructor_cost", "exam", "lab_fees", "consumables", "sme_hour", "travel_flights",
            "accomodation", "per_diem", "international", "driving_travel", "set_up_fee", "license_fee",
            "per_user_fee", "consulting", "analysis", "design", "development", "implementation", "evaluation",
            "e_learning_courseware"],
        6: ["instructor_cost", "exam", "lab_fees", "total_cost", "set_up_fee", "license_fee",
            "per_user_fee", "consulting", "analysis", "design", "development", "implementation", "evaluation",
            "e_learning_courseware", "marketing_fee"],
        7: ["instructor_cost", "exam", "lab_fees", "daily_venue_cost", "refreshment", "consumables",
            "set_up_fee", "license_fee", "per_user_fee", "consulting", "analysis", "design", "development",
            "implementation", "evaluation", "e_learning_courseware", "marketing_fee"],
    }

    # ========== GET ==========
    if request.method == "GET":
        try:
            response = requests.get(api_url, timeout=15)
            sheets = response.json().get("data", []) if response.status_code == 200 else []

            return render(request, "system_management/cost_sheet/ceo_approval_cost_sheet_form.html", {
                "client_id": sheet_id,
                "allowed_fields": client_field_map.get(sheet_id, []),
                "sheets": sheets,
                "is_ceo": is_ceo,   # <-- Important for template
            })
        except requests.exceptions.RequestException as e:
            return render(request, "system_management/cost_sheet/ceo_approval_cost_sheet_form.html", {
                "sheet_id": sheet_id,
                "allowed_fields": client_field_map.get(sheet_id, []),
                "sheets": [],
                "error": f"API connection failed: {str(e)}",
                "is_ceo": is_ceo,
            })

    # ========== POST ==========
    if request.method == "POST":

        # CEO-only enforcement
        if not is_ceo:
            return JsonResponse({"status": "error", "message": "Only CEO can perform this action."}, status=403)

        try:
            data = json.loads(request.body)
            action = data.get("action")
            cost_sheet_id = data.get("sheet_id")

            if not cost_sheet_id or action not in ["approve", "decline"]:
                return JsonResponse({"status": "error", "message": "Invalid parameters"}, status=400)

            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
                timeout=15
            )

            return JsonResponse(response.json(), status=response.status_code)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # ========== FALLBACK ==========
    return render(request, "system_management/cost_sheet/ceo_approval_cost_sheet_form.html", {
        "sheet_id": sheet_id,
        "allowed_fields": client_field_map.get(sheet_id, []),
        "is_ceo": is_ceo,
    })


@login_required
def pending_admins_view(request):
    api_url = f"{host_url(request)}{reverse('pending_admins_api')}"

    admins = []
    error = None

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            admins = data.get("data", [])
        else:
            error = f"Failed to fetch admins: {response.status_code}"
    except requests.exceptions.RequestException as e:
        error = f"Connection error: {str(e)}"

    return render(request, "system_management/admins/pending_admins.html", {
        "admins": admins,
        "error": error,
    })




@login_required
def approve_admin_view(request, user_id):
    api_url = f"{host_url(request)}{reverse('approve_admin_api', args=[user_id])}"

    try:
        response = requests.post(api_url, timeout=10)
        if response.status_code == 200:
            # success → redirect back
            return redirect("pending_admins_view")

        else:
            # return back with error (optionally use messages framework)
            return redirect("pending_admins_view")

    except requests.exceptions.RequestException:
        return redirect("pending_admins_view")


@login_required
def decline_admin_view(request, user_id):
    """
    Sends a POST request to the API to decline (delete) a pending admin.
    """
    api_url = f"{host_url(request)}{reverse('delete_admin_api', args=[user_id])}"

    try:
        response = requests.post(api_url, timeout=10)
        if response.status_code == 200:
            # Optionally, use Django messages to show success
            return redirect("pending_admins_view")
        else:
            # Optionally, log the response content for debugging
            return redirect("pending_admins_view")
    except requests.exceptions.RequestException as e:
        # Optionally, log the exception e
        return redirect("pending_admins_view")