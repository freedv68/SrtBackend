from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from bags.models import BagDate, BagPort, BagNumber, BagHawbNo
from bags.serializers import BagDateSerializer, BagPortSerializer, BagNumberSerializer, BagHawbNoSerializer
from django.db.models import Count, Q, Prefetch, F
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
import json


class BagDateViewSet(viewsets.ModelViewSet):
    queryset = BagDate.objects.all()
    serializer_class = BagDateSerializer

    def get_queryset(self):
        return BagDate.objects.prefetch_related(
            Prefetch('bagport', queryset=BagPort.objects.prefetch_related(
                Prefetch(
                    'bagnumber', queryset=BagNumber.objects.prefetch_related('baghawbno'))
            ))
        ).annotate(Count('bagDate')).order_by('-bagDate').values(
            'id',
            'bagDate',
            bagCount=Count(Concat('bagport__bagPort',
                           'bagport__bagnumber__bagNumber'), distinct=True),
            bagHawbNoCount=Count('bagport__bagnumber__baghawbno__bagHawbNo')
        )

    def create(self, request, *args, **kwargs):
        serializer = BagDateSerializer(data=request.data)
        if serializer.is_valid():
            bag_date = serializer.save()

            port_ = ["YNT", "TAO", "WEH", "SHA", "CAN", "SGN"]
            for port in port_:
                BagPort.objects.create(bagDate=bag_date, bagPort=port)

            return JsonResponse(status=201, data={'status': 'Created'}, safe=False)

        return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = BagDate.objects.filter(pk=kwargs['pk'])
            queryset.delete()
            return JsonResponse(status=204, data={'status': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)


class BagPortViewSet(viewsets.ModelViewSet):
    queryset = BagPort.objects.all()
    serializer_class = BagPortSerializer

    def get_queryset(self):
        bag_date = self.request.query_params.get('bag_date_id', None)
        if bag_date is None:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

        q_object = Q(id=bag_date)
        return BagDate.objects.filter(q_object).prefetch_related(
            Prefetch('bagport', queryset=BagPort.objects.prefetch_related(
                Prefetch(
                    'bagnumber', queryset=BagNumber.objects.prefetch_related('baghawbno'))
            ))
        ).annotate(Count('bagport__bagPort')).values(
            bagPortId=F('bagport__id'),
            bagPort=F('bagport__bagPort'),
            bagCount=Count('bagport__bagnumber__bagNumber', distinct=True),
            bagHawbNoCount=Count('bagport__bagnumber__baghawbno__bagHawbNo')
        )

    def create(self, request, *args, **kwargs):
        try:
            BagPort.objects.create(bagDate=BagDate.objects.get(
                pk=request.data['bagDate']), bagPort=request.data['bagPort'])
            return JsonResponse(status=201, data={'status': 'Created'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = BagPort.objects.filter(pk=kwargs['pk'])
            queryset.delete()
            return JsonResponse(status=204, data={'status': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)


class BagNumberViewSet(viewsets.ModelViewSet):
    queryset = BagNumber.objects.all()
    serializer_class = BagNumberSerializer

    def get_queryset(self):
        bag_port = self.request.query_params.get("bag_port_id", None)
        if bag_port is None:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

        q_object = Q(id=bag_port)

        return BagPort.objects.filter(q_object).prefetch_related(
                Prefetch(
                    'bagnumber', queryset=BagNumber.objects.prefetch_related('baghawbno'))
            ).annotate(Count('bagnumber__bagNumber')).values(
            bagNumberId=F('bagnumber__id'),
            bagNumber=F('bagnumber__bagNumber'),
            bagHawbNoCount=Count('bagnumber__baghawbno__bagHawbNo')
        )

    def create(self, request, *args, **kwargs):
        try:
            BagNumber.objects.create(bagPort=BagPort.objects.get(
                pk=request.data['bagPort']), bagNumber=request.data['bagNumber'])
            return JsonResponse(status=201, data={'status': 'Created'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = BagNumber.objects.filter(pk=kwargs['pk'])
            queryset.delete()
            return JsonResponse(status=204, data={'status': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)


class BagHawbNoViewSet(viewsets.ModelViewSet):
    queryset = BagHawbNo.objects.all()
    serializer_class = BagHawbNoSerializer

    def get_queryset(self):
        bag_number = self.request.query_params.get("bag_number_id", None)
        if bag_number is None:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

        q_object = Q(bagNumber=bag_number)

        return BagHawbNo.objects.filter(q_object).all()

    def create(self, request, *args, **kwargs):
        try:
            BagHawbNo.objects.create(bagNumber=BagNumber.objects.get(
                pk=request.data['bagNumber']), bagHawbNo=request.data['bagHawbNo'], checked=False)
            return JsonResponse(status=201, data={'status': 'Created'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

    def update(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            bagHawbNo = get_object_or_404(BagHawbNo, id=kwargs['pk'])
            setattr(bagHawbNo, "bagNumber", BagNumber.objects.get(
                pk=data['bagNumber']))
            bagHawbNo.save()
            return JsonResponse(status=200, data={'status': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            bagHawbNo = get_object_or_404(BagHawbNo, id=kwargs['pk'])
            setattr(bagHawbNo, "checked", True)
            bagHawbNo.save()
            return JsonResponse(status=200, data={'status': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = BagHawbNo.objects.filter(pk=kwargs['pk'])
            queryset.delete()
            return JsonResponse(status=204, data={'status': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'status': 'Bad Request'}, safe=False)