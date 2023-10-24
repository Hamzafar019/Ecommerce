# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User  # Import the User model
# from .models import Order  # Import your Product model

# @receiver(post_save, sender=Order)
# def notify_superuser_on_new_product(sender, instance, created, **kwargs):
#     if created:
#         superusers = User.objects.filter(is_superuser=True)
#         for superuser in superusers:
#             # You can use any notification mechanism you prefer, such as sending an email
#             # You might need to import and configure Django's mail module
#             # mail_subject = 'New Product Added'
#             # mail_message = f'A new product "{instance.name}" has been added.'
#             # send_mail(mail_subject, mail_message, 'from@example.com', [superuser.email])

#             # For demonstration purposes, let's print a message to the console
#             print(f'New product added: {instance.id}')
