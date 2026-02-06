"""
Email Configuration Test Script
Test your email settings before using them in production
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    """Test email configuration"""
    
    print("=" * 60)
    print("VAANI EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    # Get configuration from user
    print("\n📧 Enter your email configuration:")
    print("(For Gmail, you need an App Password: https://myaccount.google.com/apppasswords)\n")
    
    smtp_server = input("SMTP Server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP Port (default: 587): ").strip() or "587"
    sender_email = input("Your Email Address: ").strip()
    sender_password = input("Your App Password (will not be shown): ").strip()
    
    if not sender_email or not sender_password:
        print("❌ Email and password are required!")
        return False
    
    test_recipient = input("Test Recipient Email (to send test email): ").strip()
    
    if not test_recipient:
        print("❌ Test recipient email is required!")
        return False
    
    print("\n🔧 Testing connection...")
    
    try:
        # Create test message
        message = MIMEMultipart("alternative")
        message["Subject"] = "VAANI Email Test"
        message["From"] = f"VAANI Platform <{sender_email}>"
        message["To"] = test_recipient
        
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">✅ Email Test Successful!</h2>
            <p>Your VAANI email configuration is working correctly.</p>
            <p>You can now use this configuration in your application.</p>
            <hr>
            <p style="color: #999; font-size: 12px;">
                SMTP Server: {server}<br>
                Port: {port}<br>
                From: {from_email}
            </p>
        </body>
        </html>
        """.format(server=smtp_server, port=smtp_port, from_email=sender_email)
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Connect and send
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        print("\n✅ Email sent successfully!")
        print(f"   Check {test_recipient} inbox")
        
        # Generate .env file
        print("\n💾 Generating .env file...")
        
        env_content = f"""# VAANI Environment Variables

# Database Configuration
DATABASE_URL={os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/vaani_db')}

# Email Configuration
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}
"""
        
        # Save to .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print("\n⚠️  IMPORTANT:")
        print("   1. The .env file contains sensitive information")
        print("   2. Never commit .env to git (it's in .gitignore)")
        print("   3. Restart your Flask server to load new settings")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication failed!")
        print("\n💡 Tips:")
        print("   For Gmail:")
        print("   1. Enable 2-Factor Authentication")
        print("   2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("   3. Use the 16-character app password (not your regular password)")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Common issues:")
        print("   - Wrong SMTP server or port")
        print("   - Firewall blocking connection")
        print("   - Less secure apps disabled (use App Password)")
        return False

if __name__ == "__main__":
    success = test_email_config()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart Flask server: python backend/app.py")
        print("2. Test NGO approval to send real emails")
    else:
        print("\n" + "=" * 60)
        print("❌ SETUP FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("- Check your email provider's SMTP settings")
        print("- Verify credentials are correct")
        print("- Try a different email provider")
