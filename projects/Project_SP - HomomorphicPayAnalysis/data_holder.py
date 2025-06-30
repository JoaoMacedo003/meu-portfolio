import argparse
import tenseal
import pandas as pd
from utils import *


def encrypt(dataset, filename):
    context = load_context_secret()
    encrypted_data = tenseal.ckks_vector(context, dataset)
    write_data(encrypted_data.serialize(), filename)


def decrypt(filename):
    context = load_context_secret()
    enc_proto = read_data(filename)

    offset = 0
    vals = []
    for _ in range(4):
        length = int.from_bytes(enc_proto[offset:offset + 4], "little")
        offset += 4
        ct_serialized = enc_proto[offset:offset + length]
        offset += length
        ct = tenseal.ckks_vector_from(context, ct_serialized)
        vals.append(ct.decrypt()[0])

    mean_m, mean_f, gap, gap_pct = vals
    print(f"Média M         = {mean_m:.2f}")
    print(f"Média F         = {mean_f:.2f}")
    print(f"Gap             = {gap:.2f}")
    print(f"Percentage gap  = {gap_pct:.2f} %")



def excel_to_salary_lists(filename):
    df = pd.read_excel(filename)

    male   = df.loc[df['Gender'] == 'M', 'Base Salary/Year ($)'].astype(float).tolist()
    female = df.loc[df['Gender'] == 'F', 'Base Salary/Year ($)'].astype(float).tolist()

    return male, female


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        choices=["encrypt", "decrypt"],
                        default="encrypt",
                        help="Executar apenas encrypt ou apenas decrypt.")
    args = parser.parse_args()

    if args.mode in ("encrypt"):
        male, female = excel_to_salary_lists("dataset.xlsx")
        print("Encrypting male data...")
        encrypt(male, "encrypted_male_data")

        print("Encrypting female data...")
        encrypt(female, "encrypted_female_data")

    elif args.mode in ("decrypt"):
        print("Decrypting results...")
        decrypt("statistics")