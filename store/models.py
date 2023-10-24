
from decimal import Decimal, ROUND_UP
from django.contrib import admin 
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import F

class Seller(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200,default=None,blank=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Initial balance is 0
    
    # Add other seller-related fields as needed
    
    def __str__(self):
        return self.name

class Payment(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)  # To indicate if the payment is fully paid
    payment_method = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('cheque', 'Cheque')], default='cash')
    is_cheque_paid = models.BooleanField(default=False)  # To indicate if the cheque is paid
    cheque_number = models.CharField(max_length=20, blank=True, null=True)
    # You can add other payment-related fields here
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update the remaining amount you owe to the seller after saving a new payment
        if self.payment_method == 'cash' and self.is_paid:
            self.seller.remaining_amount -= self.amount_to_pay
        elif self.payment_method == 'cheque' and self.is_cheque_paid:
            self.seller.remaining_amount -= self.amount_to_pay
        self.seller.save()
    
    def __str__(self):
        return f"Payment of {self.amount_to_pay} to {self.seller.name} on {self.payment_date}"


class UnitConversion(models.Model):
    name = models.CharField(max_length=50)
    basename = models.CharField(max_length=50)
    factor_to_base = models.DecimalField(max_digits=10, decimal_places=6)

    def __str__(self):
        return self.name
    













