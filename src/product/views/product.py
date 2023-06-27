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
