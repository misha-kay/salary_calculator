import re, math

RATES_AND_ALLOWANCES = {
    "PT": 12576,
    "PA": 12570,
    "LEL": 6240,
    "UEL": 50270,
    "UEL_MINUS_PA": 37700,
    "ADDITIONAL_RATE": 125140,
    "NICUEL": 50268,
}

STUDENT_LOAN_PLAN_THRESHOLDS = {
    "PLAN1": 22015,
    "PLAN2": 27295,
    "PLAN4": 27660,
    "PLAN5": 25000,
    "POSTGRAD": 21000,
}

STUDENT_LOAN_RATES = {
    "STANDARD": 0.09,
    "POSTGRAD": 0.06,
}


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
        valid_numbers = ["0", "1", "2", "4", "5", "6"]
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
    count = 0

    # User not entitled to tax-free allowance - Taxed on full gross pay
    # REGX - Make tax code blank
    if len(tax_code) == 2:
        (tax_code_chars, count) = re.subn(
            "BR|D0|0T|D1", "", tax_code, flags=re.IGNORECASE
        )
        # Set tax-free amount to zero
        tax_free = int(tax_code_chars + "0" * count)
        if count < 1:
            print("Invalid tax code. Please try again")
            quit()

    # REGX - If user does not have one of the above taxcodes, user is entitled to tax-free allowance, so run the following:
    elif count == 0:
        # Remove the letters below from the taxcode and replace with an empty character. Count how many times this was actioned
        (tax_code_chars, count) = re.subn(
            "K|L|M|N|T", "", tax_code, flags=re.IGNORECASE
        )
        # Add a zero to the end of the number to get tax-free amount
        tax_free = int(tax_code_chars + "0" * count)

    if annual_salary < tax_free:
        return (0, tax_code)

    # If K tax code, user has underpaid tax. Tax-free amount to be added to annual salary to adjust
    if "K" in tax_code:
        return (annual_salary + tax_free, tax_code)

    return (annual_salary - tax_free, tax_code)


def calculate_pension(
    pension_type, annual_gross_salary, pension_percentage, taxable_pay
):
    annual_pension, student_loan_salary = 0, 0
    if (
        pension_type == "auto"
        and annual_gross_salary >= RATES_AND_ALLOWANCES["LEL"]
        and annual_gross_salary < RATES_AND_ALLOWANCES["UEL"]
    ):
        annual_pensionable = annual_gross_salary - RATES_AND_ALLOWANCES["LEL"]
        annual_pension = annual_pensionable * pension_percentage
        # Adjustment for taxable pay and student loan
        taxable_pay -= annual_pension
        student_loan_salary = annual_gross_salary

    elif pension_type == "auto" and annual_gross_salary >= RATES_AND_ALLOWANCES["UEL"]:
        annual_pensionable = RATES_AND_ALLOWANCES["UEL"] - RATES_AND_ALLOWANCES["LEL"]
        annual_pension = annual_pensionable * pension_percentage
        # Adjustment for taxable pay and student loan
        taxable_pay -= annual_pension
        student_loan_salary = annual_gross_salary

    elif pension_type == "sac":
        annual_pension = annual_gross_salary * pension_percentage
        # Adjustment for taxable pay and student loan
        taxable_pay -= annual_pension
        student_loan_salary = annual_gross_salary - annual_pension

    elif pension_type == "none":
        annual_pension = 0
        student_loan_salary = annual_gross_salary

    else:
        print("Error: Could not calculate pension")
        quit()

    return (taxable_pay, annual_pension, student_loan_salary)


