from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from rest_framework.filters import SearchFilter, OrderingFilter
from OneToOne.serializers import StudentSerializer


# Create your views here.

class MachineViewSet(viewsets.ModelViewSet):
    """
    A simple view set for viewing and editing profiles
    """
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['machineid', 'producttype', 'mac', 'main_pack']

    def get_permissions(self):
        """
               Instantiates and returns the list of permissions that this view requires.
               """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
        # i gived all the permission to user now but i will change that later


@api_view(['GET'])
@permission_classes([IsAdminUser])
@transaction.atomic
def machine_search(request):
    search = request.GET.get('search', '')
    queryset = list(Machine.objects.filter(machineid__icontains=search))
    queryset.extend(list(Machine.objects.filter(mac__icontains=search)))
    queryset.extend(list(Machine.objects.filter(producttype__icontains=search)))
    queryset.extend(list(Machine.objects.filter(price__icontains=search)))
    queryset.extend(list(Machine.objects.filter(installdate__icontains=search)))
    queryset.extend(list(Machine.objects.filter(nextservicedate__icontains=search)))
    users = User.objects.filter(username__icontains=search)
    if len(users) != 0:
        for user in users:
            if not user.is_staff:
                queryset.extend(list(Machine.objects.filter(user=user.profile)))

    queryset = list(dict.fromkeys(queryset))  # remounve deplicated items
    serializer = MachineSerializer(queryset, many=True)
    test = serializer.data
    for i in test:
        i["user"] = Profile.objects.get(pk=i["user"]).user.username
        print("{}".format(i["user"]))
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
@transaction.atomic
def update_machine_info(request):
    # try:
    machineid = ""
    installaddress1 = ""
    installaddress2 = ""
    nextservicedate = ""
    try:
        machineid = request.data["machineid"]
        installaddress1 = request.data["installaddress1"]
        installaddress2 = request.data["installaddress2"]
        nextservicedate = request.data["nextservicedate"]

    except KeyError:
        raise serializers.ValidationError({'error': "please make sure to fill all informations"})
    if machineid == "" or installaddress1 == "" or nextservicedate == "":
        raise serializers.ValidationError({'error': "please make sure to fill all informations"})
    try:
        machine = Machine.objects.get(machineid=machineid)

    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "make sure that the machine id is correct"})

    machine.installaddress1 = installaddress1
    machine.installaddress2 = installaddress2
    machine.nextservicedate = nextservicedate
    machine.save()
    serializer = MachineSerializer(machine)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
@transaction.atomic
def update_case_info(request):
    case_id = ""
    scheduledate = ""
    time = ""
    action = ""
    suggest = ""
    comment = ""
    iscompleted = ""
    try:
        case_id = request.data["case_id"]
        scheduledate = request.data["scheduledate"]
        time = request.data["time"]
        action = request.data["action"]
        suggest = request.data["suggest"]
        comment = request.data["comment"]
        iscompleted = request.data["iscompleted"]


    except KeyError:
        raise serializers.ValidationError({'error': "please make suuuuure to fill all informations"})
    if case_id == "" or scheduledate == "" or time == "" or iscompleted=="":
        raise serializers.ValidationError({'error': "please make s to fill all informations"})
    try:
        case = Case.objects.get(case_id=case_id)

    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "make sure that the case id is correct"})

    case.scheduledate = scheduledate
    case.time = time
    case.iscompleted = iscompleted
    case.action = action
    case.suggest=suggest
    case.comment = comment
    case.save()
    serializer = CaseSerializer(case)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
