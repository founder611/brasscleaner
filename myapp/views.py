# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from django.shortcuts import render
# from django.http import HttpResponse
# import requests
# from datetime import datetime
# from Myapp.delhivery_config import DelhiveryAPI


# # Import Supabase
# from supabase import create_client

# def homepage(request):
#     return render(request, 'newhome.html')



# PRICING_TIERS = {
#     "50g":  {1: 199, 2: 349, 4: 649},
#     "175g": {1: 549, 2: 999, 4: 1899},
# }

# FREE_SHIPPING_THRESHOLD = 999   # ₹ — must match the JS
# SHIPPING_CHARGE = 49            # ₹ — must match the JS


# def calculate_price(quantity, pack_count):
#     tiers = PRICING_TIERS.get(quantity)
#     if not tiers:
#         return 0

#     if pack_count in tiers:
#         return tiers[pack_count]

#     tier_qtys = sorted(tiers.keys())
#     highest = tier_qtys[-1]

#     if pack_count > highest:
#         per_unit = tiers[highest] / highest
#         return round(per_unit * pack_count)

#     lower_qty = tier_qtys[0]
#     for tq in tier_qtys:
#         if tq <= pack_count:
#             lower_qty = tq
#     per_unit = tiers[lower_qty] / lower_qty
#     return round(per_unit * pack_count)


# def calculate_shipping(subtotal):
#     return 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_CHARGE

# def order_post(request):
#     name = request.POST['name']
#     email = request.POST['email']
#     phone = request.POST['phone']
#     address = request.POST['address']
#     quantity = request.POST['quantity']
#     city = request.POST.get('city', '')
#     district = request.POST.get('district', '')
#     state = request.POST.get('state', '')
#     pincode = request.POST.get('pincode', '')

#     try:
#         pack_count = int(request.POST.get('pack_count', 1))
#     except (TypeError, ValueError):
#         pack_count = 1
#     if pack_count < 1:
#         pack_count = 1

#     subtotal_rupees = calculate_price(quantity, pack_count)
#     shipping_rupees = calculate_shipping(subtotal_rupees)
#     total_rupees = subtotal_rupees + shipping_rupees

#     amount = int(round(total_rupees * 100))  # paise, for Razorpay

#     return render(request, 'pp.html', {
#         'name': name,
#         'email': email,
#         'phone': phone,
#         'address': address,
#         'quantity': quantity,
#         'city': city,
#         'district': district,
#         'state': state,
#         'pincode': pincode,
#         'pack_count': pack_count,
#         'subtotal_rupees': subtotal_rupees,
#         'shipping_rupees': shipping_rupees,
#         'price_rupees': total_rupees,   # keep same key your template expects
#         'amount': amount,
#         'razorpay_api_key': 'rzp_live_Su35EVyNYFeKCF',
#         'currency': 'INR'
#     })


# def raz_pay(request, amount):
#     import razorpay
#     razorpay_api_key = "rzp_live_Su35EVyNYFeKCF"
#     razorpay_secret_key = "NQE3JfS6rdlmp8YtHrxF120H"
    
#     razorpay_client = razorpay.Client(auth=(razorpay_api_key, razorpay_secret_key))
#     amount = float(amount)
    
#     order_data = {
#         'amount': amount,
#         'currency': 'INR',
#         'receipt': 'order_rcptid_11',
#         'payment_capture': '1',
#     }
    
#     order = razorpay_client.order.create(data=order_data)
    
#     return render(request, 'pp.html', {
#         'razorpay_api_key': razorpay_api_key,
#         'amount': order_data['amount'],
#         'currency': order_data['currency'],
#         'order_id': order['id']
#     })

# # ==========================================
# # SAVE ORDER TO SUPABASE - FIXED VERSION
# # ==========================================

# def save_order_to_supabase(name, email, phone, address, quantity, amount, payment_id, pack_count=1):
#     try:
#         print("===== SUPABASE FUNCTION STARTED =====")

#         supabase_url = "https://uuzumstwtrgzmeqgkjrj.supabase.co"
#         supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1enVtc3R3dHJnem1lcWdranJqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTUwODA1MSwiZXhwIjoyMDk3MDg0MDUxfQ.lZlydZ_sVQhcBteBBX1mucA_ZbmlkOS7yUVO8gYCV6U"
        
#         supabase = create_client(supabase_url, supabase_key)

#         order_data = {
#             "customer_name": name,
#             "email": email,
#             "phone": phone,
#             "address": address,
#             "quantity": quantity,
#             "amount": amount,
#             "payment_id": payment_id,
#             "payment_status": "Paid",
#             "pack_count": pack_count
#         }

#         print("ORDER DATA:", order_data)

