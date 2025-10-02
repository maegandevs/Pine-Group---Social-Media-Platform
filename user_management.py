import tkinter as tk
from tkinter import messagebox
import re
import os

# File paths
PROFILES_FILE = "profiles.txt"
CREDENTIALS_FILE = "credentials.txt"

def load_profiles():
    """Load user profiles from profiles.txt file"""
    profiles = {}
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and ':' in line:
                        email, profile_data = line.split(':', 1)
                        # Parse profile data (name|bio|grad_year|major|minor)
                        parts = profile_data.split('|')
                        if len(parts) == 5:
                            profiles[email] = {
                                'name': parts[0],
                                'bio': parts[1],
                                'grad_year': parts[2],
                                'major': parts[3],
                                'minor': parts[4]
                            }
        except Exception as e:
            print(f"Error loading profiles: {e}")
    return profiles

def save_profiles(profiles):
    """Save user profiles to profiles.txt file"""
    try:
        with open(PROFILES_FILE, 'w') as file:
            for email, profile in profiles.items():
                profile_data = f"{profile['name']}|{profile['bio']}|{profile['grad_year']}|{profile['major']}|{profile['minor']}"
                file.write(f"{email}:{profile_data}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save profiles: {e}")

def load_credentials():
    """Load login credentials from credentials.txt file"""
    credentials = {}
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and ',' in line:
                        email, password = line.split(',', 1)
                        credentials[email] = password
        except Exception as e:
            print(f"Error loading credentials: {e}")
    return credentials

def save_credentials(credentials):
    """Save login credentials to credentials.txt file"""
    try:
        with open(CREDENTIALS_FILE, 'w') as file:
            for email, password in credentials.items():
                file.write(f"{email},{password}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save credentials: {e}")

# Load initial data
user_profiles = load_profiles()
loginCredentials = load_credentials()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clear_screen(root):
    """Clear all widgets from the screen"""
    for widget in root.winfo_children():
        widget.destroy()

def show_forgot_password(root, loginCredentials):
    """Show forgot password screen"""
    clear_screen(root)
    
    # Size of screen
    root.geometry("500x400")
    root.resizable(True, True)
    
    tk.Label(root, text="Reset Password", font=('Arial', 16, 'bold')).pack(pady=30)
    
    tk.Label(root, text="Enter your email address:").pack(pady=5)
    email_entry = tk.Entry(root, width=30, font=('Arial', 10))
    email_entry.pack(pady=5)
    
    def reset_password():
        email = email_entry.get()
        
        if not validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
            
        if email in loginCredentials:
            # Generate a simple reset code
            new_password = "Temp123"
            loginCredentials[email] = new_password
            save_credentials(loginCredentials)  # Save to file
            
            messagebox.showinfo("Success", 
                f"Password reset successful!\nYour temporary password is: {new_password}\n"
                f"Please change it after logging in.")
            
            # Go back to login screen
            from marvin_code import try_login  # Import Marvin's login function
            try_login()
        else:
            messagebox.showerror("Error", "Email address not found")
    
    tk.Button(root, text="Reset Password", command=reset_password, width=20, height=2).pack(pady=10)
    tk.Button(root, text="Back to Login", 
              command=lambda: [clear_screen(root), __import__('marvin_code').try_login()], 
              width=20).pack(pady=5)

def show_login_screen(root, loginCredentials):
    """Add forgot password button to login screen"""
    btn = tk.Button(root, text="Forgot Password", 
              command=lambda: show_forgot_password(root, loginCredentials), 
              width=15, height=1, padx=6, pady=3)
    btn.grid(row=7, column=0, columnspan=2)

