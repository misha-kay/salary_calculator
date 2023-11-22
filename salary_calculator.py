import re

PT = 12576
LEL = 6240
UEL = 50270
NICUEL = 50268


def get_annual_salary():
    while True:
        annual_salary = input("What is your gross annual salary? £")
        try:
            if not annual_salary.isnumeric():
                raise ValueError(
                    "Please enter a valid number. Symbols and letters are not accepted."
                )
            return float(annual_salary)
        except ValueError as e:
            print(e)


def get_tax_code():
    while True:
        tax_code = input("What is your tax code? ").upper()
        valid_letters = ["K", "L", "M", "N", "T", "BR", "0T", "D0", "D1"]

        try:
            if not any(letter in tax_code for letter in valid_letters):
                raise ValueError("Please provide a valid tax code.")
            return tax_code
        except ValueError as e:
            print(e)


def get_student_loan_plan():
    while True:
        student_loan_plan = input(
            """
Please enter your student loan:\n
'1' for Plan 1
'2' for Plan 2
'4' for Plan 4
'5' for Plan 5
'6' for Postgraduate Loan
'0' if you don't have one
"""
        )
        valid_numbers = ["0", "1", "2", "3", "4", "5", "6"]
        try:
            if (
                student_loan_plan not in valid_numbers
                or not student_loan_plan.isdigit()
                or int(student_loan_plan) > 6
            ):
                raise ValueError(
                    "Please enter a valid single-digit number. Symbols and letters are not accepted."
                )
            return int(student_loan_plan)
        except ValueError as e:
            print(e)


def get_pension_type():
    while True:
        pension_type = input(
            """
Please enter your pension type:
'auto' for auto-enrolment
'sac' for salary sacrifice
'none' if you don't have one
"""
        ).lower()
        valid_answers = ["auto", "sac", "none"]
        try:
            if pension_type not in valid_answers:
                raise ValueError("Please enter a valid option from the list.")
            return pension_type
        except ValueError as e:
            print(e)


def get_pension_percentage():
    while True:
        pension_percentage = input("What is your pension percentage? ")
        try:
            if not pension_percentage.isnumeric():
                raise ValueError("Please enter a number (eg: 3% = '3')")
            return float(pension_percentage) / 100
        except ValueError as e:
            print(e)


def calculate_taxable_pay(tax_code, annual_salary):
    if tax_code == "D0":
        tax_rate = 0.40
    elif tax_code == "D1":
        tax_rate = 0.45
    else:
        tax_rate = 0.20

    # User not entitled to tax-free allowance - Taxed on full gross pay
    # REGX - Make tax code blank
    (tax_code_chars, count) = re.subn("BR|0T|D0|D1", "", tax_code, flags=re.IGNORECASE)
    # Set tax-free amount to zero
    tax_free = tax_code_chars + "0" * count

    # REGX - If user does not have one of the above taxcodes, user is entitled to tax-free allowance, so run the following:
    if count == 0:
        # Remove the letters below from the taxcode and replace with an empty character. Count how many times this was actioned
        (tax_code_digits, count) = re.subn(
            "K|L|M|N|T", "", tax_code, flags=re.IGNORECASE
        )
        # Add a zero to the end of the number to get tax-free amount
        tax_free = tax_code_digits + "0" * count
        tax_free = int(tax_free)
    if annual_salary < tax_free:
        return (0, 0)

    return (round(annual_salary - tax_free, 2), tax_rate)


def calculate_pension(
    pension_type, annual_gross_salary, pension_percentage, taxable_pay
):
    annual_pension, student_loan_salary = 0, 0
    if (
        pension_type == "auto"
        and annual_gross_salary >= LEL
        and annual_gross_salary < UEL
    ):
        annual_pensionable = annual_gross_salary - LEL
        annual_pension = annual_pensionable * pension_percentage
        # Adjustment for taxable pay and student loan
        taxable_pay -= annual_pension
        student_loan_salary = annual_gross_salary
    elif pension_type == "auto" and annual_gross_salary >= UEL:
        annual_pensionable = UEL - LEL
        annual_pension = annual_pensionable * pension_percentage
        # Adjustment for taxable pay and student loan
        taxable_pay -= annual_pension
        student_loan_salary = annual_gross_salary
    elif pension_type == "sac":
        annual_pension = annual_gross_salary * pension_percentage
        # Adjustment for taxable pay and student loan
        taxable_pay -= annual_pension
        student_loan_salary = annual_gross_salary - round(annual_pension, 2)
    else:
        print("Error: Could not calculate pension")

    return (round(annual_pension, 2), round(student_loan_salary, 2))


