# Django imports
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Django models
from scheduler.models import (
    CustomUser,
    Vendor,
    Course,
    Client_Type,
    Sale,
    CostSheet,
    Role,
    Studio,
    Equipment,
    StudioEquipment,
)

# Django DB
from django.db import IntegrityError

# REST Framework imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# Serializers
from .serializers import (
    VendorSerializer,
    CourseSerializer,
    CreateSaleSerializer,
    SaleSerializer,
    CostSheetSerializer,
    SignupSerializer,
    RoleSerializer,
    CostSheetViewSerializer,
    SalesPersonSerializer,
    PendingAdminSerializer,
    EquipmentSerializer,
    StudioSerializer,
    StudioEquipmentSerializer,
    UserSerializer,
)
# Email utilities
from .email import send_welcome_email
from django.shortcuts import get_object_or_404, redirect, render









#This API authenticates a user and provides a token for future requests.
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return JsonResponse({"error": "Username and password are required."}, status=400)

    # ----------------------------------------------------
    # EMAIL DOMAIN VALIDATION
    # ----------------------------------------------------
    allowed_domains = ["netcampus.com", "netcampus.co.za"]
    domain = username.split("@")[-1].lower()

    if domain not in allowed_domains:
        return JsonResponse({
            "error": "Login restricted to Netcampus staff allowed to sign in"
        }, status=400)
    # ----------------------------------------------------

    # Authenticate using work_email (username)
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Superusers bypass approval check
        if not user.is_superuser:
            if not getattr(user, 'is_approved', False):
                return JsonResponse({
                    "error": "Your account is awaiting approval by the Super Admin."
                }, status=403)

        login(request, user)
        token, created = Token.objects.get_or_create(user=user)

        user_role = CustomUser.objects.filter(id=user.id).values(
            'work_email', 'id', 'first_name', 'last_name',
            'phone_number', 'role_id', 'role_id__role'
        ).first()

        return JsonResponse({
            'user_id': user.id,
            'token': token.key,
            'status': 'success',
            'user_role': user_role,
            'message': 'Logged in successfully'
        }, status=200)

    return JsonResponse({"error": "Invalid credentials."}, status=400)