def show_dashboard(root, current_user, loginCredentials):
    """Show main dashboard after login"""
    clear_screen(root)
    root.geometry("500x400")
    root.resizable(True, True)
    
    # Ensure user has a profile
    if current_user not in user_profiles:
        user_profiles[current_user] = {
            'name': current_user.split('@')[0],  # Use username part of email as default name
            'bio': 'No bio yet',
            'grad_year': '2025',
            'major': 'Undeclared',
            'minor': 'None'
        }
        save_profiles(user_profiles)  # Save new profile
    
    user_name = user_profiles[current_user]['name']
    tk.Label(root, text=f"Welcome, {user_name}!", font=('Arial', 16, 'bold')).pack(pady=20)
    
    tk.Button(root, text="View My Profile", 
              command=lambda: show_profile(root, current_user, loginCredentials), 
              width=20, height=2).pack(pady=5)
    tk.Button(root, text="Edit My Profile", 
              command=lambda: edit_profile(root, current_user, loginCredentials), 
              width=20, height=2).pack(pady=5)
    tk.Button(root, text="Change Password", 
              command=lambda: show_change_password(root, current_user, loginCredentials), 
              width=20, height=2).pack(pady=5)
    tk.Button(root, text="Logout", 
              command=lambda: [clear_screen(root), __import__('marvin_code').try_login()], 
              width=20, height=2).pack(pady=20)

def show_profile(root, current_user, loginCredentials):
    """Show user profile"""
    clear_screen(root)
    
    # Reload profiles to ensure we have latest data
    global user_profiles
    user_profiles = load_profiles()
    
    profile = user_profiles.get(current_user, {})
    
    tk.Label(root, text="My Profile", font=('Arial', 16, 'bold')).pack(pady=20)
    
    details_frame = tk.Frame(root)
    details_frame.pack(pady=10, padx=20)
    
    tk.Label(details_frame, text=f"Name: {profile.get('name', 'Not set')}", font=('Arial', 11), anchor='w').pack(fill='x', pady=5)
    tk.Label(details_frame, text=f"Email: {current_user}", font=('Arial', 11), anchor='w').pack(fill='x', pady=5)
    tk.Label(details_frame, text=f"Bio: {profile.get('bio', 'Not set')}", font=('Arial', 11), anchor='w').pack(fill='x', pady=5)
    tk.Label(details_frame, text=f"Graduation Year: {profile.get('grad_year', 'Not set')}", font=('Arial', 11), anchor='w').pack(fill='x', pady=5)
    tk.Label(details_frame, text=f"Major: {profile.get('major', 'Not set')}", font=('Arial', 11), anchor='w').pack(fill='x', pady=5)
    tk.Label(details_frame, text=f"Minor: {profile.get('minor', 'Not set')}", font=('Arial', 11), anchor='w').pack(fill='x', pady=5)
    
    tk.Button(root, text="Edit Profile", 
              command=lambda: edit_profile(root, current_user, loginCredentials), 
              width=15).pack(pady=5)
    tk.Button(root, text="Back to Dashboard", 
              command=lambda: show_dashboard(root, current_user, loginCredentials), 
              width=15).pack(pady=5)

def edit_profile(root, current_user, loginCredentials):
    """Edit user profile"""
    clear_screen(root)
    
    # Reload profiles to ensure we have latest data
    global user_profiles
    user_profiles = load_profiles()
    
    current_profile = user_profiles.get(current_user, {
        'name': '', 'bio': '', 'grad_year': '', 'major': '', 'minor': ''
    })
    
    tk.Label(root, text="Edit Profile", font=('Arial', 16, 'bold')).pack(pady=20)
    
    form_frame = tk.Frame(root)
    form_frame.pack(pady=10, padx=20)
    
    # Name
    tk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky='w', pady=5)
    name_entry = tk.Entry(form_frame, width=30)
    name_entry.insert(0, current_profile.get('name', ''))
    name_entry.grid(row=0, column=1, pady=5, padx=10)
    
    # Bio
    tk.Label(form_frame, text="Bio:").grid(row=1, column=0, sticky='w', pady=5)
    bio_entry = tk.Entry(form_frame, width=30)
    bio_entry.insert(0, current_profile.get('bio', ''))
    bio_entry.grid(row=1, column=1, pady=5, padx=10)
    
    # Graduation Year
    tk.Label(form_frame, text="Graduation Year:").grid(row=2, column=0, sticky='w', pady=5)
    year_entry = tk.Entry(form_frame, width=30)
    year_entry.insert(0, current_profile.get('grad_year', ''))
    year_entry.grid(row=2, column=1, pady=5, padx=10)
    
    # Major
    tk.Label(form_frame, text="Major:").grid(row=3, column=0, sticky='w', pady=5)
    major_entry = tk.Entry(form_frame, width=30)
    major_entry.insert(0, current_profile.get('major', ''))
    major_entry.grid(row=3, column=1, pady=5, padx=10)
    
    # Minor
    tk.Label(form_frame, text="Minor:").grid(row=4, column=0, sticky='w', pady=5)
    minor_entry = tk.Entry(form_frame, width=30)
    minor_entry.insert(0, current_profile.get('minor', ''))
    minor_entry.grid(row=4, column=1, pady=5, padx=10)
    
    def save_profile():
        # Update profiles dictionary
        user_profiles[current_user] = {
            'name': name_entry.get(),
            'bio': bio_entry.get(),
            'grad_year': year_entry.get(),
            'major': major_entry.get(),
            'minor': minor_entry.get()
        }
        
        # Save to file
        save_profiles(user_profiles)
        
        messagebox.showinfo("Success", "Profile updated successfully!")
        show_dashboard(root, current_user, loginCredentials)
    
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Save Profile", command=save_profile, width=15).pack(side='left', padx=5)
    tk.Button(button_frame, text="Cancel", 
              command=lambda: show_dashboard(root, current_user, loginCredentials), 
              width=15).pack(side='left', padx=5)

