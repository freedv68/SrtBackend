from rest_framework import serializers
from manifest.models import Manifest

class ManifestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('id', 'no', 'hawbNo', 'shipper', 'consignee', 'item', 'ct', 'wt', 
            'value', 'attn', 'phoneNumber', 'pc', 'port', 'note', 
            'specialNote', 'charge1', 'charge2', 'team', 'address', 
            'insertDate', 'modified', 'scanned', 'inspected', 'canceled', 'exclude',
                  'stepped', 'sea', 'together', 'scanTimes', 'deliveryComplete', 'notCarry', 'flight')
    

class ManifestHawbNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('hawbNo',)


class ManifestAssignmentTeamsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Manifest
        fields = ('hawbNo', 'team')
        
class ManifestPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('port',)


class ManifestTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('team',)


class ManifestFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('flight',)


class ManifestInsertDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('insertDate',)
