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
            'password': {'required': False, 'write_only': True}
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


# machine
class MainPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainPack
        fields = ('packagecode', 'isbytime', 'isbyusage', 'price', 'exfiltermonth', 'exfiltervolume', 'packagedetail')
        extra_kwargs = {
            'packagecode': {
                'validators': [], 'required': True
            },
            'price': {
                'required': False
            }
        }


class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = ('staffcode', 'staffshort', 'staffname', 'staffcontact', 'email')
        extra_kwargs = {
            'staffcode': {
                'validators': [], 'required': True
            },
            'staffname': {
                'validators': [], 'required': False
            },
            'staffcontact': {
                'validators': [], 'required': False
            },
            'email': {
                'validators': [], 'required': False
            },

        }


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ('filtercode', 'filtername', 'filterdetail', 'price')
        extra_kwargs = {
            'filtercode': {
                'validators': [], 'required': True
            },
            'filtername': {
                'required': False
            },
            'filterdetail': {
                'required': False
            },
            'price': {
                'required': False
            },

        }


class MachineSerializer(serializers.ModelSerializer):
    """
    A MachineSerializer serializer to return the student details
    """
    user = UserSerializer(required=True)
    main_pack = MainPackSerializer(required=True)

    class Meta:
        model = Machine
        fields = ('user', 'main_pack', 'machineid', 'installaddress1', 'installaddress2',
                  'mac', 'installdate',
                  'nextservicedate', 'producttype', 'price')
        extra_kwargs = {

            'machineid': {
                'validators': [], 'required': False
            },
            'user': {
                'required': False
            },
            'producttype': {
                'required': False
            },
            'main_pack': {
                'required': False
            },
            'price': {
                'required': False
            },
            'installaddress1': {
                'required': False
            },

        }

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of machine
        :return: returns a successfully created machine record
        """

        user_data = validated_data.pop('user')
        main_pack_data = validated_data.pop('main_pack')
        if User.objects.filter(username=user_data["username"]).exists() and MainPack.objects.filter(
                packagecode=main_pack_data["packagecode"]).exists():
            user = User.objects.get(username=user_data["username"])
            main_pack = MainPack.objects.get(packagecode=main_pack_data["packagecode"])
            machine, created = Machine.objects.update_or_create(user=user, main_pack=main_pack,
                                                                **validated_data)
            return machine
        else:
            raise serializers.ValidationError({'error': "there is something wrong there"})

    # this not tested yet
    def update(self, instance, validated_data):
        machine, created = Machine.objects.update_or_create(
            **validated_data)

        return machine


class CaseSerializer(serializers.ModelSerializer):
    """
    A MachineSerializer serializer to return the student details
    """
    machines = MachineSerializer(required=True, many=True)
    user = UserSerializer(required=True)
    filters = FilterSerializer(required=True, many=True)
    handledby = TechnicianSerializer(required=True)

    class Meta:
        model = Case
        fields = ('machines', 'casetype', 'scheduledate', 'time', 'action',
                  'suggest', 'comment',
                  'iscompleted', 'user', 'filters', 'handledby')

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of machine
        :return: returns a successfully created machine record
        """

        user_data = validated_data.pop('user')
        machines_data = validated_data.pop('machines')
        filters_data = validated_data.pop('filters')
        handledby_data = validated_data.pop('handledby')
        if not User.objects.filter(username=user_data["username"]).exists() and not Technician.objects.filter(
                staffcode=handledby_data["staffcode"]).exists():
            raise serializers.ValidationError({'error': "there user not exist or the technician not exist"})
        else:
            print(str(machines_data))

            for filter_data in filters_data:
                if not Filter.objects.filter(filtercode=filter_data["filtercode"]).exists():
                    raise serializers.ValidationError(
                        {'error': 'there is no filter with this id {}'.format(filter_data["filtercode"])})
            for machine_data in machines_data:
                print(str(machine_data))
                if Machine.objects.filter(machineid=machine_data["machineid"]).exists():
                    pass
                else:
                    raise serializers.ValidationError(
                        {'error': 'there is no machine with this id {}'.format(machine_data["machineid"])})
            user = User.objects.get(username=user_data["username"])
            technician = Technician.objects.get(staffcode=handledby_data["staffcode"])

            case, created = Case.objects.update_or_create(user=user, handledby=technician,
                                                          **validated_data)
            case.save()
            #m = Machine.objects.get(machineid="0010")
            #case.machines.add(m)
            #case.filters.add(Filter.objects.filter(filtercode="0003"))
            for machine_data2 in machines_data:
                m = Machine.objects.get(machineid=machine_data2["machineid"])
                # m = Machine.objects.filter(machineid="0010")
                case.machines.add(m)
            for filter_data2 in filters_data:
                case.filters.add(Filter.objects.get(filtercode=filter_data2["filtercode"]))
            return case

    # this not tested yet
    def update(self, instance, validated_data):
        case, created = Case.objects.update_or_create(
            **validated_data)

        return case
