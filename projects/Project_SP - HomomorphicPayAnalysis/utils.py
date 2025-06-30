import base64
import os
import tenseal

PRIVATE_KEY_FILENAME = "private_key"
PUBLIC_KEY_FILENAME = "public_key"


def write_data(data: bytes, filename: str):
    data = base64.b64encode(data)

    filepath = "files/" + filename
    if not os.path.exists("files"):
        os.makedirs("files")

    with open(filepath, "wb") as file:
        file.write(data)


def read_data(filename: str) -> bytes:
    filepath = "files/" + filename
    if not os.path.exists("files"):
        os.makedirs("files")
    
    with open(filepath, "rb") as file:
        data = file.read()

    return base64.b64decode(data)


def load_context_secret():
    return tenseal.context_from(read_data(PRIVATE_KEY_FILENAME))


def load_context_public():
    return tenseal.context_from(read_data(PUBLIC_KEY_FILENAME))


def pack_cts(*cts):
    chunks = []
    for ct in cts:
        ct_serialized = ct.serialize()
        chunks.append(len(ct_serialized).to_bytes(4, "little"))
        chunks.append(ct_serialized)
    
    return b"".join(chunks)


def main():
    if os.path.exists("files/" + PRIVATE_KEY_FILENAME) and os.path.exists("files/" + PUBLIC_KEY_FILENAME):
        print("Private and public keys already exist.")
    
    else:
        print("Generating keys...")

        context = tenseal.context(
            tenseal.SCHEME_TYPE.CKKS,
            poly_modulus_degree=16384,
            coeff_mod_bit_sizes=[60, 50, 40, 40, 40, 40, 40, 60]
        )

        context.generate_galois_keys()
        context.generate_relin_keys()
        context.global_scale = 2**40
        
        secret_context = context.serialize(save_secret_key=True)
        write_data(secret_context, PRIVATE_KEY_FILENAME)
        print("Private key created and saved.")
        
        context.make_context_public()
        public_context = context.serialize()
        write_data(public_context, PUBLIC_KEY_FILENAME)
        print("Public key created and saved.")


if __name__ == "__main__":
    main()