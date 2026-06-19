import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime


# Import Supabase
from supabase import create_client

def homepage(request):
    return render(request, 'newhome.html')

def order_post(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    address = request.POST['address']
    quantity = request.POST['quantity']

    if quantity == "100ml":
        amount = 1 * 100
    elif quantity == "200ml":
        amount = 1 * 100
    elif quantity == "500ml":
        amount = 1 * 100
    else:
        amount = 0

    return render(request, 'pp.html', {
        'name': name,
        'email': email,
        'phone': phone,
        'address': address,
        'quantity': quantity,
        'amount': amount,
        'razorpay_api_key': 'rzp_live_Su35EVyNYFeKCF',
        'currency': 'INR'
    })

def raz_pay(request, amount):
    import razorpay
    razorpay_api_key = "rzp_live_Su35EVyNYFeKCF"
    razorpay_secret_key = "NQE3JfS6rdlmp8YtHrxF120H"
    
    razorpay_client = razorpay.Client(auth=(razorpay_api_key, razorpay_secret_key))
    amount = float(amount)
    
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': 'order_rcptid_11',
        'payment_capture': '1',
    }
    
    order = razorpay_client.order.create(data=order_data)
    
    return render(request, 'pp.html', {
        'razorpay_api_key': razorpay_api_key,
        'amount': order_data['amount'],
        'currency': order_data['currency'],
        'order_id': order['id']
    })

# ==========================================
# SAVE ORDER TO SUPABASE - FIXED VERSION
# ==========================================

def save_order_to_supabase(name, email, phone, address, quantity, amount, payment_id):
    try:
        print("===== SUPABASE FUNCTION STARTED =====")

        supabase_url = "https://uuzumstwtrgzmeqgkjrj.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1enVtc3R3dHJnem1lcWdranJqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTUwODA1MSwiZXhwIjoyMDk3MDg0MDUxfQ.lZlydZ_sVQhcBteBBX1mucA_ZbmlkOS7yUVO8gYCV6U"
        
        supabase = create_client(supabase_url, supabase_key)

        order_data = {
            "customer_name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "quantity": quantity,
            "amount": amount,
            "payment_id": payment_id,
            "payment_status": "Success"
        }

        print("ORDER DATA:", order_data)

        result = supabase.table("brasscleaner_orders").insert(order_data).execute()

        print("SUPABASE RESULT:", result)

        return True

    except Exception as e:
        import traceback
        print("===== SUPABASE ERROR =====")
        print(traceback.format_exc())
        return False
    

# def save_order_to_supabase(name, email, phone, address, quantity, payment_id):
#     """Save order to Supabase database"""
#     try:
#         # Your Supabase credentials - DIRECT values
#         supabase_url = "https://uuzumstwtrgzmeqgkjrj.supabase.co"
#         supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1enVtc3R3dHJnem1lcWdranJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MDgwNTEsImV4cCI6MjA5NzA4NDA1MX0.gW9eWtVM03c-9Rv42VbbXUSN1RvHqzvHTtinFdK0_8U"
        
#         # Create client
#         supabase = create_client(supabase_url, supabase_key)
        
#         # Get next order number by counting existing orders
#         try:
#             response = supabase.table('brasscleaner_orders').select('id', count='exact').execute()
#             order_no = response.count + 1 if response.count else 1
#         except Exception as e:
#             print(f"Could not get count: {e}")
#             order_no = 1
        
#         # Insert order
#         order_data = {
#             "order_no": order_no,
#             "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "customer_name": name,
#             "email": email,
#             "phone": phone,
#             "address": address,
#             "quantity": quantity,
#             "payment_id": payment_id
#         }
        
#         result = supabase.table('brasscleaner_orders').insert(order_data).execute()
#         print(f"✅ Order #{order_no} saved to Supabase")
#         return True
        
#     except Exception as e:
#         print(f"❌ Supabase error: {str(e)}")
#         return False


def send_whatsapp_message(name, phone, quantity):
    try:

        print("========== WHATSAPP FUNCTION STARTED ==========")

        # Clean phone number
        phone = str(phone).replace(" ", "").replace("+", "").strip()

        # Add country code if missing
        if not phone.startswith("91"):
            phone = f"91{phone}"

        print("FINAL PHONE:", phone)

        # WATI API URL
        # url = f"https://live-mt-server.wati.io/1043453/api/v1/sendTemplateMessage?whatsappNumber={phone}"
        
        url = f"https://live-mt-server.wati.io/1043453/api/v1/sendTemplateMessage?whatsappNumber={phone}"


        # Payload
        payload = {
            "template_name": "order_confirmation",
            "broadcast_name": "order_confirmation",
            "parameters": [
                {
                    "name": "1",
                    "value": str(name)
                },
                {
                    "name": "2",
                    "value": str(quantity)
                }
            ]
        }

        print("PAYLOAD:", payload)

        # Headers
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6InByZW1zZWtoYXJAeWF0aGlzaGEuY29tIiwibmFtZWlkIjoicHJlbXNla2hhckB5YXRoaXNoYS5jb20iLCJlbWFpbCI6InByZW1zZWtoYXJAeWF0aGlzaGEuY29tIiwiYXV0aF90aW1lIjoiMDYvMDYvMjAyNiAxNzoxOToxNCIsInRlbmFudF9pZCI6IjEwNDM0NTMiLCJkYl9uYW1lIjoibXQtcHJvZC1UZW5hbnRzIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQURNSU5JU1RSQVRPUiIsImV4cCI6MjUzNDAyMzAwODAwLCJpc3MiOiJDbGFyZV9BSSIsImF1ZCI6IkNsYXJlX0FJIn0.i7aQp3cYOtk2wraWyMjHLP7L0T8znm-xf7SthfOPvZ4",
            "Content-Type": "application/json"
        }

        # Send request
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        print("========== WATI RESPONSE ==========")
        print("STATUS CODE:", response.status_code)
        print("RESPONSE:", response.text)
        print("===================================")

        return response.status_code == 200

    except Exception as e:

        print("WhatsApp Error:", str(e))
        return False


