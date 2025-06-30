import tenseal
from utils import *

def main():
    print("Calculating statistics...")

    context = load_context_public()
    
    male_salary_proto = read_data("encrypted_male_data")
    male_salary_encrypted = tenseal.ckks_vector_from(context, male_salary_proto)
    male_salary_sum_encrypted = male_salary_encrypted.sum()
    n_male = 1 / male_salary_encrypted.size()


    female_salary_proto = read_data("encrypted_female_data")
    female_salary_encrypted = tenseal.ckks_vector_from(context, female_salary_proto)
    female_salary_sum_encrypted = female_salary_encrypted.sum()
    n_female = 1 / female_salary_encrypted.size()


    average_male_salary = male_salary_sum_encrypted * n_male
    average_female_salary = female_salary_sum_encrypted * n_female


    gap = average_male_salary - average_female_salary

    inv_guess = 1.0 / 100_000.0  
    inv_average_female_salary = inv_guess * (2.0 - average_female_salary * inv_guess)
    gap_percentage = gap * inv_average_female_salary * 100.0
    
    print("Writing statistics to file...")
    payload = pack_cts(average_male_salary, average_female_salary, gap, gap_percentage)
    write_data(payload, "statistics")


if __name__ == "__main__":
    main()