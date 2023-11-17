import re

# -------------- USER INPUT CONTROL -------------- #

annualSalary = float(input("What is your gross annual salary? £"))
taxCode = input("What is your tax code? ")
slPlan = int(
    input(
        "Please enter your student loan:\n'1' for Plan 1\n'2' for Plan 2\n'4' for Plan 4\n'5' for Plan 5\n'6' for Postgraduate Loan\n'0' if you don't have one\n"
    )
)
pensionType = input(
    "Please enter your pension type:\n'auto' for auto-enrolment\n'sac' for salary sacrifice\n'none' if you don't have one\n"
).lower()
pensionPercentage = int(input("What is your pension payment percentage? "))

# -------------- GLOBAL CONSTS & VARIABLES -------------- #

grossPay = round(annualSalary / 12, 2)
taxRate = 0
slSalary = 0
pensionPercentageConverted = float(pensionPercentage / 100)
PT = 12576
LEL = 6240
UEL = 50270
NICUEL = 50268

# -------------- WORK OUT TAX-FREE ALLOWANCE -------------- #

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

taxablePay = annualSalary - int(taxFree)

# -------------- WORK OUT PENSION DUE -------------- #

if pensionType == "auto" and annualSalary >= LEL and annualSalary < UEL:
    annualPensionable = annualSalary - LEL
    annualPension = annualPensionable * pensionPercentageConverted
    pension = annualPension / 12
    # Adjustment for taxable pay and student loan
    taxablePay -= annualPension
    slSalary = annualSalary
    print(taxablePay)

elif pensionType == "auto" and annualSalary >= UEL:
    annualPensionable = UEL - LEL
    annualPension = annualPensionable * pensionPercentageConverted
    pension = annualPension / 12
    # Adjustment for taxable pay and student loan
    taxablePay -= annualPension
    slSalary = annualSalary
else:
    pension = 0
if pensionType == "sac":
    annualPension = annualSalary * pensionPercentageConverted
    # Adjustment for taxable pay and student loan
    taxablePay -= annualPension
    pension = annualPension / 12
    slSalary = annualSalary - annualPension

pension = round(pension, 2)

# -------------- WORK OUT NICs DUE -------------- #

print(annualSalary, pensionType, taxablePay)

if annualSalary >= PT and annualSalary < NICUEL and pensionType == "auto":
    nationalInsurance = (taxablePay + annualPension) * 0.12 / 12
elif annualSalary >= PT and annualSalary < NICUEL and pensionType == "sac":
    nationalInsurance = (taxablePay) * 0.12 / 12
elif annualSalary >= NICUEL:
    perc12 = (NICUEL - PT) * 0.12
    perc2 = (annualSalary - NICUEL) * 0.02
    nationalInsurance = (perc12 + perc2) / 12

print(taxablePay)
nationalInsurance = round(nationalInsurance, 2)

# -------------- WORK OUT TAX DUE -------------- #

tax = round((taxablePay * taxRate) / 12, 2)

# -------------- WORK OUT STUDENT LOAN DUE -------------- #

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

studentLoan = int(studentLoan)

# -------------- WORK OUT NET PAY -------------- #

netPay = round(grossPay - tax - nationalInsurance - pension - studentLoan, 2)

print(
    f"Your payslip this month should be as follows:\nGross Pay:  £{grossPay}\nTax: £{tax}\nNational Insurance: £{nationalInsurance}\nPension: £{pension}\nStudent Loan: £{studentLoan}\nNet Pay: £{netPay}\n\nTherefore, your take home pay is £{netPay}\n"
)
