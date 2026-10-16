import base64
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import oqs
import streamlit as st

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM




ROOT = Path(__file__).resolve().parent

RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="QuantumSafe Secure Channel",
    page_icon="🔐",
    layout="wide",
)




ALLOWED_KEMS = [
    "ML-KEM-512",
    "ML-KEM-768",
    "ML-KEM-1024",
]

ALLOWED_SIGNATURES = [
    "ML-DSA-44",
    "ML-DSA-65",
    "ML-DSA-87",
    "Falcon-512",
    "Falcon-1024",
]




st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b1020;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #111a2e;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #164e63);
        border: 1px solid #334155;
        margin-bottom: 20px;
    }

    .hero h1 {
        color: white;
        font-size: 36px;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background: #111a2e;
        padding: 14px;
        border: 1px solid #334155;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



try:
    enabled_kems = set(oqs.get_enabled_kem_mechanisms())
    enabled_signatures = set(oqs.get_enabled_sig_mechanisms())

    KEM_OPTIONS = [
        algorithm
        for algorithm in ALLOWED_KEMS
        if algorithm in enabled_kems
    ]

    SIGNATURE_OPTIONS = [
        algorithm
        for algorithm in ALLOWED_SIGNATURES
        if algorithm in enabled_signatures
    ]

except Exception as exc:
    st.error(f"Could not read liboqs algorithms: {exc}")
    st.stop()


if not KEM_OPTIONS:
    st.error(
        "None of the three ML-KEM algorithms is available "
        "in the current liboqs installation."
    )
    st.stop()

if not SIGNATURE_OPTIONS:
    st.error(
        "None of the selected ML-DSA or Falcon algorithms "
        "is available in the current liboqs installation."
    )
    st.stop()



if "key_cache" not in st.session_state:
    st.session_state.key_cache = {}

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_error" not in st.session_state:
    st.session_state.last_error = None




def get_key_material(kem_name, signature_name):

    cache_key = (kem_name, signature_name)

    if cache_key in st.session_state.key_cache:
        return st.session_state.key_cache[cache_key]

    recipient_kem = oqs.KeyEncapsulation(kem_name)

    recipient_kem_public = recipient_kem.generate_keypair()

    sender_signature = oqs.Signature(signature_name)

    sender_signature_public = sender_signature.generate_keypair()

    keys = {
        "recipient_kem": recipient_kem,
        "recipient_kem_public": recipient_kem_public,
        "sender_signature": sender_signature,
        "sender_signature_public": sender_signature_public,
    }


    st.session_state.key_cache[cache_key] = keys

    return keys






def to_base64(value):
    return base64.b64encode(value).decode("ascii")


def from_base64(value):
    return base64.b64decode(
        value.encode("ascii"),
        validate=True,
    )






def derive_aes_key(shared_secret, sender, recipient):

    context = (
        "QuantumSafeSecureChannel|"
        + sender
        + "|"
        + recipient
    ).encode("utf-8")

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=context,
    ).derive(shared_secret)






