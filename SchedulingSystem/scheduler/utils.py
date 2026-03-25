from django.conf import settings

def host_url(request):
    """Returns the base URL of the current Django instance."""
    scheme = request.scheme  # Get 'http' or 'https'
    host = request.get_host()  # Get '127.0.0.1:8000' or domain name
    return f"{scheme}://{host}"

CLIENT_FIELD_MAP = {
    
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

    # keep the rest EXACTLY as you already have
}
