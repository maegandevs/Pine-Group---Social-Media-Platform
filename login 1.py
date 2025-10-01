import re
import tkinter as tk
from tkinter import messagebox

 # dictionary to access the data from database, we could copy
 #from database to a map to access its content. 
 
    
loginCredentials = {
  "mjosuea@gmail.com": "M@rv1n",
  "mjosue@mail.com"  : "J@5ue",
  "marvinamaya@icloud.com":"M#rv1s",
  "marvinherrera@icloud.com":"F#rd",
 }

#FUNCTIONS

def validate_login(user_email):
# Validate the input : a valid email address.
  valid = not bool(re.match(r'^[a-zA-Z0-9]+@[a-zA-Z0]+\.[a-zA-Z]{3,}$',user_email))
  print("Invalid login" if valid else "Input Accepted...")
  return valid


def main():

 login = input('Please enter your email address : ')
 validator = validate_login(login)
 while(validator):
     login = input('Please re-enter your email address : ')
     validator = validate_login(login)
 #if found , proceed to get the password; otherwise, kill the program
 for key in loginCredentials:
  result = bool(re.match(key,login))
  if(result):
    password = print('Enter Password')

    tempPassword = loginCredentials[login]
    print(f"{tempPassword} = = {password} ?")
    while password != tempPassword:
     print('Password doesnt match\nEnter the correct Password')
     password = input("Re-enter your Password....")
     if(password == "M@rv1n"):
       print(f"Hello {login}")
       root = tk.Tk() 
       root.withdraw() 
       messagebox.showinfo("Success!!!", f"Welcome {login}")
       for key in loginCredentials:
        print(f"passwords {loginCredentials[key]}")
       
  else:
    print('User Not Found')
    break
       

########### 
if __name__ == "__main__":
    main()
