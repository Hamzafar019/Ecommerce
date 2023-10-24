from PyPDF2 import PdfMerger
import pywhatkit as kit
import datetime

from io import BytesIO
from django.contrib import admin
from django.http import HttpResponse
from .models import *
from .utils import generate_buyer_invoice
from .utils import generate_agent_invoice
# Register your models here.
# admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ProductionRun)



class PaymentInline(admin.TabularInline):
    model=Payment
    extra=0

class SellerAdmin(admin.ModelAdmin):
    inlines=[PaymentInline]
admin.site.register(Seller,SellerAdmin)
# admin.site.register(Order)
# admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

# admin.site.register(Material)
admin.site.register(Purchase)

class PurchaseInline(admin.TabularInline):
    model=Purchase
    extra=0

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'totalquantity', 'display_price_per_unit', 'get_last_purchase_date')
    readonly_fields = ('display_price_per_unit',)
    inlines=[PurchaseInline]


    def get_total_purchases(self, obj):
        return ', '.join([f'{purchase.quantity} at Rs.{purchase.price} on {purchase.purchase_date.strftime("%d-%B-%Y")}' for purchase in obj.get_all_purchases()])

    get_total_purchases.short_description = "All Purchases"

    def get_last_purchase_date(self, obj):
        return obj.get_last_purchase_date()

    get_last_purchase_date.short_description = "Last Purchase Date"



    def add_custom_materials(self, request, queryset):
        quantity = float(request.POST.get('quantity', 0))
        price = float(request.POST.get('price', 0))
        
        for material in queryset:
            material.add_purchase(quantity, price)
        
        self.message_user(request, f"Added {quantity} units of materials to selected items.")
        
    add_custom_materials.short_description = "Add Custom Materials"  # Display name for the action

    actions = [add_custom_materials]

admin.site.register(Material, MaterialAdmin)


admin.site.register(UnitConversion)
# admin.site.register(ManufacturedProduct)
# admin.site.register(MaterialUsage)

class OrderItemInline(admin.TabularInline):
    model=OrderItem
    extra=0

class ShippingAddressInline(admin.TabularInline):
    model=ShippingAddress
    extra=0
class OrderDetail(admin.ModelAdmin):
    inlines=[OrderItemInline,ShippingAddressInline]
    list_display=['id','customer','complete','transaction_id','recieved_by_customer']
admin.site.register(Order,OrderDetail)


class OrdersInline(admin.TabularInline):
    model=Order
    extra=0

class CustomerOrder(admin.ModelAdmin):
    inlines=[OrdersInline]
    list_display=['id','name']
    
admin.site.register(Customer,CustomerOrder)


class MaterialUsageInline(admin.TabularInline):
    model = MaterialUsage
    extra = 0  # Set to 0 to avoid empty extra forms







@admin.register(ManufacturedProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'calculate_cost','total_amount','total_price','unit_cost_after_all_expenses')
    inlines = [MaterialUsageInline]


admin.site.register(DiscountCode)




admin.site.register(CommissionCode)
def mark_commissions_paid(modeladmin, request, queryset):
    for agent in queryset:
        agent.mark_all_commissions_paid()

mark_commissions_paid.short_description = "Mark all unpaid commissions as paid for selected agents"


def mark_payments_paid(modeladmin, request, queryset):
    for buyer in queryset:
        buyer.mark_all_payments_paid()

mark_payments_paid.short_description = "Mark all unpaid payments as paid for selected buyer"



def generate_agent_invoice_action(modeladmin, request, queryset):
    pdf_responses = []
    now = datetime.datetime.now()

    # Define the time when you want to send the message (in 24-hour format)
    # Adjust the hours and minutes as needed
    
    
    if(now.minute<58):
        min=now.minute+1
        hr=now.hour
    else:
        min=1
        hr=now.hour+1
    send_time = now.replace(hour=hr,minute=min)
    
    # Send the message and PDF file
    # kit.sendwhatmsg(phone_number, message, send_time.hour, send_
    buyer2=""
    for buyer in queryset:
        buyer2=buyer
        pdf_response = generate_agent_invoice(buyer)
        pdf_responses.append(pdf_response)

    
    phone_number = buyer2.phone_number
    message=""
    message+=f'Name: {buyer2.name}\n'
    # elements.append(Paragraph(f'Date: {timezone.now().strftime("%Y-%m-%d")}', styles['Normal']))
    # elements.append(Paragraph(f'Time: {timezone.now().strftime("%H:%M:%S")}', styles['Normal']))
 
    last_payment = None

    for payment in AgentCommission.objects.filter(agent=buyer2):
        last_payment = [payment.orderid, payment.totalamount, payment.buyerdiscount, payment.buyerpayment, payment.commission, payment.agentbuyprice, "Yes" if payment.paid else "No"]

    sell=None
    try:
        sell = Sell.objects.get(id=last_payment[0])  # Assuming you have a field named 'orderid' in your Sell model
    except:
        pass
    product_sales = ProductSale.objects.filter(sell=sell)
    
    message+=f"Order ID: {last_payment[0]}\n"
    message+="Order Details \n"
    for product_sale in product_sales:
        name = product_sale.product.name
        quantity = product_sale.quantity
        price = product_sale.price
        message+=f"Product Name: {name}, Quantity: {quantity}, Price: {price}\n"
    
    message+="---------------\n"
    message+=f"Total Amount {last_payment[1]}\n"
    message+=f"Discount {last_payment[2]}\n"
    message+=f"After Discount {last_payment[3]}\n"
    message+=f"Commission {last_payment[4]}\n"
    message+=f"Total Price {last_payment[5]}\n"
    if(last_payment[6]=="Yes"):
        message+=f"Previous Commission {buyer2.amount}\n"
        message+=f"Total Commission {buyer2.amount+last_payment[4]}\n"
    else:
        message+=f"Previous Commission {buyer2.amount-last_payment[4]}\n"
        message+=f"Total Commission {buyer2.amount}\n"
    
    message+=f"Paid {last_payment[6]}\n"
    # Merge all PDF responses into one
    merged_pdf_response = HttpResponse(content_type='application/pdf')
    merged_pdf_response['Content-Disposition'] = 'attachment; filename="buyer_invoices.pdf"'
    pdf_merger = PdfMerger()
    for pdf_response in pdf_responses:
        pdf_merger.append(BytesIO(pdf_response.content))
    pdf_merger.write(merged_pdf_response)
    # merged_pdf_response.seek(0)
    print(phone_number)
    kit.sendwhatmsg(phone_number, message, send_time.hour, send_time.minute, send_time.second)
    return merged_pdf_response

