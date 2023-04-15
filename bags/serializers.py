from rest_framework import serializers
from bags.models import BagDate, BagPort, BagNumber, BagHawbNo


class BagDateSerializer(serializers.ModelSerializer):
    bagCount = serializers.IntegerField(read_only=True)
    bagHawbNoCount = serializers.IntegerField(read_only=True)

    class Meta:
        model = BagDate
        fields = ('id', 'bagDate', 'bagCount', 'bagHawbNoCount')


class BagPortSerializer(serializers.ModelSerializer):
    bagCount = serializers.IntegerField(read_only=True)
    bagHawbNoCount = serializers.IntegerField(read_only=True)
    bagDate = serializers.IntegerField(write_only=True)
    bagPortId = serializers.IntegerField(read_only=True)

    class Meta:
        model = BagPort
        fields = ('bagPortId', 'bagDate', 'bagPort',
                  'bagCount', 'bagHawbNoCount')


class BagNumberSerializer(serializers.ModelSerializer):
    bagHawbNoCount = serializers.IntegerField(read_only=True)
    bagNumberId = serializers.IntegerField(read_only=True)
    bagPort = serializers.IntegerField(write_only=True)

    class Meta:
        model = BagNumber
        fields = ('bagNumberId', 'bagPort', 'bagNumber', 'bagHawbNoCount',)


class BagHawbNoSerializer(serializers.ModelSerializer):
    bagNumber = serializers.IntegerField(write_only=True)

    class Meta:
        model = BagHawbNo
        fields = ('id', 'bagNumber', 'bagHawbNo', 'checked',)