#         result = supabase.table("brasscleaner_orders").insert(order_data).execute()

#         print("SUPABASE RESULT:", result)

#         return True

#     except Exception as e:
#         import traceback
#         print("===== SUPABASE ERROR =====")
#         print(traceback.format_exc())
#         return False
    


# import requests

# def send_whatsapp_message_template(name, phone, quantity, payment_id, amount, order_date=""):
#     try:
#         print("========== MBG WHATSAPP TEMPLATE ==========")

#         phone = str(phone).replace(" ", "").replace("+", "").strip()
#         if not phone.startswith("91"):
#             phone = "91" + phone

#         payload = {
#             "templateName": "brasscleaner_orderconfirmation",   # Your approved template name
#             "senderId": phone,                   # No '+' unless documentation requires it
#             "chatId": "1402050",
#             "variables": {
#                 "header": [],
#                 "body": [
#                     str(name),
#                     str(quantity),
#                     str(amount),
#                     str(payment_id),
#                     str(order_date)
#                 ]
#             }
#         }

#         response = requests.post(
#             "https://chatbot.digitalmbg.com/v1/whatsapp/send_templet",
#             headers={
#                 "Content-Type": "application/json",
#                 "x-api-key": "39832662461ae94fa94b03487c7866f3"
#             },
#             json=payload,
#             timeout=30
#         )

#         print("Status:", response.status_code)
#         print("Response:", response.text)

#         return response.status_code == 200

#     except Exception as e:
#         print(e)
#         return False


# import requests
# def send_whatsapp_message(name, phone, quantity, payment_id, amount, order_date=""):

#     phone = str(phone).replace("+", "").replace(" ", "")

#     if not phone.startswith("91"):
#         phone = "91" + phone

#     payload = {
#         "senderId": "+" + phone,
#         "name": name,
#         "actions": [

#             {
#                 "action": "set_field_value",
#                 "field_name": "name",
#                 "value": name
#             },

#             {
#                 "action": "set_field_value",
#                 "field_name": "quantity",
#                 "value": str(quantity)
#             },

#             {
#                 "action": "set_field_value",
#                 "field_name": "amount",
#                 "value": str(amount)
#             },

#             {
#                 "action": "set_field_value",
#                 "field_name": "payment_id",
#                 "value": payment_id
#             },

#             {
#                 "action": "set_field_value",
#                 "field_name": "order_date",
#                 "value": order_date
#             },

#             {
#                 "action": "send_flow",
#                 "flow_id": "flow_1782640760578"
#             }

#         ]
#     }

#     response = requests.post(
#         "https://chatbot.digitalmbg.com/v1/contacts",
#         headers={
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#             "x-api-key": "39832662461ae94fa94b03487c7866f3"
#         },
#         json=payload
#     )

#     print(response.status_code)
#     print(response.text)



# # def send_whatsapp_message(name, phone, quantity):
# #     try:

# #         print("========== WHATSAPP FUNCTION STARTED ==========")

# #         # Clean phone number
# #         phone = str(phone).replace(" ", "").replace("+", "").strip()

# #         # Add country code if missing
# #         if not phone.startswith("91"):
# #             phone = f"91{phone}"

# #         print("FINAL PHONE:", phone)

# #         # WATI API URL
# #         # url = f"https://live-mt-server.wati.io/1043453/api/v1/sendTemplateMessage?whatsappNumber={phone}"
        
# #         url = f"https://live-mt-server.wati.io/1043453/api/v1/sendTemplateMessage?whatsappNumber={phone}"


# #         # Payload
# #         payload = {
# #             "template_name": "order_confirmation",
# #             "broadcast_name": "order_confirmation",
# #             "parameters": [
# #                 {
# #                     "name": "1",
# #                     "value": str(name)
# #                 },
# #                 {
# #                     "name": "2",
# #                     "value": str(quantity)
# #                 }
# #             ]
# #         }

# #         print("PAYLOAD:", payload)

# #         # Headers
# #         headers = {
# #             "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6InByZW1zZWtoYXJAeWF0aGlzaGEuY29tIiwibmFtZWlkIjoicHJlbXNla2hhckB5YXRoaXNoYS5jb20iLCJlbWFpbCI6InByZW1zZWtoYXJAeWF0aGlzaGEuY29tIiwiYXV0aF90aW1lIjoiMDYvMDYvMjAyNiAxNzoxOToxNCIsInRlbmFudF9pZCI6IjEwNDM0NTMiLCJkYl9uYW1lIjoibXQtcHJvZC1UZW5hbnRzIiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiQURNSU5JU1RSQVRPUiIsImV4cCI6MjUzNDAyMzAwODAwLCJpc3MiOiJDbGFyZV9BSSIsImF1ZCI6IkNsYXJlX0FJIn0.i7aQp3cYOtk2wraWyMjHLP7L0T8znm-xf7SthfOPvZ4",
# #             "Content-Type": "application/json"
# #         }

