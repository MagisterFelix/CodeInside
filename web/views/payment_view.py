import stripe
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models import User
from web.permissions import permissions


class PaymentView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'payment.html'

    def get(self, request, primary_key=None):
        profile_link = 'http://localhost:4200/profile'
        if primary_key and User.objects.filter(id=primary_key).exists():
            u = User.objects.get(id=primary_key)
            discount = u.achievement.aggregate(Sum('discount'))['discount__sum']

            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                success_url=f"http://127.0.0.1:8000/postpayment/{u.email}/" + "{CHECKOUT_SESSION_ID}",
                cancel_url=profile_link,
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': f'CodeInside Premium for {u.email}',
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
            u = User.objects.get(email=email)
            if not u.premium:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                try:
                    checkout = stripe.checkout.Session.retrieve(session_id)
                    if checkout['payment_status'] == 'paid':
                        u.premium = session_id
                        u.save()
                except stripe.error.InvalidRequestError:
                    pass
        return redirect('http://localhost:4200/profile')
