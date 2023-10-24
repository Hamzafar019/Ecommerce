import json
from .models import *
from reportlab.platypus.flowables import HRFlowable,Spacer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.utils import timezone


def generate_buyer_invoice(buyer):
    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{buyer.name}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Create a list of elements for the PDF

    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f'Invoice for {buyer.name}', styles['Title']))
    
    elements.append(Spacer(1, 8))
    # Add the date to the invoice
    elements.append(Paragraph(f'Date: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal']))
    # Add a blank line
    elements.append(Spacer(1, 8))

    # Add buyer information
    elements.append(Paragraph(f'Buyer Name: {buyer.name}', styles['Normal']))
    # Add a blank line
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f'Address: {buyer.address}', styles['Normal']))
    # Add a blank line
    elements.append(Spacer(1, 18))

    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
    # Add remaining

    # Create a table for payment details
    data = [
        ['Order ID', 'Total Amount', 'Discount', 'Payment', 'Paid'],
    ]

    last_payment = None

    for payment in BuyerPayments.objects.filter(buyer=buyer):
        last_payment = [payment.orderid, payment.totalamount, payment.buyerdiscount, payment.payment, "Yes" if payment.paid else "No"]

    elements.append(Paragraph(f'Order ID: {last_payment[0]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    sell=None
    try:
        sell = Sell.objects.get(id=last_payment[0])  # Assuming you have a field named 'orderid' in your Sell model
    except:
        pass
    product_sales = ProductSale.objects.filter(sell=sell)
    data=[["Product Name","Quantity","Price"],]
    for product_sale in product_sales:
        name = product_sale.product.name
        quantity = product_sale.quantity
        price = product_sale.price
        data.append([name,quantity,price])
        # Now you can use 'quantity' and 'price' for each ProductSale related to the Sell instance.
    # for payment in BuyerPayments.objects.filter(buyer=buyer):
    #     data.append([payment.orderid, payment.totalamount, payment.buyerdiscount, payment.payment, "Yes" if payment.paid else "No"])
    table = Table(data, colWidths=[80, 80, 80, 80, 80])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)

    elements.append(Spacer(1, 8))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f'Total Amount: {last_payment[1]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'Discount: {last_payment[2]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'After Discount: {last_payment[3]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    if(last_payment[4]=="Yes"):
        elements.append(Paragraph(f'Balance: {buyer.remaining_amount}', styles['Normal']))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
        elements.append(Paragraph(f'Total Amount: {buyer.remaining_amount+last_payment[3]}', styles['Normal']))
        elements.append(Spacer(1, 8)) 
    else:
        elements.append(Paragraph(f'Balance: {buyer.remaining_amount-last_payment[3]}', styles['Normal']))  
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
        elements.append(Paragraph(f'Total Amount: {buyer.remaining_amount}', styles['Normal']))
        elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'Paid: {last_payment[4]}', styles['Normal']))


    # Customize the content and style as needed
    # Add more elements to the PDF


    # Build the PDF document and return it as a response
    doc.build(elements)
    return response