def send_secure_message(
    sender,
    recipient,
    message,
    kem_name,
    signature_name,
):

    keys = get_key_material(
        kem_name,
        signature_name,
    )



    with oqs.KeyEncapsulation(kem_name) as sender_kem:

        kem_ciphertext, sender_shared_secret = (
            sender_kem.encap_secret(
                keys["recipient_kem_public"]
            )
        )


    aes_key = derive_aes_key(
        sender_shared_secret,
        sender,
        recipient,
    )

    nonce = os.urandom(12)

    plaintext = message.encode("utf-8")


    associated_data = json.dumps(
        {
            "sender": sender,
            "recipient": recipient,
            "kem": kem_name,
            "signature": signature_name,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


    encryption_start = time.perf_counter()

    encrypted_message = AESGCM(aes_key).encrypt(
        nonce,
        plaintext,
        associated_data,
    )

    encryption_ms = (
        time.perf_counter() - encryption_start
    ) * 1000


    signed_data = (
        associated_data
        + nonce
        + kem_ciphertext
        + encrypted_message
    )

    signing_start = time.perf_counter()

    digital_signature = keys["sender_signature"].sign(
        signed_data
    )

    signing_ms = (
        time.perf_counter() - signing_start
    ) * 1000

    package = {
        "sender": sender,
        "recipient": recipient,
        "kem_algorithm": kem_name,
        "signature_algorithm": signature_name,
        "encryption_algorithm": "AES-256-GCM",
        "nonce": to_base64(nonce),
        "kem_ciphertext": to_base64(kem_ciphertext),
        "encrypted_message": to_base64(encrypted_message),
        "digital_signature": to_base64(digital_signature),
        "associated_data": to_base64(associated_data),
    }

    return {
        "package": package,
        "keys": keys,
        "encryption_ms": encryption_ms,
        "signing_ms": signing_ms,
        "plaintext_length": len(plaintext),
        "ciphertext_length": len(encrypted_message),
    }






def receive_secure_message(package, keys):

    sender = package["sender"]
    recipient = package["recipient"]

    kem_name = package["kem_algorithm"]
    signature_name = package["signature_algorithm"]


    nonce = from_base64(package["nonce"])

    kem_ciphertext = from_base64(
        package["kem_ciphertext"]
    )

    encrypted_message = from_base64(
        package["encrypted_message"]
    )

    digital_signature = from_base64(
        package["digital_signature"]
    )

    associated_data = from_base64(
        package["associated_data"]
    )


    signed_data = (
        associated_data
        + nonce
        + kem_ciphertext
        + encrypted_message
    )


    verification_start = time.perf_counter()

    with oqs.Signature(signature_name) as verifier:

        signature_valid = verifier.verify(
            signed_data,
            digital_signature,
            keys["sender_signature_public"],
        )

    verification_ms = (
        time.perf_counter() - verification_start
    ) * 1000

    if not signature_valid:
        raise ValueError(
            "Digital signature verification failed. "
            "The transmitted package has been rejected."
        )



    recipient_shared_secret = (
        keys["recipient_kem"].decap_secret(
            kem_ciphertext
        )
    )


    aes_key = derive_aes_key(
        recipient_shared_secret,
        sender,
        recipient,
    )


    decryption_start = time.perf_counter()

    plaintext = AESGCM(aes_key).decrypt(
        nonce,
        encrypted_message,
        associated_data,
    )

    decryption_ms = (
        time.perf_counter() - decryption_start
    ) * 1000

    return {
        "plaintext": plaintext.decode("utf-8"),
        "signature_valid": signature_valid,
        "verification_ms": verification_ms,
        "decryption_ms": decryption_ms,
    }



def read_processor_results():

    metrics_file = (
        TABLES_DIR / "processor_ab_metrics.csv"
    )

    if not metrics_file.exists():
        return {}

    results = {}

    try:
        with metrics_file.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            for row in csv.DictReader(file):
                name = row.get("processor", "")

                if name:
                    results[name] = row

    except Exception:
        return {}

    return results



def run_processor_benchmark():

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "main.py"),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            completed.stderr
            or completed.stdout
            or "Processor simulation failed."
        )

    return completed.stdout