# ==========================================
# USER PAYMENT POST - MAIN FUNCTION
# ==========================================
def userpayment_post(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        address = request.POST.get('address')
        quantity = request.POST.get('quantity')
        payment_id = request.POST.get('payment_id')
        
        if not email:
            return HttpResponse("Email not found")
        
        # Success HTML template
        success_html = """
        <script>
        alert('Payment Successful!');
        window.location='/';
        </script>
        """
        
        # 1. Send emails (critical - if this fails, alert the user)
        email_sent = False
        try:
            # Customer HTML Email
            customer_html = f"""
            <html>
            <body style="font-family: Arial; background:#f4f4f4; padding:30px;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:15px; padding:30px;">
            <h1 style="color:#0b7d45; text-align:center;">🌿 ECOMONKS</h1>
            <h2>Thank You For Your Ordering Brass Cleaner</h2>
            <p>Dear <b>{name}</b>,</p>
            <p>Your payment has been received successfully and your order is confirmed.</p>
            <div style="background:#f7fff9; border:1px solid #d4f5dd; padding:20px; border-radius:10px;">
            <h3>🧾 Order Details</h3>
            <p><b>👤 Name:</b> {name}</p>
            <p><b>📧 Email:</b> {email}</p>
            <p><b>📞 Phone:</b> {phone}</p>
            <p><b>📍 Address:</b> {address}</p>
            <p><b>📦 Quantity:</b> {quantity}</p>
            <p><b>💰 Amount:</b> ₹{amount}</p>
            <p><b>💳 Payment ID:</b> {payment_id}</p>
            </div>
            </div>
            </body>
            </html>
            """
            
            admin_html = f"""
            <html>
            <body>
            <h2>🚨 NEW ORDER RECEIVED</h2>
            <p><b>Customer:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Phone:</b> {phone}</p>
            <p><b>Address:</b> {address}</p>
            <p><b>Quantity:</b> {quantity}</p>
            <p><b>Amount:</b> ₹{amount}</p>
            <p><b>Payment ID:</b> {payment_id}</p>
            </body>
            </html>
            """
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login("founder@ecomonks.in", "crmwddzdzoqatofz")
            
            # Customer email
            customer_msg = MIMEMultipart()
            customer_msg['From'] = "founder@ecomonks.in"
            customer_msg['To'] = email
            customer_msg['Subject'] = "ECOMONKS Order Confirmation"
            customer_msg.attach(MIMEText(customer_html, 'html', 'utf-8'))
            server.sendmail("founder@ecomonks.in", email, customer_msg.as_string())
            
            # Admin email
            admin_msg = MIMEMultipart()
            admin_msg['From'] = "founder@ecomonks.in"
            admin_msg['To'] = "founder@ecomonks.in"
            admin_msg['Subject'] = "New ECOMONKS Order Received"
            admin_msg.attach(MIMEText(admin_html, 'html', 'utf-8'))
            server.sendmail("founder@ecomonks.in", "founder@ecomonks.in", admin_msg.as_string())
            
            server.quit()
            email_sent = True
            print("✅ Emails sent successfully")
            
        except Exception as e:
            print(f"❌ Email error: {str(e)}")
            # If email fails, still continue but log it
        
        # 2. Save to Supabase (non-critical)
        try:
            # save_order_to_supabase(name, email, phone, address, quantity, payment_id)
            saved = save_order_to_supabase(
                name,
                email,
                phone,
                address,
                quantity,
                amount,
                payment_id
            )

            print("SAVE RESULT =", saved)
        except Exception as e:
            print(f"❌ Supabase save error: {str(e)}")
        
        # 3. Send WhatsApp (non-critical)
        try:
            send_whatsapp_message(name, phone, quantity)
        except Exception as e:
            print(f"❌ WhatsApp error: {str(e)}")
        
        # Always return success to user
        return HttpResponse(success_html)
    
    return HttpResponse("Invalid Request")

# ==========================================
# SUBSCRIPTION EMAIL FUNCTION
# ==========================================
def emailenquiry(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        try:
            subscription_html = f"""
            <html>
            <body style="font-family: Arial; background:#f4f4f4; padding:30px;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:15px; padding:30px;">
            <h1 style="color:#0b7d45; text-align:center;">🌿 Welcome to ECOMONKS</h1>
            <p>Thank you for subscribing to ECOMONKS.</p>
            <p>We are excited to have you as part of our growing family ❤️</p>
            </div>
            </body>
            </html>
            """
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login("founder@ecomonks.in", "crmwddzdzoqatofz")
            
            subscriber_msg = MIMEMultipart()
            subscriber_msg['From'] = "founder@ecomonks.in"
            subscriber_msg['To'] = email
            subscriber_msg['Subject'] = "ECOMONKS Subscription"
            subscriber_msg.attach(MIMEText(subscription_html, 'html', 'utf-8'))
            server.sendmail("founder@ecomonks.in", email, subscriber_msg.as_string())
            
            server.quit()
            
            return HttpResponse("""
            <script>
            alert('Subscribed Successfully');
            window.location='/';
            </script>
            """)
            
        except Exception as e:
            return HttpResponse(f"ERROR: {str(e)}")
    
    return HttpResponse("Invalid Request")