class Buyer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200,default=None,blank=True)
    discount = models.ForeignKey('DiscountCode', on_delete=models.CASCADE, blank=True, default=None, null=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Initial balance is 0
    phone_number = models.CharField(max_length=20,null=True,blank=True) 
    
    def mark_all_payments_paid(self):
        # Mark all unpaid commissions as paid and update the agent's amount
        unpaid_payments = BuyerPayments.objects.filter(buyer=self, paid=False)

        for payments in unpaid_payments:
            payments.paid = True
            payments.save()

        self.update_amount()

    def __str__(self):
        return self.name
    
    def update_amount(self):
        # Calculate the total commission for unpaid AgentCommissions
        total_unpaid_payments = BuyerPayments.objects.filter(buyer=self, paid=False).aggregate(models.Sum('payment'))['payment__sum'] or 0
        print(total_unpaid_payments)
        # Update the Agent's amount based on unpaid commissions
        self.remaining_amount = total_unpaid_payments
        print("check1")
        self.save()

    # Add other seller-related fields as needed
    
    def __str__(self):
        return self.name
    

class BuyerPayments(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, null=True, blank=True, default=None)
    orderid = models.IntegerField(null=True, blank=True, default=None)
    totalamount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    buyerdiscount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order ID: {self.orderid}, Payment: Rs.{self.payment}"
    
    def save(self, *args, **kwargs):
        # if self.paid:
            # Update the associated Agent's amount if paid is True
        super().save(*args, **kwargs)
        print("Check2")
        print(self.buyer)
        if self.buyer:
            print(self.buyer)
            self.buyer.update_amount()



class Agent(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200,default=None,blank=True)
    commission = models.ForeignKey('CommissionCode', on_delete=models.CASCADE, blank=True, default=None, null=True)
    phone_number = models.CharField(max_length=20,null=True,blank=True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Initial balance is 0
    
    # Add other seller-related fields as needed
    def mark_all_commissions_paid(self):
        # Mark all unpaid commissions as paid and update the agent's amount
        unpaid_commissions = AgentCommission.objects.filter(agent=self, paid=False)

        for commission in unpaid_commissions:
            commission.paid = True
            commission.save()

        self.update_amount()

    def __str__(self):
        return self.name
    
    def update_amount(self):
        # Calculate the total commission for unpaid AgentCommissions
        total_unpaid_commission = AgentCommission.objects.filter(agent=self, paid=False).aggregate(models.Sum('commission'))['commission__sum'] or 0
        # print(total_unpaid_commission)
        # Update the Agent's amount based on unpaid commissions
        self.amount = total_unpaid_commission
        self.save()
    
class AgentCommission(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True, default=None)
    orderid = models.IntegerField(null=True, blank=True, default=None)
    totalamount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    buyerdiscount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    buyerpayment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    agentbuyprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order ID: {self.orderid}, Commission: Rs.{self.commission}"
    
    def save(self, *args, **kwargs):
        # if self.paid:
            # Update the associated Agent's amount if paid is True
        super().save(*args, **kwargs)
        # print(self.agent)
        if self.agent:
            # print(self.agent)
            self.agent.update_amount()

    
class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.code
    
class CommissionCode(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True)
    commission_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.code
    
class Sell(models.Model):
    products = models.ManyToManyField('ManufacturedProduct', through='ProductSale')
    selling_date = models.DateTimeField(auto_now_add=True, null=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, null=True, default=None, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True, default=None)
    # total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add this field with default=0
    discount = models.ForeignKey('DiscountCode', on_delete=models.CASCADE, default=None, blank=True, null=True)
    commission = models.ForeignKey('CommissionCode', on_delete=models.CASCADE, default=None, blank=True, null=True)
    discountvalue = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, editable=False)
    commissionvalue = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, editable=False)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0,null=True)
    price_after_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0,null=True)
    
    @property
    def calculate_total_price(self):
        # Calculate the total price based on the sum of ProductSale prices
        total_price = self.productsale_set.aggregate(models.Sum('price'))['price__sum'] or 0
        return total_price
    @property
    def apply_discount(self):
        # Calculate the discount amount based on the discount_value
        total_price_after_discount=0
        discount_amount=Decimal(str(0))
        if self.buyer and self.buyer.discount:
            discount_amount=self.buyer.discount.discount_value
        elif self.discount:
            discount_amount=self.discount.discount_value
        else:
            discount_amount=0.0
            discount_amount=Decimal(str(discount_amount))
        # Calculate the total price after applying the discount
        if self.pk is not None:
            self.discountvalue=self.calculate_total_price * (discount_amount/100)
            total_price_after_discount =self.calculate_total_price - self.discountvalue
            self.price_after_discount=total_price_after_discount
        # self.save()
        # print(discount_amount)
        return total_price_after_discount

    @property
    def apply_commission(self):
        total_price_after_commission=0
        commission_amount=Decimal(str(0))
        if self.agent and self.agent.commission:
            commission_amount=self.agent.commission.commission_value
        elif self.agent and self.commission:
            commission_amount=self.commission.commission_value
        else:
            commission_amount=0.0
            commission_amount=Decimal(str(commission_amount))
        if self.pk is not None:
            self.commissionvalue=self.apply_discount * (commission_amount/100)
            total_price_after_commission=self.apply_discount - self.commissionvalue
            self.price_after_commission=total_price_after_commission
        # self.save()

        return total_price_after_commission
    def __str__(self):
        self.apply_discount
        self.apply_commission
        buyer_name = self.buyer.name if self.buyer else "None"
        return f"Order {self.id} sold to {buyer_name} on {self.selling_date.strftime('%Y-%m-%d')}  having cost Rs.{self.calculate_total_price:.2f} after agent commission Rs.{self.commissionvalue:.2f} and  discount Rs.{self.discountvalue:.2f} final cost Rs.{self.price_after_commission:.2f}"
    def save(self, *args, **kwargs):
        # Call apply_commission and save the result to the database
        self.apply_discount
        self.apply_commission
        # Check if there is an existing AgentCommission instance with the same order ID
        super().save(*args, **kwargs)
        agent_commission, created = AgentCommission.objects.get_or_create(orderid=self.id)

        agent_commission.agent = self.agent 
        agent_commission.commission = self.commissionvalue
        agent_commission.buyerpayment = self.apply_discount
        agent_commission.buyerdiscount=self.discountvalue
        agent_commission.totalamount=self.calculate_total_price
        agent_commission.agentbuyprice=self.price_after_commission
        agent_commission.save()

        buyerpayment, created = BuyerPayments.objects.get_or_create(orderid=self.id)
        buyerpayment.buyer = self.buyer 
        buyerpayment.payment = self.apply_discount
        buyerpayment.buyerdiscount=self.discountvalue
        buyerpayment.totalamount=self.calculate_total_price
        
        buyerpayment.save()
        