generate_agent_invoice_action.short_description = "Generate PDF Invoices"



class AgentCommissionInline(admin.TabularInline):
    model = AgentCommission
    extra = 0  
@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount')
    actions = [mark_commissions_paid,generate_agent_invoice_action]
    inlines=[AgentCommissionInline]
admin.site.register(ProductSale)
# admin.site.register(Buyer)











def generate_buyer_invoice_action(modeladmin, request, queryset):

    now = datetime.datetime.now()
    print(now)
    if(now.minute<58):
        min=now.minute+1
        hr=now.hour
    else:
        min=1
        hr=now.hour+1
    send_time = now.replace(hour=hr,minute=min)
    buyer2=""

    pdf_responses = []
    for buyer in queryset:
        buyer2=buyer
        pdf_response = generate_buyer_invoice(buyer)
        pdf_responses.append(pdf_response)


    message=""
    
    phone_number = buyer2.phone_number
    message=""
    message+=f'Name: {buyer2.name}\n'
    last_payment = None

    for payment in BuyerPayments.objects.filter(buyer=buyer):
        last_payment = [payment.orderid, payment.totalamount, payment.buyerdiscount, payment.payment, "Yes" if payment.paid else "No"]

    message+=f'Order Id: {last_payment[0]}\n'
    sell=None
    try:
        sell = Sell.objects.get(id=last_payment[0])  # Assuming you have a field named 'orderid' in your Sell model
    except:
        pass
    product_sales = ProductSale.objects.filter(sell=sell)
    for product_sale in product_sales:
        name = product_sale.product.name
        quantity = product_sale.quantity
        price = product_sale.price
        message+=f'Prdouct Name: {name} Quantity: {quantity} Price: {price}\n'
    message+=f'Total Amount: {last_payment[1]}\n'
    message+=f'Discount: {last_payment[2]}\n'
    message+=f'After Discount: {last_payment[3]}\n'
    if(last_payment[4]=="Yes"):
        message+=f'Balance: {buyer2.remaining_amount}\n'
        message+=f'Total Amount: {buyer2.remaining_amount+last_payment[3]}\n'
    else:
        message+=f'Balance: {buyer2.remaining_amount-last_payment[3]}\n'
        message+=f'Total Amount: {buyer2.remaining_amount}\n'

    message+=f'Paid: {last_payment[4]}\n'


    # Merge all PDF responses into one
    merged_pdf_response = HttpResponse(content_type='application/pdf')
    merged_pdf_response['Content-Disposition'] = 'attachment; filename="buyer_invoices.pdf"'
    pdf_merger = PdfMerger()
    for pdf_response in pdf_responses:
        pdf_merger.append(BytesIO(pdf_response.content))
    pdf_merger.write(merged_pdf_response)
    
    kit.sendwhatmsg(phone_number, message, send_time.hour, send_time.minute, send_time.second)
    return merged_pdf_response

generate_buyer_invoice_action.short_description = "Generate PDF Invoices"


class BuyerPaymentInline(admin.TabularInline):
    model = BuyerPayments
    extra = 0  
@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'remaining_amount')
    actions = [mark_payments_paid,generate_buyer_invoice_action]
    inlines=[BuyerPaymentInline]




class ProductSaleInline(admin.TabularInline):
    model = ProductSale
    extra = 0  # Set to 0 to avoid empty extra forms
@admin.register(Sell)
class ProductSellAdmin(admin.ModelAdmin):
    # list_display = ('selling_date','calculate_total_price','price_after_discount')
    inlines = [ProductSaleInline]

    # def view_materials_and_costs(self, obj):
    #     material_usages = MaterialUsage.objects.filter(product=obj)
    #     total_cost = sum(usage.used_amount * usage.material.price for usage in material_usages)
        
    #     return f'Total Cost: ${total_cost:.2f}'
    
    # view_materials_and_costs.short_description = 'Materials and Costs'  # Column header


# class PurchaseAdmin(admin.ModelAdmin):
#     list_display = ('material.name', 'purchase_date')
#     # Other fields and configurations...

# admin.site.register(Purchase, PurchaseAdmin)