# #         # Send request
# #         response = requests.post(
# #             url,
# #             json=payload,
# #             headers=headers,
# #             timeout=30
# #         )

# #         print("========== WATI RESPONSE ==========")
# #         print("STATUS CODE:", response.status_code)
# #         print("RESPONSE:", response.text)
# #         print("===================================")

# #         return response.status_code == 200

# #     except Exception as e:

# #         print("WhatsApp Error:", str(e))
# #         return False

# def get_weight(quantity, pack_count):
#     if quantity == "100ml":
#         return round(0.1 * pack_count, 3)

#     if quantity == "175ml":
#         return round(0.175 * pack_count, 3)

#     return 0.5
# # ==========================================
# # USER PAYMENT POST - MAIN FUNCTION
# # ==========================================
# def userpayment_post(request):
#     if request.method == "POST":
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')
#         amount = request.POST.get('amount')
#         address = request.POST.get('address')
#         quantity = request.POST.get('quantity')
#         payment_id = request.POST.get('payment_id')
#         city = request.POST.get("city")
#         district = request.POST.get("district")
#         state = request.POST.get("state")
#         pincode = request.POST.get("pincode")
#         quantity = request.POST.get('quantity')
#         payment_id = request.POST.get('payment_id')
#         amount = request.POST.get('amount')


#         full_address = f"{address}, {district}, {city}, {state} - {pincode}"


#         try:
#             amount = float(amount) / 100   # Paisa → Rupees
#         except:
#             amount = 0
        
#         if not email:
#             return HttpResponse("Email not found")
        
#         # Success HTML template
#         success_html = """
#         <script>
#         alert('Payment Successful!');
#         window.location='/';
#         </script>
#         """
        
#         # 1. Send emails (critical - if this fails, alert the user)
#         email_sent = False
#         try:
#             # Customer HTML Email
#             customer_html = f"""
#             <html>
#             <body style="font-family: Arial; background:#f4f4f4; padding:30px;">
#             <div style="max-width:600px; margin:auto; background:white; border-radius:15px; padding:30px;">
#             <h1 style="color:#0b7d45; text-align:center;">🌿 ECOMONKS</h1>
#             <h2>Thank You For Your Ordering Brass Cleaner</h2>
#             <p>Dear <b>{name}</b>,</p>
#             <p>Your payment has been received successfully and your order is confirmed.</p>
#             <div style="background:#f7fff9; border:1px solid #d4f5dd; padding:20px; border-radius:10px;">
#             <h3>🧾 Order Details</h3>
#             <p><b>👤 Name:</b> {name}</p>
#             <p><b>📧 Email:</b> {email}</p>
#             <p><b>📞 Phone:</b> {phone}</p>
#             <p><b>📍 Address:</b> {full_address}</p>
#             <p><b>📦 Quantity:</b> {quantity}</p>
#             <p><b>💰 Amount:</b> ₹{amount}</p>
#             <p><b>💳 Payment ID:</b> {payment_id}</p>
#             </div>
#             </div>
#             </body>
#             </html>
#             """
            
#             admin_html = f"""
#             <html>
#             <body>
#             <h2>🚨 NEW ORDER RECEIVED</h2>
#             <p><b>Customer:</b> {name}</p>
#             <p><b>Email:</b> {email}</p>
#             <p><b>Phone:</b> {phone}</p>
#             <p><b>Address:</b> {full_address}</p>
#             <p><b>Quantity:</b> {quantity}</p>
#             <p><b>Amount:</b> ₹{amount}</p>
#             <p><b>Payment ID:</b> {payment_id}</p>
#             </body>
#             </html>
#             """
            
#             server = smtplib.SMTP('smtp.gmail.com', 587)
#             server.starttls()
#             server.login("founder@ecomonks.in", "crmwddzdzoqatofz")
            
#             # Customer email
#             customer_msg = MIMEMultipart()
#             customer_msg['From'] = "founder@ecomonks.in"
#             customer_msg['To'] = email
#             customer_msg['Subject'] = "ECOMONKS Order Confirmation"
#             customer_msg.attach(MIMEText(customer_html, 'html', 'utf-8'))
#             server.sendmail("founder@ecomonks.in", email, customer_msg.as_string())
            
#             # Admin email
#             admin_msg = MIMEMultipart()
#             admin_msg['From'] = "founder@ecomonks.in"
#             admin_msg['To'] = "founder@ecomonks.in"
#             admin_msg['Subject'] = "New ECOMONKS Order Received"
#             admin_msg.attach(MIMEText(admin_html, 'html', 'utf-8'))
#             server.sendmail("founder@ecomonks.in", "founder@ecomonks.in", admin_msg.as_string())
            
