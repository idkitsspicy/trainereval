import PyPDF2


def extract_text_from_pdf(pdf_file):

    """
    Extracts text from uploaded PDF resume.
    Returns clean normalized text.
    """

    try:

        # Reset file pointer
        pdf_file.seek(0)

        reader = PyPDF2.PdfReader(
            pdf_file
        )

        # Empty PDF check
        if len(reader.pages) == 0:

            return (
                "ERROR: Empty PDF uploaded."
            )

        extracted_text = []

        for page in reader.pages:

            try:

                content = page.extract_text()

                if content:

                    extracted_text.append(
                        content.strip()
                    )

            except:

                continue

        text = "\n".join(
            extracted_text
        )

        # Normalize whitespace
        text = " ".join(
            text.split()
        )

        # Minimum quality check
        if len(text) < 50:

            return (
                "ERROR: Could not extract "
                "sufficient resume text."
            )

        return text

    except Exception as e:

        return (
            f"ERROR: PDF extraction failed - "
            f"{str(e)}"
        )