#This API handles vendors — both listing them and creating new ones
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def vendor_list_create_api(request):
    if request.method == "GET":
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response({
            "status": "success",
            "message": "Vendors fetched successfully",
            "count": len(serializer.data),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            vendor = serializer.save()
            return Response({
                "status": "success",
                "message": f"Vendor '{vendor.name}' created successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Vendor creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

#This API manages courses for a specific vendor. It supports both creating new courses and listing existing ones.
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def create_course_api(request, vendor_id):
    # Check vendor exists
    try:
        vendor = Vendor.objects.get(id=vendor_id)
    except Vendor.DoesNotExist:
        return Response({"status": "error", "message": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        # Inject vendor into request data
        data = request.data.copy()
        data["vendor"] = vendor.id  

        serializer = CourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Course created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "GET":
        # Return all courses for this vendor
        courses = Course.objects.filter(vendor=vendor)
        serializer = CourseSerializer(courses, many=True)
        return Response({
            "status": "success",
            "message": f"{courses.count()} course(s) found",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


#This API handles sales records — both retrieving form options and creating a sale.
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def create_sale_api(request):
    if request.method == "POST":
        # Ensure client_type exists before creating sale
        client_type_id = request.data.get("client_type")
        if not client_type_id:
            return Response({
                "status": "error",
                "message": "Client type is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            Client_Type.objects.get(id=client_type_id)
        except Client_Type.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Client type not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize and save
        serializer = CreateSaleSerializer(data=request.data)
        if serializer.is_valid():
            sale = serializer.save(user=request.user) # Link sale to logged-in user
            return Response({
                "status": "success",
                "message": "Sale created successfully",
                "data": CreateSaleSerializer(sale).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "GET":
        vendor_id = request.query_params.get("vendor_id")
        client_types = list(Client_Type.objects.all().values("id", "client_name"))
        vendors = list(Vendor.objects.all().values("id", "name"))
        sales_people = list(CustomUser.objects.filter(role_id__role='Sales Person'))
        sales_people_serialized = SalesPersonSerializer(sales_people, many=True).data


        courses_with_codes = []
        if vendor_id:
            courses_qs = Course.objects.filter(vendor_id=vendor_id)
            courses_with_codes = list(courses_qs.values("id", "course_description", "course_code"))

        return Response({
            "status": "success",
            "message": "Populaters fetched successfully",
            "populaters": {
                "client_types": client_types,
                "vendors": vendors,
                "courses": courses_with_codes,  # each item now has id, course_description, and course_code
                "sales_people": sales_people_serialized,
            }
        }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllowAny])
def request_client_type_api(request):
    try:
        client_types = list(Client_Type.objects.all().values("id", "client_name"))
        return Response({
            "status": "success",
            "message": "Client types fetched successfully",
            "data": client_types
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Something went wrong: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def cost_sheet_api(request, client_id):
    # POST: create a new CostSheet
    if request.method == "POST":
        try:
            # Check if a cost sheet already exists for this client type
            if CostSheet.objects.filter(client_type_id=client_id).exists():
                return Response({
                    "status": "error",
                    "message": "A cost sheet already exists for this client type."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Add client_type automatically to the serializer data
            data = request.data.copy()
            data["client_type"] = client_id

            serializer = CostSheetSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Cost sheet created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": "error",
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({
                "status": "error",
                "message": "A cost sheet already exists for this client type."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Something went wrong: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # GET: fetch all cost sheets for this client type
    elif request.method == "GET":
        try:
            sheets = CostSheet.objects.filter(client_type_id=client_id).order_by("-created_at")
            serializer = CostSheetSerializer(sheets, many=True)
            return Response({
                "status": "success",
                "message": "Cost sheets fetched successfully",
                "count": sheets.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Something went wrong: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only logged-in users can fetch
def sale_list_api(request):
    sales = Sale.objects.all().order_by('-date_of_application')
    serializer = SaleSerializer(sales, many=True)
    return Response({
        "status": "success",
        "message": "Sales fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)





@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def signup_api(request):
    if request.method == "POST":
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # CREATE TOKEN
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "status": "success",
                "message": "User created successfully",
                "data": SignupSerializer(user).data,
                "token": token.key  # return token in response
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)  
        return Response({
            "status": "success",
            "message": "Roles fetched successfully",
            "data": serializer.data  
        }, status=status.HTTP_200_OK)




@api_view(["POST"])
@permission_classes([AllowAny]) 
def approve_sale(request, sale_id):
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    if user.role == "Training Manager":
        sale.training_manager_approved = True
        sale.save()
        return Response({"message": "Training Manager approved the sale."}, status=200)


    return Response({"error": "You are not authorized to approve this sale."}, status=403)


@api_view(['GET'])
@permission_classes([AllowAny]) 
def cost_sheet_list_view_api(request):
    sheets = CostSheet.objects.all().order_by('-created_at')
    serializer = CostSheetViewSerializer(sheets, many=True)
    
    return Response({
        "status": "success",
        "message": "Cost sheets fetched successfully",
        "count": sheets.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def ceo_approval_cost_sheet_api(request, sheet_id=None):
    """
    GET: fetch a single cost sheet by sheet_id
    POST: approve/decline a cost sheet
    """

    # ========= GET =========
    if request.method == "GET":
        if not sheet_id:
            return Response({"error": "sheet_id required"}, status=400)

        try:
            sheet = CostSheet.objects.get(id=sheet_id)
            serializer = CostSheetSerializer(sheet)
            return Response({
                "status": "success",
                "data": serializer.data
            }, status=200)
        except CostSheet.DoesNotExist:
            return Response({"status": "error", "message": "Cost sheet not found"}, status=404)

    # ========= POST =========
    sheet_id = request.data.get("sheet_id")
    action = request.data.get("action")  # approve or decline

    if not sheet_id or action not in ["approve", "decline"]:
        return Response({"error": "Invalid data"}, status=400)

    sheet = get_object_or_404(CostSheet, id=sheet_id)
    sheet.is_approved = action == "approve"
    sheet.save()

    return Response({
        "status": "success",
        "sheet_id": sheet.id,
        "is_approved": sheet.is_approved
    })



@api_view(['GET'])
@permission_classes([AllowAny])
def pending_admins_api(request):
    users = CustomUser.objects.filter(is_approved=False, is_superuser=False)
    serializer = PendingAdminSerializer(users, many=True)
    return Response({
        "status": "success",
        "count": users.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def approve_admin_api(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id, is_superuser=False)
    except CustomUser.DoesNotExist:
        return Response({
            "status": "error",
            "message": "User not found or cannot be approved"
        }, status=status.HTTP_404_NOT_FOUND)

    user.is_approved = True
    user.save()

    return Response({
        "status": "success",
        "message": "User approved successfully"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_admin_api(request, user_id):
    """
    Decline a pending admin by deleting their account.
    """
    try:
        user = CustomUser.objects.get(id=user_id, is_superuser=False)
    except CustomUser.DoesNotExist:
        return Response({
            "status": "error",
            "message": "User not found or cannot be declined"
        }, status=status.HTTP_404_NOT_FOUND)

    user.delete()  # Delete the user
    return Response({
        "status": "success",
        "message": "User declined and deleted successfully"
    }, status=status.HTTP_200_OK)


from django.template.loader import render_to_string

@api_view(['POST','GET'])
@permission_classes([AllowAny])
def studio_api(request):

    if request.method == "POST":

        serializer = StudioSerializer(data=request.data)

        if serializer.is_valid():
            studio = serializer.save()

            # 🔥 GET IT PERSON
            it_person_id = request.data.get("it_person")

            if it_person_id:
                try:
                    it_user = CustomUser.objects.get(id=it_person_id)
                    domain = request.build_absolute_uri('/')[:-1]  # removes trailing /
                    # 🔥 USE TEMPLATE (NOT HARD CODE)
                    html_content = render_to_string(
                        'system_management/email_templates/studio_assignment.html',
                        {
                            'user': it_user,
                            'studio': studio,
                            'domain': domain
                        }
                    )

                    # 🔥 SEND EMAIL
                    send_welcome_email(
                        to_email=it_user.work_email,
                        subject="New Studio Assignment",
                        content=html_content
                    )

                except CustomUser.DoesNotExist:
                    pass

            return Response({
                "status": "success",
                "message": "Studio created and IT notified",
                "data": StudioSerializer(studio).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST','GET'])
@permission_classes([AllowAny])
def equipment_api(request):

    if request.method == "POST":

        serializer = EquipmentSerializer(data=request.data)

        if serializer.is_valid():
            equipment = serializer.save()

            return Response({
                "status": "success",
                "message": "Equipment created successfully",
                "data": EquipmentSerializer(equipment).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    if request.method == "GET":

        equipment = Equipment.objects.all()
        serializer = EquipmentSerializer(equipment, many=True)

        return Response({
            "status": "success",
            "message": "Equipment fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

@api_view(['POST','GET'])
@permission_classes([AllowAny])
def studio_equipment_api(request):

    if request.method == "POST":

        serializer = StudioEquipmentSerializer(data=request.data)

        if serializer.is_valid():
            studio_equipment = serializer.save()

            return Response({
                "status": "success",
                "message": "Equipment assigned to studio successfully",
                "data": StudioEquipmentSerializer(studio_equipment).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    if request.method == "GET":

        data = StudioEquipment.objects.all()
        serializer = StudioEquipmentSerializer(data, many=True)

        return Response({
            "status": "success",
            "message": "Studio equipment fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def studio_detail_api(request, studio_id):

    try:
        studio = Studio.objects.get(id=studio_id)
    except Studio.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Studio not found"
        }, status=404)

    equipment = StudioEquipment.objects.filter(studio=studio)

    return Response({
        "status": "success",
        "studio": StudioSerializer(studio).data,
        "equipment": StudioEquipmentSerializer(equipment, many=True).data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def it_users_api(request):
    try:
        it_role = Role.objects.get(role="IT")
        users = CustomUser.objects.filter(role=it_role)

        serializer = UserSerializer(users, many=True)

        return Response({
            "status": "success",
            "data": serializer.data
        })

    except Role.DoesNotExist:
        return Response({
            "status": "error",
            "message": "IT role not found"
        }, status=404)
    
    