#             server.quit()
#             email_sent = True
#             print("✅ Emails sent successfully")
            
#         except Exception as e:
#             print(f"❌ Email error: {str(e)}")
#             # If email fails, still continue but log it
        
#         # 2. Save to Supabase (non-critical)
#         try:
#             # save_order_to_supabase(name, email, phone, address, quantity, payment_id)
#             saved = save_order_to_supabase(
#                 name,
#                 email,
#                 phone,
#                 full_address,
#                 quantity,
#                 amount,
#                 payment_id
#             )

#             print("SAVE RESULT =", saved)
#         except Exception as e:
#             print(f"❌ Supabase save error: {str(e)}")
        
#         # 3. Send WhatsApp (non-critical)
#         try:
#             send_whatsapp_message(name, phone, quantity, payment_id, amount, order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#         except Exception as e:
#             print(f"❌ WhatsApp error: {str(e)}")


#         #4.
#          try:
#             print(f"Creating Delhivery shipment for order: {name}, {phone}, {full_address}, {quantity}, {payment_id}, {amount}")
#             print("="*70)
#             print("DELIVERY ADDRESS")
#             print("Address :", address)
#             print("District:", district)
#             print("City    :", city)
#             print("State   :", state)
#             print("Pincode :", pincode)
#             print("Supabase Address :", full_address)
#             print("="*70)
#             delhivery = DelhiveryAPI()
#             waybill = delhivery.generate_waybill()

#             print(f"Generated waybill: {waybill}")
#             order_data = {
#                 "customer_name": name,
#                 "phone": phone,

#                 "address": address,
#                 "district": district,
#                 "city": city,
#                 "state": state,
#                 "pincode": pincode,

#                 "order_id": payment_id,
#                 "amount": amount,
#                 "quantity": quantity,
#                 "waybill": waybill,
#                 "weight": get_weight(quantity, pack_count)
#             }
#             print(f"Order data for Delhivery: {order_data}")
#             shipment_response = delhivery.create_shipment(order_data)

#             print(f"Shipment response: {shipment_response}")    
#             if shipment_response:
#                 print(f"Shipment created: {shipment_response}")
#             else:
#                 print("Shipment creation failed")


#         except Exception as e:
#             print(f"❌ Delhivery API error: {str(e)}")

        
#         # Always return success to user
#         return HttpResponse(success_html)
    
#     return HttpResponse("Invalid Request")

# # ==========================================
# # SUBSCRIPTION EMAIL FUNCTION
# # ==========================================
# def emailenquiry(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
        
#         try:
#             subscription_html = f"""
#             <html>
#             <body style="font-family: Arial; background:#f4f4f4; padding:30px;">
#             <div style="max-width:600px; margin:auto; background:white; border-radius:15px; padding:30px;">
#             <h1 style="color:#0b7d45; text-align:center;">🌿 Welcome to ECOMONKS</h1>
#             <p>Thank you for subscribing to ECOMONKS.</p>
#             <p>We are excited to have you as part of our growing family ❤️</p>
#             </div>
#             </body>
#             </html>
#             """
            
#             server = smtplib.SMTP('smtp.gmail.com', 587)
#             server.starttls()
#             server.login("founder@ecomonks.in", "crmwddzdzoqatofz")
            
#             subscriber_msg = MIMEMultipart()
#             subscriber_msg['From'] = "founder@ecomonks.in"
#             subscriber_msg['To'] = email
#             subscriber_msg['Subject'] = "ECOMONKS Subscription"
#             subscriber_msg.attach(MIMEText(subscription_html, 'html', 'utf-8'))
#             server.sendmail("founder@ecomonks.in", email, subscriber_msg.as_string())
            
#             server.quit()
            
#             return HttpResponse("""
#             <script>
#             alert('Subscribed Successfully');
#             window.location='/';
#             </script>
#             """)
            
#         except Exception as e:
#             return HttpResponse(f"ERROR: {str(e)}")
    
#     return HttpResponse("Invalid Request")






# import json
# import random
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.core.cache import cache

# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return ''.join([str(random.randint(0, 9)) for _ in range(6)])