st.markdown(
    """
    <div class="hero">
        <h1>🔐 QuantumSafe Secure Channel</h1>
        <p>
            Post-quantum key establishment, encrypted messaging,
            digital signatures, and quantum processor simulation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "QFF 2026 | ML-KEM | ML-DSA | Falcon | AES-256-GCM | Qiskit Aer"
)



st.sidebar.title("Security Configuration")

kem_name = st.sidebar.selectbox(
    "Key Encapsulation Mechanism",
    KEM_OPTIONS,
    index=(
        KEM_OPTIONS.index("ML-KEM-768")
        if "ML-KEM-768" in KEM_OPTIONS
        else 0
    ),
)

signature_name = st.sidebar.selectbox(
    "Digital Signature Algorithm",
    SIGNATURE_OPTIONS,
    index=(
        SIGNATURE_OPTIONS.index("ML-DSA-65")
        if "ML-DSA-65" in SIGNATURE_OPTIONS
        else 0
    ),
)

processor_name = st.sidebar.radio(
    "Quantum Processor",
    ["Processor A", "Processor B"],
)

st.sidebar.markdown("---")
st.sidebar.write("Encryption: AES-256-GCM")

if processor_name == "Processor A":
    st.sidebar.info("Processor A: 5 qubits")
else:
    st.sidebar.info("Processor B: 9 qubits")




tab_message, tab_processor, tab_about = st.tabs(
    [
        "Secure Messaging",
        "Processor Analysis",
        "About",
    ]
)






with tab_message:

    st.subheader("Compose Your Message")

    col1, col2 = st.columns(2)

    with col1:
        sender = st.text_input(
            "Sender",
            value="Alice",
            max_chars=80,
        )

    with col2:
        recipient = st.text_input(
            "Recipient",
            value="Bob",
            max_chars=80,
        )

    message = st.text_area(
        "Message",
        placeholder="Type the message you want to send...",
        height=150,
        max_chars=10000,
    )

    st.info(
        "Your message is encrypted before being placed "
        "in the transmitted package."
    )

    send_button = st.button(
        "Send Secure Message",
        type="primary",
        use_container_width=True,
    )

    if send_button:

        if not sender.strip() or not recipient.strip():
            st.error("Enter both sender and recipient names.")

        elif sender.strip() == recipient.strip():
            st.error(
                "For this demonstration, sender and recipient "
                "must have different names."
            )

        elif not message.strip():
            st.error("Please enter a message.")

        else:

            try:

                with st.spinner(
                    "Generating keys, encrypting, and signing..."
                ):

                    transmission = send_secure_message(
                        sender.strip(),
                        recipient.strip(),
                        message,
                        kem_name,
                        signature_name,
                    )

                    reception = receive_secure_message(
                        transmission["package"],
                        transmission["keys"],
                    )

                st.session_state.last_result = {
                    "transmission": transmission,
                    "reception": reception,
                }

                st.session_state.last_error = None

            except Exception as exc:

                st.session_state.last_error = (
                    f"{type(exc).__name__}: {exc}"
                )

                st.session_state.last_result = None

    if st.session_state.last_error:

        st.error(
            "Secure transmission failed: "
            + st.session_state.last_error
        )

    if st.session_state.last_result:

        result = st.session_state.last_result

        transmission = result["transmission"]
        reception = result["reception"]

        package = transmission["package"]

        st.markdown("---")
        st.subheader("Transmission Results")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Signature Verification",
            "PASSED"
            if reception["signature_valid"]
            else "FAILED",
        )

        c2.metric(
            "Encryption",
            "AES-256-GCM",
        )

        c3.metric(
            "Key Encapsulation",
            package["kem_algorithm"],
        )

        st.success(
            f"Signature verified. {package['recipient']} "
            "successfully decrypted the message."
        )

        st.markdown("### Recipient's Decrypted Message")

        st.text_area(
            "Recovered plaintext",
            value=reception["plaintext"],
            height=100,
            disabled=True,
            key="recovered_message",
        )

        st.markdown("### Operation Timings")

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Encryption",
            f"{transmission['encryption_ms']:.3f} ms",
        )

        m2.metric(
            "Signing",
            f"{transmission['signing_ms']:.3f} ms",
        )

        m3.metric(
            "Verification",
            f"{reception['verification_ms']:.3f} ms",
        )

        m4.metric(
            "Decryption",
            f"{reception['decryption_ms']:.3f} ms",
        )

        st.markdown("### Encrypted Transmitted Package")

        package_json = json.dumps(
            package,
            indent=2,
        )

        st.code(
            package_json,
            language="json",
        )

        st.download_button(
            "Download Encrypted Package",
            data=package_json,
            file_name="secure_message_package.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("---")
        st.subheader("Tampering Detection")

        st.write(
            "This test changes the encrypted message and checks "
            "whether the recipient rejects the modified package."
        )

        if st.button(
            "Test Tampering Detection",
            use_container_width=True,
        ):

            tampered_package = dict(package)

            tampered_bytes = bytearray(
                from_base64(
                    tampered_package["encrypted_message"]
                )
            )

            if tampered_bytes:
                tampered_bytes[0] ^= 1

            tampered_package["encrypted_message"] = to_base64(
                bytes(tampered_bytes)
            )

            try:

                receive_secure_message(
                    tampered_package,
                    transmission["keys"],
                )

                st.error(
                    "The modified package was unexpectedly accepted."
                )

            except Exception:

                st.success(
                    "Tampering detected. The modified package "
                    "was rejected."
                )




    st.subheader("Processor A/B Architecture Analysis")

    st.write(
        "Run the existing Qiskit Aer simulation using the "
        "processor configuration files in your project."
    )

    st.warning(
        "The cryptographic algorithms run as software on your computer. "
        "The processor experiment is a separate quantum-circuit simulation."
    )

    if st.button(
        "Run Processor A/B Simulation",
        type="primary",
        use_container_width=True,
    ):

        try:

            with st.spinner(
                "Running the existing Processor A/B benchmark..."
            ):

                console_output = run_processor_benchmark()

            st.success("Processor simulation completed.")

            with st.expander("Simulation console output"):

                st.code(console_output)

        except Exception as exc:

            st.error(
                f"Processor simulation failed: {exc}"
            )

    processor_results = read_processor_results()

    selected_processor = (
        "Processor A"
        if processor_name == "Processor A"
        else "Processor B"
    )

    row = processor_results.get(selected_processor)

    if row:

        st.markdown(
            f"### Results for {selected_processor}"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Physical Qubits",
            row.get("physical_qubits", "N/A"),
        )

        c2.metric(
            "Circuit Depth",
            row.get("depth", "N/A"),
        )

        c3.metric(
            "CX Gates",
            row.get("cx_count", "N/A"),
        )

        c4, c5, c6 = st.columns(3)

        c4.metric(
            "Logical Qubits",
            row.get("logical_qubits", "N/A"),
        )

        c5.metric(
            "Explicit SWAP Gates",
            row.get("explicit_swap_count", "N/A"),
        )

        tvd = row.get("tvd_ideal_vs_noisy", "N/A")

        try:
            tvd = f"{float(tvd):.6f}"
        except (TypeError, ValueError):
            pass

        c6.metric(
            "Ideal vs Noisy TVD",
            tvd,
        )

        st.caption(
            "TVD measures the difference between ideal and noisy "
            "measurement distributions. Lower values indicate "
            "closer distributions for this simulated experiment."
        )

    else:

        st.info(
            "No saved processor results were found. "
            "Run the simulation using the button above."
        )

    st.markdown("### Existing Simulation Charts")

    chart_names = [
        "processor_depth_comparison.png",
        "processor_cx_comparison.png",
        "processor_swap_comparison.png",
        "processor_noise_comparison.png",
    ]

    charts_found = False

    for chart_name in chart_names:

        chart_path = FIGURES_DIR / chart_name

        if chart_path.exists():

            st.image(
                str(chart_path),
                caption=chart_name.replace("_", " ").replace(".png", ""),
                use_container_width=True,
            )

            charts_found = True

    if not charts_found:

        st.caption(
            "Run the processor simulation to generate comparison charts."
        )


with tab_about:

    st.subheader("About the Project")

    st.markdown(
        """
        ### Key Encapsulation

        ML-KEM establishes a shared secret between communicating parties.

        ### Symmetric Encryption

        AES-256-GCM encrypts the message and authenticates its ciphertext.

        ### Digital Signatures

        ML-DSA or Falcon signs the transmitted package so the recipient
        can verify its integrity and authenticity.

        ### Processor Simulation

        Qiskit Aer simulates the separate Processor A and Processor B
        circuit architectures with the configured noise models.
        """
    )

    st.markdown("### Available KEM Algorithms")

    st.write(", ".join(KEM_OPTIONS))

    st.markdown("### Available Signature Algorithms")

    st.write(", ".join(SIGNATURE_OPTIONS))

    st.markdown("### Important Security Limitations")

    st.markdown(
        """
        - This is an educational demonstration, not a production messaging service.
        - The demonstration retains key objects within the current Streamlit session.
        - A real deployment needs authenticated public-key distribution and
          secure private-key storage.
        - Downloading the encrypted package does not transfer the recipient's
          private key.
        - Processor A/B simulations do not execute the cryptographic algorithms
          on quantum hardware.
        """
    )



st.markdown("---")

st.caption(
    "QuantumSafe Secure Channel | QFF 2026 | Educational Prototype"
)