import stripe
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe.error import InvalidRequestError

from core.web.models import User
from core.web.permissions import permissions


class PaymentView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment.html'

    def get(self, request, primary_key=None):
        profile_link = 'https://codeinside-web.herokuapp.com/profile'
        if primary_key and User.objects.filter(id=primary_key).exists():
            user = User.objects.get(id=primary_key)
            discount = user.achievement.aggregate(Sum('discount'))['discount__sum']

            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                success_url=f"https://codeinside.herokuapp.com/postpayment/{user.email}/" + "{CHECKOUT_SESSION_ID}",
                cancel_url=profile_link,
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': f'CodeInside Premium for {user.email}',
                        'quantity': 1,
                        'currency': 'usd',
                        'amount': f'{int(500 * (1 - discount / 100))}' if discount else '500',
                    }
                ]
            )

            return Response({'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
                             'sessionId': checkout_session['id'],
                             'publicKey': stripe.api_key})
        return redirect(profile_link)


class PostPaymentView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, email=None, session_id=None):
        if email and session_id and User.objects.filter(email=email).exists() and not User.objects.filter(
                premium=session_id).exists():
            user = User.objects.get(email=email)
            if not user.premium:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                try:
                    checkout = stripe.checkout.Session.retrieve(session_id)
                    if checkout['payment_status'] == 'paid':
                        user.premium = session_id
                        user.save()
                except InvalidRequestError:
                    pass
        return redirect('https://codeinside-web.herokuapp.com/profile')
