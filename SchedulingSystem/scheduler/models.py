from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission



class Role(models.Model):
    role = models.CharField(max_length=100)
    def __str__(self):
        return self.role



class Client_Type(models.Model):
    client_name = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.client_name
    
    
class CostSheet(models.Model):
    instructor_cost = models.FloatField(default=0.0)
    client_type = models.ForeignKey(
    Client_Type,
    on_delete=models.CASCADE,
    related_name="cost_sheets"
    )

    courseware = models.FloatField(default=0.0)
    exam = models.FloatField(default=0.0)
    lab_fees = models.FloatField(default=0.0)
    lms_license = models.FloatField(default=0.0)
    data = models.FloatField(default=0.0)
    project_man_fee = models.FloatField(default=0.0)
    corporate_cost_content_dev = models.FloatField(default=0.0)
    admin_cost = models.FloatField(default=0.0)
    set_up_fee = models.FloatField(default=0.0)
    license_fee = models.FloatField(default=0.0)
    per_user_fee = models.FloatField(default=0.0)
    consulting = models.FloatField(default=0.0)
    analysis = models.FloatField(default=0.0)
    design = models.FloatField(default=0.0)
    development = models.FloatField(default=0.0)
    implementation = models.FloatField(default=0.0)
    evaluation = models.FloatField(default=0.0)
    e_learning_courseware = models.FloatField(default=0.0)
    daily_venue_cost = models.FloatField(default=0.0)
    refreshment = models.FloatField(default=0.0)
    consumables = models.FloatField(default=0.0)
    corporate_costs_content_dev = models.FloatField(default=0.0)
    qcto_seta_consumables = models.FloatField(default=0.0)
    assessor_fees = models.FloatField(default=0.0)
    sme_hour = models.FloatField(default=0.0)
    recruitment = models.FloatField(default=0.0)
    labs = models.FloatField(default=0.0)
    welcome_packs = models.FloatField(default=0.0)
    travel_flights = models.FloatField(default=0.0)
    accomodation = models.FloatField(default=0.0)
    per_diem = models.FloatField(default=0.0)
    international = models.FloatField(default=0.0)
    driving_travel = models.FloatField(default=0.0)
    marketing_fee = models.FloatField(default=0.0)
    total_cost = models.FloatField(default=0.0)
    # per_learner = models.IntegerField(default=0)
    # days = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)


    def __str__(self):
        return f"CostSheet for {self.client_type.client_name if self.client_type else 'Unknown'}"

    
class CustomUserManager(BaseUserManager):
    def create_user(self, work_email, password=None, **extra_fields):
        if not work_email:
            raise ValueError('Users must have an email address')
        work_email = self.normalize_email(work_email)
        user = self.model(work_email=work_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, work_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if 'role' not in extra_fields:
            role, _ = Role.objects.get_or_create(role='admin')
            extra_fields['role'] = role

        return self.create_user(work_email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    work_email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    join_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    # Avoid clashes with default User
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'work_email'   # 🔑 MUST match your actual field
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.work_email

class Vendor(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Sale(models.Model):
    # Existing fields ...
    date_of_application = models.DateField(auto_now_add=True)  
    sales_person = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    client_type = models.ForeignKey('Client_Type', on_delete=models.SET_NULL, null=True, blank=True)
    training_location = models.CharField(max_length=250, null=True, blank=True)
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    course_code = models.CharField(max_length=50, null=True, blank=True)
    class_type = models.CharField(max_length=50, null=True, blank=True)
    number_of_students = models.PositiveIntegerField(null=True, blank=True)
    training_name = models.CharField(max_length=100, null=True, blank=True)
    proposed_date = models.DateField(null=True, blank=True)
    training_end_date = models.CharField(max_length=100, null=True, blank=True)
    sales_pack_uploaded = models.BooleanField(default=False)
    existing_account = models.BooleanField(default=False)
    confirmed_training = models.BooleanField(default=False)
    proof_of_payment = models.BooleanField(default=False)
    accepted_pricing = models.BooleanField(default=False)
    order_purchased = models.CharField(max_length=50, null=True, blank=True)
    pricing_approved_by = models.CharField(max_length=50, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_training_scheduled = models.BooleanField(default=False)
    proposed_date_alternative = models.DateField(null=True, blank=True)
    dietary_option = models.CharField(max_length=100, blank=True, null=True)
    specify = models.CharField(max_length=100, blank=True, null=True)
    gp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    # New approval workflow
    training_manager_approved = models.BooleanField(default=False)
    trainer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_trained')
    notes = models.TextField(null=True, blank=True)


    status = models.CharField(max_length=50, choices=[
        ("pending", "Pending"),
        ("partially_approved", "Partially Approved"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="pending")

    def update_status(self):
        """Auto update status based on approvals."""
        if self.training_manager_approved :
            self.status = "approved"
            
        else:
            self.status = "pending"
        self.save()

    def __str__(self):
        return f"{self.company} - {self.date_of_application}"

    
class Course(models.Model):
    course_code = models.CharField(max_length=100, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    course_description = models.CharField(max_length=100, null=True, blank=True)
    exam = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('vendor', 'course_code')


class Approval(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cost_sheet = models.ForeignKey(CostSheet, on_delete=models.SET_NULL, null=True, blank=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)   # Role of approver (e.g., Manager, Admin)
    status = models.CharField(max_length=50, choices=[   # Approval status
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Approval {self.date} - {self.status}"


class Studio(models.Model):
    it_person = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name
    
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
class StudioEquipment(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name="studio_equipment")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.studio.name} - {self.equipment.name} ({self.quantity})"