@transaction.atomic
def update_main_pack_info(request):
    packagecode = ""
    price = ""
    exfiltermonth = ""
    exfiltervolume = ""
    packagedetail = ""
    try:
        packagecode = request.data["packagecode"]
        price = request.data["price"]
        exfiltermonth = request.data["exfiltermonth"]
        exfiltervolume = request.data["exfiltervolume"]
        packagedetail = request.data["packagedetail"]

    except KeyError:
        raise serializers.ValidationError({'error': "please make sure to fill all informations"})
    if packagecode == "" or price == "" or exfiltermonth == "" or exfiltervolume == "":
        raise serializers.ValidationError({'error': "please make sure to fill all informations"})
    try:
        main_pack = MainPack.objects.get(packagecode=packagecode)

    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "make sure that the packagecode is correct"})

    main_pack.packagedetail = packagedetail
    main_pack.price = price
    main_pack.exfiltermonth = exfiltermonth
    main_pack.exfiltervolume = exfiltervolume
    main_pack.save()
    serializer = MainPackSerializer(main_pack)
    return Response(serializer.data)


class MainPackViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def create(self, request):
        pass

    @permission_classes([IsAuthenticated, ])
    def list(self, request):
        search = request.GET.get('search', '')
        queryset = list(MainPack.objects.filter(packagecode__icontains=search))
        print(queryset)
        queryset.extend(list(MainPack.objects.filter(price__icontains=search)))
        queryset.extend(list(MainPack.objects.filter(exfiltermonth__icontains=search)))
        queryset.extend(list(MainPack.objects.filter(exfiltervolume__icontains=search)))
        queryset.extend(list(MainPack.objects.filter(packagedetail__icontains=search)))
        queryset = list(dict.fromkeys(queryset))
        serializer = MainPackSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = MainPack.objects.all()
        main_pack = get_object_or_404(queryset, pk=pk)
        serializer = MainPackSerializer(main_pack)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request):
        # i catch those exception to be sure that the request contain the price and the exfilltermonth and the
        # exfiltervolume
        try:
            packagecode = request.data["packagecode"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the package code of the main pack"})
        if MainPack.objects.filter(
                packagecode=request.data["packagecode"]).exists():
            raise serializers.ValidationError(
                {'error': "there is already another main pack with the same package code"})
        try:
            price = request.data["price"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the price of the main pack"})
        try:
            exfiltermonth = request.data["exfiltermonth"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the exfiltermonth of the main pack"})
        try:
            exfiltervolume = request.data["exfiltervolume"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the exfiltervolume of the main pack"})
        main_pack = MainPackSerializer.create(MainPackSerializer(), validated_data=request.data)
        return Response(MainPackSerializer(main_pack).data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
@transaction.atomic
def update_technicien_info(request):
    # try:
    staffcode = ""
    staffshort = ""
    staffname = ""
    staffcontact = ""
    email = ""
    try:
        staffcode = request.data["staffcode"]
        staffshort = request.data["staffshort"]
        staffname = request.data["staffname"]
        staffcontact = request.data["staffcontact"]
        email = request.data["email"]

    except KeyError:
        raise serializers.ValidationError({'error': "please make sure to fill all informations"})
    if staffname == "" or staffshort == "" or staffname == "" or staffcontact == "" or email == "":
        raise serializers.ValidationError({'error': "please make sure to fill all informations"})
    try:
        technician = Technician.objects.get(staffcode=staffcode)

    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "make sure that the staffcode is correct"})

    technician.staffcontact = staffcontact
    technician.staffshort = staffshort
    technician.staffname = staffname
    technician.email = email
    technician.save()
    serializer = TechnicianSerializer(technician)
    return Response(serializer.data)


class TechnicianViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def create(self, request):
        pass

    @permission_classes([IsAuthenticated, ])
    def list(self, request):
        search = request.GET.get('search', '')
        queryset = list(Technician.objects.filter(staffcode__icontains=search))
        print(queryset)
        queryset.extend(list(Technician.objects.filter(staffshort__icontains=search)))
        queryset.extend(list(Technician.objects.filter(staffname__icontains=search)))
        queryset.extend(list(Technician.objects.filter(staffcontact__icontains=search)))
        queryset.extend(list(Technician.objects.filter(email__icontains=search)))
        queryset = list(dict.fromkeys(queryset))
        serializer = TechnicianSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Technician.objects.all()
        technician = get_object_or_404(queryset, pk=pk)
        serializer = TechnicianSerializer(technician)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request):
        # i catch those exception to be sure that the request contain the price and the exfilltermonth and the
        # exfiltervolume
        try:
            staffcode = request.data["staffcode"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the staffcode of the technician"})

        try:
            email = request.data["email"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the email of the technician"})
        if Technician.objects.filter(
                staffcode=request.data["staffcode"]).exists():
            raise serializers.ValidationError(
                {'error': "there is already another Tachnician with the same staffcode"})

        if Technician.objects.filter(
                email=request.data["email"]).exists():
            raise serializers.ValidationError(
                {'error': "there is already another Tachnician with the same email"})

        try:
            staffname = request.data["staffname"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the staffname of the technician"})
        try:
            staffcontact = request.data["staffcontact"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the staffcontact of the technician"})
        try:
            email = request.data["email"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the email of the technician"})
        tachnician = TechnicianSerializer.create(TechnicianSerializer(), validated_data=request.data)
        return Response(TechnicianSerializer(tachnician).data)


class FilterViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def create(self, request):
        pass

    @permission_classes([IsAuthenticated, ])
    def list(self, request):
        search = request.GET.get('search', '')
        queryset = list(Filter.objects.filter(filtercode__icontains=search))
        print(queryset)
        queryset.extend(list(Filter.objects.filter(filtername__icontains=search)))
        queryset.extend(list(Filter.objects.filter(filterdetail__icontains=search)))
        queryset.extend(list(Filter.objects.filter(price__icontains=search)))
        queryset = list(dict.fromkeys(queryset))
        serializer = FilterSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Filter.objects.all()
        filter = get_object_or_404(queryset, pk=pk)
        serializer = FilterSerializer(filter)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request):
        # i catch those exception to be sure that the request contain the price and the exfilltermonth and the
        # exfiltervolume
        try:
            staffcode = request.data["filtercode"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the filtercode of the Filter"})

        if Technician.objects.filter(
                staffcode=request.data["filtercode"]).exists():
            raise serializers.ValidationError(
                {'error': "there is already another Filter with the same filter code"})
        try:
            staffname = request.data["filtername"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the filter name"})
        try:
            staffcontact = request.data["price"]
        except  KeyError:
            raise serializers.ValidationError({'error': "please enter the price of the filter"})
        filter = FilterSerializer.create(FilterSerializer(), validated_data=request.data)
        return Response(FilterSerializer(filter).data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
@transaction.atomic
def update_filter_info(request):
    filtercode = ""
    price = ""
    filtername = ""
    filterdetail = ""

    try:
        filtercode = request.data["filtercode"]
        price = request.data["price"]
        filtername = request.data["filtername"]
        filterdetail = request.data["filterdetail"]
    except KeyError:
        raise serializers.ValidationError({'error': "please make suuurre to fill all informations"})
    if filtercode == "" or price == "" or filtername == "":
        raise serializers.ValidationError({'error': "please make s2222ure to fill all informations"})
    try:
        filter = Filter.objects.get(filtercode=filtercode)

    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "make sure that the filter code is correct"})

    filter.filtercode = filtercode
    filter.price = price
    filter.filtername = filtername
    filter.filterdetail = filterdetail
    filter.save()
    serializer = FilterSerializer(filter)
    return Response(serializer.data)


class CaseViewSet(viewsets.ModelViewSet):
    """
    A simple view set for viewing and editing profiles
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['scheduledate', 'casetype', 'machines__machineid']

    def get_permissions(self):
        """
               Instantiates and returns the list of permissions that this view requires.
               """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

        # i gived all the permission to user now but i will change that later


@api_view(['GET'])
@permission_classes([IsAdminUser])
@transaction.atomic
def client_name_and_id(request):
    try:
        clients = User.objects.all()
        li = []
        di = {}
        for client in clients:
            if not client.is_staff:
                di["username"] = client.username
                di["id"] = client.profile.pk
                li.append(di.copy())
                di.clear()
    except:
        raise Response({"error": "there is something wrong"})
    print("lajflsjflskad")
    return Response(li)
