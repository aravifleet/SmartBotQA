from playwright.sync_api import sync_playwright
from pathlib import Path
import csv


def read_all_credentials(csv_name="credentials.csv"):
    path = Path(__file__).with_name(csv_name)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def Create_users():
    creds_list = read_all_credentials()

    # First row = admin login
    admin = creds_list[0]
    users_to_create = creds_list[1:]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # ---------------- ADMIN LOGIN ----------------
        print(f"Logging in as ADMIN: {admin['username']}")
        page.goto("https://live-icsample1657400753.pantheonsite.io/")
        page.click("//a[@title='Log in']")
        page.fill("//input[@id='edit-name']", admin["username"])
        page.fill("//input[@id='edit-pass']", admin["password"])
        page.click("//input[@id='edit-submit']")

        # ✅ wait until Dashboard is visible
        page.wait_for_selector("//span[text()='Dashboard']")
        print("✅ Admin login successful, Dashboard is visible!")

        # ---------------- CREATE USERS ----------------
        for user in users_to_create:
            print(f"Creating new user: {user['username']} with role {user['role']}")

            # Navigate: Dashboard → Users → Add user
            page.click("//span[text()='Dashboard']")
            page.wait_for_selector("//a[text()='Users']")
            page.click("//a[text()='Users']")
            page.wait_for_selector("//a[text()='Add user']")
            page.click("//a[text()='Add user']")
            page.wait_for_selector("//input[@id='edit-mail']")

            # Fill user details
            page.fill("//input[@id='edit-mail']", user["username"])
            page.fill("//input[@id='edit-pass-pass1']", user["password"])
            page.fill("//input[@id='edit-pass-pass2']", user["password"])

            # Select role dynamically from CSV
            role_xpath = f"//label[text()='{user['role']}']"
            page.click(role_xpath)

            # Accept terms
            page.click("//input[@id='edit-terms-of-use']")

            # Submit form
            page.click("//input[@id='edit-submit']")
            page.wait_for_timeout(2000)  # wait before next user

        # ---------------- LOGOUT ADMIN ----------------
        print("Logging out admin...")
        page.click("//span[text()='Logout']")
        page.wait_for_selector("//a[@title='Log in']")
        print("✅ Admin logged out")

        browser.close()


if __name__ == "__main__":
    Create_users()
