import os
import sys
import time
from playwright.sync_api import sync_playwright

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(REPO_ROOT, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def run():
    print(f"Saving screenshots to: {SCREENSHOTS_DIR}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5
        )
        page = context.new_page()

        # 1. Landing Page
        print("Capturing 01_landing_page.png...")
        page.goto("http://localhost:5174/", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_landing_page.png"), full_page=True)

        # 2. Login Page
        print("Capturing 02_login_page.png...")
        page.goto("http://localhost:5174/login", wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_login_page.png"))

        # 3. Register Page
        print("Capturing 03_register_page.png...")
        page.goto("http://localhost:5174/register", wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_register_page.png"))

        # Log in
        print("Logging in as test@syllabus.com...")
        page.goto("http://localhost:5174/login", wait_until="networkidle")
        page.fill('input[type="email"]', "test@syllabus.com")
        page.fill('input[type="password"]', "Password123!")
        page.click('button[type="submit"]')
        page.wait_for_url("**/dashboard", timeout=10000)
        page.wait_for_timeout(1500)

        # 4. Dashboard Page
        print("Capturing 04_dashboard.png...")
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_dashboard.png"), full_page=True)

        # 5. Resume & JD Upload Page
        print("Capturing 05_resume_upload.png...")
        page.goto("http://localhost:5174/resume", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "05_resume_upload.png"), full_page=True)

        # 6. Syllabus Upload Page
        print("Capturing 06_syllabus_upload.png...")
        page.goto("http://localhost:5174/syllabus", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "06_syllabus_upload.png"), full_page=True)

        # 7. Interview Setup Page
        print("Capturing 07_interview_setup.png...")
        page.goto("http://localhost:5174/setup", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "07_interview_setup.png"), full_page=True)

        # 8. History Page
        print("Capturing 08_history.png...")
        page.goto("http://localhost:5174/history", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "08_history.png"), full_page=True)

        # 9. Profile Page
        print("Capturing 09_profile.png...")
        page.goto("http://localhost:5174/profile", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "09_profile.png"), full_page=True)

        # 10. Performance Dashboard Page
        print("Capturing 10_performance_dashboard.png...")
        page.goto("http://localhost:5174/performance", wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "10_performance_dashboard.png"), full_page=True)

        # 11. Results Page (Session 13)
        print("Capturing 11_results_scorecard.png...")
        page.goto("http://localhost:5174/results/13", wait_until="networkidle")
        page.wait_for_timeout(1500)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "11_results_scorecard.png"), full_page=True)

        # 12. Remediation Page (Session 13)
        print("Capturing 12_remedial_mastery_mode.png...")
        page.goto("http://localhost:5174/remediation/13", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "12_remedial_mastery_mode.png"), full_page=True)

        # 13. Active Interview Session (Session 11)
        print("Capturing 13_live_interview_session.png...")
        page.goto("http://localhost:5174/interview/11", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "13_live_interview_session.png"), full_page=True)

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    run()

