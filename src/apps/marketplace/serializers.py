from rest_framework import serializers
from django.db import transaction
from .models import Category, Product, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_id', 'name', 'description',
                  'price', 'stock_count', 'created_at']
        read_only_fields = ['created_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Narx 0 dan kichik bo'lishi mumkin emas.")
        return value

    def validate_stock_count(self, value):
        if value < 0:
            raise serializers.ValidationError("Ombor qoldig'i manfiy bo'lishi mumkin emas.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_purchase']
        read_only_fields = ['price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'created_at']
        read_only_fields = ['total_price', 'created_at', 'user']

    def validate(self, data):
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("Buyurtmada kamida 1 ta mahsulot bo'lishi kerak.")

        for item in items:
            product = item['product']
            quantity = item['quantity']
            if product.stock_count < quantity:
                raise serializers.ValidationError(
                    f"'{product.name}' mahsulotidan faqat {product.stock_count} ta mavjud."
                )
        return data

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        total = sum(
            item['product'].price * item['quantity']
            for item in items_data
        )

        order = Order.objects.create(user=user, total_price=total, **validated_data)

        for item in items_data:
            product = item['product']
            quantity = item['quantity']

            # Advanced: stock_count avtomatik kamayadi
            product.stock_count -= quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )

        return order