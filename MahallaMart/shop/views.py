from datetime import date

from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import Counter

import requests

import json
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import re
import os



@csrf_exempt
def update_cart_quantity(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))

        cart = request.session.get("cart", [])
        cart.append(product_id)
        request.session["cart"] = cart

    return JsonResponse({"message": "Successfully"}, status=200) 
    return JsonResponse({"error": "Invalid request method"}, status=400) 


def category_detail(request, id):

    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'category_detail.html', {
        'shop': category,
        'products': products,
        'cart_items': cart_view(request)[0],
        'total': cart_view(request)[1],
        'all_products_count': cart_view(request)[2]
    })

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def search_api(request):
    query = request.GET.get('q', '')
    products = []

    if query:
        products_queryset = Product.objects.filter(name__icontains=query)[:10]
        products = [{'id': p.id, 'image_url':p.image_url, 'name': p.name, 'price': p.price} for p in products_queryset]

    return JsonResponse({'products': products})

def search(request):
    products = Product.objects.select_related('discount', 'category', 'shop').all()
    today = date.today()

    for product in products:
        try:
            discount = product.discount
            if discount.valid_from <= today <= discount.valid_until:
                product.discounted_price = discount.discounted_price()
                product.discount_percent = discount.percent
            else:
                product.discounted_price = None
                product.discount_percent = 0
        except:
            product.discounted_price = None
            product.discount_percent = 0

    base_context = {
        'categories': Category.objects.all(),
        'shops': Shop.objects.all(),
        'products': products,
        'offers': Offer.objects.all(),
        'cart_items': cart_view(request)[0],
        'total': cart_view(request)[1],
        'all_products_count': cart_view(request)[2]
    }
    query = request.GET.get('q', '').strip()
    filtered_products = Product.objects.filter(name__icontains=query)
    filtered_shops = Shop.objects.filter(shop_name__icontains=query)

    context = {
        **base_context,
        'query': query,
        'search_products': filtered_products,
        'search_shops': filtered_shops,
    }

    return render(request, 'index.html', context)

def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def complete_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        full_name = escape_markdown(data.get('full_name'))
        phone_number = escape_markdown(data.get('phone_number'))
        address = escape_markdown(data.get('address'))
        promo_code = escape_markdown(data.get('promo_code') or 'Yo‘q')
        payment_method = escape_markdown(data.get('payment_method'))
        finish_total = escape_markdown(data.get('total'))
        products_count = escape_markdown(data.get('all_products_count'))
        raw_products = data.get('cart_items')
        products = escape_markdown(',\n'.join([str(product) for product in raw_products]))
        formatted_products = []
        for idx, product in enumerate(raw_products, 1):
            name = escape_markdown(product.get("name", "Nomaʼlum"))
            quantity = escape_markdown(product.get("quantity", "1"))
            unit = escape_markdown(product.get("unit", "dona"))
            total = escape_markdown(product.get("total", "0 SO'M"))

            line = f"{escape_markdown(str(idx))}\\.{name} \\- {quantity} {unit} \\- {total}"
            formatted_products.append(line)

        products = '\n'.join(formatted_products)

        message = (
            f"📦 *Yangi buyurtma keldi\\!*\n"
            f"👤 *Ism:* {full_name}\n"
            f"📞 *Telefon:* {phone_number}\n"
            f"🛒 *Mahsulotlar soni:* {products_count}\n"
            f"📋 *Mahsulotlar:*\n{products}\n\n"
            f"\n\n💰 *Jami:* {finish_total} SO'M\n"
            f"📍 *Manzil:* {address}\n"
            f"🎁 *Promokod:* {promo_code}\n"
            f"💳 *To'lov:* {payment_method}"
        )


        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'MarkdownV2',
            'reply_markup': json.dumps({
                "inline_keyboard": [
                    [
                        {
                            "text": "✅ Buyurtma yetib keldi",
                            "callback_data": f"delivered:{phone_number}"
                        }
                    ]
                ]
            })
        }
        response = requests.post(telegram_url, data=payload)

        if response.status_code == 200:
            return JsonResponse({'success': True})
        else:
            print(f"Error sending message: {response.status_code}")
            print(f"Response: {response.text}")
            return JsonResponse({'success': False, 'error': response.text})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def checkout(request):
    context = {
        'cart_items': cart_view(request)[0],
        'total': cart_view(request)[1],
        'all_products_count': cart_view(request)[2]
    }   

    return render(request, 'checkout.html', context)

