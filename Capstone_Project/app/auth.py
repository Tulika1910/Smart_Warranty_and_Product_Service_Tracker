import pyrebase
import streamlit as st

# Firebase configuration using your secrets
config = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"],
    "databaseURL": ''
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

def login_user(email, password):
    try:
        # 1. Attempt to sign in
        user = auth.sign_in_with_email_and_password(email, password)
        
        # 2. Get account details to check 'emailVerified' status
        account_info = auth.get_account_info(user['idToken'])
        is_verified = account_info['users'][0].get('emailVerified', False)
        
        # 3. Handle verification check
        if not is_verified:
            st.warning("Please verify your email before logging in.")
            return None
        
        return user # Return user object if sign-in and verification succeed
        
    except Exception:
        # This catches actual authentication failures (wrong password/email)
        st.error("Invalid email or password.")
        return None

def create_user(email, password):
    try:
        # Create the user account
        auth.create_user_with_email_and_password(email, password)
        
        # Sign in immediately to retrieve a valid token
        user = auth.sign_in_with_email_and_password(email, password)
        
        # Send the verification email using the new token
        auth.send_email_verification(user['idToken'])
        
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False