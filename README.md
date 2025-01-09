#Banking Application

This is a simple Banking Application built with Flask and SQLite to simulate basic banking operations such as user registration, login, account balance management, and transaction history.

##Features->  
    1.Add User: Allows adding a new user with personal details like name, account number, contact, email, and initial balance.  
    2.Login: Users can log in using their contact number and password.  
    3.Dashboard: Displays the user's account overview, recent transactions, and options for transfers, deposits, and withdrawals.  
    4.Profile Management: Users can view and update their profile information.  
    5.Transaction Management: Credit, Debit, and Transfer funds between accounts.  
    6.Account Status: Activate or deactivate user accounts.  
    7.Logout: Allows users to log out of the application.

##Tech Stack->  
    1.Backend: Flask (Python)  
    2.Database: SQLite (SQLAlchemy ORM)  
    3.Frontend: HTML, CSS (Bootstrap)  
    4.Authentication: Simple session-based authentication  

##Routes->  
    1./: Home page, redirects to login if not logged in.  
    2./login: Login page where users can sign in with their contact number and password.  
    3./dashboard: User dashboard showing account details and transactions.  
    4./profile: User profile management page.  
    5./logout: Logs the user out and redirects to login.  

##Usage->  
    1.Create a new user: Navigate to the registration page and enter all required details,      including the name, contact number, password, and initial balance.  
    2.Login: After registration, log in with your contact number and password to access the user dashboard.  
    3.Dashboard: The dashboard will show your account balance, recent transactions, and actions like transfer funds, deposit, or withdraw money.  
    4.Profile: You can view and update your profile information under the profile page.  
