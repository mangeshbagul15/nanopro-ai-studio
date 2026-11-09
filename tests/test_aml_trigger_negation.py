"""Negated AML instructions must never start a pipeline run."""
import unittest

from app.core.data_modeling_ai import _detect_aml_action


class TestAmlTriggerNegation(unittest.TestCase):

    def test_negated_action_is_not_a_run(self):
        messages = [
            "Do not execute anything yet. Reply with the plan only.",
            "Don't run the AML full load, just outline the plan.",
            "Please show the AML plan without loading any data.",
            "No need to start the AML pipeline now.",
            "AML sathi ajun kahi nako, fakt plan dakhav.",
        ]
        for message in messages:
            self.assertIsNone(_detect_aml_action(message), message)

    def test_negated_clause_with_status_reads_status(self):
        self.assertEqual(
            _detect_aml_action("Don't run anything new — show the AML status."),
            "status",
        )

    def test_real_commands_still_trigger(self):
        self.assertEqual(_detect_aml_action("run aml full load"), "full")
        self.assertEqual(_detect_aml_action("Please append the new AML transactions"), "incremental")
        self.assertEqual(_detect_aml_action("execute aml load now"), "full")

    def test_negation_in_one_clause_keeps_later_command(self):
        self.assertEqual(
            _detect_aml_action("Do not execute anything yet, but run the AML full load after I confirm."),
            "full",
        )


if __name__ == "__main__":
    unittest.main()
