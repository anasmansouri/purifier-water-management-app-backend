from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers, status
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator()],
            },
            'password': {'required': False,'write_only': True}
        }


class StudentSerializer(serializers.ModelSerializer):
    """
    A student serializer to return the student details
    """
    user = UserSerializer(required=True)

    class Meta:
        model = Profile
        fields = ('user', 'contactname', 'billingaddress1',
                  'installaddress1', 'billingaddress2',
                  'installaddress2', 'contactno', 'mobile', 'invitationcode', 'source',
                  'comment')

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of student
        :return: returns a successfully created student record
        """

        user_data = validated_data.pop('user')
        if User.objects.filter(username=user_data["username"]).exists():
            raise serializers.ValidationError({"error": {"username": "the username must be unique"}})

        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user.set_password("123456789")

        profile, created = Profile.objects.update_or_create(user=user,
                                                            **validated_data)
        return profile

    # this not tested yet
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.get_or_create(username=user_data["username"])[0]
        instance.user = user
        profile, created = Profile.objects.update_or_create(user=user,
                                                            **validated_data)

        return profile


# registration serializer
class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    user = UserSerializer(required=True)

    class Meta:
        model = Profile
        fields = ('user', 'password2',
                  'invitationcode',)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        ## validate the password
        if user_data["password"] != validated_data["password2"]:
            raise serializers.ValidationError({'error': "password1 and password 2 must match"})
        elif len(user_data["password"]) < 8:
            raise serializers.ValidationError({'error': "the password lenght must be greather than 8 characters"})
        if instance.invitationcode != validated_data["invitationcode"]:
            raise serializers.ValidationError({'error': "please make sure that you put your invitation code correctly"})
        instance.user.email = user_data["email"]
        instance.user.set_password(user_data["password"])
        print("we passed here ")
        instance.user.save()
        # user = UserSerializer.update(UserSerializer(), validated_data=user_data)
        # instance.user.set_password(validated_data["password"])
        instance.save()
        return instance
