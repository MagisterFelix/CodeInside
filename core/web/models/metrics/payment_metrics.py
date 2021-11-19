from core.web.models import User
from django.conf import settings
import stripe


class PaymentMetrics(User):
    class Meta:
        proxy = True
        verbose_name = 'Payments'
        verbose_name_plural = 'Payments'

    @staticmethod
    def country_stats():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customers = stripe.Customer.list()['data']
        customer_metrics = {
            "AF": ["Afghanistan", 0],
            "AX": ["Åland Islands", 0],
            "AL": ["Albania", 0],
            "DZ": ["Algeria", 0],
            "AS": ["American Samoa", 0],
            "AD": ["Andorra", 0],
            "AO": ["Angola", 0],
            "AI": ["Anguilla", 0],
            "AG": ["Antigua and Barbuda", 0],
            "AR": ["Argentina", 0],
            "AM": ["Armenia", 0],
            "AW": ["Aruba", 0],
            "AU": ["Australia", 0],
            "AT": ["Austria", 0],
            "AZ": ["Azerbaijan", 0],
            "BS": ["Bahamas", 0],
            "BH": ["Bahrain", 0],
            "BD": ["Bangladesh", 0],
            "BB": ["Barbados", 0],
            "BY": ["Belarus", 0],
            "BE": ["Belgium", 0],
            "BZ": ["Belize", 0],
            "BJ": ["Benin", 0],
            "BM": ["Bermuda", 0],
            "BT": ["Bhutan", 0],
            "BA": ["Bosnia and Herzegovina", 0],
            "BW": ["Botswana", 0],
            "BR": ["Brazil", 0],
            "BN": ["Brunei Darussalam", 0],
            "BG": ["Bulgaria", 0],
            "BF": ["Burkina Faso", 0],
            "BI": ["Burundi", 0],
            "KH": ["Cambodia", 0],
            "CM": ["Cameroon", 0],
            "CA": ["Canada", 0],
            "CV": ["Cape Verde", 0],
            "KY": ["Cayman Islands", 0],
            "CF": ["Central African Republic", 0],
            "TD": ["Chad", 0],
            "CL": ["Chile", 0],
            "CN": ["China", 0],
            "CO": ["Colombia", 0],
            "KM": ["Comoros", 0],
            "CG": ["Congo", 0],
            "CR": ["Costa Rica", 0],
            "CI": ["Côte d'Ivoire", 0],
            "HR": ["Croatia", 0],
            "CU": ["Cuba", 0],
            "CY": ["Cyprus", 0],
            "CZ": ["Czech Republic", 0],
            "DK": ["Denmark", 0],
            "DJ": ["Djibouti", 0],
            "DM": ["Dominica", 0],
            "DO": ["Dominican Republic", 0],
            "EC": ["Ecuador", 0],
            "EG": ["Egypt", 0],
            "SV": ["El Salvador", 0],
            "GQ": ["Equatorial Guinea", 0],
            "ER": ["Eritrea", 0],
            "EE": ["Estonia", 0],
            "ET": ["Ethiopia", 0],
            "FK": ["Falkland Islands (Malvinas)", 0],
            "FO": ["Faroe Islands", 0],
            "FJ": ["Fiji", 0],
            "FI": ["Finland", 0],
            "FR": ["France", 0],
            "GF": ["French Guiana", 0],
            "GA": ["Gabon", 0],
            "GM": ["Gambia", 0],
            "GE": ["Georgia", 0],
            "DE": ["Germany", 0],
            "GH": ["Ghana", 0],
            "GI": ["Gibraltar", 0],
            "GR": ["Greece", 0],
            "GL": ["Greenland", 0],
            "GD": ["Grenada", 0],
            "GP": ["Guadeloupe", 0],
            "GU": ["Guam", 0],
            "GT": ["Guatemala", 0],
            "GG": ["Guernsey", 0],
            "GN": ["Guinea", 0],
            "GW": ["Guinea-Bissau", 0],
            "GY": ["Guyana", 0],
            "HT": ["Haiti", 0],
            "VA": ["Holy See (Vatican City State)", 0],
            "HN": ["Honduras", 0],
            "HK": ["Hong Kong", 0],
            "HU": ["Hungary", 0],
            "IS": ["Iceland", 0],
            "IN": ["India", 0],
            "ID": ["Indonesia", 0],
            "IQ": ["Iraq", 0],
            "IE": ["Ireland", 0],
            "IM": ["Isle of Man", 0],
            "IL": ["Israel", 0],
            "IT": ["Italy", 0],
            "JM": ["Jamaica", 0],
            "JP": ["Japan", 0],
            "JE": ["Jersey", 0],
            "JO": ["Jordan", 0],
            "KZ": ["Kazakhstan", 0],
            "KE": ["Kenya", 0],
            "KI": ["Kiribati", 0],
            "KW": ["Kuwait", 0],
            "KG": ["Kyrgyzstan", 0],
            "LA": ["Lao People's Democratic Republic", 0],
            "LV": ["Latvia", 0],
            "LB": ["Lebanon", 0],
            "LS": ["Lesotho", 0],
            "LR": ["Liberia", 0],
            "LY": ["Libyan Arab Jamahiriya", 0],
            "LI": ["Liechtenstein", 0],
            "LT": ["Lithuania", 0],
            "LU": ["Luxembourg", 0],
            "MO": ["Macao", 0],
            "MG": ["Madagascar", 0],
            "MW": ["Malawi", 0],
            "MY": ["Malaysia", 0],
            "MV": ["Maldives", 0],
            "ML": ["Mali", 0],
            "MT": ["Malta", 0],
            "MH": ["Marshall Islands", 0],
            "MQ": ["Martinique", 0],
            "MR": ["Mauritania", 0],
            "MU": ["Mauritius", 0],
            "YT": ["Mayotte", 0],
            "MX": ["Mexico", 0],
            "MC": ["Monaco", 0],
            "MN": ["Mongolia", 0],
            "ME": ["Montenegro", 0],
            "MS": ["Montserrat", 0],
            "MA": ["Morocco", 0],
            "MZ": ["Mozambique", 0],
            "MM": ["Myanmar", 0],
            "NA": ["Namibia", 0],
            "NR": ["Nauru", 0],
            "NP": ["Nepal", 0],
            "NL": ["Netherlands", 0],
            "NC": ["New Caledonia", 0],
            "NZ": ["New Zealand", 0],
            "NI": ["Nicaragua", 0],
            "NE": ["Niger", 0],
            "NG": ["Nigeria", 0],
            "NO": ["Norway", 0],
            "OM": ["Oman", 0],
            "PK": ["Pakistan", 0],
            "PW": ["Palau", 0],
            "PA": ["Panama", 0],
            "PG": ["Papua New Guinea", 0],
            "PY": ["Paraguay", 0],
            "PE": ["Peru", 0],
            "PH": ["Philippines", 0],
            "PL": ["Poland", 0],
            "PT": ["Portugal", 0],
            "PR": ["Puerto Rico", 0],
            "QA": ["Qatar", 0],
            "RE": ["Réunion", 0],
            "RO": ["Romania", 0],
            "RU": ["Russian Federation", 0],
            "RW": ["Rwanda", 0],
            "KN": ["Saint Kitts and Nevis", 0],
            "LC": ["Saint Lucia", 0],
            "PM": ["Saint Pierre and Miquelon", 0],
            "VC": ["Saint Vincent and the Grenadines", 0],
            "WS": ["Samoa", 0],
            "SM": ["San Marino", 0],
            "ST": ["Sao Tome and Principe", 0],
            "SA": ["Saudi Arabia", 0],
            "SN": ["Senegal", 0],
            "RS": ["Serbia", 0],
            "SC": ["Seychelles", 0],
            "SL": ["Sierra Leone", 0],
            "SG": ["Singapore", 0],
            "SK": ["Slovakia", 0],
            "SI": ["Slovenia", 0],
            "SB": ["Solomon Islands", 0],
            "SO": ["Somalia", 0],
            "ZA": ["South Africa", 0],
            "GS": ["South Georgia and the South Sandwich Islands", 0],
            "ES": ["Spain", 0],
            "LK": ["Sri Lanka", 0],
            "SD": ["Sudan", 0],
            "SR": ["Suriname", 0],
            "SZ": ["Swaziland", 0],
            "SE": ["Sweden", 0],
            "CH": ["Switzerland", 0],
            "SY": ["Syrian Arab Republic", 0],
            "TJ": ["Tajikistan", 0],
            "TH": ["Thailand", 0],
            "TL": ["Timor-Leste", 0],
            "TG": ["Togo", 0],
            "TO": ["Tonga", 0],
            "TT": ["Trinidad and Tobago", 0],
            "TN": ["Tunisia", 0],
            "TR": ["Turkey", 0],
            "TM": ["Turkmenistan", 0],
            "TC": ["Turks and Caicos Islands", 0],
            "TV": ["Tuvalu", 0],
            "UG": ["Uganda", 0],
            "UA": ["Ukraine", 0],
            "AE": ["United Arab Emirates", 0],
            "GB": ["United Kingdom", 0],
            "US": ["United States", 0],
            "UY": ["Uruguay", 0],
            "UZ": ["Uzbekistan", 0],
            "VU": ["Vanuatu", 0],
            "VN": ["Viet Nam", 0],
            "EH": ["Western Sahara", 0],
            "YE": ["Yemen", 0],
            "ZM": ["Zambia", 0],
            "ZW": ["Zimbabwe", 0],
        }
        for customer in customers:
            country = customer['address']['country']
            customer_metrics[country][1] += 1
        return sorted(
            customer_metrics.items(),
            key=lambda items: items[1][1], reverse=True)

    @staticmethod
    def payment_stats():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payments = stripe.PaymentIntent.list()['data']
        incoming = []
        risks = []

        for payment in payments:
            if payment['status'] == 'succeeded' and payment['currency'] == 'usd':
                incoming.append(payment['amount'])
                risks.append(payment['charges']['data'][0]['outcome']['risk_score'])

        payment_metrics = {
            'balance': float(sum(incoming)) / 100,
            'max_payment': float(max(incoming)) / 100,
            'min_payment': float(min(incoming)) / 100,
            'avg_payment': round(float(sum(incoming) / len(incoming)) / 100, 2) if len(incoming) else 0,
            'avg_risk': round(sum(risks) / len(risks), 2) if len(risks) else 0,
        }
        return payment_metrics

    def __str__(self):
        return self.premium