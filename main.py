from salary_calculator import calculate, get_input, print_output


def main():
    (
        annual_gross,
        monthly_gross,
        tax_code,
        student_loan_plan,
        pension_percentage,
        pension_type,
    ) = get_input()

    (
        monthly_gross,
        tax,
        national_insurance,
        student_loan,
        monthly_pension,
        net_pay,
    ) = calculate(
        annual_gross,
        monthly_gross,
        tax_code,
        student_loan_plan,
        pension_percentage,
        pension_type,
    )

    print_output(
        monthly_gross, tax, national_insurance, student_loan, monthly_pension, net_pay
    )


main()