def calculate_NIC(gross_annual_salary, pension_type, annual_pension):
    unrounded_national_insurance = 0
    if (
        gross_annual_salary >= RATES_AND_ALLOWANCES["PT"]
        and gross_annual_salary < RATES_AND_ALLOWANCES["NICUEL"]
        and (pension_type == "auto" or pension_type == "none")
    ):
        unrounded_national_insurance = (
            (gross_annual_salary - RATES_AND_ALLOWANCES["PT"]) * 0.12
        ) / 12

    elif (
        gross_annual_salary >= RATES_AND_ALLOWANCES["PT"]
        and gross_annual_salary >= RATES_AND_ALLOWANCES["NICUEL"]
        and (pension_type == "auto" or pension_type == "none")
    ):
        percent12 = (RATES_AND_ALLOWANCES["NICUEL"] - RATES_AND_ALLOWANCES["PT"]) * 0.12
        percent2 = (gross_annual_salary - RATES_AND_ALLOWANCES["NICUEL"]) * 0.02
        unrounded_national_insurance = (percent12 + percent2) / 12

    elif (
        gross_annual_salary >= RATES_AND_ALLOWANCES["PT"]
        and gross_annual_salary < RATES_AND_ALLOWANCES["NICUEL"]
        and pension_type == "sac"
    ):
        unrounded_national_insurance = (
            (gross_annual_salary - annual_pension - RATES_AND_ALLOWANCES["PT"]) * 0.12
        ) / 12

    elif (
        gross_annual_salary >= RATES_AND_ALLOWANCES["PT"]
        and gross_annual_salary >= RATES_AND_ALLOWANCES["NICUEL"]
        and pension_type == "sac"
    ):
        percent12 = (RATES_AND_ALLOWANCES["NICUEL"] - RATES_AND_ALLOWANCES["PT"]) * 0.12
        percent2 = (
            gross_annual_salary - annual_pension - RATES_AND_ALLOWANCES["NICUEL"]
        ) * 0.02
        unrounded_national_insurance = (percent12 + percent2) / 12

    elif gross_annual_salary <= RATES_AND_ALLOWANCES["PT"]:
        return 0

    else:
        print("Error: Could not calculate NI contributions")
        quit()

    return math.ceil(unrounded_national_insurance * 10) / 10


def calculate_tax(taxable_pay, annual_salary, tax_code):
    if taxable_pay <= 0:
        return 0

    if "K" in tax_code:
        # 20% tax
        if taxable_pay <= RATES_AND_ALLOWANCES["UEL_MINUS_PA"]:
            return (taxable_pay * 0.20) / 12
        # 40% tax
        if (
            taxable_pay > RATES_AND_ALLOWANCES["UEL_MINUS_PA"]
            and taxable_pay <= RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]
        ):
            tax_at_20_perc = (
                (RATES_AND_ALLOWANCES["UEL"] - RATES_AND_ALLOWANCES["PA"]) * 0.20
            ) / 12
            tax_at_40_perc = (
                (taxable_pay - RATES_AND_ALLOWANCES["UEL_MINUS_PA"]) * 0.4
            ) / 12
            return tax_at_20_perc + tax_at_40_perc
        # 45% tax
        tax_at_20_perc = (
            (RATES_AND_ALLOWANCES["UEL"] - RATES_AND_ALLOWANCES["PA"]) * 0.20
        ) / 12
        tax_at_40_perc = (
            (
                RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]
                - RATES_AND_ALLOWANCES["UEL_MINUS_PA"]
            )
            * 0.4
        ) / 12
        tax_at_45_perc = (
            (taxable_pay - RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]) * 0.45
        ) / 12
        return tax_at_20_perc + tax_at_40_perc + tax_at_45_perc

    if tax_code == "BR":
        return (taxable_pay * 0.20) / 12

    if tax_code == "D0":
        return (taxable_pay * 0.40) / 12

    if tax_code == "D1":
        return (taxable_pay * 0.45) / 12

    # 20% tax
    if annual_salary <= RATES_AND_ALLOWANCES["UEL"]:
        return (taxable_pay * 0.20) / 12

    # 40% tax
    if (
        annual_salary > RATES_AND_ALLOWANCES["UEL"]
        and annual_salary <= RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]
    ):
        if taxable_pay >= RATES_AND_ALLOWANCES["UEL"]:
            tax_at_20_perc = (
                (RATES_AND_ALLOWANCES["UEL"] - RATES_AND_ALLOWANCES["PA"]) * 0.20
            ) / 12
            tax_at_40_perc = (
                (taxable_pay - RATES_AND_ALLOWANCES["UEL_MINUS_PA"]) * 0.40
            ) / 12
            return tax_at_20_perc + tax_at_40_perc
        # Else, 20% tax
        return (taxable_pay * 0.20) / 12

    # 45% tax
    if taxable_pay >= RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]:
        tax_at_20_perc = (
            (RATES_AND_ALLOWANCES["UEL"] - RATES_AND_ALLOWANCES["PA"]) * 0.2
        ) / 12
        tax_at_40_perc = (
            (
                RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]
                - RATES_AND_ALLOWANCES["UEL_MINUS_PA"]
            )
            * 0.4
        ) / 12
        tax_at_45_perc = (
            (taxable_pay - RATES_AND_ALLOWANCES["ADDITIONAL_RATE"]) * 0.45
        ) / 12
        return tax_at_20_perc + tax_at_40_perc + tax_at_45_perc
    # Else, 40% tax
    tax_at_20_perc = (
        (RATES_AND_ALLOWANCES["UEL"] - RATES_AND_ALLOWANCES["PA"]) * 0.2
    ) / 12
    tax_at_40_perc = ((taxable_pay - RATES_AND_ALLOWANCES["UEL_MINUS_PA"]) * 0.4) / 12
    return tax_at_20_perc + tax_at_40_perc


