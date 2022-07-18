# Based on AHA Back-end Exam document
https://docs.google.com/document/d/15tA1qlVOg14cmpX0DbIPPnUQa9GYlSXcb9haRCojVEU/edit

# Install dependencies
python install -r requirements.txt

# Secret key for Flask
Execute `python -c "import os; print(os.urandom(20).hex())"`.
Set the value of "SECRET_KEY" in ".env" file

# Google App Passwords
Go to your [Google Account](https://myaccount.google.com/).
Activate 2-Step-Verification then generate an App Password.
Set the values of "GMAIL_PASSWORD" and "GMAIL_ADDRESS" in ".env" file

# Google OAuth
Go to your [Google Console](https://console.developers.google.com/).
Create an OAuth credential for "Web Application" with "Authorized redirect URIs" set to "{your_domain}/login/google/authorized".
Download the json file as "google.json" in this current directory

# Create/reset the database
python www\init_db.py

# Start the dev web server
flask run

# TODO
[x] Email/Password signup
[x] Send email verification
[x] Login/Logout
[x] User profile
[x] Reset password
[x] Dashboard
[x] User statistics
[x] Google OAuth signup/login
[ ] Facebook OAuth signup/login
[x] Verify OAuth account automatically -> no email verification
