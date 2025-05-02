# !/usr/bin/env python3 
# Copyright (c) 2025, Balgrist University Clinic, Digital Medicine Unit.
# Distributed under the terms of the Modified BSD License.


"""
Create admin user for JupyterHub.
Run this script inside the JupyterHub container to create an admin user.

Example:
    docker exec -it jupyterhub python /srv/jupyterhub/create-admin.py admin mypassword
"""
import sys
import os
import argparse
import bcrypt
from jupyterhub.orm import User
from nativeauthenticator.orm import UserInfo
from jupyterhub.app import JupyterHub
from sqlalchemy import inspect

def create_admin_user(username, password):
    hub = JupyterHub()
    hub.load_config_file('/srv/jupyterhub/jupyterhub_config.py')
    hub.init_db()
    
    db = hub.db
    
    # Check if user already exists
    user = db.query(User).filter_by(name=username).first()
    
    # Hash the password properly for the database
    # Keep it as bytes for storage in the database
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    if user is None:
        # Create user
        user = User(name=username, admin=True)
        db.add(user)
        db.commit()
        print(f"Created user: {username}")
        
        # Create separate user info record
        try:
            # Determine columns in the UserInfo table
            user_info_columns = inspect(UserInfo).columns.keys()
            
            # Create user info with required fields only
            user_info_data = {
                'username': username, 
                'password': password_hash
            }
            
            # Add optional fields if they exist in the model
            if 'is_authorized' in user_info_columns:
                user_info_data['is_authorized'] = True
                
            # Create the UserInfo record
            user_info = UserInfo(**user_info_data)
            db.add(user_info)
            db.commit()
            print(f"Created authentication for user: {username}")
        except Exception as e:
            print(f"Error adding user authentication: {str(e)}")
            # Fallback method if the above fails
            try:
                db.execute(
                    "INSERT INTO users_info (username, password, is_authorized) VALUES (:username, :password, :is_authorized)",
                    {"username": username, "password": password_hash, "is_authorized": True}
                )
                db.commit()
                print(f"Added authentication for user {username} via direct SQL")
            except Exception as e2:
                print(f"Fallback method also failed: {str(e2)}")
    else:
        print(f"User {username} already exists. Updating password...")
        # Update password
        try:
            user_info = db.query(UserInfo).filter_by(username=username).first()
            if user_info:
                user_info.password = password_hash
                db.commit()
                print(f"Password updated for user: {username}")
            else:
                # Determine columns in the UserInfo table
                user_info_columns = inspect(UserInfo).columns.keys()
                
                # Create user info with required fields only
                user_info_data = {
                    'username': username, 
                    'password': password_hash
                }
                
                # Add optional fields if they exist in the model
                if 'is_authorized' in user_info_columns:
                    user_info_data['is_authorized'] = True
                
                user_info = UserInfo(**user_info_data)
                db.add(user_info)
                db.commit()
                print(f"Created authentication for existing user: {username}")
        except Exception as e:
            print(f"Error updating authentication: {str(e)}")
    
    # Ensure user has admin privileges
    if not user.admin:
        user.admin = True
        db.commit()
        print(f"Granted admin privileges to: {username}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create JupyterHub admin user')
    parser.add_argument('username', help='Admin username')
    parser.add_argument('password', help='Admin password')
    
    args = parser.parse_args()
    
    create_admin_user(args.username, args.password)
    print(f"Admin user setup complete. You can now log in with username: {args.username}") 