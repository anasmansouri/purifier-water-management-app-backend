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
from .serializers import StudentSerializer, RegistrationSerializer
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from rest_framework import serializers

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout


class StudentViewSet(viewsets.ModelViewSet):
    """
    A simple view set for viewing and editing profiles
    """
    queryset = Profile.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        """
               Instantiates and returns the list of permissions that this view requires.
               """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

        # i gived all the permission to user now but i will change that later


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def preregistration_view(request):
    serializer = StudentSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        profile = serializer.save()
        data['response'] = 'successfully registered a new user'
        data['username'] = profile.user.username
        token = Token.objects.get(user=profile.user).key
        data["token"] = token
    else:
        data = serializer.errors
    return Response(data)


@api_view(['put'])
@permission_classes([AllowAny])
@transaction.atomic
def registration_view(request):
    try:
        if request.data["user"]["username"] is None or request.data["user"]["email"] is None or \
                request.data["user"]["password"] is None:
            raise serializers.ValidationError(
                {'error': "you have to be sure that you field all the required informations "})
    except KeyError:
        raise serializers.ValidationError("you have to be sure that you field all the required informations ")
    user = None
    try:
        user = User.objects.get(username=request.data["user"]["username"])
    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "there is no user with that user name in the database"})
    serializer = RegistrationSerializer(user.profile, data=request.data)
    data = {}
    if serializer.is_valid():
        print("{}".format("valid 5dmmate"))
        profile = serializer.save()
        data['response'] = 'successfully registered a new user'
        data['username'] = profile.user.username
        data['email'] = profile.user.email
        token = Token.objects.get(user=profile.user).key
        data["token"] = token
        email_verification = EmailVerification.objects.create(username=request.data["user"]["username"],
                                                              code_of_verification=str(random.randint(1000, 9999)))
        send_mail('hello from osmosis', email_verification.code_of_verification,
                  'osmosis.testing.app@gmail.com',
                  [request.data["user"]["email"]],
                  fail_silently=False)
    else:
        print("{}".format("valid ma5damach"))

        data = serializer.errors
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def verify_email(request):
    print(request.data)
    code = ""
    try:
        code = request.data["code"]
    except KeyError:
        raise serializers.ValidationError("please check your email , we send a code there , and put here ")

    if code == EmailVerification.objects.get(username=request.user.username).code_of_verification:
        p = User.objects.get(username=request.user.username).profile
        EmailVerification.objects.get(username=request.user.username).delete()
        p.isconfirm = True
        p.save()
        return Response({"response": "email verified "})
    else:
        return Response({"error": "the code is wrong"})


class StudentRecordView(APIView):
    """
    A class based view for creating and fetching student records
    """

    def get(self, format=None):
        """
        Get all the student records
        :param format: Format of the student records to return to
        :return: Returns a list of student records
        """
        students = Profile.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a student record
        :param format: Format of the student records to return to
        :param request: Request object for creating student
        :return: Returns a student record
        """
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages,
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def logout(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        raise serializers.ValidationError({'error': "there something wrong there !"})
    return Response({"response": "Successfully logged out."},
                    status=status.HTTP_200_OK)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        if user.profile.isconfirm is False:
            raise serializers.ValidationError({'error': "please verify your email !"})

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'is_admin': user.is_staff
        })


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def forgotpassword(request):
    # try:
    invitationcode = ""
    username = ""
    user = ""
    try:
        invitationcode = request.data["invitationcode"]
        username = request.data["username"]
    except KeyError:
        raise serializers.ValidationError("please enter your invitation code and your username")

    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user, invitationcode=invitationcode)
    except  ObjectDoesNotExist:
        raise serializers.ValidationError({'error': "make sure that the username and the invitation code are correct"})

    code = str(random.randint(1000, 999999999))
    send_mail('hello from osmosis', "this is your password" + code + "  now change it when you login in ",
              'osmosis.testing.app@gmail.com',
              [profile.user.email],
              fail_silently=False)
    profile.user.set_password(code)
    profile.user.save()
    return Response({"response": "we sent the new password in your email"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def updada_password(request):
    print(request.data)
    current_password = ""
    new_password = ""
    new_password2 = ""
    try:
        current_password = request.data["current_password"]
        new_password = request.data["new_password"]
        new_password2 = request.data["new_password2"]
    except KeyError:
        raise serializers.ValidationError({'error': "there something wrong there !"})

    if not request.user.check_password(current_password):
        raise serializers.ValidationError({'error': "your password is wrong "})
    else:
        if len(new_password) < 8:
            raise serializers.ValidationError({'error': "the lenght of the new password must be greather than 8"})
        elif new_password != new_password2:
            raise serializers.ValidationError({'error': "password1 and password 2 must match"})
        else:
            request.user.set_password(new_password)
            request.user.save()
            return Response({"response": "the password has been updated successfully"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def updada_contact_name(request):
    print(request.data)
    password = ""
    new_contact_name = ""
    try:
        password = request.data["password"]
        new_contact_name = request.data["new_contact_name"]
    except KeyError:
        raise serializers.ValidationError({'error': "there something wrong there !"})

    if not request.user.check_password(password):
        raise serializers.ValidationError({'error': "your password is wrong "})
    else:
        profile = Profile.objects.get(user=request.user)
        profile.contactname = new_contact_name
        profile.save()
        return Response({"response": "your contact name has been updated successfully"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def updada_email_address(request):
    print(request.data)
    password = ""
    current_email = ""
    new_email = ""
    try:
        password = request.data["password"]
        current_email = request.data["current_email"]
        new_email = request.data["new_email"]
    except KeyError:
        raise serializers.ValidationError({'error': "there something wrong there !"})

    if not request.user.check_password(password):
        raise serializers.ValidationError({'error': "your password is wrong "})

    elif current_email != request.user.email:
        raise serializers.ValidationError({'error': "your email is wrong"})
    else:
        request.user.email = new_email
        email_verification = EmailVerification.objects.create(username=request.user.username,
                                                              code_of_verification=str(random.randint(1000, 9999)))
        send_mail('hello from osmosis', email_verification.code_of_verification,
                  'osmosis.testing.app@gmail.com',
                  [new_email],
                  fail_silently=False)
        p = User.objects.get(username=request.user.username).profile
        request.user.save()
        p.isconfirm = False
        p.save()
        return Response({"response": "your email address has been updated successfully"})


# machine


class MachineViewSet(viewsets.ModelViewSet):
    """
    A simple view set for viewing and editing profiles
    """
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    def get_permissions(self):
        """
               Instantiates and returns the list of permissions that this view requires.
               """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

        # i gived all the permission to user now but i will change that later


class MainPackViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def create(self, request):
        pass

    @permission_classes([IsAuthenticated, ])
    def list(self, request):
        queryset = MainPack.objects.all()
        serializer = MainPackSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = MainPack.objects.all()
        main_pack = get_object_or_404(queryset, pk=pk)
        serializer = MainPackSerializer(main_pack)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request):
        # i catch those exception to be sure that the request contain the price and the exfilltermonth and the exfiltervolume
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


class TechnicianViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def create(self, request):
        pass

    @permission_classes([IsAuthenticated, ])
    def list(self, request):
        queryset = Technician.objects.all()
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
        queryset = Filter.objects.all()
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


class CaseViewSet(viewsets.ModelViewSet):
    """
    A simple view set for viewing and editing profiles
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def get_permissions(self):
        """
               Instantiates and returns the list of permissions that this view requires.
               """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

        # i gived all the permission to user now but i will change that later