# def send_email_otp(email, otp):
#     """Send OTP via email"""
#     try:
#         html_content = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; background:#f4f4f4; padding:30px;">
#             <div style="max-width:450px; margin:auto; background:white; border-radius:12px; padding:30px; text-align:center;">
#                 <h1 style="color:#0b7d45; margin-bottom:8px;">🌿 ECOMONKS</h1>
#                 <h2 style="color:#333; font-weight:300;">Your Verification Code</h2>
#                 <div style="background:#f7fff9; padding:20px; border-radius:10px; margin:20px 0;">
#                     <div style="font-size:2.2rem; font-weight:700; letter-spacing:8px; color:#0b7d45; font-family:monospace;">
#                         {otp}
#                     </div>
#                 </div>
#                 <p style="color:#666; font-size:0.9rem;">
#                     Enter this code to verify your email and complete your order.<br>
#                     This code expires in 5 minutes.
#                 </p>
#                 <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
#                 <p style="color:#999; font-size:0.75rem;">
#                     If you didn't request this, please ignore this email.
#                 </p>
#             </div>
#         </body>
#         </html>
#         """
        
#         msg = MIMEMultipart()
#         msg['From'] = "founder@ecomonks.in"
#         msg['To'] = email
#         msg['Subject'] = "🔐 ECOMONKS - Email Verification Code"
#         msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login("founder@ecomonks.in", "crmwddzdzoqatofz")
#         server.sendmail("founder@ecomonks.in", email, msg.as_string())
#         server.quit()
        
#         return True
#     except Exception as e:
#         print(f"Email OTP error: {e}")
#         return False

# @csrf_exempt
# def send_otp(request):
#     """Send OTP to user's email"""
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    
#     try:
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#         except:
#             return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
#         email = data.get('email', '').strip()
        
#         if not email:
#             return JsonResponse({'status': 'error', 'message': 'Email required'}, status=400)
        
#         otp = generate_otp()
#         cache_key = f"otp_{email}"
#         cache.set(cache_key, otp, timeout=300)
        
#         if send_email_otp(email, otp):
#             return JsonResponse({'status': 'success', 'message': 'OTP sent to email'})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'Failed to send email'}, status=500)
            
#     except Exception as e:
#         print(f"Send OTP error: {e}")
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# @csrf_exempt
# def verify_otp(request):
#     """Verify the OTP submitted by user"""
#     if request.method != 'POST':
#         return JsonResponse({'verified': False, 'message': 'Invalid method'}, status=405)
    
#     try:
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#         except:
#             return JsonResponse({'verified': False, 'message': 'Invalid JSON'}, status=400)
        
#         otp_input = data.get('otp', '').strip()
#         email = data.get('email', '').strip()
        
#         if not email or not otp_input:
#             return JsonResponse({'verified': False, 'message': 'Missing data'}, status=400)
        
#         cache_key = f"otp_{email}"
#         stored_otp = cache.get(cache_key)
        
#         if not stored_otp:
#             return JsonResponse({'verified': False, 'message': 'OTP expired or not found'}, status=400)
        
#         if str(stored_otp) == str(otp_input):
#             cache.delete(cache_key)
#             return JsonResponse({'verified': True, 'message': 'OTP verified successfully'})
#         else:
#             return JsonResponse({'verified': False, 'message': 'Invalid OTP'}, status=400)
            
#     except Exception as e:
#         print(f"Verify OTP error: {e}")
#         return JsonResponse({'verified': False, 'message': str(e)}, status=500)


import os
import smtplib
import json
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import requests
from datetime import datetime

# Import Supabase
from supabase import create_client

# Import your Delhivery config
from myapp.delhivery_config import DelhiveryAPI



PRICING_TIERS = {
    "100ml": {1: 199, 2: 349, 4: 649},
    "200ml": {1: 349, 2: 649, 4: 1199},
}

FREE_SHIPPING_THRESHOLD = 999   # ₹
SHIPPING_CHARGE = 49            # ₹

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://uuzumstwtrgzmeqgkjrj.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1enVtc3R3dHJnem1lcWdranJqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTUwODA1MSwiZXhwIjoyMDk3MDg0MDUxfQ.lZlydZ_sVQhcBteBBX1mucA_ZbmlkOS7yUVO8gYCV6U")

RAZORPAY_API_KEY = os.environ.get("RAZORPAY_API_KEY", "rzp_live_Su35EVyNYFeKCF")
RAZORPAY_SECRET_KEY = os.environ.get("RAZORPAY_SECRET_KEY", "NQE3JfS6rdlmp8YtHrxF120H")

MBG_API_KEY = os.environ.get("MBG_API_KEY", "39832662461ae94fa94b03487c7866f3")

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "founder@ecomonks.in")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "crmwddzdzoqatofz")


# ==========================================
# VIEWS
# ==========================================

def homepage(request):
    return render(request, 'updatehome.html')


