class ImpexusIngestor:

    def __init__(self):

        self.subjects = [
            "Python",
            "Java",
            "C",
            "DSA"
        ]

    def derive_engagement(
        self,
        subject,
        toc,
        duration,
        budget,
        mode,
        batch_size,
        project
    ):

        # Difficulty estimation
        difficulty = (
            "High"
            if "DSA" in subject or duration >= 40
            else "Medium"
        )

        # AI-generated trainer persona
        persona = (
            f"Expert trainer in {subject} capable of "
            f"handling {batch_size} students in "
            f"{mode} mode. Must demonstrate "
            f"strong diagnostic teaching ability, "
            f"patience, and concept simplification."
        )

        # Capability tasks
        tasks = [

            {
                "id": "CAP_DIAG",

                "cap": "Diagnostic Teaching",

                "task": (
                    f"A student's {subject} code compiles "
                    f"but produces incorrect output.\n\n"
                    f"Ask 3 diagnostic questions that help "
                    f"identify the root cause instead of "
                    f"immediately giving the answer."
                )
            },

            {
                "id": "CAP_SIMP",

                "cap": "Concept Simplification",

                "task": (
                    f"Explain recursion:\n\n"

                    f"1. To a 10-year-old\n"

                    f"2. To a computer science student\n"

                    f"3. To a senior software engineer\n\n"

                    f"Ensure all three explanations remain "
                    f"conceptually accurate."
                )
            },

            {
                "id": "CAP_PATIENCE",

                "cap": "Patience",

                "task": (
                    f"You are in the 38th hour of a "
                    f"40-hour {subject} bootcamp.\n\n"

                    f"A frustrated student repeatedly "
                    f"interrupts your explanation and says:\n"

                    f"'I still don't understand anything.'\n\n"

                    f"How do you respond?"
                )
            },

            {
                "id": "CAP_SCENARIO",

                "cap": "Deep Scenario Response",

                "task": (
                    f"A student says:\n\n"

                    f"'This topic is useless because "
                    f"ChatGPT can already do it.'\n\n"

                    f"How would you handle the next "
                    f"5 minutes of class?"
                )
            },

            {
                "id": "CAP_AI",

                "cap": "AI Stance",

                "task": (
                    f"Do you think AI tools should be "
                    f"allowed during learning?\n\n"

                    f"Explain where AI genuinely helps "
                    f"students and where overdependence "
                    f"becomes harmful."
                )
            }
        ]

        # Final requirement object
        return {

            "meta": {

                "subject": subject,

                "difficulty": difficulty,

                "toc": toc,

                "duration": duration,

                "budget": budget,

                "mode": mode,

                "batch_size": batch_size,

                "project": project
            },

            "persona": persona,

            "tasks": tasks,

            "skills_derived": [

                subject,

                "Pedagogy",

                "Diagnostic Teaching",

                "Concept Simplification",

                "Classroom Management",

                "AI-Assisted Learning"
            ]
        }


# WORKED EXAMPLE

if __name__ == "__main__":

    ingestor = ImpexusIngestor()

    java_dsa_spec = ingestor.derive_engagement(

        subject="Java with DSA",

        toc=[
            "Recursion",
            "Trees",
            "Sorting"
        ],

        duration=40,

        budget=40000,

        mode="online",

        batch_size=30,

        project="mini"
    )

    import json

    print(
        json.dumps(
            java_dsa_spec,
            indent=4
        )
    )