def show_change_password(root, current_user, loginCredentials):
    """Change password screen"""
    clear_screen(root)
    
    tk.Label(root, text="Change Password", font=('Arial', 16, 'bold')).pack(pady=20)
    
    tk.Label(root, text="Current Password:").pack(pady=5)
    current_pass_entry = tk.Entry(root, width=30, show="*")
    current_pass_entry.pack(pady=5)
    
    tk.Label(root, text="New Password:").pack(pady=5)
    new_pass_entry = tk.Entry(root, width=30, show="*")
    new_pass_entry.pack(pady=5)
    
    tk.Label(root, text="Confirm New Password:").pack(pady=5)
    confirm_pass_entry = tk.Entry(root, width=30, show="*")
    confirm_pass_entry.pack(pady=5)
    
    def change_password():
        current_pass = current_pass_entry.get()
        new_pass = new_pass_entry.get()
        confirm_pass = confirm_pass_entry.get()
        
        if loginCredentials[current_user] != current_pass:
            messagebox.showerror("Error", "Current password is incorrect")
        elif new_pass != confirm_pass:
            messagebox.showerror("Error", "New passwords do not match")
        elif len(new_pass) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
        else:
            loginCredentials[current_user] = new_pass
            save_credentials(loginCredentials)  # Save to file
            messagebox.showinfo("Success", "Password changed successfully!")
            show_dashboard(root, current_user, loginCredentials)
    
    tk.Button(root, text="Change Password", command=change_password, width=20, height=2).pack(pady=10)
    tk.Button(root, text="Cancel", 
              command=lambda: show_dashboard(root, current_user, loginCredentials), 
              width=20).pack(pady=5)

def start_user_management(current_user, loginCredentials):
    """Start the user management GUI - called from login.py"""
    root = tk.Tk()
    root.title("University User Management")
    root.geometry("500x400")
    root.resizable(False, False)
    
    show_dashboard(root, current_user, loginCredentials)
    root.mainloop()

# For testing this module independently
if __name__ == "__main__":
    # Create sample files if they don't exist
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'w') as f:
            f.write("amatulllah@gmail.com:Amatullah|Computer Science Student|2025|Computer Science|Mathematics\n")
            f.write("fiza@gmai.com:Fiza|Engineering Student|2024|Electrical Engineering|Physics\n")
    
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'w') as f:
            f.write("amatulllah@gmail.com,password123\n")
            f.write("fiza@gmai.com,password456\n")
    
    # Reload data
    user_profiles = load_profiles()
    loginCredentials = load_credentials()
    
    # Test with first user
    if user_profiles:
        test_user = list(user_profiles.keys())[0]
        start_user_management(test_user, loginCredentials)
    else:
        print("No profiles found for testing")