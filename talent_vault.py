import json
import os


class TalentVault:

    def __init__(
        self,
        file_path='talent_vault.json'
    ):

        self.file_path = file_path

        self.vault = self._load_vault()

    # ---------------------------------------------------
    # LOAD VAULT
    # ---------------------------------------------------

    def _load_vault(self):

        if os.path.exists(
            self.file_path
        ):

            try:

                with open(
                    self.file_path,
                    'r'
                ) as f:

                    return json.load(f)

            except:

                return []

        return []

    # ---------------------------------------------------
    # SAVE VAULT
    # ---------------------------------------------------

    def _save_vault(self):

        with open(
            self.file_path,
            'w'
        ) as f:

            json.dump(
                self.vault,
                f,
                indent=4
            )

    # ---------------------------------------------------
    # NORMALIZE CANDIDATE
    # ---------------------------------------------------

    def _normalize_candidate(
        self,
        candidate_data
    ):

        normalized = {

            "candidate_id":

                candidate_data.get(
                    "candidate_id"
                ),

            "name":

                candidate_data.get(
                    "name",
                    "Anonymous"
                ),

            "hashed_email":

                candidate_data.get(
                    "hashed_email"
                ),

            "status":

                candidate_data.get(
                    "status",
                    "REJECTED"
                ),

            "final_score":

                candidate_data.get(
                    "final_score",
                    0
                ),

            # ---------------------------------
            # Resume Metrics
            # ---------------------------------

            "skill_match":

                candidate_data.get(
                    "skill_match",
                    0
                ),

            "experience_score":

                candidate_data.get(

                    "experience_score",

                    candidate_data.get(
                        "depth_of_experience",
                        0
                    )
                ),

            "role_alignment":

                candidate_data.get(
                    "role_alignment",
                    0
                ),

            "additional_strengths":

                candidate_data.get(
                    "additional_strengths",
                    0
                ),

            # ---------------------------------
            # Integrity / Validation
            # ---------------------------------

            "credibility_score":

                candidate_data.get(

                    "credibility_score",

                    candidate_data.get(
                        "validation",
                        {}
                    ).get(
                        "credibility_score",
                        0
                    )
                ),

            "severity":

                candidate_data.get(

                    "severity",

                    candidate_data.get(
                        "validation",
                        {}
                    ).get(
                        "severity",
                        "Low"
                    )
                ),

            "red_flags":

                candidate_data.get(

                    "red_flags",

                    candidate_data.get(
                        "validation",
                        {}
                    ).get(
                        "red_flags",
                        []
                    )
                ),

            # ---------------------------------
            # Pedagogical Capabilities
            # ---------------------------------

            "capabilities":

                candidate_data.get(
                    "capabilities",
                    {}
                ),

            "subjects":

                candidate_data.get(
                    "subjects",
                    []
                ),

            # ---------------------------------
            # Reasoning
            # ---------------------------------

            "reason":

                candidate_data.get(

                    "reason",

                    candidate_data.get(
                        "rejection_reason",
                        "No reason available"
                    )
                )
        }

        return normalized

    # ---------------------------------------------------
    # SAVE CANDIDATE
    # ---------------------------------------------------

    def save_candidate(
        self,
        candidate_data
    ):

        normalized = (
            self._normalize_candidate(
                candidate_data
            )
        )

        # Prevent duplicate email entries

        existing = [

            c for c in self.vault

            if c.get(
                "hashed_email"
            ) == normalized.get(
                "hashed_email"
            )
        ]

        if existing:

            return False

        self.vault.append(
            normalized
        )

        self._save_vault()

        return True

    # ---------------------------------------------------
    # GET ALL CANDIDATES
    # ---------------------------------------------------

    def get_all_candidates(self):

        return self.vault

    # ---------------------------------------------------
    # GET ONLY SELECTED
    # ---------------------------------------------------

    def get_selected_candidates(self):

        return [

            c

            for c in self.vault

            if c.get(
                "status"
            ) == "SELECTED"
        ]

    # ---------------------------------------------------
    # TOP CANDIDATES
    # ---------------------------------------------------

    def get_top_candidates(
        self,
        limit=5
    ):

        sorted_candidates = sorted(

            self.vault,

            key=lambda x:
                x.get(
                    "final_score",
                    0
                ),

            reverse=True
        )

        return sorted_candidates[:limit]

    # ---------------------------------------------------
    # REQUIREMENT MATCHING
    # ---------------------------------------------------

    def match_requirement(
        self,
        new_req_meta
    ):

        results = []

        target_subject = (

            new_req_meta.get(
                'subject',
                ''
            ).lower()
        )

        for trainer in self.vault:

            base_confidence = (

                trainer.get(
                    'final_score',
                    0
                ) / 100
            )

            trainer_subjects = [

                s.lower()

                for s in trainer.get(
                    'subjects',
                    []
                )
            ]

            confidence = base_confidence

            reasoning = (
                "Strong alignment with "
                "core requirement."
            )

            # ---------------------------------
            # Subject mismatch penalty
            # ---------------------------------

            if target_subject not in trainer_subjects:

                confidence *= 0.6

                reasoning = (

                    f"Cross-domain transfer "
                    f"estimated from expertise in "
                    f"{', '.join(trainer_subjects[:2])}."
                )

            # ---------------------------------
            # Integrity penalty
            # ---------------------------------

            if trainer.get(
                'severity'
            ) == "High":

                confidence *= 0.5

                reasoning += (

                    " Heavy integrity penalty applied."
                )

            # ---------------------------------
            # Rejected candidates penalty
            # ---------------------------------

            if trainer.get(
                'status'
            ) == "REJECTED":

                confidence *= 0.7

                reasoning += (
                    " Prior rejection penalty applied."
                )

            results.append({

                "candidate_id":

                    trainer.get(
                        "candidate_id"
                    ),

                "name":

                    trainer.get(
                        "name",
                        "Anonymous"
                    ),

                "score":

                    round(
                        confidence * 100,
                        2
                    ),

                "status":

                    trainer.get(
                        "status",
                        "REJECTED"
                    ),

                "subjects":

                    trainer.get(
                        "subjects",
                        []
                    ),

                "reasoning":

                    reasoning
            })

        return sorted(

            results,

            key=lambda x:
                x['score'],

            reverse=True
        )

    # ---------------------------------------------------
    # ANALYTICS
    # ---------------------------------------------------

    def get_analytics(self):

        total = len(self.vault)

        if total == 0:

            return {

                "total_candidates": 0,

                "selected": 0,

                "rejected": 0,

                "selection_rate": 0,

                "avg_score": 0
            }

        selected = len([

            c

            for c in self.vault

            if c.get(
                "status"
            ) == "SELECTED"
        ])

        rejected = total - selected

        avg_score = round(

            sum(

                c.get(
                    "final_score",
                    0
                )

                for c in self.vault

            ) / total,

            2
        )

        return {

            "total_candidates": total,

            "selected": selected,

            "rejected": rejected,

            "selection_rate":

                round(
                    (selected / total) * 100,
                    2
                ),

            "avg_score": avg_score
        }