def calculate_student_loan(student_loan_plan, student_loan_salary):
    if (
        student_loan_plan == 1
        and student_loan_salary >= STUDENT_LOAN_PLAN_THRESHOLDS["PLAN1"]
    ):
        return int(
            (student_loan_salary - STUDENT_LOAN_PLAN_THRESHOLDS["PLAN1"])
            * STUDENT_LOAN_RATES["STANDARD"]
            / 12
        )
    if (
        student_loan_plan == 2
        and student_loan_salary >= STUDENT_LOAN_PLAN_THRESHOLDS["PLAN2"]
    ):
        return int(
            (student_loan_salary - STUDENT_LOAN_PLAN_THRESHOLDS["PLAN2"])
            * STUDENT_LOAN_RATES["STANDARD"]
            / 12
        )
    if (
        student_loan_plan == 4
        and student_loan_salary >= STUDENT_LOAN_PLAN_THRESHOLDS["PLAN4"]
    ):
        return int(
            (student_loan_salary - STUDENT_LOAN_PLAN_THRESHOLDS["PLAN4"])
            * STUDENT_LOAN_RATES["STANDARD"]
            / 12
        )
    if (
        student_loan_plan == 5
        and student_loan_salary >= STUDENT_LOAN_PLAN_THRESHOLDS["PLAN5"]
    ):
        return int(
            (student_loan_salary - STUDENT_LOAN_PLAN_THRESHOLDS["PLAN5"])
            * STUDENT_LOAN_RATES["STANDARD"]
            / 12
        )
    if (
        student_loan_plan == 6
        and student_loan_salary >= STUDENT_LOAN_PLAN_THRESHOLDS["POSTGRAD"]
    ):
        return int(
            (student_loan_salary - STUDENT_LOAN_PLAN_THRESHOLDS["POSTGRAD"])
            * STUDENT_LOAN_RATES["POSTGRAD"]
            / 12
        )

    return 0


def get_input():
    annual_gross = get_annual_salary()
    monthly_gross = annual_gross / 12
    tax_code = get_tax_code()
    student_loan_plan = get_student_loan_plan()
    pension_type = get_pension_type()

    pension_percentage = 0
    if pension_type != "none":
        pension_percentage = get_pension_percentage()

    return (
        annual_gross,
        monthly_gross,
        tax_code,
        student_loan_plan,
        pension_percentage,
        pension_type,
    )


def calculate(
    annual_gross,
    monthly_gross,
    tax_code,
    student_loan_plan,
    pension_percentage,
    pension_type,
):
    (taxable_pay, tax_code) = calculate_taxable_pay(tax_code, annual_gross)
    (taxable_pay, annual_pension, student_loan_salary) = calculate_pension(
        pension_type, annual_gross, pension_percentage, taxable_pay
    )

    national_insurance = calculate_NIC(annual_gross, pension_type, annual_pension)

    tax = calculate_tax(taxable_pay, annual_gross, tax_code)
    student_loan = calculate_student_loan(student_loan_plan, student_loan_salary)

    monthly_pension = round(annual_pension / 12, 2)

    net_pay = round(
        monthly_gross - tax - national_insurance - monthly_pension - student_loan, 2
    )

    return (
        round(monthly_gross, 2),
        round(tax, 2),
        round(national_insurance, 2),
        round(student_loan, 2),
        round(monthly_pension, 2),
        round(net_pay, 2),
    )


def print_output(
    monthly_gross, tax, national_insurance, student_loan, monthly_pension, net_pay
):
    print(
        f"""
    Your payslip this month should be as follows:\n
    Gross Pay:  £{monthly_gross:.2f}
    Tax: £{abs(tax):.2f}
    National Insurance: £{national_insurance:.2f}
    Student Loan: £{student_loan:.2f}
    Pension: £{monthly_pension:.2f}
    Net Pay: £{net_pay:.2f}\n
    Therefore, your take home pay is £{net_pay:.2f}
    """
    )
