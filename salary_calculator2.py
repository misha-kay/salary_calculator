import re

PT = 12576
LEL = 6240
UEL = 50270
NICUEL = 50268


def getUserInput():
    annualGross = float(input("What is your gross annual salary? £"))
    taxCode = input("What is your tax code? ")
    slPlan = int(
        input(
            """
        Please enter your student loan:\n
        '1' for Plan 1\n
        '2' for Plan 2\n
        '4' for Plan 4\n
        '5' for Plan 5\n
        '6' for Postgraduate Loan\n
        '0' if you don't have one\n
        """
        )
    )
    pensionType = input(
        """
    Please enter your pension type:\n
    'auto' for auto-enrolment\n
    'sac' for salary sacrifice\n
    'none' if you don't have one\n
    """
    ).lower()
    pensionPercentage = int(input("What is your pension payment percentage? "))

    return (
        annualGross,
        annualGross / 12,
        taxCode,
        slPlan,
        pensionType,
        float(pensionPercentage / 100),
    )


def calculateTaxablePay(taxCode, annualSalary):
    if taxCode == "D0":
        taxRate = 0.40
    elif taxCode == "D1":
        taxRate = 0.45
    else:
        taxRate = 0.20

    # User not entitled to tax-free allowance - Taxed on full gross pay
    # Make tax code blank
    (taxCodeChars, count) = re.subn("BR|0T|D0|D1", "", taxCode, flags=re.IGNORECASE)
    # Set tax-free amount to zero
    taxFree = taxCodeChars + "0" * count

    # If user does not have one of the above taxcodes, user is entitled to tax-free allowance, so run the following:
    if count == 0:
        # Remove the letters below from the taxcode and replace with an empty character. Count how many times this was actioned
        (taxCodeDigits, count) = re.subn("K|L|M|N|T", "", taxCode, flags=re.IGNORECASE)
        # Add a zero to the end of the number to get tax-free amount
        taxFree = taxCodeDigits + "0" * count

    # Check for invalid taxcodes
    if taxCode == taxFree:
        print("Invalid taxcode")

    return (round(annualSalary - int(taxFree), 2), taxRate)


def calculatePension(pensionType, annualGrossSalary, pensionPercentage, taxablePay):
    annualPension, slSalary = 0, 0

    if pensionType == "auto" and annualGrossSalary >= LEL and annualGrossSalary < UEL:
        annualPensionable = annualGrossSalary - LEL
        annualPension = annualPensionable * pensionPercentage
        # Adjustment for taxable pay and student loan
        taxablePay -= annualPension
        slSalary = annualGrossSalary
    elif pensionType == "auto" and annualGrossSalary >= UEL:
        annualPensionable = UEL - LEL
        annualPension = annualPensionable * pensionPercentage
        # Adjustment for taxable pay and student loan
        taxablePay -= annualPension
        slSalary = annualGrossSalary
    elif pensionType == "sac":
        annualPension = annualGrossSalary * pensionPercentage
        # Adjustment for taxable pay and student loan
        taxablePay -= annualPension
        slSalary = annualGrossSalary - round(annualPension, 2)

    return (round(annualPension, 2), round(slSalary, 2))


def calculateNIC(grossAnnualSalary, pensionType, taxablePay, annualPension):
    if grossAnnualSalary >= PT and grossAnnualSalary < NICUEL and pensionType == "auto":
        nationalInsurance = (taxablePay + annualPension) * 0.12 / 12
    elif (
        grossAnnualSalary >= PT and grossAnnualSalary < NICUEL and pensionType == "sac"
    ):
        nationalInsurance = taxablePay * 0.12 / 12
    elif grossAnnualSalary >= NICUEL:
        perc12 = (NICUEL - PT) * 0.12
        perc2 = grossAnnualSalary - NICUEL * 0.02
        nationalInsurance = (perc12 + perc2) / 12

    return round(nationalInsurance, 2)


def calculateTax(taxablePay, taxRate, annualPension):
    return round((taxablePay - annualPension) * taxRate / 12, 2)


def calculateStudentLoan(slPlan, slSalary):
    if slPlan == 0:
        studentLoan = 0
    elif slPlan == 1 and slSalary < 22015:
        studentLoan = 0
    elif slPlan == 1 and slSalary >= 22015:
        studentLoan = (slSalary - 22015) * 0.09 / 12
    elif slPlan == 2 and slSalary < 27295:
        studentLoan = 0
    elif slPlan == 2 and slSalary >= 27295:
        studentLoan = (slSalary - 27295) * 0.09 / 12
    elif slPlan == 4 and slSalary < 27660:
        studentLoan = 0
    elif slPlan == 4 and slSalary >= 27660:
        studentLoan = (slSalary - 27660) * 0.09 / 12
    elif slPlan == 5 and slSalary < 25000:
        studentLoan = 0
    elif slPlan == 5 and slSalary >= 25000:
        studentLoan = (slSalary - 25000) * 0.09 / 12
    elif slPlan == 6 and slSalary < 21000:
        studentLoan = 0
    elif slPlan == 6 and slSalary >= 21000:
        studentLoan = (slSalary - 21000) * 0.06 / 12

    return int(studentLoan)


def main():
    (
        annualGross,
        monthlyGross,
        taxCode,
        slPlan,
        pensionType,
        pensionPercentage,
    ) = getUserInput()

    (taxablePay, taxRate) = calculateTaxablePay(taxCode, annualGross)

    (annualPension, slSalary) = calculatePension(
        pensionType, annualGross, pensionPercentage, taxablePay
    )

    nationalInsurance = calculateNIC(
        annualGross, pensionType, taxablePay - annualPension, annualPension
    )

    tax = calculateTax(taxablePay, taxRate, annualPension)
    studentLoan = calculateStudentLoan(slPlan, slSalary)

    monthlyPension = annualPension / 12

    netPay = round(
        monthlyGross - tax - nationalInsurance - monthlyPension - studentLoan, 2
    )

    print(
        f"""
    Your payslip this month should be as follows:\n
    Gross Pay:  £{monthlyGross}\n
    Tax: £{tax}\n
    National Insurance: £{nationalInsurance}\n
    Pension: £{monthlyPension}\n
    Student Loan: £{studentLoan}\n
    Net Pay: £{netPay}\n\n
    Therefore, your take home pay is £{netPay}\n
    """
    )


main()
