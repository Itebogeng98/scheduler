# serializers.py
from rest_framework import serializers
from scheduler.models import Vendor, Course,Sale,CostSheet,CustomUser, Role, Studio, Equipment, StudioEquipment


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"   # or ["id", "name", "user", "is_active"]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class CreateSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['id', 'date_of_application', 'user']


class CostSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostSheet
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        client_type_id = kwargs.pop('client_type_id', None)
        super().__init__(*args, **kwargs)

        # Define allowed fields per client type (cleaned up)
        client_field_map = {
            1: [
                "instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data",
                "project_man_fee", "corporate_cost_content_dev", "admin_cost", "set_up_fee",
                "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware"
            ],
            2: [
                "instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data",
                "project_man_fee", "corporate_cost_content_dev", "admin_cost", "set_up_fee",
                "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware",
                "daily_venue_cost", "refreshment", "consumables"
            ],
            3: [
                "instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data",
                "project_man_fee", "daily_venue_cost", "refreshment", "consumables",
                "qcto_seta_consumables", "assessor_fees", "sme_hour", "labs", "welcome_packs",
                "set_up_fee", "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware"
            ],
            4: [
                "instructor_cost", "courseware", "exam", "lab_fees", "lms_license", "data",
                "project_man_fee", "daily_venue_cost", "refreshment", "consumables",
                "qcto_seta_consumables", "assessor_fees", "sme_hour", "labs", "welcome_packs",
                "set_up_fee", "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware", "recruitment"
            ],
            5: [
                "instructor_cost", "exam", "lab_fees", "consumables", "sme_hour",
                "travel_flights", "accomodation", "per_diem", "international", "driving_travel",
                "set_up_fee", "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware"
            ],
            6: [
                "instructor_cost", "exam", "lab_fees", "total_cost",
                "set_up_fee", "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware", "marketing_fee"
            ],
            7: [
                "instructor_cost", "exam", "lab_fees", "daily_venue_cost", "refreshment", "consumables",
                "set_up_fee", "license_fee", "per_user_fee", "consulting", "analysis", "design",
                "development", "implementation", "evaluation", "e_learning_courseware", "marketing_fee"
            ],
        }

        # Always keep these base fields
        always_keep = ['id', 'client_type', 'created_at', 'updated_at', 'total_cost']

        if client_type_id:
            allowed_fields = client_field_map.get(client_type_id, [])
            for field_name in list(self.fields):
                if field_name not in allowed_fields and field_name not in always_keep:
                    self.fields.pop(field_name)

        # Debugging log to confirm field list (optional)
        # print("✅ Final serializer fields:", list(self.fields.keys()))

class SaleSerializer(serializers.ModelSerializer):
    client_type_name = serializers.CharField(source='client_type.client_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'


# serializers.py


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'work_email', 'first_name', 'last_name', 'phone_number', 'role', 'password']

    def validate_work_email(self, value):
        allowed_domains = ["netcampus.com", "netcampus.co.za"]

        domain = value.split("@")[-1]
        if domain not in allowed_domains:
            raise serializers.ValidationError(
                "Only Netcampus staff emails are allowed (must end with @netcampus.com or @netcampus.co.za)."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'role']   # return role id and name




class CostSheetViewSerializer(serializers.ModelSerializer):
    # Replace the numeric ID with the actual client name
    client_type = serializers.CharField(source='client_type.client_name', read_only=True)

    class Meta:
        model = CostSheet
        fields = '__all__'

class SalesPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'work_email']


class PendingAdminSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.role', read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'work_email', 'role', 'is_approved']

class EquipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipment
        fields = "__all__"

class StudioEquipmentSerializer(serializers.ModelSerializer):

    equipment_name = serializers.CharField(source="equipment.name", read_only=True)

    class Meta:
        model = StudioEquipment
        fields = "__all__"


class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = '__all__'

    def validate_it_person(self, value):
        if value and value.role.role != "IT":
            raise serializers.ValidationError("Selected user is not an IT person.")
        return value
    

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)  # 🔥 nested role
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'work_email',
            'first_name',
            'last_name',
            'phone_number',
            'role',      # 🔥 for GET (readable)
            'role_id',   # 🔥 for POST
        ]