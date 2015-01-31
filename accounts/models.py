from django.dispatch import receiver
from registration.signals import user_registered

@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
	user.first_name = request.POST.get('first_name')
	user.last_name = request.POST.get('last_name')
	user.save()
