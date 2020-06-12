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
from rest_framework.filters import SearchFilter, OrderingFilter


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


# only for listing
class ProfileView(viewsets.ModelViewSet):
    """
    A simple view set for viewing and editing profiles
    """
    queryset = Profile.objects.all()
    serializer_class = StudentSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['mobile', 'user__username', 'contactname', 'contactno', 'invitationcode', 'joindate', 'source']

    def get_permissions(self):
        """
               Instantiates and returns the list of permissions that this view requires.
               """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


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
        pk = -1
        if not user.is_staff:
            if user.profile.isconfirm is False:
                raise serializers.ValidationError({'error': "please verify your email !"})
            else:
                pk = Profile.objects.get(user=user).pk
        else:
            pk = user.pk

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': pk,
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
