from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.decorators import api_view, renderer_classes
from core.models import User
from .models import Category, Hosting, Property
from .serializers import CategorySerializer, HostingSerializer, PropertySerializer
from rest_framework import viewsets
from django.core import serializers
from rest_framework.decorators import action

# from .serializers import UserSerializer
from rest_framework import status
import json
import requests


@api_view(['GET'])
def getCategories(request):
    try:
        categories = Category.objects.all().values_list('category_name', flat=True).distinct()
    except Category.DoesNotExist:
        return Response({"error": "No category to show"}, status=status.HTTP_404_NOT_FOUND)
    return Response({'categories': categories, 'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getSubCategories(request, category=None, *arg, **kwargs):
    # category = request.data["category"]
    try:
        sub_categories = Category.objects.all().filter(category_name=category)
    except Category.DoesNotExist:
        return Response({"error": "No subcategory to show"}, status=status.HTTP_404_NOT_FOUND)
    sub_categories = CategorySerializer(sub_categories, many=True)
    return Response({'subcategories': sub_categories.data, 'success': True}, status=status.HTTP_200_OK)


# class CategoryViewSet(viewsets.ModelViewSet):
#     category_serializer = CategorySerializer
#
#     @action(methods=['GET'], detail=True, url_path='categories')
#     def getCategories(self, request):
#         try:
#             categories = Category.objects.all().values_list('categoryName', flat=True).distinct()
#         except Category.DoesNotExist:
#             return Response({"error": "No category to show"}, status=status.HTTP_404_NOT_FOUND)
#         return Response({'categories': categories, 'success': True}, status=status.HTTP_200_OK)

class PropertyHostingView(
    APIView,
    UpdateModelMixin,
    DestroyModelMixin,
):

    def post(self, request):
        try:
            hosting = Hosting.objects.create(title=request.data.get('title'),
                                             description=request.data.get('description'),
                                             max_days_refund=request.data.get('maxDaysRefund'),
                                             hosting_start_date=request.data.get('hostingStartDate'),
                                             published=(True if request.data.get('published') is True else False),
                                             owner_id=request.data.get('ownerId'))
        except Hosting.DoesNotExist:
            Response({"error": "Hosting creation error"}, status=status.HTTP_400_BAD_REQUEST)
        hosting_serializer = HostingSerializer(hosting)
        try:
            # user = User.objects.get(userId=request.data.get('ownerId'))
            property = Property.objects.create(hosting_id=hosting_serializer.data.get("hosting_id"),
                                               per_night_cost=request.data.get('perNightCost'),
                                               entire_private_or_shared=request.data.get('maxDaysRefund'),
                                               highest_guest_no=request.data.get('hostingStartDate'),
                                               beds=request.data.get('beds'),
                                               bedrooms=request.data.get('bedrooms'),
                                               bathrooms=request.data.get('bathrooms'),
                                               private_bathroom_available=request.data.get('privateBathroomAvailable'),
                                               need_host_confirmation=(True if request.data.get('needHostConfirmation') is True else False),
                                               partial_pay_allowed=(True if request.data.get('partialPayAllowed') is True else False),
                                               category_id=request.data.get('categoryId'))
        except Property.DoesNotExist:
            return Response({"error": "Property creation error"}, status=status.HTTP_400_BAD_REQUEST)
        property_serializer = PropertySerializer(property)
        return Response({"hosting": hosting_serializer.data, "property": property_serializer.data}, status=status.HTTP_201_CREATED)

    def put(self, request, hosting_id=None, *args, **kwargs):
        try:
            hosting = Hosting.objects.get(hosting_id=hosting_id)
        except Hosting.DoesNotExist:
            return Response({'errors': 'This hosting does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        hosting.title = request.data.get('title') if request.data.get('title') else hosting.title
        hosting.description = request.data.get('description') if request.data.get('description') else hosting.description
        hosting.max_days_refund = request.data.get('maxDaysRefund') if request.data.get('maxDaysRefund') else hosting.max_days_refund
        hosting.hosting_start_date = request.data.get('hostingStartDate') if request.data.get('hostingStartDate') else hosting.hosting_start_date
        hosting.published = request.data.get('published') if request.data.get('published') else hosting.published

        try:
            hosting.save()
        except Hosting.DoesNotExist:
            return Response({'errors': 'Could not update hosting.'}, status=status.HTTP_400_BAD_REQUEST)
        hosting_serializer = HostingSerializer(hosting)
        try:
            property = Property.objects.get(hosting=hosting_id)
        except Property.DoesNotExist:
            return Response({'errors': 'This property does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        property.per_night_cost = request.data.get('perNightCost') if request.data.get('perNightCost') else property.per_night_cost
        property.entire_private_or_shared = request.data.get('entirePrivateOrShared') if request.data.get('entirePrivateOrShared') else property.entire_private_or_shared
        property.highest_guest_no = request.data.get('highest_guest_no') if request.data.get('highest_guest_no') else property.highest_guest_no
        property.beds = request.data.get('beds') if request.data.get('beds') else property.beds
        property.bedrooms = request.data.get('bedrooms') if request.data.get('bedrooms') else property.bedrooms
        property.bathrooms = request.data.get('bathrooms') if request.data.get('bathrooms') else property.bathrooms
        property.private_bathroom_available = request.data.get('privateBathroomAvailable') if request.data.get('privateBathroomAvailable') else property.private_bathroom_available
        property.need_host_confirmation = request.data.get('needHostConfirmation') if request.data.get('needHostConfirmation') else property.need_host_confirmation
        property.partial_pay_allowed = request.data.get('partialPayAllowed') if request.data.get('partialPayAllowed') else property.partial_pay_allowed

        try:
            property.save()
        except Property.DoesNotExist:
            return Response({'errors': 'Could not update hosting.'}, status=status.HTTP_400_BAD_REQUEST)
        property_serializer = PropertySerializer(property)
        return Response({"hosting": hosting_serializer.data, "property": property_serializer.data}, status=status.HTTP_200_OK)


