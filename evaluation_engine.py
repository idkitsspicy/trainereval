import json
import os


class MultiStageEval:

    def __init__(self):

        # Capability Weights

        self.weights = {

            "Patience": 0.20,

            "Diagnostic": 0.25,

            "Simplification": 0.20,

            "AI_Stance": 0.15,

            "Scenario": 0.20
        }

    # ---------------------------------------------------
    # STAGE 1 — SIGNAL EXTRACTION
    # ---------------------------------------------------

    def stage_1_signal_extraction(
        self,
        text_responses
    ):

        text_blob = " ".join(
            text_responses.values()
        ).lower()

        signals = {

            # Diagnostic probing quality
            "diag_probing":

                text_responses.get(
                    "CAP_DIAG",
                    ""
                ).count("?"),

            # Simplification / analogy usage
            "analogy_present":

                any(

                    word in text_responses.get(
                        "CAP_SIMP",
                        ""
                    ).lower()

                    for word in [

                        "like",

                        "imagine",

                        "suppose",

                        "similar"
                    ]
                ),

            # Effort / patience proxy
            "word_count":

                len(text_blob.split()),

            # Scenario depth
            "scenario_depth":

                len(

                    text_responses.get(
                        "CAP_SCENARIO",
                        ""
                    ).split()
                )
        }

        return signals

    # ---------------------------------------------------
    # STAGE 2 — CAPABILITY SCORING
    # ---------------------------------------------------

    def stage_2_capability_scoring(
        self,
        signals,
        ai_score
    ):

        # Diagnostic Teaching

        diagnostic = (

            90

            if signals["diag_probing"] >= 3

            else 70

            if signals["diag_probing"] == 2

            else 40
        )

        # Concept Simplification

        simplification = (

            85

            if signals["analogy_present"]

            else 45
        )

        # Patience

        patience = (

            90

            if signals["word_count"] > 350

            else 75

            if signals["word_count"] > 180

            else 40
        )

        # Scenario Response

        scenario = (

            90

            if signals["scenario_depth"] > 180

            else 70

            if signals["scenario_depth"] > 90

            else 45
        )

        capabilities = {

            "Diagnostic": diagnostic,

            "Simplification": simplification,

            "Patience": patience,

            "AI_Stance": ai_score,

            "Scenario": scenario
        }

        return capabilities

    # ---------------------------------------------------
    # STAGE 3 — FINAL AGGREGATION
    # ---------------------------------------------------

    def stage_3_final_scoring(
        self,
        capabilities
    ):

        composite = (

            capabilities["Diagnostic"]
            * self.weights["Diagnostic"]

            +

            capabilities["Simplification"]
            * self.weights["Simplification"]

            +

            capabilities["Patience"]
            * self.weights["Patience"]

            +

            capabilities["AI_Stance"]
            * self.weights["AI_Stance"]

            +

            capabilities["Scenario"]
            * self.weights["Scenario"]
        )

        composite = round(
            composite,
            2
        )

        # Rejection Logic

        status = (

            "SELECTED"

            if composite >= 70

            else "REJECTED"
        )

        # Professional Reasoning

        reason = (
            "Candidate meets the pedagogical "
            "engagement quality threshold."
        )

        if status == "REJECTED":

            if capabilities[
                "AI_Stance"
            ] < 50:

                reason = (
                    "Candidate responses exhibit "
                    "low originality/authenticity."
                )

            elif capabilities[
                "Diagnostic"
            ] < 50:

                reason = (
                    "Candidate failed to demonstrate "
                    "root-cause diagnostic teaching."
                )

            elif capabilities[
                "Scenario"
            ] < 50:

                reason = (
                    "Candidate showed weak reasoning "
                    "under live classroom pressure."
                )

            else:

                reason = (
                    "Overall capability scores fall "
                    "below the engagement threshold."
                )

        return {

            "final_score": composite,

            "status": status,

            "reason": reason
        }

    # ---------------------------------------------------
    # MASTER EVALUATION METHOD
    # ---------------------------------------------------

    def evaluate_candidate(
        self,
        text_responses,
        ai_score
    ):

        signals = self.stage_1_signal_extraction(
            text_responses
        )

        capabilities = (
            self.stage_2_capability_scoring(
                signals,
                ai_score
            )
        )

        final = self.stage_3_final_scoring(
            capabilities
        )

        return {

            "signals": signals,

            "capabilities": capabilities,

            "final_score": final[
                "final_score"
            ],

            "status": final[
                "status"
            ],

            "reason": final[
                "reason"
            ]
        }

    # ---------------------------------------------------
    # OPTIONAL BATCH PROCESSOR
    # ---------------------------------------------------

    def evaluate_all(
        self,
        applicant_dir='applicants',
        vault_file='talent_vault.json'
    ):

        vault_results = []

        if not os.path.exists(
            applicant_dir
        ):

            return []

        for filename in os.listdir(
            applicant_dir
        ):

            if filename.endswith(".json"):

                with open(

                    os.path.join(
                        applicant_dir,
                        filename
                    ),

                    'r'

                ) as f:

                    app_data = json.load(f)

                # Placeholder AI score
                ai_score = app_data.get(
                    "ai_score",
                    70
                )

                results = self.evaluate_candidate(

                    app_data[
                        "text_responses"
                    ],

                    ai_score
                )

                entry = {

                    "candidate_id":

                        app_data.get(
                            "candidate_id"
                        ),

                    "final_score":

                        results[
                            "final_score"
                        ],

                    "status":

                        results[
                            "status"
                        ],

                    "reason":

                        results[
                            "reason"
                        ],

                    "capabilities":

                        results[
                            "capabilities"
                        ],

                    "subjects":

                        app_data.get(
                            "subjects",
                            []
                        ),

                    "hashed_email":

                        app_data.get(
                            "hashed_email"
                        )
                }

                vault_results.append(
                    entry
                )

        with open(
            vault_file,
            'w'
        ) as f:

            json.dump(
                vault_results,
                f,
                indent=4
            )

        return vault_results