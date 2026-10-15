"""
Unit Tests for Upgraded Career & Job Search Hub (Mangesh Bagul - 4 Yrs Data Engineer)
"""

import os
import unittest
from app.agents.career_agent import (
    career_agent,
    MANGESH_RESUME_PROFILE,
    VERIFIED_MNC_JOBS,
    SCENARIO_INTERVIEW_QUESTIONS,
    STUDY_MATERIALS_CATALOG,
    RESUME_FILE_PATH
)

class TestCareerHub(unittest.TestCase):
    def test_candidate_resume_profile(self):
        profile = career_agent.get_candidate_profile()
        self.assertEqual(profile["name"], "Mangesh Vasant Bagul")
        self.assertIn("Data Engineer", profile["headline"])
        self.assertEqual(profile["current_company"], "Utkarsh Small Finance Bank")
        self.assertIn("Thane", profile["location"])
        self.assertEqual(profile["contact"]["phone"], "+91 84337 55448")
        self.assertEqual(profile["contact"]["email"], "mangeshbagul15@gmail.com")
        self.assertTrue(os.path.exists(RESUME_FILE_PATH), f"Resume file missing at {RESUME_FILE_PATH}")
        self.assertGreater(os.path.getsize(RESUME_FILE_PATH), 1000)

    def test_verified_mnc_jobs_filtering_and_validation(self):
        search_result = career_agent.search_jobs()
        self.assertEqual(search_result["status"], "success")
        jobs = search_result["jobs"]
        self.assertGreaterEqual(len(jobs), 8)
        
        allowed_locations = ["mumbai", "suburban mumbai", "thane", "navi mumbai", "andheri", "vashi", "powai", "goregaon", "airoli", "mahape", "mahāpe", "kanjurmarg"]
        
        for job in jobs:
            # 1. Role must be Data Engineer / Snowflake / AWS
            title_lower = job["title"].lower()
            is_valid_role = any(r in title_lower for r in ["data engineer", "snowflake", "aws"])
            self.assertTrue(is_valid_role, f"Invalid title: {job['title']}")
            
            # 2. Experience must be between 3 and 6 years
            min_exp = job["min_exp"]
            max_exp = job["max_exp"]
            self.assertTrue(min_exp >= 3 and max_exp <= 7, f"Experience criteria violation in {job['id']}: {min_exp}-{max_exp}")
            
            # 3. Salary must be at least 6-7 LPA
            salary_min = job["salary_min_lpa"]
            self.assertGreaterEqual(salary_min, 6.0, f"Salary below 6 LPA in {job['id']}: {salary_min}")
            
            # 4. Location must be Mumbai / Thane / Navi Mumbai / Andheri / Vashi
            loc_lower = job["location"].lower()
            is_valid_loc = any(loc in loc_lower for loc in allowed_locations)
            self.assertTrue(is_valid_loc, f"Location out of bounds: {job['location']}")
            
            # 5. Cross validation: Real vs Fake
            self.assertEqual(job["is_verified"], True)
            self.assertIn("Verified", job["verification_badge"])
            self.assertTrue(len(job["verification_reason"]) > 10)
            
            # 6. Candidate match score
            self.assertGreaterEqual(job["match_score_pct"], 90.0)

    def test_job_search_filter(self):
        # Filter with min_salary_lpa
        res = career_agent.search_jobs(min_salary_lpa=12.0)
        self.assertTrue(res["total_verified"] >= 1)
        for j in res["jobs"]:
            self.assertGreaterEqual(j["salary_min_lpa"], 12.0)

    def test_scenario_interview_questions(self):
        scenarios = career_agent.get_scenario_questions()
        self.assertGreaterEqual(len(scenarios), 8)
        for s in scenarios:
            self.assertIn("id", s)
            self.assertIn("category", s)
            self.assertIn("scenario", s)
            self.assertIn("in_depth_answer", s)
            self.assertIn("interviewer_tip", s)
            self.assertTrue(len(s["in_depth_answer"]) > 50)

    def test_study_materials_catalog(self):
        catalog = career_agent.get_study_catalog()
        self.assertIn("books", catalog)
        self.assertIn("concept_shorts", catalog)
        self.assertIn("study_schedule_7days", catalog)
        
        self.assertGreaterEqual(len(catalog["books"]), 3)
        self.assertGreaterEqual(len(catalog["concept_shorts"]), 4)
        self.assertEqual(len(catalog["study_schedule_7days"]), 7)

    def test_hr_email_drafting(self):
        # Draft email for job job_mum_tcs_01
        draft = career_agent.draft_hr_application_email("job_mum_tcs_01")
        self.assertEqual(draft["status"], "success")
        self.assertIn("Mangesh Vasant Bagul", draft["body"])
        self.assertIn("Utkarsh Small Finance Bank", draft["body"])
        self.assertIn("Finacle", draft["body"])
        self.assertIn("Tata Consultancy Services", draft["body"])
        self.assertTrue(draft["attachment_exists"])
        self.assertEqual(draft["attachment_path"], RESUME_FILE_PATH)
        self.assertTrue(os.path.exists(draft["attachment_path"]))

    def test_telegram_broadcast_payload(self):
        res = career_agent.broadcast_hourly_jobs_to_telegram()
        self.assertIn(res["status"], ["success", "warning"])
        self.assertGreaterEqual(res["jobs_count"], 1)

if __name__ == "__main__":
    unittest.main()