class ProductSale(models.Model):
    product = models.ForeignKey('ManufacturedProduct', on_delete=models.CASCADE)
    sell = models.ForeignKey(Sell, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # payment_id = models.ForeignKey('SellPayment', on_delete=models.SET_NULL, null=True, editable=False)  # Reference to the seller

    def save(self, *args, **kwargs):
        # Get the original instance if it exists
        original_instance = None
        if self.pk:
            original_instance = ProductSale.objects.get(pk=self.pk)

        # Calculate the quantity difference
        quantity_diff = self.quantity - (original_instance.quantity if original_instance else 0)

        # Calculate the price based on the calculate_cost function of the associated ManufacturedProduct
        calculated_price = self.product.unit_cost_after_all_expenses * quantity_diff

        # Update the associated ManufacturedProduct
        self.product.total_amount -= quantity_diff
        self.product.total_price -= calculated_price
        self.product.save()


        super(ProductSale, self).save(*args, **kwargs)

    def __str__(self):
        return self.product.name
    
# class SellPayment(models.Model):
#     seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
#     new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     remaining = models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
#     amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     is_paid = models.BooleanField(default=False)  # To indicate if the payment is fully paid
#     payment_method = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('cheque', 'Cheque')], default='cash')
#     is_cheque_paid = models.BooleanField(default=False)  # To indicate if the cheque is paid
#     cheque_number = models.CharField(max_length=20, blank=True, null=True)
#     # You can add other payment-related fields here
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
        
#         # Update the remaining amount you owe to the seller after saving a new payment
#         if self.payment_method == 'cash' and self.is_paid:
#             self.seller.remaining_amount -= self.amount_to_pay
#         elif self.payment_method == 'cheque' and self.is_cheque_paid:
#             self.seller.remaining_amount -= self.amount_to_pay
#         self.seller.save()
    
#     def __str__(self):
#         return f"Payment of {self.amount_to_pay} to {self.seller.name} on {self.payment_date}"











class Purchase(models.Model):
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    unit = models.ForeignKey(UnitConversion, on_delete=models.CASCADE, default=None, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True) 
    payment_id = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, editable=False)  # Reference to the seller

    image = models.ImageField(null=True, blank=True)

    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new purchases
            super().save(*args, **kwargs)
            
            payment = Payment.objects.create(
                seller=self.seller,
                amount_to_pay=self.price+self.seller.remaining_amount,
                new_price=self.price,
                remaining=self.seller.remaining_amount,
                total=self.price+self.seller.remaining_amount,
                payment_method='cash'
            )
            
            self.seller.remaining_amount += self.price
            self.seller.save()
            
            self.payment_id = payment  # Save the payment ID in the Purchase model
            self.save()
        else:
            old_purchase = Purchase.objects.get(pk=self.pk)
            if old_purchase.price != self.price:
                payment_id = self.payment_id.id  # Get the payment ID from the Purchase model
                payment = Payment.objects.get(pk=payment_id)
                
                price_difference = self.price - old_purchase.price
                # payment.amount += price_difference
                payment.new_price += price_difference
                # payment.remaining += price_difference
                payment.total += price_difference
                payment.save()
                
                self.seller.remaining_amount += price_difference
                self.seller.save()
            
            super().save(*args, **kwargs)
        



    def __str__(self):
        return f"Purchase of {self.material.name} from {self.seller.name}"
    
@receiver(post_save, sender=Purchase)
def update_material_total(sender, instance, created, **kwargs):
    if created:
        instance.material.totalquantity += (instance.quantity*instance.unit.factor_to_base)
        instance.material.totalprice += instance.price
        instance.material.save()


@receiver(pre_save, sender=Purchase)
def update_material_total(sender, instance, **kwargs):
    if instance.pk:  # Only for existing purchases (not new ones)
        old_instance = Purchase.objects.get(pk=instance.pk)
        
        quantity_difference = instance.quantity * instance.unit.factor_to_base - old_instance.quantity * old_instance.unit.factor_to_base
        price_difference = instance.price - old_instance.price
        print(price_difference)
        print(instance.price)
        print(old_instance.price)
        instance.material.totalquantity += quantity_difference
        instance.material.totalprice += price_difference
        instance.material.save()
class Material(models.Model):
    name = models.CharField(max_length=100)
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.0)
    totalquantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.0)
    # amount2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.0)
    # unit = models.ForeignKey(UnitConversion, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return self.name
    
    # def add_purchase(self, quantity, price):
    #     self.totalquantity += quantity
    #     self.totalprice += price * quantity
    #     self.save()
    
    @property
    def price_per_unit(self):
        if self.totalquantity != 0:
            # conversion_factor = self.unit.factor_to_base
            return self.totalprice / self.totalquantity
        return 0.0
    
    @admin.display(description='Price per Unit')
    def display_price_per_unit(self):
        return self.price_per_unit
    

    def get_all_purchases(self):
        return Purchase.objects.filter(material=self)

    def get_last_purchase_date(self):
        last_purchase = self.purchase_set.order_by('-purchase_date').first()
        return last_purchase.purchase_date if last_purchase else None
