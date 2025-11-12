from decimal import Decimal, getcontext

getcontext().prec = 6  # optional: set precision for Decimal calculations

def calculate_sale_cost_and_revenue(costsheet, course, number_of_students):
    total_cost = Decimal(costsheet.total_cost or 0) * Decimal(number_of_students)
    course_total = Decimal(course.price or 0) * Decimal(number_of_students)
    revenue = course_total - total_cost
    return total_cost.quantize(Decimal("0.01")), revenue.quantize(Decimal("0.01"))



def calculate_sale_cost_revenue_gp(costsheet, course, number_of_students):
    """
    Calculates total cost, revenue, and GP% for a sale.
    total_cost = cost per student * number_of_students
    revenue = (course.price * number_of_students) - total_cost
    GP% = (revenue / (course.price * number_of_students)) * 100
    """
    if not costsheet or not course or not number_of_students:
        return Decimal("0.00"), Decimal("0.00"), Decimal("0.00")

    students = Decimal(number_of_students)
    total_cost = Decimal(costsheet.total_cost or 0) * students  # total cost for all students
    course_total = Decimal(course.price or 0) * students
    revenue = course_total - total_cost
    # Calculate GP%
    gp_percent = (revenue / course_total * Decimal("100.00")) if course_total > 0 else Decimal("0.00")
    return total_cost.quantize(Decimal("0.01")), revenue.quantize(Decimal("0.01")), gp_percent.quantize(Decimal("0.01"))
