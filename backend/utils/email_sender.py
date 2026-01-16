"""
Email utility for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_approval_email(recipient_email, org_name, temp_password):
    """
    Send approval notification email to NGO
    
    Args:
        recipient_email: NGO email address
        org_name: Organization name
        temp_password: Temporary password for login
    """
    # Email configuration (can be moved to config.py)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "vaani.isl@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    
    # Create email
    message = MIMEMultipart("alternative")
    message["Subject"] = "🎉 Your Partnership Request with VAANI Has Been Approved!"
    message["From"] = f"VAANI Platform <{SENDER_EMAIL}>"
    message["To"] = recipient_email
    
    # Email body
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .credentials {{ background: white; padding: 20px; border-left: 4px solid #667eea; 
                           margin: 20px 0; border-radius: 5px; }}
            .button {{ background: #667eea; color: white; padding: 12px 30px; text-decoration: none; 
                      border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .footer {{ text-align: center; color: #999; margin-top: 30px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Congratulations!</h1>
                <p style="margin: 0; font-size: 18px;">Your partnership request has been approved</p>
            </div>
            <div class="content">
                <p>Dear <strong>{org_name}</strong>,</p>
                
                <p>We are excited to inform you that your partnership request with <strong>VAANI - Indian Sign Language Platform</strong> has been <strong>approved</strong>! 🎊</p>
                
                <p>Welcome to the VAANI community! Together, we can make a significant impact in empowering the deaf and hard-of-hearing community through technology and sign language recognition.</p>
                
                <div class="credentials">
                    <h3 style="margin-top: 0; color: #667eea;">🔐 Your Login Credentials</h3>
                    <p><strong>Email:</strong> {recipient_email}</p>
                    <p><strong>Temporary Password:</strong> <code style="background: #eee; padding: 5px 10px; border-radius: 3px; font-size: 16px; color: #d63031;">{temp_password}</code></p>
                    <p style="color: #e67e22; margin-top: 15px;">
                        ⚠️ <strong>Important:</strong> Please change your password after your first login for security purposes.
                    </p>
                </div>
                
                <a href="http://127.0.0.1:5000/ngo.html" class="button">Access NGO Dashboard</a>
                
                <h3>What's Next?</h3>
                <ul>
                    <li>✅ Login to your NGO dashboard</li>
                    <li>✅ Update your organization profile</li>
                    <li>✅ Post events for the community</li>
                    <li>✅ Connect with VAANI users</li>
                    <li>✅ Track your impact metrics</li>
                </ul>
                
                <p>If you have any questions or need assistance, please don't hesitate to reach out to our support team.</p>
                
                <p>Thank you for partnering with us!</p>
                
                <p style="margin-top: 30px;">
                    <strong>Best Regards,</strong><br>
                    The VAANI Team<br>
                    <em>Empowering Communication Through Technology</em>
                </p>
            </div>
            <div class="footer">
                <p>© 2026 VAANI Platform. All rights reserved.</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Attach HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        # Send email
        if not SENDER_PASSWORD:
            print("⚠️ Email not sent: SENDER_PASSWORD not configured")
            print(f"   Would send approval email to: {recipient_email}")
            print(f"   Organization: {org_name}")
            print(f"   Temp Password: {temp_password}")
            return False
            
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Approval email sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_rejection_email(recipient_email, org_name, reason=""):
    """
    Send rejection notification email to NGO
    
    Args:
        recipient_email: NGO email address
        org_name: Organization name
        reason: Optional rejection reason
    """
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "vaani.isl@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Update on Your Partnership Request with VAANI"
    message["From"] = f"VAANI Platform <{SENDER_EMAIL}>"
    message["To"] = recipient_email
    
    reason_section = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f1f1f1; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; color: #999; margin-top: 30px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Partnership Request Update</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{org_name}</strong>,</p>
                
                <p>Thank you for your interest in partnering with VAANI - Indian Sign Language Platform.</p>
                
                <p>After careful consideration, we regret to inform you that we are unable to approve your partnership request at this time.</p>
                
                {reason_section}
                
                <p>We encourage you to reapply in the future if circumstances change.</p>
                
                <p>Thank you for your understanding.</p>
                
                <p style="margin-top: 30px;">
                    <strong>Best Regards,</strong><br>
                    The VAANI Team
                </p>
            </div>
            <div class="footer">
                <p>© 2026 VAANI Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    try:
        if not SENDER_PASSWORD:
            print("⚠️ Email not sent: SENDER_PASSWORD not configured")
            print(f"   Would send rejection email to: {recipient_email}")
            return False
            
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Rejection email sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send email to {recipient_email}: {str(e)}")
        return False