def calculate_price(quantity, pack_count):
    """Calculate price based on quantity and pack count"""
    tiers = PRICING_TIERS.get(quantity)
    if not tiers:
        return 0

    if pack_count in tiers:
        return tiers[pack_count]

    tier_qtys = sorted(tiers.keys())
    highest = tier_qtys[-1]

    if pack_count > highest:
        per_unit = tiers[highest] / highest
        return round(per_unit * pack_count)

    lower_qty = tier_qtys[0]
    for tq in tier_qtys:
        if tq <= pack_count:
            lower_qty = tq
    per_unit = tiers[lower_qty] / lower_qty
    return round(per_unit * pack_count)


def calculate_shipping(subtotal):
    """Calculate shipping charge based on subtotal"""
    return 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_CHARGE


def get_weight(quantity, pack_count):
    """Get weight in kg for Delhivery shipment"""
    if quantity == "100ml":
        return round(0.1 * pack_count, 3)
    elif quantity == "200ml":
        return round(0.2 * pack_count, 3)
    return 0.5


def order_post(request):
    """Handle order form submission and render payment page"""
    if request.method != "POST":
        return HttpResponse("Invalid Request")

    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    address = request.POST.get('address', '')
    quantity = request.POST.get('quantity', '')
    city = request.POST.get('city', '')
    district = request.POST.get('district', '')
    state = request.POST.get('state', '')
    pincode = request.POST.get('pincode', '')

    try:
        pack_count = int(request.POST.get('pack_count', 1))
    except (TypeError, ValueError):
        pack_count = 1
    if pack_count < 1:
        pack_count = 1

    subtotal_rupees = calculate_price(quantity, pack_count)
    shipping_rupees = calculate_shipping(subtotal_rupees)
    total_rupees = subtotal_rupees + shipping_rupees
    amount_paise = int(round(total_rupees * 100))  # paise for Razorpay

    return render(request, 'pp.html', {
        'name': name,
        'email': email,
        'phone': phone,
        'address': address,
        'quantity': quantity,
        'city': city,
        'district': district,
        'state': state,
        'pincode': pincode,
        'pack_count': pack_count,
        'subtotal_rupees': subtotal_rupees,
        'shipping_rupees': shipping_rupees,
        'price_rupees': total_rupees,
        'amount': amount_paise,
        'razorpay_api_key': RAZORPAY_API_KEY,
        'currency': 'INR'
    })


def raz_pay(request, amount):
    """Create Razorpay order"""
    import razorpay

    razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_SECRET_KEY))
    amount_float = float(amount)

    order_data = {
        'amount': int(amount_float * 100),  # paise
        'currency': 'INR',
        'receipt': 'order_rcptid_11',
        'payment_capture': '1',
    }

    order = razorpay_client.order.create(data=order_data)

    return render(request, 'pp.html', {
        'razorpay_api_key': RAZORPAY_API_KEY,
        'amount': order_data['amount'],
        'currency': order_data['currency'],
        'order_id': order['id']
    })


# ==========================================
# SUPABASE FUNCTIONS
# ==========================================

