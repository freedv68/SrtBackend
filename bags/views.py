import traceback
from django.http import JsonResponse
from rest_framework import viewsets
from bags.models import BagDate, BagPort, BagNumber, BagHawbNo, BagCheckHawbNo
from bags.serializers import BagDateSerializer, BagPortSerializer, BagNumberSerializer, BagHawbNoSerializer, BagCheckHawbNoSerializer, BagHawbNoListSerializer, BagCheckHawbNoListSerializer
from django.db import transaction
from django.db.models import Count, Q, Prefetch, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from helper.helper import get_or_none
import json
import threading

lock = threading.Lock()

class BagDateViewSet(viewsets.ModelViewSet):
    queryset = BagDate.objects.all()
    serializer_class = BagDateSerializer

    def get_queryset(self):
        return BagDate.objects.prefetch_related(
            Prefetch('bagport', queryset=BagPort.objects.prefetch_related(
                Prefetch(
                    'bagnumber', queryset=BagNumber.objects.prefetch_related('baghawbno')),
                'bagcheckhawbno'
            ))
        ).annotate(Count('bagDate')).order_by('-bagDate').values(
            'id',
            'bagDate',
            bagCount=Count(Concat('bagport__bagPort',
                           'bagport__bagnumber__id'), 
                           filter=Q(bagport__bagnumber__bagNumber__isnull=False), distinct=True),
            bagHawbNoCount=Count('bagport__bagnumber__baghawbno__id', distinct=True),
            bagCheckedHawbNoCount=Count('bagport__bagnumber__baghawbno__id', 
                                      filter=Q(bagport__bagnumber__baghawbno__checked=True), distinct=True),
            bagCheckBlCount=Count('bagport__bagcheckhawbno__id', distinct=True)
        )

    def create(self, request, *args, **kwargs):
        try:
            lock.acquire()

            serializer = BagDateSerializer(data=request.data)
            if serializer.is_valid():
                bag_date = serializer.save()

                port_ = ["YNT", "TAO", "TAO-1", "WEH", "SHA", "CAN", "SGN", "CGK"]
                for port in port_:
                    BagPort.objects.create(bagDate=bag_date, bagPort=port)

                lock.release()
                return JsonResponse(status=201, data={'code': 201, 'message': 'Created'}, safe=False)
            else:
                lock.release()
                return JsonResponse(status=409, data={'code': 409, 'message': 'Already Exist'}, safe=False)
        except Exception as ex:
            if lock.locked():
                lock.release()
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = BagDate.objects.filter(pk=kwargs['pk'])
            queryset.delete()
            return JsonResponse(status=200, data={'code': 200, 'message': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


class BagPortViewSet(viewsets.ModelViewSet):
    queryset = BagPort.objects.all()
    serializer_class = BagPortSerializer

    def get_queryset(self):
        bag_date = self.request.query_params.get('bag_date_id', None)
        if bag_date is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_object = Q(bagDate=BagDate.objects.get(pk=bag_date))
        return BagPort.objects.filter(q_object).prefetch_related(
                Prefetch(
                    'bagnumber', queryset=BagNumber.objects.prefetch_related('baghawbno')), 'bagcheckhawbno'
            ).annotate(Count('bagPort'), filter=Q(bagPort__isnull=False)
            ).values(
            'id', 
            'bagPort', 
            bagCount=Count('bagnumber__id', distinct=True),
            bagHawbNoCount=Count('bagnumber__baghawbno__id', distinct=True),
            bagCheckedHawbNoCount=Count('bagnumber__baghawbno__id', filter=Q(bagnumber__baghawbno__checked=True), distinct=True),
            bagCheckBlCount=Count('bagcheckhawbno__id', distinct=True)
        )

    def create(self, request, *args, **kwargs):
        try:
            lock.acquire()
            
            BagPort.objects.create(bagDate=BagDate.objects.get(
                pk=request.data['bagDateId']), bagPort=request.data['bagPort'])
            
            lock.release()
            return JsonResponse(status=201, data={'code': 201, 'message': 'Created'}, safe=False)
        except Exception as ex:
            if lock.locked():
                lock.release()
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            queryset = BagPort.objects.filter(pk=kwargs['pk'])
            queryset.delete()
            return JsonResponse(status=200, data={'code': 200, 'message': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


class BagPortListViewSet(viewsets.ModelViewSet):
    queryset = BagPort.objects.all()
    serializer_class = BagPortSerializer

    def get_queryset(self):
        bag_date = self.request.query_params.get('bag_date', None)
        if bag_date is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        bagDateObj = get_or_none(BagDate, bagDate=bag_date)
        if bagDateObj is None:
            q_object = Q(bagPort="AAAAA")
            return BagPort.objects.filter(q_object).values(
                'id', 
                'bagPort')
        else:
            q_object = Q(bagDate=bagDateObj)
            return BagPort.objects.filter(q_object).values(
                'id', 
                'bagPort')


class BagNumberViewSet(viewsets.ModelViewSet):
    queryset = BagNumber.objects.all()
    serializer_class = BagNumberSerializer

    def get_queryset(self):
        bag_port = self.request.query_params.get("bag_port_id", None)
        if bag_port is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_objectPort = Q(pk=bag_port)
        q_object = Q(bagPort=BagPort.objects.get(pk=bag_port))

        checkBag = BagPort.objects.filter(q_objectPort).prefetch_related(Prefetch('bagcheckhawbno', queryset=BagCheckHawbNo.objects.only('bagHawbNo', 'checked'))).annotate(
            bagNumber=Value(0),
            bagComment=Value(""),
            bagHawbNoCount=Count('bagcheckhawbno'), 
            bagCheckedHawbNoCount=Count('bagcheckhawbno', filter=Q(bagcheckhawbno__checked=True))).values(
                'id',
                'bagNumber',
                'bagComment',
                'bagHawbNoCount',
                'bagCheckedHawbNoCount'
                )

        bagNumber = BagNumber.objects.filter(q_object).prefetch_related(Prefetch('baghawbno', queryset=BagHawbNo.objects.only('bagHawbNo', 'checked'))).annotate(
            bagHawbNoCount=Count('baghawbno__bagHawbNo'), 
            bagCheckedHawbNoCount=Count('baghawbno', filter=Q(baghawbno__checked=True))).values(
                'id',
                'bagNumber',
                'bagComment',
                'bagHawbNoCount',
                'bagCheckedHawbNoCount'
                )

        return checkBag.union(bagNumber, all=True).order_by('bagNumber')

    def create(self, request, *args, **kwargs):
        try:
            lock.acquire()

            bagNumber, created = BagNumber.objects.get_or_create(bagPort=BagPort.objects.get(
                pk=request.data['bagPortId']), bagNumber=request.data['bagNumber'], defaults={"bagPort": BagPort.objects.get(
                pk=request.data['bagPortId']), "bagNumber": request.data['bagNumber'], "bagComment": request.data['bagComment']})
            if created:
                lock.release()
                return JsonResponse(status=201, data={'code': 201, 'message': 'Created'}, safe=False)
            else:
                lock.release()
                return JsonResponse(status=409, data={'code': 409, 'message': 'Already Exist'}, safe=False)

        except Exception as ex:
            if lock.locked():
                lock.release()
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            lock.acquire()
            with transaction.atomic():
                hawbNos = BagHawbNo.objects.filter(bagNumber=BagNumber.objects.get(pk=kwargs['pk']))
                for check in hawbNos:
                    checkHawbNo = BagCheckHawbNo.objects.filter(Q(bagHawbNo=check.bagHawbNo) & Q(checked=True)).first()
                    if checkHawbNo is not None:
                        setattr(checkHawbNo, 'checked', False)
                        checkHawbNo.save()
                        
                queryset = BagNumber.objects.filter(pk=kwargs['pk'])
                queryset.delete()
                lock.release()
                return JsonResponse(status=200, data={'code': 200, 'message': 'Deleted'}, safe=False)
        except Exception as ex:
            if lock.locked():
                lock.release()
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            bagNumber = get_object_or_404(BagNumber, pk=kwargs['pk'])

            update_ok = True
            
            if bagNumber.bagNumber != data['bagNumber']:
                bagNumberExist = get_or_none(BagNumber, bagPort=bagNumber.bagPort, bagNumber=data['bagNumber'])
                if (bagNumberExist is not None):
                    update_ok = False

            if update_ok:                    
                setattr(bagNumber, 'bagNumber', data['bagNumber'])
                setattr(bagNumber, 'bagComment', data['bagComment'])

                bagNumber.save()
                return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
            else:
                return JsonResponse(status=409, data={'code': 409, 'message': 'Already Exist'}, safe=False)

        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

class BagHawbNoViewSet(viewsets.ModelViewSet):
    queryset = BagHawbNo.objects.all()
    serializer_class = BagHawbNoSerializer

    def get_queryset(self):
        bag_number = self.request.query_params.get("bag_number_id", None)
        if bag_number is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_object = Q(bagNumber=bag_number)

        return BagHawbNo.objects.filter(q_object).all()

    def create(self, request, *args, **kwargs):
        
        try:
            lock.acquire()
            with transaction.atomic():
                code = 201
                message = "Created"
                checked = False
                checkHawbNo = BagCheckHawbNo.objects.filter(bagHawbNo=request.data['bagHawbNo']).first()
                if checkHawbNo is not None:
                    if checkHawbNo.bagPort != BagPort.objects.get(pk=request.data['bagPortId']):
                        message = f'다른 지역({checkHawbNo.bagPort.bagPort})으로 체크된 아이템입니다.'
                        if lock.locked():
                            lock.release()
                        return JsonResponse(status=400, data={'code': 400, 'message': message}, safe=False)

                if request.data['addType'] == 0:
                    bagHawbNos = BagHawbNo.objects.filter(bagHawbNo__contains=request.data['bagHawbNo'])
                    messages = ""
                    for bagHawbNo in bagHawbNos:
                        if messages != "":
                            messages += ","
                        messages += f'{bagHawbNo.id}:{bagHawbNo.bagNumber.bagNumber}:{bagHawbNo.bagNumber.bagPort.id}:{bagHawbNo.bagNumber.bagPort.bagPort}'
                        
                    if messages != "":
                        if lock.locked():
                            lock.release()
                        return JsonResponse(status=409, data={'code': 409, 'message': messages}, safe=False)

                checkHawbNo = BagCheckHawbNo.objects.filter(Q(bagHawbNo=request.data['bagHawbNo']) & Q(checked=False)).first()
                if checkHawbNo is not None:
                    checked = True
                    setattr(checkHawbNo, 'checked', checked)
                    checkHawbNo.save()
                                                                                    
                BagHawbNo.objects.create(bagNumber = BagNumber.objects.get(pk=request.data['bagNumberId']), bagHawbNo = request.data['bagHawbNo'], checked = checked)

                if lock.locked():
                    lock.release()
                return JsonResponse(status=code, data={'code': code, 'message': 'message'}, safe=False)
        except Exception as ex:
            if lock.locked():
                lock.release()
                
            message = traceback.format_exc()
            print(message)
    
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def update(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            checked = False
            checkHawbNo = BagCheckHawbNo.objects.filter(bagHawbNo=request.data['bagHawbNo']).first()
            if checkHawbNo is not None:
                if checkHawbNo.bagPort == BagPort.objects.get(pk=request.data['bagPortId']):
                    setattr(checkHawbNo, 'checked', True)
                    checkHawbNo.save()
                    checked = True
                else:
                    message = f'다른 지역({checkHawbNo.bagPort.bagPort})으로 체크된 아이템입니다.'
                    lock.release()
                    return JsonResponse(status=400, data={'code': 400, 'message': message}, safe=False)

            bagHawbNo = get_object_or_404(BagHawbNo, id=kwargs['pk'])
            setattr(bagHawbNo, "bagNumber", BagNumber.objects.get(
                pk=data['bagNumberId']))
            setattr(bagHawbNo, 'checked', checked)
            bagHawbNo.save()
            return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            bagHawbNo = get_object_or_404(BagHawbNo, id=kwargs['pk'])
            setattr(bagHawbNo, "checked", True)
            bagHawbNo.save()
            return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                bagHawbNo = get_object_or_404(BagHawbNo, id=kwargs['pk'])
                checkHawbNo = BagCheckHawbNo.objects.filter(Q(bagHawbNo=bagHawbNo.bagHawbNo) & Q(checked=True)).first()
                if checkHawbNo is not None:
                    setattr(checkHawbNo, 'checked', False)
                    checkHawbNo.save()

                queryset = BagHawbNo.objects.filter(pk=kwargs['pk'])
                queryset.delete()
            """
            원래는 204를 리턴해야 하나 retrofit2에서 data가 있다는 이유로 에러처리를 해서 200으로 리턴
            """
            return JsonResponse(status=200, data={'code': 200, 'message': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

class BagCheckHawbNoViewSet(viewsets.ModelViewSet):
    queryset = BagCheckHawbNo.objects.all()
    serializer_class = BagCheckHawbNoSerializer

    def get_queryset(self):
        bag_port = self.request.query_params.get("bag_port_id", None)
        if bag_port is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_object = Q(bagPort=bag_port)

        return BagCheckHawbNo.objects.filter(q_object).all()

    def create(self, request, *args, **kwargs):
        try:
            lock.acquire()
            with transaction.atomic():
                code = 201
                message = "Created"
                checked = False
                hawbNo = BagHawbNo.objects.filter(bagHawbNo=request.data['bagHawbNo']).select_related('bagNumber').first()
                if hawbNo is not None:
                    if hawbNo.bagNumber.bagPort != BagPort.objects.get(pk=request.data['bagPortId']):
                        message = f'다른 지역({hawbNo.bagNumber.bagPort.bagPort}:{hawbNo.bagNumber.bagNumber}번 패키지)로 배정된 아이템입니다.'
                        lock.release()
                        return JsonResponse(status=400, data={'code': 400, 'message': message}, safe=False)

                bagCheckHawbNos = BagCheckHawbNo.objects.filter(bagHawbNo__contains=request.data['bagHawbNo'])
                if request.data['addType'] == 0:
                    if bagCheckHawbNos is not None:
                        messages = ""
                        for bagCheckHawbNo in bagCheckHawbNos:
                            if messages != "":
                                messages += ","
                            messages += f'{bagCheckHawbNo.id}:{bagCheckHawbNo.bagPort.id}:{bagCheckHawbNo.bagPort.bagPort}'
                            
                        if messages != "":
                            print(messages)
                            lock.release()
                            return JsonResponse(status=409, data={'code': 409, 'message': messages}, safe=False)
                                                                                    
                hawbNo = BagHawbNo.objects.filter(Q(bagHawbNo=request.data['bagHawbNo'])).first()
                if hawbNo is not None:
                    checked = True
                    setattr(hawbNo, 'checked', checked)
                    hawbNo.save()
                    
                if bagCheckHawbNos is None or bagCheckHawbNos.count() == 0:
                    BagCheckHawbNo.objects.create(bagPort = BagPort.objects.get(pk=request.data['bagPortId']), bagHawbNo = request.data['bagHawbNo'], checked = checked)
                
                lock.release()
                return JsonResponse(status=201, data={'code': code, 'message': message}, safe=False)

        except Exception as ex:
            if lock.locked():
                lock.release()
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def update(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            if isinstance(data, list):
                for m in data:
                    bagCheckHawbNo = get_object_or_404(BagCheckHawbNo, id=m['id'])
                    setattr(bagCheckHawbNo, "bagPort", BagPort.objects.get(
                        pk=m['bagPortId']))
                    bagCheckHawbNo.save()
                return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
            else:
                bagCheckHawbNo = get_object_or_404(BagCheckHawbNo, id=kwargs['pk'])
                setattr(bagCheckHawbNo, "bagPort", BagPort.objects.get(
                    pk=data['bagPortId']))
                bagCheckHawbNo.save()
                return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            bagCheckHawbNo = get_object_or_404(BagCheckHawbNo, id=kwargs['pk'])
            setattr(bagCheckHawbNo, "checked", True)
            bagCheckHawbNo.save()
            return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                if int(kwargs['pk']) < 0:
                    queryset = BagCheckHawbNo.objects.filter(bagPort=BagPort.objects.get(pk=(int(kwargs['pk'])*-1)))
                    for check in queryset:
                        hawbNo = BagHawbNo.objects.filter(Q(bagHawbNo=check.bagHawbNo) & Q(checked=True)).first() 
                        if hawbNo is not None:
                            setattr(hawbNo, 'checked', False)
                            hawbNo.save() 
                    queryset.delete()
                else:
                    bagCheckHawbNo = get_object_or_404(BagCheckHawbNo, id=kwargs['pk'])

                    hawbNo = BagHawbNo.objects.filter(Q(bagHawbNo=bagCheckHawbNo.bagHawbNo) & Q(checked=True)).first() 
                    if hawbNo is not None:
                        setattr(hawbNo, 'checked', False)
                        hawbNo.save()            

                    queryset = BagCheckHawbNo.objects.filter(pk=kwargs['pk'])
                    queryset.delete()
            """
            원래는 204를 리턴해야 하나 retrofit2에서 data가 있다는 이유로 에러처리를 해서 200으로 리턴
            """
            return JsonResponse(status=200, data={'code': 200, 'message': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

class BagHawbNoListViewSet(viewsets.ModelViewSet):
    queryset = BagHawbNo.objects.all()
    serializer_class = BagHawbNoListSerializer
    
    def get_queryset(self):
        bag_date = self.request.query_params.get("bag_date", None)
        bag_port = self.request.query_params.get("bag_port", None)
        bag_number = self.request.query_params.get("bag_number", None)
        checked = self.request.query_params.get("checked", None)
        if bag_port is None or bag_date is None or bag_number is None or checked is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_object = Q(bagNumber__bagPort__bagDate__bagDate__exact=bag_date)
        if (bag_port != '전체'):
            q_object &= Q(bagNumber__bagPort__bagPort__exact=bag_port)
        if (bag_number is not None and bag_number != '전체'):
            q_object &= Q(bagNumber__bagNumber__exact=bag_number)
        if (checked is not None and checked != '전체'):
            q_object &= Q(checked=True if checked == '체크' else False)
            
        return BagHawbNo.objects.select_related('bagNumber').filter(q_object)
    
    
class BagCheckHawbNoListViewSet(viewsets.ModelViewSet):
    queryset = BagCheckHawbNo.objects.all()
    serializer_class = BagCheckHawbNoListSerializer
    
    def list(self, request):
        bag_date = self.request.query_params.get("bag_date", None)
        bag_port = self.request.query_params.get("bag_port", None)
        checked = self.request.query_params.get("checked", None)
        if bag_port is None or bag_date is None or checked is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_object = Q(bagPort__bagDate__bagDate__exact=bag_date)
        if (bag_port != '전체'):
            q_object &= Q(bagPort__bagPort__exact=bag_port)
        if (checked is not None and checked != '전체'):
            q_object &= Q(checked=True if checked == '체크' else False)
            
        queryset = BagCheckHawbNo.objects.select_related('bagPort').filter(q_object)
        
        bagsResponse = []
        for checkHawbNo in queryset:
            hawbNo = get_or_none(BagHawbNo, bagHawbNo=checkHawbNo.bagHawbNo)
            bagNumber = 0
            bagComment = ''
            if hawbNo is not None:
                bagNumber = hawbNo.bagNumber.bagNumber
                bagNumberObj = get_or_none(BagNumber, id=hawbNo.bagNumber.id)
                if bagNumberObj is not None:
                    bagComment = bagNumberObj.bagComment
                
            bagsResponse.append({
                "id": checkHawbNo.id,
                "bagHawbNo": checkHawbNo.bagHawbNo,
                "checked": checkHawbNo.checked,
                "bagNumber": bagNumber,
                "bagPort": checkHawbNo.bagPort.bagPort,
                "bagComment": bagComment               
            })

        return JsonResponse(status=200, data=bagsResponse, safe=False)
