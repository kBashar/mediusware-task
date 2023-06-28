import json
from django.views import generic

from product.models import (
    Variant,
    Product,
    ProductImage,
    ProductVariant,
    ProductVariantPrice,
)


class CreateProductView(generic.TemplateView):
    template_name = "products/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values("id", "title")
        context["product"] = True
        context["variants"] = list(variants.all())
        return context

    def post(self, request, *args, **kwargs):
        product_data = json.loads(request.body)
        print(product_data)
        title = product_data.get("title", None)
        sku = product_data.get('sku', None)
        description = product_data.get("description", None)
        product_variants = product_data.get("product_variant", None)
        images = product_data.get("product_image", None)
        prices = product_data.get("product_variant_prices", None)

        _product = Product.objects.create(title=title, sku=sku, description=description)

        # iterate over product_variant_price and get or create product_variant
        variant_count = Variant.objects.count()
        if prices:
            for product_price in prices:
                product_variant_tags = product_price.get("title").strip().split("/")[:3]
                product_variants_array = [None, None, None, None]
                for index, product_variant_tag in enumerate(product_variant_tags):
                    variant = Variant.objects.get(
                        id=product_variants[index].get("option")
                    )
                    product_variants_array[product_variants[index].get("option")] = ProductVariant.objects.get_or_create(
                        product=_product,
                        variant=variant,
                        variant_title=product_variant_tag,
                    )[0]
                ProductVariantPrice.objects.create(
                    product_variant_one = product_variants_array[0],
                    product_variant_two = product_variants_array[1],
                    product_variant_three = product_variants_array[2],

                    price = product_price.get('price', 0),
                    stock = product_price.get('stock', 0),

                    product = _product
                )

        if images:
            for image in images:
                ProductImage.objects.create(product=_product, image=image)

        return self.render_to_response(self.get_context_data())


class ListProductView(generic.TemplateView):
    template_name = "products/list.html"

    def get_context_data(self, **kwargs):
        context = super(ListProductView, self).get_context_data(**kwargs)
        # variants = Variant.objects.filter(active=True).values('id', 'title')
        context["products"] = Product.objects.all()
        context["product"] = True
        # context['variants'] = list(variants.all())
        return context


class ProductListView(generic.ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    extra_context = {"product": True}
    paginate_by = 2

    def get_queryset(self):
        product_title = self.request.GET.get("title", None)
        variant = self.request.GET.get("variant", None)
        price_from = self.request.GET.get("price_from", None)
        price_to = self.request.GET.get("price_to", None)
        creation_date = self.request.GET.get("date", None)

        products = Product.objects.all()

        if product_title:
            products = products.filter(title__icontains=product_title)
        if variant:
            products = products.filter(productvariant__id=variant)
        if price_from and price_to:
            products = products.filter(
                product_variants__price__range=(price_from, price_to)
            )
        if creation_date:
            products = products.filter(created_at__date=creation_date)

        return products

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).all()
        context["variants"] = list(variants.all())
        return context