def save_order_to_supabase(name, email, phone, address, quantity, amount, payment_id, pack_count=1):
    """Save order to Supabase database"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        order_data = {
            "customer_name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "quantity": quantity,
            "amount": float(amount),
            "payment_id": payment_id,
            "payment_status": "Paid",
            "pack_count": pack_count
        }

        result = supabase.table("brasscleaner_orders").insert(order_data).execute()
        print("SUPABASE RESULT:", result)

        return True

    except Exception:
        import traceback
        print("===== SUPABASE ERROR =====")
        print(traceback.format_exc())
        return False


# ==========================================
# WHATSAPP FUNCTIONS
# ==========================================

def send_whatsapp_message(name, phone, quantity, payment_id, amount, order_date=""):
    """Send WhatsApp message using MBG API"""
    try:
        phone = str(phone).replace(" ", "").replace("+", "").strip()
        if not phone.startswith("91"):
            phone = "91" + phone

        if not order_date:
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "templateName": "brasscleaner_orderconfirmation",
            "senderId": phone,
            "chatId": "1402050",
            "variables": {
                "header": [],
                "body": [
                    str(name),
                    str(quantity),
                    str(amount),
                    str(payment_id),
                    str(order_date)
                ]
            }
        }

        response = requests.post(
            "https://chatbot.digitalmbg.com/v1/whatsapp/send_templet",
            headers={
                "Content-Type": "application/json",
                "x-api-key": MBG_API_KEY
            },
            json=payload,
            timeout=30
        )

        print("WhatsApp status:", response.status_code)
        return response.status_code == 200

    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False


def send_whatsapp_flow(name, phone, quantity, payment_id, amount, order_date=""):
    """Send WhatsApp flow using MBG contacts API"""
    try:
        phone = str(phone).replace("+", "").replace(" ", "").strip()
        if not phone.startswith("91"):
            phone = "91" + phone

        if not order_date:
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "senderId": "+" + phone,
            "name": name,
            "actions": [
                {"action": "set_field_value", "field_name": "name", "value": name},
                {"action": "set_field_value", "field_name": "quantity", "value": str(quantity)},
                {"action": "set_field_value", "field_name": "amount", "value": str(amount)},
                {"action": "set_field_value", "field_name": "payment_id", "value": payment_id},
                {"action": "set_field_value", "field_name": "order_date", "value": order_date},
                {"action": "send_flow", "flow_id": "flow_1782640760578"}
            ]
        }

        response = requests.post(
            "https://chatbot.digitalmbg.com/v1/contacts",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-key": MBG_API_KEY
            },
            json=payload,
            timeout=30
        )

        print("WhatsApp Flow status:", response.status_code)
        return response.status_code == 200

    except Exception as e:
        print(f"WhatsApp Flow Error: {e}")
        return False


# ==========================================
# EMAIL FUNCTIONS
# ==========================================

def send_email(subject, to_email, html_content):
    """
    Send email using SMTP.
    Returns (success: bool, error_message: str|None) so callers — especially
    the OTP flow — can tell the difference between "sent" and "silently failed".
    """
    server = None
    try:
        if not SMTP_PASSWORD:
            return False, "SMTP_PASSWORD is not configured on the server"

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True, None

    except smtplib.SMTPAuthenticationError as e:
        print(f"Email auth error: {e}")
        return False, "SMTP authentication failed — check SMTP_USER/SMTP_PASSWORD/SMTP_HOST"
    except Exception as e:
        print(f"Email error: {e}")
        return False, str(e)
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


# ==========================================
# PAYMENT POST - MAIN FUNCTION
# ==========================================

def userpayment_post(request):
    """Handle successful payment and process order"""
    if request.method != "POST":
        return HttpResponse("Invalid Request")

    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    amount = request.POST.get('amount', '0')
    address = request.POST.get('address', '')
    quantity = request.POST.get('quantity', '')
    payment_id = request.POST.get('payment_id', '')
    city = request.POST.get('city', '')
    district = request.POST.get('district', '')
    state = request.POST.get('state', '')
    pincode = request.POST.get('pincode', '')

    try:
        pack_count = int(request.POST.get('pack_count', 1))
    except (TypeError, ValueError):
        pack_count = 1

    full_address = f"{address}, {district}, {city}, {state} - {pincode}"

    try:
        amount_rupees = float(amount) / 100
    except (TypeError, ValueError):
        amount_rupees = 0

    if not email:
        return HttpResponse("Email not found")

    success_html = """
    <script>
    alert('Payment Successful!');
    window.location='/';
    </script>
    """

    # ─── 1. SEND EMAILS ───
    try:
        customer_html = f"""
        <html>
        <body style="font-family: Arial; background:#f4f4f4; padding:30px;">
        <div style="max-width:600px; margin:auto; background:white; border-radius:15px; padding:30px;">
        <h1 style="color:#0b7d45; text-align:center;">🌿 ECOMONKS</h1>
        <h2>Thank You For Your Order</h2>
        <p>Dear <b>{name}</b>,</p>
        <p>Your payment has been received successfully and your order is confirmed.</p>
        <div style="background:#f7fff9; border:1px solid #d4f5dd; padding:20px; border-radius:10px;">
        <h3>🧾 Order Details</h3>
        <p><b>👤 Name:</b> {name}</p>
        <p><b>📧 Email:</b> {email}</p>
        <p><b>📞 Phone:</b> {phone}</p>
        <p><b>📍 Address:</b> {full_address}</p>
        <p><b>📦 Quantity:</b> {quantity} ({pack_count} pack(s))</p>
        <p><b>💰 Amount:</b> ₹{amount_rupees:.2f}</p>
        <p><b>💳 Payment ID:</b> {payment_id}</p>
        </div>
        </div>
        </body>
        </html>
        """
        ok, err = send_email("ECOMONKS Order Confirmation", email, customer_html)
        if not ok:
            print(f"❌ Customer email failed: {err}")

        admin_html = f"""
        <html>
        <body>
        <h2>🚨 NEW ORDER RECEIVED</h2>
        <p><b>Customer:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Phone:</b> {phone}</p>
        <p><b>Address:</b> {full_address}</p>
        <p><b>Quantity:</b> {quantity} ({pack_count} pack(s))</p>
        <p><b>Amount:</b> ₹{amount_rupees:.2f}</p>
        <p><b>Payment ID:</b> {payment_id}</p>
        </body>
        </html>
        """
        ok, err = send_email("New ECOMONKS Order Received", "founder@ecomonks.in", admin_html)
        if not ok:
            print(f"❌ Admin email failed: {err}")

    except Exception as e:
        print(f"❌ Email error: {str(e)}")

    # ─── 2. SAVE TO SUPABASE ───
    try:
        saved = save_order_to_supabase(
            name, email, phone, full_address, quantity,
            amount_rupees, payment_id, pack_count
        )
        print(f"Supabase save result: {saved}")
    except Exception as e:
        print(f"❌ Supabase error: {str(e)}")

    # ─── 3. SEND WHATSAPP ───
    try:
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        send_whatsapp_message(name, phone, quantity, payment_id, amount_rupees, order_date)
    except Exception as e:
        print(f"❌ WhatsApp error: {str(e)}")

    # ─── 4. CREATE DELHIVERY SHIPMENT ───
    try:
        delhivery = DelhiveryAPI()
        waybill = delhivery.generate_waybill()

        order_data = {
            "customer_name": name,
            "phone": phone,
            "address": address,
            "district": district,
            "city": city,
            "state": state,
            "pincode": pincode,
            "order_id": payment_id,
            "amount": float(amount_rupees),
            "quantity": quantity,
            "waybill": waybill,
            "weight": get_weight(quantity, pack_count)
        }

        shipment_response = delhivery.create_shipment(order_data)

        if shipment_response:
            print(f"✅ Shipment created: {shipment_response}")
        else:
            print("❌ Shipment creation failed")

    except Exception as e:
        print(f"❌ Delhivery API error: {str(e)}")

    return HttpResponse(success_html)


# ==========================================
# SUBSCRIPTION EMAIL
# ==========================================

def emailenquiry(request):
    """Handle subscription email"""
    if request.method != "POST":
        return HttpResponse("Invalid Request")

    email = request.POST.get('email', '')

    if not email:
        return HttpResponse("Email required")

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

    ok, err = send_email("ECOMONKS Subscription", email, subscription_html)
    if not ok:
        return HttpResponse(f"ERROR: {err}")

    return HttpResponse("""
    <script>
    alert('Subscribed Successfully');
    window.location='/';
    </script>
    """)


# ==========================================
# OTP FUNCTIONS
# ==========================================

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_email_otp(email, otp):
    """Send OTP via email. Returns (success, error_message)."""
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f4f4f4; padding:30px;">
        <div style="max-width:450px; margin:auto; background:white; border-radius:12px; padding:30px; text-align:center;">
            <h1 style="color:#0b7d45; margin-bottom:8px;">🌿 ECOMONKS</h1>
            <h2 style="color:#333; font-weight:300;">Your Verification Code</h2>
            <div style="background:#f7fff9; padding:20px; border-radius:10px; margin:20px 0;">
                <div style="font-size:2.2rem; font-weight:700; letter-spacing:8px; color:#0b7d45; font-family:monospace;">
                    {otp}
                </div>
            </div>
            <p style="color:#666; font-size:0.9rem;">
                Enter this code to verify your email and complete your order.<br>
                This code expires in 5 minutes.
            </p>
            <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
            <p style="color:#999; font-size:0.75rem;">
                If you didn't request this, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    return send_email("🔐 ECOMONKS - Email Verification Code", email, html_content)


@csrf_exempt
def send_otp(request):
    """Send OTP to user's email"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '').strip()

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email required'}, status=400)

        otp = generate_otp()
        cache_key = f"otp_{email}"
        cache.set(cache_key, otp, timeout=300)

        ok, err = send_email_otp(email, otp)
        if ok:
            return JsonResponse({'status': 'success', 'message': 'OTP sent to email'})
        else:
            # Surface the real reason instead of swallowing it, so the
            # frontend can actually tell the user what went wrong.
            return JsonResponse({'status': 'error', 'message': err or 'Failed to send email'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Send OTP error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def verify_otp(request):
    """Verify the OTP submitted by user"""
    if request.method != 'POST':
        return JsonResponse({'verified': False, 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        otp_input = data.get('otp', '').strip()
        email = data.get('email', '').strip()

        if not email or not otp_input:
            return JsonResponse({'verified': False, 'message': 'Missing data'}, status=400)

        cache_key = f"otp_{email}"
        stored_otp = cache.get(cache_key)

        if not stored_otp:
            return JsonResponse({'verified': False, 'message': 'OTP expired or not found'}, status=400)

        if str(stored_otp) == str(otp_input):
            cache.delete(cache_key)
            return JsonResponse({'verified': True, 'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'verified': False, 'message': 'Invalid OTP'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'verified': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Verify OTP error: {e}")
        return JsonResponse({'verified': False, 'message': str(e)}, status=500)