def generate_agent_invoice(agent):
    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{agent.name}.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Create a list of elements for the PDF

    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f'Invoice for {agent.name}', styles['Title']))
    
    elements.append(Spacer(1, 8))
    # Add the date to the invoice
    elements.append(Paragraph(f'Date: {timezone.now().strftime("%Y-%m-%d")}', styles['Normal']))
    elements.append(Paragraph(f'Time: {timezone.now().strftime("%H:%M:%S")}', styles['Normal']))
    # Add a blank line
    elements.append(Spacer(1, 8))

    # Add buyer information
    elements.append(Paragraph(f'Buyer Name: {agent.name}', styles['Normal']))
    # Add a blank line
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f'Address: {agent.address}', styles['Normal']))
    # Add a blank line
    elements.append(Spacer(1, 18))

    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
    # Add remaining

    # Create a table for payment details
    data = [
        ['Order ID', 'Total Amount', 'Discount', 'Payment', 'Paid'],
    ]

    last_payment = None

    for payment in AgentCommission.objects.filter(agent=agent):
        last_payment = [payment.orderid, payment.totalamount, payment.buyerdiscount, payment.buyerpayment, payment.commission, payment.agentbuyprice, "Yes" if payment.paid else "No"]

    elements.append(Paragraph(f'Order ID: {last_payment[0]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    sell=None
    try:
        sell = Sell.objects.get(id=last_payment[0])  # Assuming you have a field named 'orderid' in your Sell model
    except:
        pass
    product_sales = ProductSale.objects.filter(sell=sell)
    data=[["Product Name","Quantity","Price"],]
    for product_sale in product_sales:
        name = product_sale.product.name
        quantity = product_sale.quantity
        price = product_sale.price
        data.append([name,quantity,price])
        # Now you can use 'quantity' and 'price' for each ProductSale related to the Sell instance.
    # for payment in BuyerPayments.objects.filter(buyer=buyer):
    #     data.append([payment.orderid, payment.totalamount, payment.buyerdiscount, payment.payment, "Yes" if payment.paid else "No"])
    table = Table(data, colWidths=[80, 80, 80, 80, 80])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)

    elements.append(Spacer(1, 8))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f'Total Amount: {last_payment[1]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'Discount: {last_payment[2]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'After Discount: {last_payment[3]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'Commission: {last_payment[4]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'Total Price: {last_payment[5]}', styles['Normal']))
    elements.append(Spacer(1, 8))
    if(last_payment[6]=="Yes"):
        elements.append(Paragraph(f'Previous Commission: {agent.amount}', styles['Normal']))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
        elements.append(Paragraph(f'Total Commission: {agent.amount+last_payment[4]}', styles['Normal']))
        elements.append(Spacer(1, 8)) 
    else:
        elements.append(Paragraph(f'Previous Commission: {agent.amount-last_payment[4]}', styles['Normal']))  
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round'))
        elements.append(Paragraph(f'Total Commission: {agent.amount}', styles['Normal']))
        elements.append(Spacer(1, 8))
    elements.append(Paragraph(f'Paid: {last_payment[6]}', styles['Normal']))


    # Customize the content and style as needed
    # Add more elements to the PDF


    # Build the PDF document and return it as a response
    doc.build(elements)
    return response








# def generate_buyer_invoice(buyer):
#     # Create a PDF document
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="invoice_{buyer.name}.pdf"'
#     doc = SimpleDocTemplate(response, pagesize=letter)

#     # Create a list of elements for the PDF
#     elements = []

#     # Add a title
#     styles = getSampleStyleSheet()
#     elements.append(Paragraph(f'Invoice for {buyer.name}', styles['Title']))

#     # Create a table for payment details
#     data = [
#         ['Order ID', 'Total Amount', 'Discount', 'Payment', 'Paid'],
#     ]
#     for payment in BuyerPayments.objects.filter(buyer=buyer):
#         data.append([payment.orderid, payment.totalamount, payment.buyerdiscount, payment.payment, "Yes" if payment.paid else "No"])
#     table = Table(data, colWidths=[80, 80, 80, 80, 80])
#     table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                                 ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
#     elements.append(table)

#     # Customize the content and style as needed
#     # Add more elements to the PDF

#     # Build the PDF document and return it as a response
#     doc.build(elements)
#     return response


# def cookieCart(request):
#     try:
#         cart=json.loads(request.COOKIES['cart'])
#     except:
#         cart={}
#     items=[]
#     order={
#         'get_cart_total':0,
#         'get_cart_items':0,
#         'shipping':False
#     }
#     cartItems=order['get_cart_items']
#     for i in cart:
#         try:
#             cartItems+=cart[i]['quantity']

#             product=Product.objects.get(id=i)
#             total=(product.price*cart[i]['quantity'])
#             order['get_cart_total']+=total
#             order['get_cart_items']+=cart[i]['quantity']
#             item={
#                 'product':{
#                     'id':product.id,
#                     'name':product.name,
#                     'price':product.price,
#                     'imageURL':product.imageURL,
#                 },
#                 'quantity':cart[i]['quantity'],
#                 'get_total':total
#             }
#             items.append(item)
#             if product.digital==False:
#                 order['shipping']=True
#         except:
#             pass
#     return{'cartItems':cartItems,'order':order,'items':items}

def cartData(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
    #    cookieData=cookieCart(request)
       
       items=[]
       order={
           'get_cart_total':0,
           'get_cart_items':0,
           'shipping':False
        }
       cartItems=order['get_cart_items']
    #    items=cookieData['items']
    #    order=cookieData['order']
    #    cartItems=cookieData['cartItems'] 
    return {'cartItems':cartItems,'order':order,'items':items}


# def guestOrder(request, data):
#     print("User is not logged in..")
#     name=data['form']['name']
#     email=data['form']['email']

#     cookieData=cookieCart(request)
#     items=cookieData['items']
#     customer,created=Customer.objects.get_or_create(email=email)
#     customer.name=name
#     customer.save()

#     order=Order.objects.create(
#         customer=customer,
#         complete=False
#     )

#     for item in items:
#         product=Product.objects.get(id=item['product']['id'])
#         orderItem=OrderItem.objects.create(
#             product=product,
#             order=order,
#             quantity=item['quantity']
#         )
#     return customer, order