def apply_promocode(request):
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect(request.META.get('HTTP_REFERER', 'index'))

from datetime import date
import os

def cart_view(request):
    cart_list = request.session.get("cart", [])
    cart_counter = Counter(cart_list)
    
    products = Product.objects.filter(id__in=cart_counter.keys())
    cart_items = []
    total = 0
    all_products_count = 0
    
    today = date.today()
    
    for product in products:
        quantity = cart_counter[str(product.id)]
        
        # Check if product has a discount and if it's valid today
        discount = getattr(product, 'discount', None)
        if discount and discount.valid_from <= today <= discount.valid_until:
            price_per_item = discount.discounted_price()
        else:
            price_per_item = product.price
        
        total_price = price_per_item * quantity
        all_products_count += quantity
        total += total_price
        cart_items.append({
            "product": product,
            "quantity": quantity,
            "total_price": total_price,
        })
        
    return [cart_items, total, all_products_count]



@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
            
            cart = request.session.get("cart", [])
            cart.append(product_id)
            request.session["cart"] = cart
            return JsonResponse({"message": "Mahsulot savatga qo'shildi!"})
        except Product.DoesNotExist:
            return JsonResponse({"error": "Mahsulot topilmadi!"}, status=404)


def shop(request, id):

    try:
        shop = Shop.objects.get(id=id)                      
    except Shop.DoesNotExist:
        return render(request, '404.html', status=404)      
    products = Product.objects.filter(shop=shop)
    categories = Category.objects.all()

    context = {
        'shop': shop,
        'products':products,
        'categories': categories,
        'cart_items': cart_view(request)[0],
        'total': cart_view(request)[1],
        'all_products_count': cart_view(request)[2]
    }   

    return render(request, 'shop.html', context)



def index(request):
    products = Product.objects.select_related('discount', 'category', 'shop').all()
    today = date.today()

    for product in products:
        try:
            discount = product.discount
            if discount.valid_from <= today <= discount.valid_until:
                product.discounted_price = discount.discounted_price()
                product.discount_percent = discount.percent
            else:
                product.discounted_price = None
                product.discount_percent = 0
        except:
            product.discounted_price = None
            product.discount_percent = 0

    context = {
        'categories': Category.objects.all(),
        'shops': Shop.objects.all(),
        'products': products,
        'offers': Offer.objects.all(),
        'cart_items': cart_view(request)[0],
        'total': cart_view(request)[1],
        'all_products_count': cart_view(request)[2]
    }
    return render(request, 'index.html', context)


def itest(request):
    return render(request, 'test.html')


def admin_offers(request):
    if request.method == 'POST':
        form = ProductDiscountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_offers') 
    else:
        formProduct = ProductDiscountForm()             

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_offers')
    else:
        form = OfferForm()

    offers = Offer.objects.all()
    offerProducts = ProductDiscount.objects.all()

    return render(request, 'admin/offers.html', {'discounts':offerProducts,'form': form, 'offers': offers, 'formProduct': formProduct, 'products': Product.objects.all()})

def admin_dashboard(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'products': Product.objects.all(),
        'shops': Shop.objects.all(),
    }
    return render(request, 'admin/dashboard.html', context)

def admin_products(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_products')
    else:
        form = ProductForm()

    products = Product.objects.all()
    return render(request, 'admin/products.html', {'form': form, 'products': products})

def admin_shops(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_shops') 
    else:
        form = ShopForm()

    shops = Shop.objects.all()

    return render(request, 'admin/shops.html', {'form': form, 'shops': shops})

def admin_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_categories')
    else:
        form = CategoryForm()

    categories = Category.objects.all()

    return render(request, 'admin/categories.html', {'form': form, 'categories': categories}) 