def calculate_NIC(gross_annual_salary, pension_type, taxable_pay, annual_pension):
    national_insurance = 0
    if (
        gross_annual_salary >= PT
        and gross_annual_salary < NICUEL
        and pension_type == "auto"
    ):
        national_insurance = ((gross_annual_salary - PT) * 0.12) / 12
    elif (
        gross_annual_salary >= PT
        and gross_annual_salary < NICUEL
        and pension_type == "sac"
    ):
        national_insurance = (taxable_pay * 0.12) / 12
    elif gross_annual_salary >= NICUEL:
        percent12 = (NICUEL - PT) * 0.12
        percent2 = gross_annual_salary - NICUEL * 0.02
        national_insurance = (percent12 + percent2) / 12
    else:
        print("Error: Could not calculate NICs")

    return round(national_insurance, 2)


def calculate_tax(taxable_pay, tax_rate, annual_pension):
    return round(((taxable_pay - annual_pension) * tax_rate) / 12, 2)


def calculate_student_loan(student_loan_plan, student_loan_salary):
    plan1_threshold = 22015
    plan2_threshold = 27295
    plan4_threshold = 27660
    plan5_threshold = 25000
    postgrad_threshold = 21000
    standard_rate = 0.09
    postgrad_rate = 0.06

    if student_loan_plan == 0:
        return 0
    elif student_loan_plan == 1 and student_loan_salary < plan1_threshold:
        return 0
    elif student_loan_plan == 1 and student_loan_salary >= plan1_threshold:
        return int((student_loan_salary - plan1_threshold) * standard_rate / 12)
    elif student_loan_plan == 2 and student_loan_salary < plan2_threshold:
        return 0
    elif student_loan_plan == 2 and student_loan_salary >= plan2_threshold:
        return int((student_loan_salary - plan2_threshold) * standard_rate / 12)
    elif student_loan_plan == 4 and student_loan_salary < plan4_threshold:
        return 0
    elif student_loan_plan == 4 and student_loan_salary >= plan4_threshold:
        return int((student_loan_salary - plan4_threshold) * standard_rate / 12)
    elif student_loan_plan == 5 and student_loan_salary < plan5_threshold:
        return 0
    elif student_loan_plan == 5 and student_loan_salary >= plan5_threshold:
        return int((student_loan_salary - plan5_threshold) * standard_rate / 12)
    elif student_loan_plan == 6 and student_loan_salary < postgrad_threshold:
        return 0
    elif student_loan_plan == 6 and student_loan_salary >= postgrad_threshold:
        return int((student_loan_salary - postgrad_threshold) * postgrad_rate / 12)
    else:
        print("Error: Could not calculate student loan repayment")
        return 0


def main():
    annual_gross = 0
    monthly_gross = 0
    tax_code = 0
    student_loan_plan = 0
    pension_type = 0
    pension_percentage = 0

    annual_gross = get_annual_salary()
    monthly_gross = annual_gross / 12
    tax_code = get_tax_code()
    student_loan_plan = get_student_loan_plan()
    pension_type = get_pension_type()
    if pension_type != "none":
        pension_percentage = get_pension_percentage()

    (taxable_pay, tax_rate) = calculate_taxable_pay(tax_code, annual_gross)

    (annual_pension, student_loan_salary) = calculate_pension(
        pension_type, annual_gross, pension_percentage, taxable_pay
    )

    national_insurance = calculate_NIC(
        annual_gross, pension_type, taxable_pay - annual_pension, annual_pension
    )

    tax = calculate_tax(taxable_pay, tax_rate, annual_pension)
    student_loan = calculate_student_loan(student_loan_plan, student_loan_salary)

    monthly_pension = annual_pension / 12

    net_pay = round(
        monthly_gross - tax - national_insurance - monthly_pension - student_loan, 2
    )

    print(
        f"""
    Your payslip this month should be as follows:\n
    Gross Pay:  £{round(monthly_gross,2)}\n
    Tax: £{abs(tax)}\n
    National Insurance: £{national_insurance}\n
    Pension: £{round(monthly_pension,2)}\n
    Student Loan: £{student_loan}\n
    Net Pay: £{net_pay}\n\n
    Therefore, your take home pay is £{net_pay}\n
    """
    )


main()
