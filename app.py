import streamlit as st
import base64
import bcrypt
import smtplib
import random
import time
import os
import pandas as pd
import mysql.connector as msc
from email.utils import formataddr
from PIL import Image

# Set page configuration and permanent black background
st.set_page_config(
    page_title="NSTI Leave Management",
    page_icon="https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set permanent black background using custom CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #000 !important;
        }
        body {
            background-color: #000 !important;
        }
    </style>
""", unsafe_allow_html=True)



def verify_password(plain_password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

class mysql_connection:
    def __init__(self):
        self.conn = None
        self.connection()

    def connection(self):
        try:
            self.conn = msc.connect(
                host='localhost',
                user='root',
                password='root',
                database='Nsti_manage'
            )
            if self.conn.is_connected():
                pass
        except Exception as e:
            print(f'Cannot connect to database: {e}')

class login(mysql_connection):
    def __init__(self):
        super().__init__()
        self.main()

    def get_base64_image(self, image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    def otp_page(self, user_email):
        st.markdown("<h1 style='text-align: center; color: white;'>OTP PAGE</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: white;'>Enter the OTP sent to your email</h2>", unsafe_allow_html=True)

        otp_entered = st.text_input("Enter OTP", placeholder="Enter the OTP sent to your email", label_visibility="collapsed").strip()

        sender_email = "gauravkashyapnstik@gmail.com"
        sender_password = "tugvkfvyygzunsfe"
        formatted_sender = formataddr(("NSTI Leave Management System", sender_email))

        if not st.session_state.get("otp_sent", False):
            st.session_state.otp = random.randint(100000, 999999)
            # print(f"Generated OTP: {st.session_state.otp}")  # For debugging purposes
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    subject = "Your OTP Code"
                    message = f"Your OTP is: {st.session_state.otp}"
                    email_message = f"Subject: {subject}\nFrom: {formatted_sender}\nTo: {user_email}\n\n{message}"
                    server.sendmail(sender_email, user_email, email_message)
                    st.success("OTP sent to your email!")
                    st.session_state.otp_sent = True
                    
            except Exception as e:
                st.error(f"Failed to send email: {e}")
                st.session_state.page = "login"
                st.rerun()

        verify = st.button("Verify OTP",use_container_width=True)
        if verify:
            if otp_entered and otp_entered.isdigit() and int(otp_entered) == st.session_state.otp:
                st.success("OTP verified successfully!")

                # Check if stored password matches '1234'
                cursor = self.conn.cursor()
                cursor.execute('SELECT password FROM user WHERE username = %s', (user_email,))
                user_result = cursor.fetchone()
                cursor.execute('SELECT password FROM professional WHERE username = %s', (user_email,))
                pro_result = cursor.fetchone()
                result = user_result or pro_result

                if result and verify_password('Test@1234', result[0]):
                    st.session_state.page = "change_password"
                    st.session_state.otp_sent = False
                    st.rerun()
                else:
                    cursor.execute('SELECT * FROM user WHERE username = %s', (user_email,))
                    result = cursor.fetchone()
                    if result:
                        st.session_state.page = "home"
                    else:
                        cursor.execute('SELECT * FROM professional WHERE username = %s', (user_email,))
                        result = cursor.fetchone()
                        if result:
                            st.session_state.page = "professional"
                        else:
                            st.session_state.page = "login"
                   
                    st.session_state.otp_sent = False
                    st.rerun()
            else:
                st.error("Invalid OTP. Please try again.")

    def home(self):

        # Custom CSS for colorful design
        st.markdown("""
        <style>
            .main {
                background-color: #f0f2f6;
            }
            .header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            .section {
                background-color: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 1.5rem;
            }
            .card {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left: 4px solid #2a5298;
            }
            .visitors {
                background-color: #e3f2fd;
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
            }
            .footer {
                text-align: center;
                padding: 1rem;
                margin-top: 2rem;
                background-color: #2a5298;
                color: white;
                border-radius: 10px;
            }
        </style>
        """, unsafe_allow_html=True)

        # Header with centered logo and title
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Display the logo image in the center column with markdown for alignment and styling
            st.markdown(
                """
                <div style="display: flex; justify-content: center; align-items: center;">
                    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSfw5bS6uDVpRg_9Xxg5_J8wY-M6LcO2vJCAatx7fG1fOYGcNDK8c8p0TAaFda6iDkTcoM&usqp=CAU"
                         alt="NSTI Logo"
                         style="width:190px; height:190px; border-radius: 16px; box-shadow: 0 4px 16px #888; margin-top: 24px; margin-bottom: 10px;">
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.markdown("""
        <div class="header">
            <h1>NATIONAL SKILL TRAINING INSTITUTE KANPUR</h1>
            <h3>Ministry of Skill Development and Entrepreneurship</h3>
            <p>Azadi Ka Amrit Mahotsav</p>
        </div>
        """, unsafe_allow_html=True)

        # Main content sections
        st.markdown("""
        <div class="section">
            <h2 style="color: #1e3c72;">OUR FACILITIES</h2>
            <div class="card">
                <h3 style="color: #2a5298;">🏫 Modern Classrooms</h3>
                <p>State-of-the-art learning environments with digital facilities</p>
            </div>
            <div class="card">
                <h3 style="color: #2a5298;">🔬 Advanced Labs</h3>
                <p>Industry-standard laboratories for practical skill development</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Skills sections in colorful columns
        st.markdown("""
        <div class="section">
            <h2 style="color: #1e3c72;">OUR PROGRAMS</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div style="background: #e8f5e9; padding: 1rem; border-radius: 10px;">
                <h3 style="color: black;">📚 BIBLIA'S SKILLS</h3>
                <ul style="color: black;">
                <li><b>Bhart Stills</b></li>
                <li>Nihil Online</li>
                <li>Sulfi Attendance</li>
                </ul>
            </div>
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px;">
                <h3 style="color: black;">💻 E-LEARNING</h3>
                <ul style="color: black;">
                <li><b>E-BHR</b></li>
                <li>IBM</li>
                <li>Cisco</li>
                <li>Quart Employability Skills</li>
                </ul>
            </div>
            <div style="background: #f3e5f5; padding: 1rem; border-radius: 10px;">
                <h3 style="color: black;">🌐 DIGITAL PLATFORM</h3>
                <ul style="color: black;">
                <li><b>Student Attendance</b></li>
                <li>Sourceer</li>
                <li>Gov Email</li>
                </ul>
            </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Visitors and Address section
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("""
            <div class="visitors">
                <h3 style="color: red;">👥 VISITORS</h3>
                <p style="color: black;"><b>Rasi Vision:</b> 26,318,923</p>
                <p style="color: black;"><b>Unique Vision:</b> 1,557,540</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="section">
                <h3 style="color: #1e3c72;">📍 CONTACT US</h3>
                <p style="color: black;"><b>Address:</b> NSTI KANPUR, Udhyog Nagar, near CTI Chouraha, Sanjay Nagar, Kanpur, Uttar Pradesh 208022</p>
                <p style="color: black;"><b>Phone:</b> 0512-2977244, 2296088</p>
                <p style="color: black;"><b>Email:</b> rdace.ujr-mad@agav.in, nsti-kanpur@dgt.gov.in</p>
                <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            """, unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div class="footer">
            <p>© 2025 National Skill Training Institute, Kanpur. All Rights Reserved.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def change_password_page_for_admin(self):
        st.markdown("<h1 style='text-align: center; color: red;'>Change Password</h1>", unsafe_allow_html=True)
        cursor = self.conn.cursor()
        
        # Input for email
        email_to_change = st.text_input("Email", label_visibility="collapsed", placeholder="Enter user's email")
        
        if st.button("Change Password", use_container_width=True):
            if not email_to_change:
                st.warning("Please enter an email.")
                return
            
            try:
                # Check if user exists in either table
                cursor.execute('SELECT * FROM user WHERE username = %s', (email_to_change,))
                user_result = cursor.fetchone()
                cursor.execute('SELECT * FROM professional WHERE username = %s', (email_to_change,))
                pro_result = cursor.fetchone()

                if not user_result and not pro_result:
                    st.error("User not found.")
                    return
                    
                # Reset password to default
                new_password = "Test@1234"
                hashed_password = hash_password(new_password)
                
                if user_result:
                    cursor.execute('UPDATE user SET password = %s WHERE username = %s', 
                                (hashed_password, email_to_change))
                    self.conn.commit()
                    subject_pass_reset="Password reset successfully"
                    
                    # Send email notification
                    self.send_mail(subject_pass_reset,
                        email_to_change, 
                        "Your password has been reset by admin.\n\n"
                        f"Your new password is: {new_password}\n\n"
                        "Please change it after logging in."
                    )
                    
                    st.success("Password reset successfully for trainee!")
                    
                elif pro_result:
                    cursor.execute('UPDATE professional SET password = %s WHERE username = %s', 
                                (hashed_password, email_to_change))
                    self.conn.commit()
                    
                    # Send email notification
                    subject_pass_reset="Password reset successfully"
                    self.send_mail(subject_pass_reset,
                        email_to_change, 
                        "Your password has been reset by admin.\n\n"
                        f"Your new password is: {new_password}\n\n"
                        "Please change it after logging in."
                    )
                    
                    st.success("Password reset successfully for professional!")
                
                # Return to admin page
                st.session_state.page = "professional"
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                self.conn.rollback()
            finally:
                cursor.close()
            
            
           
    def loginpage(self):
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))


        # Construct the path to the image
        image_path = os.path.join(current_dir, "bg.JPG")
        image_base64 = self.get_base64_image(image_path)

        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{image_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            .title {{
                position: absolute; 
                top: 80px;
                text-align: center;
                color: white;
                font-family: 'Times New Roman', Times, serif;
                font-size: 42px;
                font-weight: bold;
                margin-top: 100px;
                background:dimgrey;
                padding: 0px 15px 0px 10px;
                border-radius: 10px;
                width: 100%;
                margin-left: auto;
                margin-right: auto;
            }}
            .login-box {{
                padding: 10px;
                border-radius: 15px;
                width: 400px;
                margin: 130px auto;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
                text-align: center;
            }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:30px;' class='title'>LEAVE MANAGEMENT SYSTEM</div>", unsafe_allow_html=True)

        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='background-color: black; padding: 10px; border-radius: 5px; position: relative; top: 20px; left: 0px;'>"
            "<h3 style='color:white; font-family: \"Times New Roman\", Times, serif;'>Email</h3>"
            "</div>",
            unsafe_allow_html=True,
        )
        username = st.text_input(" ", placeholder="Enter your email", label_visibility="collapsed").strip()
        st.markdown(
            "<div style='background-color: black; padding: 10px; border-radius: 5px; position: relative; top: 20px; left: 0px;'>"
            "<h3 style='color:white; font-family: \"Times New Roman\", Times, serif;'>Password</h3>"
            "</div>",
            unsafe_allow_html=True,
        )

        password = st.text_input(" ", placeholder="Enter your password", type="password", label_visibility="collapsed").strip()
        login_button = st.button("Login", use_container_width=True)

        if login_button:
            cursor = self.conn.cursor()

            #password training officer
            cursor.execute('SELECT password FROM professional WHERE username = %s', (username,))
            pro_result = cursor.fetchone()

            #password student
            cursor.execute('SELECT password FROM user WHERE username = %s', (username,))
            user_result = cursor.fetchone()

            if pro_result:
                stored_password = pro_result[0]
                if verify_password(password, stored_password):
                    st.success("Login successful (Professional)!")
                    st.session_state.page = "otp"
                    st.session_state.email = username
                   
                    st.rerun()
                else:
                    st.error("Invalid password for professional user.")
            elif user_result:
                stored_password = user_result[0]
                if verify_password(password, stored_password):
                    st.success("Login successful (Student)!")
                    st.session_state.page = "otp"
                    st.session_state.email = username
                    st.rerun()
                else:
                    st.error("Invalid password for user.")
            else:
                st.error("Username not found.")

        st.markdown("</div>", unsafe_allow_html=True)
    
    def send_mail(self, subject,email,message):
        sender_email = "gauravkashyapnstik@gmail.com"
        sender_password = "tugvkfvyygzunsfe"
        formatted_sender = formataddr(("NSTI Leave Management System", sender_email))
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                subject_to_send = subject
                if not subject_to_send:
                    subject_to_send = "Notification from NSTI Leave Management"

               
                email_message = f"Subject: {subject_to_send}\nFrom: {formatted_sender}\nTo: {email}\n\n{message}"
                server.sendmail(sender_email, email, email_message)
                st.success("Email sent successfully!")

        except Exception as e:
            st.error(f"Failed to send email: {e}")

    def all_users(self):
        st.markdown("<h1 style='text-align: center; color: white;'>All Users</h1>", unsafe_allow_html=True)
        
        cursor = self.conn.cursor()

        # Dropdown for selecting user type
        user_type = st.selectbox("Select User Type", ["User", "Professional"])

        if user_type == "User":
            cursor.execute('SELECT id, name, image, username, address, trade_id, status FROM user')
            users = cursor.fetchall()

            if not users:
                st.warning("No users found in the User table.")
                return

            df = pd.DataFrame(users, columns=['ID', 'Name', 'Image', 'Username', 'Address', 'Trade ID', 'Status'])
            st.dataframe(df, use_container_width=True)

        elif user_type == "Professional":
            cursor.execute('''
                SELECT p.id, p.name, p.image, p.username, p.post, p.address, d.department_name
                FROM professional p
                LEFT JOIN department d ON p.department_id = d.id
            ''')
            professionals = cursor.fetchall()

            if not professionals:
                st.warning("No users found in the Professional table.")
                return

            df = pd.DataFrame(professionals, columns=['ID', 'Name', 'Image', 'Username', 'Post', 'Address', 'Department Name'])
            st.dataframe(df, use_container_width=True)



    def change_password(self, email):
        
        st.markdown("<h1 style='text-align: center; color: white;'>Change Password</h1>", unsafe_allow_html=True)
        cursor = self.conn.cursor()
        cursor.execute('SELECT password FROM user WHERE username = %s', (email,))
        user_result = cursor.fetchone()

        cursor.execute('SELECT password FROM professional WHERE username = %s', (email,))
        pro_result = cursor.fetchone()

        if user_result or pro_result:

            if user_result is not None:
                stored_password = user_result[0]
            else:
                stored_password = pro_result[0]


            current_pass = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            check_type = st.selectbox("Select User Type", ["Student", "Professional"])
            if current_pass== new_password:
                st.warning("Current password and new password cannot be the same.")
            else:
                if st.button("Change Password",use_container_width=True):
                    if verify_password(current_pass, stored_password):
                        if new_password == confirm_password:
                            hashed_new_password = hash_password(new_password)
                            if check_type == "Student":
                                cursor.execute('UPDATE user SET password = %s WHERE username = %s', (hashed_new_password, email))
                                st.session_state.page = "home"
                        
                        
                            else:
                                cursor.execute('UPDATE professional SET password = %s WHERE username = %s', (hashed_new_password, email))
                                st.session_state.page = "professional"
                            self.conn.commit()
                            st.success("Password changed successfully!")
                            
                            st.rerun()
                        else:
                            st.error("Passwords do not match.")
                    else:
                        st.error("Current password is incorrect.")

    def profile_page(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (st.session_state.email,))
        result = cursor.fetchone()
        # Add image placeholder at center, large size
        # Show current image or placeholder (image is stored as BLOB in result[5])
        if result and result[2]:
            image_bytes = result[2]
            st.markdown(
                "<div style='display: flex; justify-content: center;'>"
                f"<img src='data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}' width='320' style='border-radius: 10px; box-shadow: 0 4px 16px #888;' alt='Profile Image'/>"
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='display: flex; justify-content: center;'>"
                "<img src='https://nstikanpur.dgt.gov.in/themes/nsti_barrio_old123_bk/images/emblem-black.png' width='320' style='border-radius: 10px; box-shadow: 0 4px 16px #888;' alt='Profile Image'/>"
                "</div>",
                unsafe_allow_html=True
            )

        # Allow image upload/change, store in result[5] (BLOB)
        uploaded_image = st.file_uploader("Upload/Change Profile Image", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None and result:
            img_bytes = uploaded_image.read()
            cursor.execute('UPDATE user SET image = %s WHERE username = %s', (img_bytes, result[3]))
            self.conn.commit()
            st.success("Profile image updated! Please refresh to see changes.")
        if result:
            st.markdown(
                f"<h2 style='color: Aqua; text-shadow: 1px 1px 0 grey, -0px -0px 0 grey, 0px -0px 0 grey, -0px 0px 0 grey;'>{result[1]}</h2>",
                unsafe_allow_html=True
            )
            st.write(f"Email: {result[3]}")
        st.markdown("<h3>Description:</h3>", unsafe_allow_html=True)
        st.write("This is the profile page for the user. Here you can view and update your profile image and see your details.")

    def leave_application(self):
        st.markdown("<h1 style='text-align: center; color: mediumblue; text-shadow: 2px 2px 0px grey'>Leave Application</h1>", unsafe_allow_html=True)
        leave_type = st.selectbox("Select Leave Type", ["Medical Leave", "Home-Leave","other"])
        if leave_type == "other":
            leave_type = st.text_input("Enter Leave Type", placeholder="For Examination, For Marriage, etc...", label_visibility="collapsed")
        leave_type = leave_type.strip()
        days = st.number_input("Number of Days", min_value=1, max_value=10, step=1, label_visibility="collapsed")
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT trade_id FROM user WHERE username = %s', (st.session_state.email,))
        user_trade_id = cursor.fetchone()[0]

        cursor.execute('SELECT trade_name FROM trade WHERE id = %s', (user_trade_id,))
        user_trade = cursor.fetchone()[0]

        leave_reason = st.text_area("Leave Reason", placeholder="Enter the reason for leave (at least 10 words)", label_visibility="collapsed")
        
        if leave_reason:
            word_count = len(leave_reason.split())
            st.write(f"Words written: {word_count}")
            
            if leave_reason == "":
                st.warning("Please write at least 10 words.")
            else:
                if st.button("Submit Leave Application",use_container_width=True):
                    if not leave_type or not leave_reason:
                        st.warning("Please fill in all fields.")
                    else:
                 
                        cursor.execute('SELECT * FROM leave_application WHERE email = %s AND status = %s', (st.session_state.email, '2'))
                        pending_applications = cursor.fetchall()
                    
                    if pending_applications:
                        st.warning("You already have a pending leave application.")
                    else:
                        if word_count <= 10:
                            st.warning("Please write at least 10 words.")
                        else:
                            cursor.execute('SELECT * FROM user WHERE username = %s', (st.session_state.email,))
                            result = cursor.fetchone()  
                            name = result[1]
                            email = result[3]
                            trade = user_trade_id
                            
                            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                            # When submitting a new application:
                            cursor.execute('''
                                INSERT INTO leave_application 
                                (name, email, leave_type, leave_description, trade_id, days, time_of_application, status, to_approval, dd_approval) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, '2', '2', '2')
                            ''', (name, email, leave_type, leave_reason, trade, days, current_time))  # '2' for pending status
                                                       
                            self.conn.commit()
                            
                            # Update user status to pending (if needed)
                            cursor.execute('UPDATE user SET status = %s WHERE username = %s', ('2', email))
                            self.conn.commit()
                            
                            st.success("Leave application submitted successfully! Status: Pending")
                            time.sleep(2)
                            st.rerun()
    
    def delete_user_for_admin(self):
            st.markdown("<h1 style='text-align: center; color: red;'>Delete User</h1>", unsafe_allow_html=True)
            cursor = self.conn.cursor()
            user_type = st.selectbox("User Type", ["Trainee", "Professional"])
            email = st.text_input("Enter Email of User to Delete")

            if st.button("Delete User",use_container_width=True):
                if not email:
                    st.warning("Please enter an email.")
                else:
                    if user_type == "Trainee":
                        cursor.execute("SELECT * FROM user WHERE username = %s", (email,))
                        user = cursor.fetchone()
                        if user:
                            cursor.execute("DELETE FROM user WHERE username = %s", (email,))
                            self.conn.commit()
                            st.success("Trainee deleted successfully.")
                            subject_del="Notification from Management"
                            self.send_mail(subject_del,
                                email, 
                                "Your account has been deleted by admin. If this was a mistake, please contact support."
                            )
                        else:
                            st.error("Trainee not found.")
                    else:
                        cursor.execute("SELECT * FROM professional WHERE username = %s", (email,))
                        user = cursor.fetchone()
                        if user:
                            if user[4] == "Admin":
                                st.error("Cannot delete Admin user.")
                            else:
                                cursor.execute("DELETE FROM professional WHERE username = %s", (email,))
                                self.conn.commit()
                                st.success("Professional deleted successfully.")
                                subject = "Account Deletion Notification"
                                self.send_mail(subject,
                                    email, 
                                    "Your account has been deleted by admin. If this was a mistake, please contact support."
                                )
                        else:
                            st.error("Professional not found.")


    def update_details_by_admin(self):
        st.markdown("<h1 style='text-align: center; color: orange;'>Update User Details</h1>", unsafe_allow_html=True)
        cursor = None
        
        try:
            # Initialize session state only once
            if "update_admin_data" not in st.session_state:
                st.session_state.update_admin_data = {
                    "user_fetched": False,
                    "user_data": None,
                    "selected_type": None,
                    "email_entered": ""
                }

            # Basic Inputs
            user_type = st.selectbox("User Type", ["Trainee", "Professional"])
            email = st.text_input("Enter Email of User to Update", 
                                value=st.session_state.update_admin_data["email_entered"]).strip()

            fetch_button = st.button("Fetch User Details")
            
            if fetch_button:
                if not email:
                    st.warning("Please enter an email.")
                    return

                cursor = self.conn.cursor()
                st.session_state.update_admin_data["selected_type"] = user_type
                st.session_state.update_admin_data["email_entered"] = email

                if user_type == "Trainee":
                    # Single optimized query for trainee
                    cursor.execute("""
                        SELECT u.name, u.address, u.trade_id, t.trade_name 
                        FROM user u
                        LEFT JOIN trade t ON u.trade_id = t.id
                        WHERE u.username = %s
                    """, (email,))
                    user = cursor.fetchone()

                    if not user:
                        st.error("Trainee not found.")
                        return

                else:  # Professional
                    # Single query for professional
                    cursor.execute("""
                        SELECT name, address, post 
                        FROM professional 
                        WHERE username = %s AND post != 'Admin'
                    """, (email,))
                    user = cursor.fetchone()

                    if not user:
                        st.error("Professional not found or is Admin.")
                        return

                st.session_state.update_admin_data["user_fetched"] = True
                st.session_state.update_admin_data["user_data"] = user
                st.success(f"{user_type} found!")

            # Display update form if user data is available
            if st.session_state.update_admin_data["user_fetched"]:
                user = st.session_state.update_admin_data["user_data"]
                user_type = st.session_state.update_admin_data["selected_type"]
                email = st.session_state.update_admin_data["email_entered"]

                if user_type == "Trainee":
                    # Pre-fetch trade data once
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT id, trade_name FROM trade")
                    trades = cursor.fetchall()
                    trade_dict = {trade_name: id_ for id_, trade_name in trades}
                    trade_names = list(trade_dict.keys())
                    current_trade = user[3] if user[3] else None

                    fields = st.multiselect("Select fields to update", 
                                        ["Name", "Address", "Trade"], 
                                        key="trainee_fields")

                    updates = {}
                    if "Name" in fields:
                        updates["name"] = st.text_input("New Name", 
                                                    value=user[0], 
                                                    key="trainee_name")
                    if "Address" in fields:
                        updates["address"] = st.text_input("New Address", 
                                                        value=user[1], 
                                                        key="trainee_address")
                    if "Trade" in fields:
                        selected_trade = st.selectbox(
                            "New Trade",
                            trade_names,
                            index=trade_names.index(current_trade) if current_trade in trade_names else 0,
                            key="trainee_trade"
                        )
                        updates["trade_id"] = trade_dict[selected_trade]

                    if st.button("Update Trainee", key="update_trainee_btn"):
                        if updates:
                            try:
                                cursor = self.conn.cursor()
                                set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
                                query = f"UPDATE user SET {set_clause} WHERE username = %s"
                                cursor.execute(query, tuple(updates.values()) + (email,))
                                self.conn.commit()
                                st.success("Trainee details updated successfully!")
                                
                                # Clear the form after successful update
                                st.session_state.update_admin_data["user_fetched"] = False
                                # Prepare update summary for email (only updated fields)
                                update_msgs = []
                                if "name" in updates:
                                    update_msgs.append(f"New Name: {updates['name']}")
                                if "address" in updates:
                                    update_msgs.append(f"New Address: {updates['address']}")
                                if "trade_id" in updates:
                                    update_msgs.append(f"New Trade: {trade_names[trade_names.index(current_trade)] if not updates['trade_id'] else [k for k,v in trade_dict.items() if v == updates['trade_id']][0]}")

                                if update_msgs:
                                    update_summary = "\n".join(update_msgs)
                                    subject = "Detail Updation by administration."
                                    self.send_mail(subject,
                                        email,
                                        f"Your details have been updated by admin.\n\n{update_summary}"
                                    )
                            except Exception as e:
                                st.error(f"Update failed: {str(e)}")
                                self.conn.rollback()

                else:  # Professional
                    fields = st.multiselect("Select fields to update", 
                                        ["Name", "Address", "Post"], 
                                        key="pro_fields")

                    updates = {}
                    if "Name" in fields:
                        updates["name"] = st.text_input("New Name", 
                                                    value=user[0], 
                                                    key="pro_name")
                    if "Address" in fields:
                        updates["address"] = st.text_input("New Address", 
                                                        value=user[1], 
                                                        key="pro_address")
                    if "Post" in fields:
                        post_options = ["training_officer", "Director", "Warden", "Joint Director"]
                        current_post = user[2]
                        selected_post = st.selectbox(
                            "New Post",
                            post_options,
                            index=post_options.index(current_post) if current_post in post_options else 0,
                            key="pro_post"
                        )
                        updates["post"] = selected_post

                    if st.button("Update Professional", key="update_pro_btn"):
                        if updates:
                            try:
                                cursor = self.conn.cursor()
                                set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
                                query = f"UPDATE professional SET {set_clause} WHERE username = %s"
                                cursor.execute(query, tuple(updates.values()) + (email,))
                                self.conn.commit()
                                st.success("Professional details updated successfully!")
                                
                                # Prepare update summary for email
                                update_msgs = []
                                if "name" in updates:
                                    update_msgs.append(f"New Name: {updates['name']}")
                                if "address" in updates:
                                    update_msgs.append(f"New Address: {updates['address']}")
                                if "post" in updates:
                                    update_msgs.append(f"New Post: {updates['post']}")

                                if update_msgs:
                                    update_summary = "\n".join(update_msgs)
                                    subject_pro = "Detail Updation by administration."
                                    self.send_mail(subject_pro,
                                        email,
                                        f"Your details have been updated by admin.\n\n{update_summary}"
                                    )

                                # Clear the form after successful update
                                st.session_state.update_admin_data["user_fetched"] = False
                            except Exception as e:
                                st.error(f"Update failed: {str(e)}")
                                self.conn.rollback()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            if cursor:
                cursor.close()


    def professional_page(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM professional WHERE username = %s', (st.session_state.email,))
        result = cursor.fetchone()
        
        if result[4]=='Admin':


        
            # Add image and name above sidebar
            # Sidebar: Show profile image (from DB if available), name, and email
            if result[5]:
                # result[5] is expected to be BLOB (bytes)
                image_bytes = result[5]
                image_base64 = base64.b64encode(image_bytes).decode()
                image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
            else:
                image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

            st.sidebar.markdown(
                "<div style='text-align: center;'>"
                f"{image_html}"
                f"<h2 style='color: #0691FF; font-family: Lucida Bright, Times, serif; margin-bottom: 0;'>{result[1].capitalize()}</h2>"
                f"<h4 style='color: white; margin-top: 0;'>{result[2]}</h4>"
                "</div>",
                unsafe_allow_html=True
            )

            choice = st.sidebar.selectbox("Home", ["Home", "Profile", "Register-User", "Delete User", "Update-User", "Change Password","All_Users"])
            logout = st.sidebar.button("Logout", use_container_width=True)
            if logout:
                st.session_state.page = "login"
                st.session_state.otp_sent = False
                st.session_state.email = None
                st.session_state.otp = None
                st.rerun()

            if choice == "Home":
                self.home()

            elif choice == "Change Password":
                self.change_password_page_for_admin()
            
            elif choice=="All_Users":
                self.all_users()

            elif choice == "Profile":
                cursor.execute('SELECT * FROM professional WHERE username = %s', (st.session_state.email,))
                result = cursor.fetchone()
                st.markdown("""
                <h1 style='
                text-align: center; 
                color: #2471A3; 
                text-shadow: 
                -1px -1px 0 #D6EAF8, 
                1px -1px 0 #D6EAF8, 
                -1px 1px 0 #D6EAF8, 
                1px 1px 0 #D6EAF8;
                border: 2px solid grey;
                border-radius: 12px;
                padding: 12px 0;
                font-family: "Segoe UI", Arial, sans-serif;
                font-weight: bold;
                margin-bottom: 24px;
                '>NATIONAL SKILL TRAINING INSTITUTE</h1>
                """, unsafe_allow_html=True)
                # Show current image or placeholder
                if result[5]:
                    image_bytes = result[5]
                    st.markdown(
                        "<div style='display: flex; justify-content: center;'>"
                        f"<img src='data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}' width='220' style='border-radius: 10px;' alt='Profile Image'/>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div style='display: flex; justify-content: center;'>"
                        "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='220' style='border-radius: 10px;' alt='Profile Image'/>"
                        "</div>",
                        unsafe_allow_html=True
                    )

                # Allow image upload/change
                uploaded_image = st.file_uploader("Upload/Change Profile Image", type=["png", "jpg", "jpeg"])
                if uploaded_image is not None:
                    img_bytes = uploaded_image.read()
                    cursor.execute('UPDATE professional SET image = %s WHERE username = %s', (img_bytes, result[2]))
                    self.conn.commit()
                    st.success("Profile image updated! Please refresh to see changes.")

                st.write(f"Name: {result[1]}")
                st.write(f"Email: {result[2]}")
            elif choice =="Delete User":
                st.markdown("""
                <h1 style='
                text-align: center; 
                color: #2471A3; 
                text-shadow: 
                -1px -1px 0 #D6EAF8, 
                1px -1px 0 #D6EAF8, 
                -1px 1px 0 #D6EAF8, 
                1px 1px 0 #D6EAF8;
                border: 2px solid grey;
                border-radius: 12px;
                padding: 12px 0;
                font-family: "Segoe UI", Arial, sans-serif;
                font-weight: bold;
                margin-bottom: 24px;
                '>NATIONAL SKILL TRAINING INSTITUTE</h1>
            """, unsafe_allow_html=True)
                
                self.delete_user_for_admin()

            elif choice=="Update-User":
                st.markdown("""
                <h1 style='
                text-align: center; 
                color: #2471A3; 
                text-shadow: 
                -1px -1px 0 #D6EAF8, 
                1px -1px 0 #D6EAF8, 
                -1px 1px 0 #D6EAF8, 
                1px 1px 0 #D6EAF8;
                border: 2px solid grey;
                border-radius: 12px;
                padding: 12px 0;
                font-family: "Segoe UI", Arial, sans-serif;
                font-weight: bold;
                margin-bottom: 24px;
                '>NATIONAL SKILL TRAINING INSTITUTE</h1>
            """, unsafe_allow_html=True)
                
                self.update_details_by_admin()

            elif choice == "Register-User":
                st.markdown("""
                <h1 style='
                    text-align: center; 
                    color: #2C3E50; 
                    border: 2px solid grey; 
                    border-radius: 10px; 
                    padding: 10px 0; 
                    background: #F4F6F7;
                    font-family: "Segoe UI", Arial, sans-serif;
                    font-weight: bold;
                    margin-bottom: 24px;
                '>Register User</h1>
            """, unsafe_allow_html=True)
                
             
                cursor = self.conn.cursor()
                user_type = st.selectbox("Register as", ["Trainee", "Director", "Training Officer"])

             
                name_user = st.text_input("Name", placeholder="Enter name", key="reg_name").strip()

                email = st.text_input("Email", placeholder="Enter email", key="reg_email").strip()

                
                password_user = 'Test@1234'  # Default password for registration

            
                address = st.text_input("Address", placeholder="Enter address", key="reg_address")

                if user_type == "Trainee":
                    cursor.execute('SELECT * FROM trade')
                    trade_result = cursor.fetchall()
                    trade_list = [trade[1] for trade in trade_result]
                    trade = st.selectbox("Trade", trade_list, index=0, key="reg_trade")

                elif user_type == "Training Officer":
     
                    cursor.execute('SELECT id, department_name FROM department')
                    departments = cursor.fetchall()
                    department_options = {str(row[0]): row[1] for row in departments}
                    department_display = [f"{name} (ID: {id_})" for id_, name in department_options.items()]
                    selected_department = st.selectbox("Department", department_display, key="reg_department")
                    # Extract department id from selection
                    department = list(department_options.keys())[department_display.index(selected_department)]

                elif user_type == "Director":
                    department = None  # Not needed for director

                if st.button("Register",use_container_width=True):
                    if not (name_user and email and password_user and address):
                        st.warning("Please fill in all fields.")
                    elif len(password_user) < 4:
                        st.warning("Password must be at least 4 characters long.")
                    elif len(name_user) < 3:
                        st.warning("Name must be at least 3 characters long.")
                    elif len(address) < 5:
                        st.warning("Address must be at least 5 characters long.")
                    else:
                        if user_type == "Trainee":
                            cursor.execute('SELECT * FROM user WHERE username = %s', (email,))
                            result = cursor.fetchone()
                            if result:
                                st.warning("Email already exists.")
                            else:
                                trade_id = trade_result[trade_list.index(trade)][0]
                                cursor.execute(
                                    'INSERT INTO user (name, username, password, address, trade_id) VALUES (%s, %s, %s, %s, %s)',
                                    (name_user, email, hash_password(password_user), address, trade_id)
                                )
                                self.conn.commit()
                                st.success("Trainee registered successfully!")
                                subject_for_registration="Registration Mail"
                                self.send_mail(subject_for_registration,email, "You have been registered as a Trainee. Please login to the system for the first time.\nUsername: " + email + "\nPassword: " + password_user+ "\n\nPlease change your password after first login.")
                        else:
                            cursor.execute('SELECT * FROM professional WHERE username = %s', (email,))
                            result = cursor.fetchone()
                            if result:
                                st.warning("Email already exists.")
                            else:
                                if user_type == "Director":
                                    post = "Director"
                                    depart_id = None
                                else:
                                    post = "training_officer"
                                    depart_id = int(department)
                                cursor.execute(
                                    'INSERT INTO professional (name, username, password, address, post, department_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                    (name_user, email, hash_password(password_user), address, post, depart_id)
                                )
                                self.conn.commit()
                                st.success(f"{user_type} registered successfully!")
                                subject_for_register_pro="Registration Mail"
                                self.send_mail(subject_for_register_pro,email, "You have been registered as a " + user_type + ". Please login to the system for the first time.\nUsername: " + email + "\nPassword: " + password_user+ "\n\nPlease change your password after first login.")




        elif result[4]=='training_officer':
            self.training_officer_page()

        elif result[4]=='Warden':
            pass

        elif result[4]=='Joint Director' or result[4]=='Director':
            self.director_page()
       
                
            
    def training_officer_profile(self):
        st.markdown("""
            <h1 style='
            text-align: center; 
            color: #2471A3; 
            text-shadow: 
            -1px -1px 0 #D6EAF8, 
            1px -1px 0 #D6EAF8, 
            -1px 1px 0 #D6EAF8, 
            1px 1px 0 #D6EAF8;
            border: 2px solid grey;
            border-radius: 12px;
            padding: 12px 0;
            font-family: "Segoe UI", Arial, sans-serif;
            font-weight: bold;
            margin-bottom: 24px;
            '>NATIONAL SKILL TRAINING INSTITUTE</h1>
        """, unsafe_allow_html=True)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM professional WHERE username = %s', (st.session_state.email,))
        result = cursor.fetchone()
        # Add image placeholder at center, large size
        # Show current image or placeholder (image is stored as BLOB in result[5])
        if result and result[5]:
            image_bytes = result[5]
            st.markdown(
                "<div style='display: flex; justify-content: center;'>"
                f"<img src='data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}' width='320' style='border-radius: 10px; box-shadow: 0 4px 16px #888;' alt='Profile Image'/>"
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='display: flex; justify-content: center;'>"
                "<img src='https://nstikanpur.dgt.gov.in/themes/nsti_barrio_old123_bk/images/emblem-black.png' width='320' style='border-radius: 10px; box-shadow: 0 4px 16px #888;' alt='Profile Image'/>"
                "</div>",
                unsafe_allow_html=True
            )

        # Allow image upload/change, store in result[5] (BLOB)
        uploaded_image = st.file_uploader("Upload/Change Profile Image", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None and result:
            img_bytes = uploaded_image.read()
            cursor.execute('UPDATE professional SET image = %s WHERE username = %s', (img_bytes, result[2]))
            self.conn.commit()
            st.success("Profile image updated! Please refresh to see changes.")
        if result:
            st.markdown(
                f"<h2 style='color: blue; text-shadow: 1px 1px 0 grey, -0px -0px 0 grey, 0px -0px 0 grey, -0px 0px 0 grey;'>{result[1]}</h2>",
                unsafe_allow_html=True
            )
            st.write(f"Email: {result[2]}")
            cursor.execute('SELECT department_name FROM department WHERE id = %s', (result[7],))
            department_result = cursor.fetchone()

            st.write(f"Department: {department_result[0]}")
            st.write(f"Address: {result[6]}")

        st.markdown("<h3>Description:</h3>", unsafe_allow_html=True)
        st.write("This is the profile page for the Training officer. Here you can view and update your profile image and see your details.")
        

    def training_officer_page(self):
       
        
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM professional WHERE username = %s', (st.session_state.email,))
        result = cursor.fetchone()
        if result[4]=='training_officer':


            if result[7]==1:

                # Show Training Officer Home Page title above sidebar
                # st.markdown("<h1 style='text-align: center; color: grey;'>Training Officer Home Page</h1>", unsafe_allow_html=True)

                # Show user name above sidebar
                # Show profile image (from DB if available), name above sidebar
                if result[5]:
                    image_bytes = result[5]
                    image_base64 = base64.b64encode(image_bytes).decode()
                    image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
                else:
                    image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

                st.sidebar.markdown(
                    "<div style='text-align: center;'>"
                    f"{image_html}"
                    f"<h2 style='color: #0691FF; font-family: Lucida Bright, Times, serif; margin-bottom: 0;'>{result[1].capitalize()}</h2>"
                    "</div>",
                    unsafe_allow_html=True
                )
                choice=st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application Recieved", "Leave History","Register-User","contact-us"])
                logout=st.sidebar.button("Logout", use_container_width=True)
                if logout:
                    st.session_state.page = "login"
                    st.session_state.otp_sent = False
                    st.session_state.email = None
                    st.session_state.otp = None
                    st.rerun()

                if choice == "Home":
                    self.home()
                
                elif choice == "Profile":
                    self.training_officer_profile()

                elif choice == "contact-us":
                    self.contact_us_form()

                elif choice == "Register-User":
                    self.register_user_officer(result[7])

                elif choice == "Leave Application Recieved":
                    self.Leave_Application_Received(result[7])
                
                elif choice == "Leave History":
                    self.leave_history_for_management()


            elif result[7]=='2':
                # Fetch and display profile image and name above sidebar
                if result[5]:
                    image_bytes = result[5]
                    image_base64 = base64.b64encode(image_bytes).decode()
                    image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
                else:
                    image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

                st.sidebar.markdown(
                    "<div style='text-align: center;'>"
                    f"{image_html}"
                    f"<h2 style='color: #0691FF; font-family: Lucida Bright, Times, serif; margin-bottom: 0;'>{result[1].capitalize()}</h2>"
                    "</div>",
                    unsafe_allow_html=True
                )
                choice=st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application Recieved", "Leave History","Register-User"])
                logout=st.sidebar.button("Logout", use_container_width=True)
                if logout:
                    st.session_state.page = "login"
                    st.session_state.otp_sent = False
                    st.session_state.email = None
                    st.session_state.otp = None
                    st.rerun()

                if choice == "Home":
                    self.home_training_officer(result[7])
                
                elif choice == "Profile":
                    self.training_officer_profile() 
                elif choice == "Register-User":
                    self.register_user_officer(result[7])
                                

                elif choice == "Leave Application Recieved":
                    self.Leave_Application_Received(result[7])

                elif choice == "Leave History":
                    self.leave_history_for_management()


            elif result[7]=='3':
                # Fetch and display profile image and name above sidebar
                if result[5]:
                    image_bytes = result[5]
                    image_base64 = base64.b64encode(image_bytes).decode()
                    image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
                else:
                    image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

                st.sidebar.markdown(
                    "<div style='text-align: center;'>"
                    f"{image_html}"
                    f"<h2 style='color: #0691FF; font-family: Lucida Bright, Times, serif; margin-bottom: 0;'>{result[1].capitalize()}</h2>"
                    "</div>",
                    unsafe_allow_html=True
                )
                choice=st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application Recieved", "Leave History","Register-User"])
                logout=st.sidebar.button("Logout", use_container_width=True)
                if logout:
                    st.session_state.page = "login"
                    st.session_state.otp_sent = False
                    st.session_state.email = None
                    st.session_state.otp = None
                    st.rerun()

                if choice == "Home":
                    st.markdown("<h1 style='text-align: center; color: grey;'>Home Page</h1>", unsafe_allow_html=True)
                    st.write("Welcome to the Home Page!")
                
                elif choice == "Profile":
                        self.training_officer_profile() 

                elif choice == "Register-User":
                    self.register_user_officer(result[7])

                elif choice == "Leave Application Recieved":
                    self.Leave_Application_Received(result[7])

                elif choice == "Leave History":
                    self.leave_history_for_management()

            elif result[7]=='4':
                # Fetch and display profile image and name above sidebar
                if result[5]:
                    image_bytes = result[5]
                    image_base64 = base64.b64encode(image_bytes).decode()
                    image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
                else:
                    image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

                st.sidebar.markdown(
                    "<div style='text-align: center;'>"
                    f"{image_html}"
                    f"<h2 style='color: #0691FF; font-family: Lucida Bright, Times, serif; margin-bottom: 0;'>{result[1].capitalize()}</h2>"
                    "</div>",
                    unsafe_allow_html=True
                )
                choice=st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application Recieved", "Leave History","Register-User"])
                logout=st.sidebar.button("Logout", use_container_width=True)
                if logout:
                    st.session_state.page = "login"
                    st.session_state.otp_sent = False
                    st.session_state.email = None
                    st.session_state.otp = None
                    st.rerun()

                if choice == "Home":
                    st.markdown("<h1 style='text-align: center; color: grey;'>Home Page</h1>", unsafe_allow_html=True)
                    st.write("Welcome to the Home Page!")
                
                elif choice == "Profile":
                    self.training_officer_profile() 
                elif choice == "Register-User":
                    self.register_user_officer(result[7])
                                

                elif choice == "Leave Application Recieved":
                    self.Leave_Application_Received(result[7])


            elif result[7]=='5':
                # Fetch and display profile image and name above sidebar
                if result[5]:
                    image_bytes = result[5]
                    image_base64 = base64.b64encode(image_bytes).decode()
                    image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
                else:
                    image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

                st.sidebar.markdown(
                    "<div style='text-align: center;'>"
                    f"{image_html}"
                    f"<h2 style='color: #0691FF; font-family: Lucida Bright, Times, serif; margin-bottom: 0;'>{result[1].capitalize()}</h2>"
                    "</div>",
                    unsafe_allow_html=True
                )
                choice=st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application Recieved", "Leave History","Register-User"])
                logout=st.sidebar.button("Logout", use_container_width=True)
                if logout:
                    st.session_state.page = "login"
                    st.session_state.otp_sent = False
                    st.session_state.email = None
                    st.session_state.otp = None
                    st.rerun()

                if choice == "Home":
                   self.home_training_officer(result[7])
                
                elif choice == "Profile":
                    self.training_officer_profile() 

                elif choice == "Register-User":
                    self.register_user_officer(result[7])

                elif choice =='Leave Application Recieved':
                    self.Leave_Application_Received(result[7])

                elif choice == "Leave History":
                    self.leave_history_for_management()


    def register_user_officer(self,department_id):
                    
            st.markdown("""
                <h1 style='
                    text-align: center; 
                    color: #2C3E50; 
                    border: 2px solid grey; 
                    border-radius: 10px; 
                    padding: 10px 0; 
                    background: #F4F6F7;
                    font-family: "Segoe UI", Arial, sans-serif;
                    font-weight: bold;
                    margin-bottom: 24px;
                '>Register Trainee</h1>
            """, unsafe_allow_html=True)


            cursor = self.conn.cursor()
            name_user = st.text_input("Name", placeholder="Enter user name").strip()
            email = st.text_input("Email", placeholder="Enter user email").strip()
            password_user = 'Test@1234'  # Default password for registration
            address = st.text_input("Address", placeholder="Enter user address")
            
            # Fetch trades with department_id = 1
            cursor.execute('SELECT trade_name FROM trade WHERE depart_id = %s', (department_id,))
            trade_result = cursor.fetchall()
            trade_list = [trade[0] for trade in trade_result]

            if trade_list:
                trade = st.selectbox("Select Trade", trade_list)
                cursor.execute('SELECT id FROM trade WHERE trade_name = %s', (trade,))
                result = cursor.fetchone()
               
                t_id=result[0]
            else:
                st.warning("No trades available for the selected department.")

            if st.button("Register",use_container_width=True):
                if name_user and email and password_user and address:
                    if len(password_user) < 4:  
                        st.warning("Password must be at least 4 characters long.")
                        if len(name_user) < 3:
                            st.warning("Name must be at least 3 characters long.")
                            if len(address) < 5:
                                st.warning("Address must be at least 5 characters long.")
                            else:   
                                st.warning("Please fill in all fields.")
                    else:
                        cursor.execute('SELECT * FROM user WHERE username = %s', (email,))
                        result = cursor.fetchone()
                        if result:
                            st.warning("Email already exists.")
                        else:
                            cursor.execute('insert into user (name, username, password, address, trade_id) values (%s, %s, %s, %s, %s)', (name_user, email, hash_password(password_user), address, t_id))
                            self.conn.commit()
                           
                            st.success("User registered successfully!")
                            subject_to_trainee="Trainee Registration"
                            self.send_mail(subject_to_trainee,email, f"You have been successfully registered as a trainee.\nName: {name_user}\nUsername: {email}\nTrade: {trade}\npassword: {password_user}\n\nPlease change your password after first login.")
                            st.success('Registration Mail sent successfully')

    def home_training_officer(self,department_id):
            
            st.markdown("<h1 style='text-align: center; color: grey;'>Home Page</h1>", unsafe_allow_html=True)

            
    def Leave_Application_Received(self, department_id):
        st.markdown("""
            <h1 style='
            text-align: center; 
            color: #2471A3; 
            text-shadow: 
            -1px -1px 0 #D6EAF8, 
            1px -1px 0 #D6EAF8, 
            -1px 1px 0 #D6EAF8, 
            1px 1px 0 #D6EAF8;
            border: 2px solid grey;
            border-radius: 12px;
            padding: 12px 0;
            font-family: "Segoe UI", Arial, sans-serif;
            font-weight: bold;
            margin-bottom: 24px;
            '>NATIONAL SKILL TRAINING INSTITUTE</h1>
        """, unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: grey;'>Leave Applications Received</h1>", unsafe_allow_html=True)
        cursor = self.conn.cursor()

        # Get current user's role
        cursor.execute('SELECT post FROM professional WHERE username = %s', (st.session_state.email,))
        current_role = cursor.fetchone()[0]

        # Get trades under this department
        cursor.execute('SELECT id, trade_name FROM trade WHERE depart_id = %s', (department_id,))
        trades = cursor.fetchall()
        trade_dict = {trade[0]: trade[1] for trade in trades}

        selected_trade = st.selectbox("Select Trade", ["--select--"] + list(trade_dict.values()))

        if selected_trade != "--select--":
            trade_id = next((key for key, value in trade_dict.items() if value == selected_trade), None)

            cursor.execute('''
                SELECT la.id, la.name, la.email, la.leave_type, la.leave_description, 
                    la.days, la.to_approval, la.dd_approval, la.status, la.rejection_reason ,la.to_Approval, la.dd_Approval
                FROM leave_application la
                JOIN user u ON la.email = u.username
                WHERE u.trade_id = %s AND la.status = '2'
            ''', (trade_id,))
            applications = cursor.fetchall()

            if applications:
                for index, app in enumerate(applications, start=1):
                    leave_id, name, email, leave_type, desc, days, to_app, dd_app, status, reason,to_stat,ddstat = app

                    # Prevent re-rendering if already approved/rejected
                    if (current_role == "training_officer" and to_app != "2") or (current_role == "Director" and dd_app != "2"):
                        continue

                    st.markdown(f"### Application {index}")
                    st.write(f"Name: {name}")
                    st.write(f"Email: {email}")
                    st.write(f"Leave Type: {leave_type}")
                    st.write(f"Leave Description: {desc}")
                    st.write(f"Days: {days}")

                    if ddstat == "1" and current_role == "training_officer":
                        st.write("Director Approval: Approved")

                    elif ddstat == "0" and current_role == "training_officer":
                        st.write("Director Approval: Rejected")
                    else:
                        st.write("Director Approval: Pending")

                    # Calculate total approved leave days for this user
                    cursor.execute(
                        'SELECT COALESCE(SUM(days), 0) FROM leave_application WHERE email = %s AND status = "1"',
                        (email,)
                    )
                    total_days_taken = cursor.fetchone()[0] or 0
                    allowed_days = 60
                    percent_taken = (total_days_taken / allowed_days) * 100 if allowed_days else 0
                    will_exceed = (total_days_taken + days) > allowed_days

                    # Color indicator and info
                    if will_exceed:
                        st.markdown(
                            f"<span style='color: red; font-weight: bold;'>Warning: This leave will exceed allowed limit by {total_days_taken + days - allowed_days} days!</span>",
                            unsafe_allow_html=True
                        )
                    elif percent_taken >= 80:
                        st.markdown(
                            f"<span style='color: orange; font-weight: bold;'>Leave taken: {total_days_taken}/{allowed_days} days ({percent_taken:.1f}%)</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<span style='color: green; font-weight: bold;'>Leave taken: {total_days_taken}/{allowed_days} days ({percent_taken:.1f}%)</span>",
                            unsafe_allow_html=True
                        )

                    if to_stat == "1" and current_role == "Director":
                        st.write("Training Officer Approval: Approved")

                    elif to_stat == "0" and current_role == "Director":
                        st.write("Training Officer Approval: Rejected")
                    else:
                        st.write("Training Officer Approval: Pending")

                    col1, col2 = st.columns(2)

                    # APPROVE BUTTON
                  
                    with col1:
                            if st.button(f"Approve {index}", key=f"approve_{leave_id}"):
                                approval_field = "to_approval" if current_role == "training_officer" else "dd_approval"
                                cursor.execute(f'UPDATE leave_application SET {approval_field} = %s WHERE id = %s', ("1", leave_id))
                                cursor.execute('Select to_approval, dd_approval from leave_application where id = %s', (leave_id,))
                                result = cursor.fetchone()
                                to_app, dd_app = result
                                
                                # Check if both approvals are done
                                if to_app == "1" and dd_app == "1":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("1", leave_id))
                                    cursor.execute('UPDATE user SET status = %s WHERE username = %s', ("1", email))
                                    self.conn.commit()
                                    
                                    # Send approval email
                                    subject = "Leave Application Approved"
                                    message = f"Your leave application has been fully approved by both authorities."
                                    self.send_mail(subject, email, message)
                                    st.success("Approved and email sent!")
                                    
                                elif to_app == "0" and dd_app == "0":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("0", leave_id))
                                    cursor.execute('UPDATE user SET status = %s WHERE username = %s', ("0", email))
                                    self.conn.commit()
                                else:
                                    # Partial approval - only update the specific approval field
                                    self.conn.commit()
                                    st.success("Approval recorded. Waiting for other authority.")
                                
                                st.rerun()

                    #REJECT BUTTON        

                    with col2:
                        reason_input = st.text_input(f"Reason for rejection (Application {index})", key=f"reason_{leave_id}")
                        if st.button(f"Reject {index}", key=f"reject_{leave_id}"):
                            if reason_input.strip():
                                rejection_field = "to_approval" if current_role == "training_officer" else "dd_approval"
                                cursor.execute(
                                    f'UPDATE leave_application SET {rejection_field} = %s, rejection_reason = %s WHERE id = %s',
                                    ("0", reason_input.strip(), leave_id)
                                )
                                self.conn.commit()
                                st.warning("Rejected.")

                                cursor.execute('Select to_approval, dd_approval from leave_application where id = %s', (leave_id,))
                                result = cursor.fetchone()
                                to_app, dd_app = result
                                if to_app == "1" and dd_app == "1":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("1", leave_id))
                            
                                elif to_app == "0" and dd_app == "0":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("0", leave_id))
                                    
                                else:
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("2", leave_id))
                             
                                if to_app == "0" and dd_app=="0":
                                    message = f"Your leave application has been rejected for reason {reason_input}."
                                    subject_for_reject="Application Status"
                                    self.send_mail(subject_for_reject, email, message)
                                    st.success('Mail sent successfully')
                                    
                                    st.rerun()
                            else:
                                st.warning("Please provide a reason for rejection.")

                    # After action, check for matching approvals
                    cursor.execute('SELECT to_approval, dd_approval FROM leave_application WHERE id = %s', (leave_id,))
                    to_app, dd_app = cursor.fetchone()

                    if to_app == dd_app and to_app in ("1", "0"):
                        cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', (to_app, leave_id))
                        cursor.execute('UPDATE user SET status = %s WHERE username = %s', (to_app, email))
                        self.conn.commit()
            else:
                st.info("No leave applications found for the selected trade.")
        else:
            st.info("Please select a trade to view leave applications.")
            
    def director_page(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM professional WHERE username = %s', (st.session_state.email,))
        result = cursor.fetchone()
        # Show profile image (from DB if available), name above sidebar
        if result[5]:
            image_bytes = result[5]
            image_base64 = base64.b64encode(image_bytes).decode()
            image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
        else:
            image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

        st.sidebar.markdown(
            "<div style='text-align: center;'>"
            f"{image_html}"
            f"<h1 style='font-weight: bold; font-family: Lucida bright; color: #0691FF;'>{result[1]}</h1>"
            "</div>",
            unsafe_allow_html=True
        )
        choice = st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application Received", 'leave history','contact-us'])

        if result:
            st.sidebar.markdown(
                f"<h1 style='color: Aqua; font-family: Lucida bright; text-align: center;  text-shadow: 1px 1px 2px grey;'>{result[4]}</h1>",
                unsafe_allow_html=True
            )

            # Add image placeholder in the sidebar
            st.sidebar.markdown(
                "<div style='text-align: center;'>"
                "<img src='https://nstikanpur.dgt.gov.in/themes/nsti_barrio_old123_bk/images/emblem-black.png' width='100'>"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.sidebar.markdown(f"<h4 style='color: white;'>(About Director)</h4>", unsafe_allow_html=True)

        if st.sidebar.button("Logout",use_container_width=True):
            st.session_state.page = "login"
            st.session_state.otp_sent = False
            st.session_state.email = None
            st.session_state.otp = None
            st.rerun()

       

        if choice == "Home":
            self.home()

        elif choice=="contact-us":
            self.contact_us_form()

        elif choice == "Profile":
            st.markdown("""
            <h1 style='
            text-align: center; 
            color: #2471A3; 
            text-shadow: 
            -1px -1px 0 #D6EAF8, 
            1px -1px 0 #D6EAF8, 
            -1px 1px 0 #D6EAF8, 
            1px 1px 0 #D6EAF8;
            border: 2px solid grey;
            border-radius: 12px;
            padding: 12px 0;
            font-family: "Segoe UI", Arial, sans-serif;
            font-weight: bold;
            margin-bottom: 24px;
            '>NATIONAL SKILL TRAINING INSTITUTE</h1>
        """, unsafe_allow_html=True)
            # Show current image or placeholder
            if result[5]:
                # result[5] is expected to be BLOB (bytes)
                image_bytes = result[5]
                st.markdown(
                    "<div style='display: flex; justify-content: center;'>"
                    f"<img src='data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}' width='220' style='border-radius: 10px;' alt='Profile Image'/>"
                    "</div>",
                    unsafe_allow_html=True
                )
            else:
                    st.markdown(
                    "<div style='display: flex; justify-content: center;'>"
                    "<img src='https://nstikanpur.dgt.gov.in/themes/nsti_barrio_old123_bk/images/emblem-black.png' width='220' style='border-radius: 10px;' alt='Profile Image'/>"
                    "</div>",
                    unsafe_allow_html=True
                )

            # Allow image upload/change
            uploaded_image = st.file_uploader("Upload/Change Profile Image", type=["png", "jpg", "jpeg"])
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                cursor = self.conn.cursor()
                cursor.execute('UPDATE professional SET image = %s WHERE username = %s', (img_bytes, result[2]))
                self.conn.commit()
                st.success("Profile image updated! Please refresh to see changes.")

            st.markdown(
                f"<h2 style='color: blue; text-shadow: 1px 1px 0 grey, -0px -0px 0 grey, 0px -0px 0 grey, -0px 0px 0 grey;'>{result[1]}</h2>",
                unsafe_allow_html=True
            )
            
            st.write(f"Email: {result[2]}")

            st.markdown("<h3>Description:</h3>", unsafe_allow_html=True)
            st.write("This is the profile page for the Director. Here you can view and update your profile image and see your details.")
        
        elif choice == "leave history":
            self.leave_history_for_management()

        elif choice == "Leave Application Received":
            st.markdown("<h1 style='text-align: center; color: grey;'>Leave Applications Received</h1>", unsafe_allow_html=True)
            cursor.execute('''
                SELECT la.id, la.name, la.email, la.leave_type, la.leave_description, 
                    la.days, la.to_approval, la.dd_approval, la.status, la.rejection_reason, u.trade_id
                FROM leave_application la
                JOIN user u ON la.email = u.username
                WHERE la.status = '2' AND la.dd_approval = '2'
            ''')
            applications = cursor.fetchall()

            if applications:
                for index, app in enumerate(applications, start=1):
                    cursor.execute('SELECT trade_name FROM trade WHERE id = %s', (app[10],))
                    trade_result = cursor.fetchone()
                    trade_name = trade_result[0] if trade_result else "Unknown Trade"

                    leave_id, name, email, leave_type, desc, days, to_app, dd_app, status, reason, _ = app

                    # Check if already finalized
                    if to_app == "1" and dd_app == "1":
                        st.success(f"Application {index} has already been approved. Skipping in 5 seconds...")
                        cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("1", leave_id))
                        cursor.execute('UPDATE user SET status = %s WHERE username = %s', ("1", email))
                        self.conn.commit()
                        time.sleep(5)
                        st.rerun()
                    elif to_app == "0" and dd_app == "0":
                        st.error(f"Application {index} has already been rejected. Skipping in 5 seconds...")
                        cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("0", leave_id))
                        cursor.execute('UPDATE user SET status = %s WHERE username = %s', ("0", email))
                        self.conn.commit()
                        time.sleep(5)
                        st.rerun()

                    st.markdown(f"### Application {index}")
                    st.write(f"**Name:** {name}")
                    st.write(f"**Email:** {email}")
                    st.write(f"**Trade Name:** {trade_name}")
                    st.write(f"**Leave Type:** {leave_type}")
                    st.write(f"**Description:** {desc}")
                    st.write(f"**Days:** {days}")
                   
                    if to_app == "1":
                        st.write("**Training Officer Approval:** Approved")
                    elif to_app == "0":
                        st.write("**Training Officer Approval:** Rejected")
                    else:
                        st.write("**Training Officer Approval:** Pending")

                    col1, col2 = st.columns(2)


                    # Calculate total approved leave days for this user
                    cursor.execute(
                        'SELECT COALESCE(SUM(days), 0) FROM leave_application WHERE email = %s AND status = "1"',
                        (email,)
                    )
                    total_days_taken = cursor.fetchone()[0] or 0
                    allowed_days = 60
                    percent_taken = (total_days_taken / allowed_days) * 100 if allowed_days else 0
                    will_exceed = (total_days_taken + days) > allowed_days

                    # Color indicator and info
                    if will_exceed:
                        st.markdown(
                            f"<span style='color: red; font-weight: bold;'>Warning: This leave will exceed allowed limit by {total_days_taken + days - allowed_days} days!</span>",
                            unsafe_allow_html=True
                        )
                    elif percent_taken >= 80:
                        st.markdown(
                            f"<span style='color: orange; font-weight: bold;'>Leave taken: {total_days_taken}/{allowed_days} days ({percent_taken:.1f}%)</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<span style='color: green; font-weight: bold;'>Leave taken: {total_days_taken}/{allowed_days} days ({percent_taken:.1f}%)</span>",
                            unsafe_allow_html=True
                        )
    
                    with col1:
                            if st.button(f"Approve {index}", key=f"approve_{leave_id}"):
                                cursor.execute('UPDATE leave_application SET dd_approval = %s WHERE id = %s', ("1", leave_id))
                                
                                cursor.execute('SELECT to_approval, dd_approval FROM leave_application WHERE id = %s', (leave_id,))
                                to_new, dd_new = cursor.fetchone()

                                if to_new == "1" and dd_new == "1":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("1", leave_id))
                                    cursor.execute('UPDATE user SET status = %s WHERE username = %s', ("1", email))
                                    self.conn.commit()
                                    
                                    # Send approval email
                                    subject = "Leave Application Approved"
                                    message = f"Your leave application has been fully approved by both authorities."
                                    self.send_mail(subject, email, message)
                                    st.success("Approved and email sent!")
                                    
                                else:
                                    self.conn.commit()
                                    st.success("Director approval recorded. Waiting for training officer.")
                                
                                st.rerun()

                    with col2:
                        reason_input = st.text_input(f"Reason for rejection (Application {index})", key=f"reason_{leave_id}")
                        if st.button(f"Reject {index}", key=f"reject_{leave_id}"):
                            if reason_input.strip():
                                cursor.execute('UPDATE leave_application SET dd_approval = %s, rejection_reason = %s WHERE id = %s', ("0", reason_input.strip(), leave_id))
                                self.conn.commit()

                                cursor.execute('SELECT to_approval, dd_approval FROM leave_application WHERE id = %s', (leave_id,))
                                to_new, dd_new = cursor.fetchone()

                                if to_new == dd_new and to_new in ("1", "0"):
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', (to_new, leave_id))
                                    cursor.execute('UPDATE user SET status = %s WHERE username = %s', (to_new, email))
                                    self.conn.commit()

                                st.warning("Rejection recorded. Refreshing applications...")

                                cursor.execute('Select to_approval, dd_approval from leave_application where id = %s', (leave_id,))
                                result = cursor.fetchone()
                                to_app, dd_app = result
                                if to_app == "1" and dd_app == "1":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("1", leave_id))
                            
                                elif to_app == "0" and dd_app == "0":
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("0", leave_id))
                                    
                                else:
                                    cursor.execute('UPDATE leave_application SET status = %s WHERE id = %s', ("2", leave_id))
                                    

                                if to_app == "0" and dd_app=="0":
                                    subject_for_reject="Application Status"
                                    message = f"Your leave application has been rejected for reason {reason_input}."
                                    self.send_mail(subject_for_reject,email, message)
                                    st.success('Mail sent successfully')
                                    st.rerun()
                            else:
                                st.warning("Please provide a reason before rejecting.")

            elif choice == "Leave_History":
                self.leave_history_for_management()

            else:
                st.info("No leave applications found.")
    
    def contact_us_form(self):
        st.markdown("<h1 style='text-align: center; color: grey;'>Contact Us</h1>", unsafe_allow_html=True)
        role=st.selectbox('post',['Training_officer','Director'])
        name=st.text_input('Your Name')
        email_user=st.text_input('Your Email')
        message=st.text_area(f'Your Message ')
        message_new=f"from {role},\n\n{message}\n\nBest regards,\n{name}\n\nContact: {email_user}"
    
        if st.button('Submit'):
            if name and email_user and message:
                # Here you can add code to send the message to your email or store it in a database
                email = "ypratyaksh59@gmail.com"
                subject_to_admin="Requesting Update or change"
                self.send_mail(subject_to_admin,email, message_new)
                st.success("Your message has been sent successfully!")
            else:
                st.warning("Please fill in all fields.")
        st.write("For any queries or support, please reach out to us at:")
        

    def leave_history(self):
        st.markdown("<h1 style='text-align: center; color: white;'>Leave History</h1>", unsafe_allow_html=True)
        cursor = self.conn.cursor()
        
        # Get all leave applications for the current user
        cursor.execute('''
            SELECT la.id, la.name, la.leave_type, la.leave_description, 
                la.days, la.time_of_application, la.status, la.rejection_reason,
                t.trade_name
            FROM leave_application la
            JOIN trade t ON la.trade_id = t.id
            WHERE la.email = %s
            ORDER BY la.time_of_application DESC
        ''', (st.session_state.email,))
        
        applications = cursor.fetchall()
        STATUS_MAP = {
    '0': 'Rejected',
    '1': 'Approved',
    '2': 'Pending',
    '3': 'Under Review',  # If you have additional statuses
}
        
        if applications:
            for app in applications:
                app_id, name, leave_type, description, days, app_time, status, reason, trade = app
                
                # Get status text
                status_text = STATUS_MAP.get(status, 'Unknown')
                
                # Display application details
                st.markdown(f"### Application ID: {app_id}")
                st.write(f"**Date Applied:** {app_time}")
                st.write(f"**Leave Type:** {leave_type}")
                st.write(f"**Trade:** {trade}")
                st.write(f"**Days Requested:** {days}")
                st.write(f"**Status:** {status_text}")
                
                if status == '0' and reason:  # Only show reason if rejected
                    st.write(f"**Rejection Reason:** {reason}")
                
                st.write(f"**Description:** {description}")
                st.markdown("---")
        else:
            st.info("No leave applications found in your history.")


    def leave_history_for_management(self):
        st.markdown("""
        <h1 style='
        text-align: center; 
        color: #2471A3; 
        text-shadow: 
        -1px -1px 0 #D6EAF8, 
        1px -1px 0 #D6EAF8, 
        -1px 1px 0 #D6EAF8, 
        1px 1px 0 #D6EAF8;
        border: 2px solid grey;
        border-radius: 12px;
        padding: 12px 0;
        font-family: "Segoe UI", Arial, sans-serif;
        font-weight: bold;
        margin-bottom: 24px;
        '>NATIONAL SKILL TRAINING INSTITUTE</h1>
        """, unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: red;'>Leave History</h1>", unsafe_allow_html=True)
        cursor = self.conn.cursor()

        # Fetch user role and department/trade info
        cursor.execute('SELECT * FROM professional WHERE username = %s', (st.session_state.email,))
        user = cursor.fetchone()
        role = user[4]

        if role == "Director":
            # Only show users with at least one pending application (status=2 and dd_approval=2)
            cursor.execute('''
                SELECT DISTINCT la.email
                FROM leave_application la
                JOIN user u ON la.email = u.username
                WHERE la.status = '2' AND la.dd_approval = '2'
            ''')
            applicants = cursor.fetchall()

            if applicants:
                st.markdown("#### Users with Pending Leave Applications (Director)")
                data = []
                for applicant in applicants:
                    email = applicant[0]
                    # Get applicant name and trade
                    cursor.execute('SELECT name, trade_id FROM user WHERE username = %s', (email,))
                    user_info = cursor.fetchone()
                    if not user_info:
                        continue
                    name, trade_id = user_info
                    cursor.execute('SELECT trade_name FROM trade WHERE id = %s', (trade_id,))
                    trade_row = cursor.fetchone()
                    trade_name = trade_row[0] if trade_row else "Unknown"
                    # Count pending applications
                    cursor.execute('SELECT COUNT(*) FROM leave_application WHERE email = %s AND status = "2"', (email,))
                    pending_count = cursor.fetchone()[0]
                    if pending_count > 0:
                        data.append({
                            "Username": email,
                            "Name": name,
                            "Trade": trade_name,
                            "Pending Applications": pending_count,
                            "Max Leaves Allowed": 60
                        })
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No users with pending leave applications for Director.")
            else:
                st.info("No users with pending leave applications for Director.")

        elif role == "training_officer":
            # Only show users in this department with at least one pending application
            department_id = user[7]
            cursor.execute('SELECT id FROM trade WHERE depart_id = %s', (department_id,))
            trade_ids = [row[0] for row in cursor.fetchall()]
            if not trade_ids:
                st.write("No trades found for your department.")
                return
            format_strings = ','.join(['%s'] * len(trade_ids))
            cursor.execute(f'''
                SELECT DISTINCT u.username
                FROM user u
                WHERE u.trade_id IN ({format_strings})
            ''', tuple(trade_ids))
            applicants = cursor.fetchall()

            if applicants:
                st.markdown("#### Trainees with Pending Leave Applications")
                data = []
                for applicant in applicants:
                    email = applicant[0]
                    # Count pending applications
                    cursor.execute('SELECT COUNT(*) FROM leave_application WHERE email = %s AND status = "2"', (email,))
                    pending_count = cursor.fetchone()[0]
                    if pending_count > 0:
                        cursor.execute('SELECT name, trade_id FROM user WHERE username = %s', (email,))
                        user_info = cursor.fetchone()
                        if not user_info:
                            continue
                        name, trade_id = user_info
                        cursor.execute('SELECT trade_name FROM trade WHERE id = %s', (trade_id,))
                        trade_row = cursor.fetchone()
                        trade_name = trade_row[0] if trade_row else "Unknown"
                        data.append({
                            "Username": email,
                            "Name": name,
                            "Trade": trade_name,
                            "Pending Applications": pending_count,
                            "Max Leaves Allowed": 60
                        })
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write("No trainees with pending leave applications in your department.")
            else:
                st.write("No trainees found for your department.")
        else:
            st.write("You do not have permission to view this data.")

    def home_page(self):

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (st.session_state.email,))
        result = cursor.fetchone()
        # print(result)
        
        # Show profile image (from DB if available), name above sidebar
        if result[2]:
            image_bytes = result[2]
            image_base64 = base64.b64encode(image_bytes).decode()
            image_html = f"<img src='data:image/jpeg;base64,{image_base64}' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"
        else:
            image_html = "<img src='https://nstihaldwani.dgt.gov.in/sites/default/files/2021-08/90Hi3zsH_400x400.jpg' width='120' style='border-radius: 50%; margin-bottom: 10px;'/>"

        st.sidebar.markdown(
            "<div style='text-align: center;'>"
            f"{image_html}"
            f"<h2 style='font-weight: bold; font-family: Lucida Bright, Times, serif; color: #0691FF; margin-bottom: 0;'>{result[1]}</h2>"
            "</div>",
            unsafe_allow_html=True
        )
        choice = st.sidebar.selectbox("Home", ["Home", "Profile", "Leave Application", "Leave History"])
        if result:
            st.sidebar.markdown(
                "<h1 style='"
                "color: white; "
                "text-align: center; "
                "font-weight: bold; "
                "font-family: Lucida Bright, Times, serif; "
                "text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;"
                "'>Trainee</h1>",
                unsafe_allow_html=True
            )

            st.sidebar.markdown(f"<h4 style='color: white;'>{result[3]}</h4>", unsafe_allow_html=True)

            st.sidebar.markdown(f"<h6 style='color: white;'>{result[5]}</h6>", unsafe_allow_html=True)
        
        if st.sidebar.button("Logout",use_container_width=True):
            st.session_state.page = "login"
            st.session_state.otp_sent = False
            st.session_state.email = None
            st.session_state.otp = None
            st.rerun()




        if choice == "Home":
            self.home()
        elif choice == "Profile":
            self.profile_page()

        elif choice == "Leave Application":
            self.leave_application()

        elif choice == "Leave History":
            self.leave_history()

 


    def main(self):
        if "email" not in st.session_state:
            st.session_state.email = None

        if "page" not in st.session_state:
            st.session_state.page = "login"

        if "otp" not in st.session_state:
            st.session_state.otp = None  

        if st.session_state.page == "login":
            self.loginpage()
        elif st.session_state.page == "otp":
            self.otp_page(st.session_state.email)
        elif st.session_state.page == "change_password":
            self.change_password(st.session_state.email)
        elif st.session_state.page == "home":
            self.home_page()
        
        elif st.session_state.page == "professional":
            self.professional_page()

# Run app
leave = login()