class ManufacturedProduct(models.Model):
    name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    materials = models.ManyToManyField(Material, through='MaterialUsage')
    # quantity_produced = models.PositiveIntegerField(default=1)
    # labor_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # transport_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # electricity_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    @property
    def calculate_cost(self):
        total_material_cost = sum(
            usage.used_amount * usage.material.price_per_unit for usage in self.materialusage_set.all()
        )
        # total_material_cost=total_material_cost*self.quantity_produced
        # total_expenses = self.labor_charges + self.transport_charges + self.electricity_charges + self.other_expenses
        # total_cost = total_material_cost + total_expenses
        return total_material_cost
    
    @property
    def unit_cost_after_all_expenses(self):
        # cost=3
        if(self.total_price == 0 or self.total_amount == 0 ):
            cost=0
            return cost
        else:
            cost=self.total_price/self.total_amount
            return cost.quantize(Decimal('0.00'), rounding=ROUND_UP) 

    def __str__(self):
        return self.name
    

class MaterialUsage(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    product = models.ForeignKey(ManufacturedProduct, on_delete=models.CASCADE)
    used_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.material.name
    

# @receiver(post_save, sender=MaterialUsage)
# def update_material(sender, instance, **kwargs):
#     remaining_amount = instance.material.totalquantity - instance.used_amount*instance.product.quantity_produced
#     remaining_price = instance.material.totalprice - instance.used_amount*instance.material.price_per_unit*instance.product.quantity_produced
#     # if remaining_amount >= 0:
#     instance.material.totalquantity = remaining_amount
#     instance.material.totalprice = remaining_price
#     instance.material.save()

        
    # else:
        # Handle the case where the remaining amount is negative (if needed)
        # pass




class ProductionRun(models.Model):
    product = models.ForeignKey(ManufacturedProduct, on_delete=models.CASCADE)
    quantity_produced = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    labor_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    transport_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    electricity_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    @property
    def calculate_cost(self):
        total_material_cost = self.product.calculate_cost * self.quantity_produced
        total_expenses = self.labor_charges + self.transport_charges + self.electricity_charges + self.other_expenses
        total_cost = total_material_cost + total_expenses
        return total_cost
    
    def update_materials(self, previous_instance=None):
        quantity=self.quantity_produced 
        price=self.calculate_cost 
        
        if previous_instance:
            quantity-=previous_instance.quantity_produced
            price-=previous_instance.calculate_cost
        product_amount=self.product.total_amount
        product_price=self.product.total_price
        product_amount+=quantity
        product_price+=price
        self.product.total_amount=product_amount
        self.product.total_price=product_price
        self.product.save()
        
        material_usages = self.product.materialusage_set.all()
        
        # print(material_usages)
        for usage in material_usages:
            used_amount = usage.used_amount * self.quantity_produced
            if previous_instance:
                used_amount -= usage.used_amount * previous_instance.quantity_produced
               
            
            remaining_amount = usage.material.totalquantity - used_amount
            remaining_price = usage.material.totalprice - used_amount * usage.material.price_per_unit
            
            
            # print(remaining_price)
            Material.objects.filter(pk=usage.material_id).update(totalquantity=remaining_amount, totalprice=remaining_price)

    def save(self, *args, **kwargs):
        if self.pk:
            # If editing an existing instance, get the previous instance
            previous_instance = ProductionRun.objects.get(pk=self.pk)
        else:
            previous_instance = None
        super().save(*args, **kwargs)
        self.update_materials(previous_instance)

    def __str__(self):
        return f"{self.quantity_produced} {self.product.name} produced on {self.date} at the cost: Rs.{self.calculate_cost}"

# Signal to update materials after saving a ProductionRun
# @receiver(post_save, sender=ProductionRun)
# def update_materials(sender, instance, created, **kwargs):
#     if created:
#         instance.update_materials()


# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name=models.CharField(max_length=200, null=True)
    # email=models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name=models.CharField(max_length=200,null=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    digital=models.BooleanField(default=False, null=True, blank=False)
    image=models.ImageField(null=True,blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url

    
class Order(models.Model):
    customer=models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered=models.DateTimeField(auto_now_add=True)
    complete=models.BooleanField(default=False, null=True, blank=False)
    transaction_id=models.CharField(max_length=200, null=True)
    recieved_by_customer=models.BooleanField(default=False, null=True, blank=False)
    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self):
        shipping=False
        orderitems=self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping=True
        return shipping


    @property
    def get_cart_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product=models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity=models.IntegerField(default=0, null=True, blank=True)
    date_added=models.DateTimeField(auto_now_add=True)
    
    @property
    def get_total(self):
        total=self.product.price*self.quantity
        return total

class ShippingAddress(models.Model):
    customer=models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address=models.CharField(max_length=200, null=True)
    city=models.CharField(max_length=200, null=True)
    state=models.CharField(max_length=200, null=True)
    zipcode=models.CharField(max_length=200, null=True)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
    
    



