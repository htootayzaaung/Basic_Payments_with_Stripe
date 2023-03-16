import os
from flask import Flask, render_template, abort, redirect, request
import stripe

app = Flask(__name__)
stripe.api_key = os.environ['STRIPE_SECRET_KEY']

products = {
    'megatutorial': {
        'name': 'The Flask Mega-Tutorial',
        'price': 100, #price is an integer in cents
    },
    'support': {
        'name': 'Python 1:1 support',
        'price': 100, #price is an integer in cents
        'per': 'hour',
    },
}

@app.route('/all_products')
def index():
    return render_template('index.html', products=products)


"""

When the /order/<product_id> endpoint is invoked, the Flask application 
has received a request from the user to buy the given product. At this 
point Stripe needs to be informed of what the user wants to buy, and then 
control needs to be transferred so that the ordering process is carried 
out on Stripe's servers.

"""

@app.route('/order/<product_id>', methods=['POST'])
def order(product_id):
    if product_id not in products:
        abort(404)  #error 404 is returned if the "product_id" is not a key in the "products" dictionary.

    """
        Stripe checkout session is created by invoking "stripe.checkout.Session.create()" function 
    """
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price_data': {
                    'product_data': {
                        'name': products[product_id]['name'],
                    },
                    'unit_amount': products[product_id]['price'],
                    'currency': 'gbp',
                },
                'quantity': 1,  #default quantity is 1
                'adjustable_quantity': products[product_id].get(
                    'adjustable_quantity', {'enabled': True}),  #'enabled' toggles "True" or "False"
            },
        ],
        payment_method_types=['card'],
        mode='payment',
        success_url=request.host_url + 'order/success',
        cancel_url=request.host_url + 'order/cancel',
    )
    return redirect(checkout_session.url)

#Order success and cancellation
@app.route('/order/success')
def success():
    return render_template('success.html')


@app.route('/order/cancel')
def cancel():
    return render_template('cancel.html')

#Reference link: https://blog.miguelgrinberg.com/post/accept-credit-card-payments-in-flask-with-stripe-checkout