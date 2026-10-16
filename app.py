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