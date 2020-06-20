from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers, status

from OneToOne.serializers import UserSerializer
from .models import *


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
    # user = UserSerializer(required=True)
    # main_pack = MainPackSerializer(required=True)

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
        try:
            machineid = validated_data["machineid"]
            producttype = validated_data["producttype"]
            user = validated_data["user"]
            main_pack = validated_data["main_pack"]
            installaddress1 = validated_data["installaddress1"]
            price = validated_data["price"]
        except KeyError:
            raise serializers.ValidationError({'error': "please make sure to fill all informations"})
        if machineid == "" or price == "" or producttype == "" or user == "" or main_pack =="" or installaddress1 == "":
            raise serializers.ValidationError({'error': "please make sure to fill all informations"})
        if Machine.objects.filter(machineid=validated_data["machineid"]).exists():
            raise serializers.ValidationError({'error': 'there is a machine with the same machine id'})

        machine, created = Machine.objects.update_or_create(**validated_data)
        return machine

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
    # user = UserSerializer(required=True)
    filters = FilterSerializer(required=True, many=True)
    handledby = TechnicianSerializer(required=True)

    class Meta:
        model = Case
        fields = ('machines', 'casetype', 'scheduledate', 'time', 'action',
                  'suggest', 'comment',
                  'iscompleted',  # 'user',
                  'filters', 'handledby')

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of machine
        :return: returns a successfully created machine record
        """

        # user_data = validated_data.pop('user')
        machines_data = validated_data.pop('machines')
        filters_data = validated_data.pop('filters')
        handledby_data = validated_data.pop('handledby')

        for machine_data in machines_data:
            if not Machine.objects.filter(machineid=machine_data["machineid"]).exists():
                raise serializers.ValidationError({'error': "the machine with the {} id is not exist".format(
                    machine_data["machineid"])})

        for filter_data in filters_data:
            if not Filter.objects.filter(filtercode=filter_data["filtercode"]).exists():
                raise serializers.ValidationError(
                    {'error': 'there is no filter with this id {}'.format(filter_data["filtercode"])})

        if not Technician.objects.filter(
                staffcode=handledby_data["staffcode"]).exists():
            raise serializers.ValidationError({'error': "there user not exist or the technician not exist"})
        userTemp = Machine.objects.get(machineid=machines_data[0]["machineid"]).user

        for machine_data3 in machines_data:
            user = Machine.objects.get(machineid=machine_data3["machineid"]).user
            if user != userTemp:
                raise serializers.ValidationError({'error': "all the machines in the same case must have the same "
                                                            "client"})
            else:
                userTemp = user
        technician = Technician.objects.get(staffcode=handledby_data["staffcode"])

        case, created = Case.objects.update_or_create(handledby=technician,
                                                      **validated_data)
        case.save()
        # m = Machine.objects.get(machineid="0010")
        # case.machines.add(m)
        # case.filters.add(Filter.objects.filter(filtercode="0003"))
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
