from rest_framework import serializers
from bags.models import BagDate, BagPort, BagNumber, BagHawbNo, BagCheckHawbNo


class BagDateSerializer(serializers.ModelSerializer):
    bagCount = serializers.IntegerField(read_only=True)
    bagHawbNoCount = serializers.IntegerField(read_only=True)
    bagCheckedHawbNoCount = serializers.IntegerField(read_only=True)
    bagCheckBlCount = serializers.IntegerField(read_only=True)

    class Meta:
        model = BagDate
        fields = ('id', 'bagDate', 'bagCount', 'bagHawbNoCount', 'bagCheckedHawbNoCount', 'bagCheckBlCount')


class BagPortSerializer(serializers.ModelSerializer):
    bagCount = serializers.IntegerField(read_only=True)
    bagHawbNoCount = serializers.IntegerField(read_only=True)
    bagCheckedHawbNoCount = serializers.IntegerField(read_only=True)
    bagCheckBlCount = serializers.IntegerField(read_only=True)
    bagDate = serializers.IntegerField(write_only=True)

    class Meta:
        model = BagPort
        fields = ('id', 'bagDate', 'bagPort',
                  'bagCount', 'bagHawbNoCount', 'bagCheckedHawbNoCount', 'bagCheckBlCount')


class BagPortListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BagPort
        fields = ('id', 'bagPort')
                  
        
class BagNumberSerializer(serializers.ModelSerializer):
    bagHawbNoCount = serializers.IntegerField(read_only=True)
    bagCheckedHawbNoCount = serializers.IntegerField(read_only=True)
    bagPort = serializers.IntegerField(write_only=True)

    class Meta:
        model = BagNumber
        fields = ('id', 'bagNumber', 'bagComment', 'bagPort', 'bagHawbNoCount', 'bagCheckedHawbNoCount')


class BagHawbNoSerializer(serializers.ModelSerializer):
    bagNumber = serializers.IntegerField(write_only=True)

    class Meta:
        model = BagHawbNo
        fields = ('id', 'bagNumber', 'bagHawbNo', 'checked',)


class BagCheckHawbNoSerializer(serializers.ModelSerializer):
    bagPort = serializers.IntegerField(write_only=True)

    class Meta:
        model = BagCheckHawbNo
        fields = ('id', 'bagPort', 'bagHawbNo', 'checked',)

class BagHawbNoListSerializer(serializers.ModelSerializer):
    bagNumber = serializers.IntegerField(source='bagNumber.bagNumber', read_only=True)
    bagPort = serializers.CharField(source='bagNumber.bagPort.bagPort', read_only=True)
    bagComment = serializers.CharField(source='bagNumber.bagComment', read_only=True)
    
    class Meta:
        model = BagHawbNo
        fields = ('id', 'bagHawbNo', 'checked', 'bagNumber', 'bagPort', 'bagComment')
        
        
class BagCheckHawbNoListSerializer(serializers.ModelSerializer):
    bagPort = serializers.CharField(source='bagPort.bagPort', read_only=True)
    bagNumber = serializers.IntegerField(default=0, read_only=True)
    bagComment = serializers.CharField(default='', read_only=True)
    
    class Meta:
        model = BagCheckHawbNo
        fields = ('id', 'bagHawbNo', 'checked', 'bagNumbe', 'bagPort', 'bagComment')
        
        
      