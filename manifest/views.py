import json
from django.http import JsonResponse
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404
from manifest.models import Manifest
from manifest.serializers import ManifestFlightSerializer, ManifestSerializer, ManifestHawbNoSerializer, ManifestPortSerializer, ManifestTeamSerializer, ManifestInsertDateSerializer, ManifestAssignmentTeamsSerializer
from datetime import datetime, timedelta
import threading


lock = threading.Lock()  # threading에서 Lock 함수 가져오기

class ManifestViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        q_objects = []
        
        hawb_no = self.request.query_params.get("hawb_no", None)
        if hawb_no is not None:
            return Manifest.objects.filter(hawbNo=hawb_no).values()

        from_insert_date = self.request.query_params.get("s_date", None)
        to_insert_date = self.request.query_params.get("e_date", None)
        keyword = self.request.query_params.get("keyword", None)

        page_s = self.request.query_params.get("page", None)
        page = int(self.request.query_params.get("page", 1))
        page_size_s = self.request.query_params.get("page_size", None)
        page_size = int(self.request.query_params.get("page_size", 15))

        if from_insert_date is None or to_insert_date is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_objects = Q(insertDate__gte=from_insert_date) & Q(
            insertDate__lte=to_insert_date)

        if keyword is not None:
            """
            date_time_obj = datetime.strptime(
                from_insert_date, '%Y-%m-%d') - timedelta(7)
            from_date = date_time_obj.strftime('%Y-%m-%d')
            q_objects = Q(insertDate__gte=from_date) & Q(
                insertDate__lte=to_insert_date)
            """
            q_objects = Q(hawbNo__icontains=keyword) | Q(
                shipper__icontains=keyword) | Q(consignee__icontains=keyword) | Q(attn__icontains=keyword) | Q(phoneNumber__icontains=keyword)
        else:
            partner = self.request.query_params.get("partner", None)
            port = self.request.query_params.get("port", None)
            team = self.request.query_params.get("team", None)
            scanned = self.request.query_params.get("scanned", None)
            inspected = self.request.query_params.get("inspected", "false")
            canceled = self.request.query_params.get("canceled", "false")
            exclude = self.request.query_params.get("exclude", "false")
            stepped = self.request.query_params.get("stepped", "false")
            sea = self.request.query_params.get("sea", "false")
            together = self.request.query_params.get("together", "false")
            deliveryComplete = self.request.query_params.get("delivery_complete", None)
            notCarry = self.request.query_params.get("not_carry", None)
            flight = self.request.query_params.get("flight", None)

            if partner is not None and partner != '전체':
                if partner == '실크로드':
                    q_objects &= Q(hawbNo__istartswith="SRT")
                else:
                    q_objects &= Q(hawbNo__istartswith="JGE")

            if port is not None and len(port) > 0 and port != '전체':
                ports = port.split(',')
                if (len(ports) == 1):
                    q_objects &= Q(port__exact=port)
                else:
                    q_objects &= Q(port__in=ports)

            if team is not None and len(team) > 0 and team != '전체':
                teams = team.split(',')
                if (len(teams) == 1):
                    q_objects &= Q(team__exact=team)
                else:
                    q_objects &= Q(team__in=teams)

            if flight is not None and len(flight) > 0 and flight != '전체':
                flights = flight.split(',')
                if (len(flights) == 1):
                    q_objects &= Q(flight__exact=flight)
                else:
                    q_objects &= Q(flight__in=flights)
                    
            if scanned is not None and scanned != '전체':
                if scanned == '스캔':
                    q_objects &= Q(scanned=True)
                else:
                    q_objects &= Q(scanned=False)

            if deliveryComplete is not None and deliveryComplete != '전체':
                if deliveryComplete == '배송':
                    q_objects &= Q(deliveryComplete=True)
                else:
                    q_objects &= Q(deliveryComplete=False)
                    
            q_objects_ex = []
            if inspected == "true":
                q_objects_ex = Q(inspected=True)
            if canceled == "true":
                if q_objects_ex == []:
                    q_objects_ex = Q(canceled=True)
                else:
                    q_objects_ex |= Q(canceled=True)
            if exclude == "true":
                if q_objects_ex == []:
                    q_objects_ex = Q(exclude=True)
                else:
                    q_objects_ex |= Q(exclude=True)
            if stepped == "true":
                if q_objects_ex == []:
                    q_objects_ex = Q(stepped=True)
                else:
                    q_objects_ex |= Q(stepped=True)
            if sea == "true":
                if q_objects_ex == []:
                    q_objects_ex = Q(sea=True)
                else:
                    q_objects_ex |= Q(sea=True)
            if together == "true":
                if q_objects_ex == []:
                    q_objects_ex = Q(together=True)
                else:
                    q_objects_ex |= Q(together=True)
            if notCarry == "true":
                if q_objects_ex == []:
                    q_objects_ex = Q(notCarry=True)
                else:
                    q_objects_ex |= Q(notCarry=True)

            if q_objects_ex != []:
                q_objects &= q_objects_ex

        queryset = Manifest.objects.filter(
            q_objects).order_by('-insertDate', 'id')
        itemCount = queryset.count()

        if itemCount == 0 or page_s is None or page_size_s is None:
            return JsonResponse(status=200, data={'itemCount': itemCount, 'manifests': list(queryset.values())}, safe=False)
        else:
            if page_size * (page - 1) >= itemCount:
                page = (itemCount // page_size)
                if (itemCount % page_size):
                    page += 1

            limit = int(page_size) * int(page)
            offset = int(limit) - int(page_size)

            return JsonResponse(status=200, data={'itemCount': itemCount, 'manifests': list(queryset[offset:limit].values())}, safe=False)


    def retrieve(self, request, pk=None):
        queryset = Manifest.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = ManifestSerializer(user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            try:
                mani_objs=[]
                for m in request.data:
                    mani_obj = Manifest(id=m['id'], no=m['no'], hawbNo=m['hawbNo'], shipper=m['shipper'], 
                                        consignee=m['consignee'], item=m['item'], ct=m['ct'], wt=m['wt'], 
                                        value=m['value'], attn=m['attn'], phoneNumber=m['phoneNumber'], 
                                        pc=m['pc'], port=m['port'], note=m['note'], specialNote=m['specialNote'], 
                                        charge1=m['charge1'], charge2=m['charge2'], team=m['team'], 
                                        address=m['address'], insertDate=m['insertDate'], modified=m['modified'], 
                                        scanned=m['scanned'], inspected=m['inspected'], canceled=m['canceled'], exclude=m['exclude'],
                                        stepped=m['stepped'], sea=m['sea'], together=m['together'], scanTimes=m['scanTimes'], 
                                        deliveryComplete=m['deliveryComplete'], notCarry=m['notCarry'], flight=m['flight'], scanDate=m['scanDate'])

                    mani_objs.append(mani_obj)

                Manifest.objects.bulk_create(mani_objs)

                return JsonResponse(status=201, data={'code': 201, 'message': 'Created'}, safe=False)
                
            except Exception as ex:
                return JsonResponse(status=400, data={'code': 400, 'message': f'Bad Request - {ex}'}, safe=False)

        else:
            try:
                lock.acquire()

                data = json.loads(request.body)
                # manifest, created = Manifest.objects.update_or_create(**data)
                manifest, created = Manifest.objects.get_or_create(
                    hawbNo=data['hawbNo'], defaults=data)

                if created:
                    lock.release()
                    return JsonResponse(status=201, data={'code': 201, 'message': 'Created'}, safe=False)
                else:
                    setattr(manifest, 'no', data['no'])
                    setattr(manifest, 'shipper', data['shipper'])
                    setattr(manifest, 'consignee', data['consignee'])
                    setattr(manifest, 'item', data['item'])
                    setattr(manifest, 'ct', data['ct'])
                    setattr(manifest, 'wt', data['wt'])
                    setattr(manifest, 'value', data['value'])
                    setattr(manifest, 'attn', data['attn'])
                    setattr(manifest, 'phoneNumber', data['phoneNumber'])
                    setattr(manifest, 'pc', data['pc'])
                    setattr(manifest, 'port', data['port'])
                    setattr(manifest, 'note', data['note'])
                    setattr(manifest, 'specialNote', data['specialNote'])
                    setattr(manifest, 'charge1', data['charge1'])
                    setattr(manifest, 'charge2', data['charge2'])
                    setattr(manifest, 'team', data['team'])
                    setattr(manifest, 'address', data['address'])
                    setattr(manifest, 'flight', data['flight'])

                    manifest.save()
                    lock.release()
                    return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)

            except Exception as ex:
                if lock.locked():
                    lock.release()
                return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


    def update(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if isinstance(data, list):
            try:
                mani_objs = []
                for m in data:
                    mani_obj = Manifest(id=m['id'], no=m['no'], hawbNo=m['hawbNo'], shipper=m['shipper'],
                                        consignee=m['consignee'], item=m['item'], ct=m['ct'], wt=m['wt'],
                                        value=m['value'], attn=m['attn'], phoneNumber=m['phoneNumber'],
                                        pc=m['pc'], port=m['port'], note=m['note'], specialNote=m['specialNote'],
                                        charge1=m['charge1'], charge2=m['charge2'], team=m['team'],
                                        address=m['address'], insertDate=m['insertDate'], modified=m['modified'],
                                        scanned=m['scanned'], inspected=m['inspected'], canceled=m['canceled'], exclude=m['exclude'],
                                        stepped=m['stepped'], sea=m['sea'], together=m['together'], scanTimes=m['scanTimes'], 
                                        deliveryComplete=m['deliveryComplete'], notCarry=m['notCarry'], flight=m['flight'], scanDate=m['scanDate'])

                    mani_objs.append(mani_obj)

                Manifest.objects.bulk_update(
                    mani_objs, fields=['no', 'shipper', 'consignee', 'item', 'ct', 'wt', 'value', 'attn', 'phoneNumber',
                                        'pc', 'port', 'note', 'specialNote', 'charge1', 'charge2', 'team', 'address', 'insertDate', 'flight'])
                return JsonResponse(status=201, data={'code': 201, 'message': 'Updated'}, safe=False)

            except Exception as ex:
                return JsonResponse(status=400, data={'code': 400, 'message': f'Bad Request - {ex}'}, safe=False)

        else:
            try:
                data = json.loads(request.body)
                
                if kwargs['pk'] != data['hawbNo']:
                    mani = Manifest.objects.filter(hawbNo=data['hawbNo']).first()
                    if (mani):
                        return JsonResponse(status=409, data={'code': 409, 'message': '이미 있는 비엘번호입니다.'}, safe=False)
                    
                lock.acquire()
                manifest = get_object_or_404(Manifest, hawbNo=kwargs['pk'])
                setattr(manifest, 'no', data['no'])
                setattr(manifest, 'hawbNo', data['hawbNo'])
                setattr(manifest, 'shipper', data['shipper'])
                setattr(manifest, 'consignee', data['consignee'])
                setattr(manifest, 'item', data['item'])
                setattr(manifest, 'ct', data['ct'])
                setattr(manifest, 'wt', data['wt'])
                setattr(manifest, 'value', data['value'])
                setattr(manifest, 'attn', data['attn'])
                setattr(manifest, 'phoneNumber', data['phoneNumber'])
                setattr(manifest, 'pc', data['pc'])
                setattr(manifest, 'port', data['port'])
                setattr(manifest, 'note', data['note'])
                setattr(manifest, 'specialNote', data['specialNote'])
                setattr(manifest, 'charge1', data['charge1'])
                setattr(manifest, 'charge2', data['charge2'])
                setattr(manifest, 'team', data['team'])
                setattr(manifest, 'address', data['address'])
                setattr(manifest, 'flight', data['flight'])
                """
                setattr(manifest, 'scanned', data['scanned'])
                setattr(manifest, 'inspcected', data['inspected'])
                setattr(manifest, 'canceled', data['canceled'])
                setattr(manifest, 'exclude', data['exclude'])
                setattr(manifest, 'stepped', data['stepped'])
                setattr(manifest, 'sea', data['sea'])
                setattr(manifest, 'together', data['together'])
                setattr(manifest, 'scanTimes', data['scanTimes'])
                """
                manifest.save()
                
                if kwargs['pk'] != data['hawbNo']: #비엘 번호가 변경되는 경우는 새로 추가가 되기때문에 기존 자료를 삭제
                    queryset = Manifest.objects.filter(hawbNo=kwargs['pk'])
                    queryset.delete()
                    
                lock.release()
                return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)

            except Exception as ex:
                if lock.locked():
                    lock.release()
                return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            manifest = get_object_or_404(Manifest, hawbNo=kwargs['pk'])

            setattr(manifest, data['field'], data['value'])
            print('update1')
            if (data['field'] == 'scanned'):
                # setattr(manifest, 'scanTimes', int(manifest.ct))
                
                formatted_date = ''
                if manifest.scanned:
                    now = datetime.now()
                    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")            
                    
                print(formatted_date)    
                setattr(manifest, 'scanDate', formatted_date)   
                
            if 'field1' in data:
                field1 = data['field1']
                value1 = data['value1']
                setattr(manifest, field1, value1)
                if (data['field1'] == 'scanned'):
                    # setattr(manifest, 'scanTimes', int(manifest.ct))
                    
                    formatted_date = ''
                    if int(manifest.scanTimes) > 0:
                        now = datetime.now()
                        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")            
                        
                    print(formatted_date)    
                    setattr(manifest, 'scanDate', formatted_date) 
                
            manifest.save()
            return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


    def destroy(self, request, *args, **kwargs):
        hawbNos = kwargs['pk'].split(',')
        queryset = Manifest.objects.all()

        if len(hawbNos) > 1:
            if hawbNos[0] == 'date' and len(hawbNos) == 3:
                queryset = Manifest.objects.filter(Q(
                    insertDate__gte=hawbNos[1]) & Q(insertDate__lte=hawbNos[2]))
            else:
                queryset = Manifest.objects.filter(hawbNo__in=hawbNos)
        else:
            queryset = Manifest.objects.filter(hawbNo=hawbNos[0])

        try:
            queryset.delete()
            return JsonResponse(status=204, data={'code': 204, 'message': 'Deleted'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)



class ManifestAssignmentTeamsViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestAssignmentTeamsSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
        
    def create(self, request, *args, **kwargs):
        #try:
            hawb_list = []
            for h in request.data:
                q_object = Q(shipper=h["shipper"])
                q_object &= Q(consignee=h["consignee"])

                mani = Manifest.objects.filter(q_object).values('team').annotate(teamCount=Count('team')).order_by('-teamCount').first()
                if mani is not None:
                    hawb_list.append({'hawbNo': h["hawbNo"], 'team': mani['team']})
                else:
                    hawb_list.append({'hawbNo': h["hawbNo"], 'team': ''})
                    
            return Response(status=200, data=hawb_list)
        
        #except Exception as ex:
        #    return JsonResponse(status=400, data={'code': 400, 'message': f'Bad Request - {ex}'}, safe=False)
        
class ManifestHawbNoViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestHawbNoSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        try:
            hawb_list = []
            for h in request.data:
                hawb_list.append(h["hawbNo"])

            manifestHawbNo = Manifest.objects.filter(hawbNo__in=hawb_list).order_by('insertDate', 'id')
            serializer = ManifestHawbNoSerializer(manifestHawbNo, many=True)
            return Response(status=200, data=serializer.data)
            
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': f'Bad Request - {ex}'}, safe=False)


    def get_queryset(self):

        hawb_nos = self.request.query_params.get("hawb_nos", None)
        if hawb_nos is not None:
            hawb_objs = json.loads(hawb_nos)
            hawb_list=[]
            for h in hawb_objs:
                hawb_list.append(h["hawbNo"])

            return Manifest.objects.filter(hawbNo__in=hawb_list).order_by('insertDate', 'id')

        return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            hawb_nos = json.loads(data['hawbNos'])

            print('update2')
            for hawb in hawb_nos:
                manifest = get_object_or_404(Manifest, hawbNo=hawb['hawbNo'])
                setattr(manifest, data['field'], data['value'])
                if (data['field'] == 'scanned'):
                    setattr(manifest, 'scanTimes', int(manifest.ct))
                    
                    formatted_date = ''
                    if int(manifest.scanTimes) > 0:
                        now = datetime.now()
                        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")            
                        
                    print(formatted_date)    
                    setattr(manifest, 'scanDate', formatted_date)   

                manifest.save()

            return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


# Port 수입지역 목록 블러오기
class ManifestPortViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestPortSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        group = self.request.query_params.get("group", None)
        from_insert_date = self.request.query_params.get("s_date", None)
        to_insert_date = self.request.query_params.get("e_date", None)

        if from_insert_date is None or to_insert_date is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_objects = Q(insertDate__gte=from_insert_date) & Q(
            insertDate__lte=to_insert_date)

        if group == "port":
            return Manifest.objects.filter(q_objects).values("port").annotate(Count('port'))

        return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


# Team 배송팀 목록 불러오기
class ManifestTeamViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestTeamSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        group = self.request.query_params.get("group", None)
        from_insert_date = self.request.query_params.get("s_date", None)
        to_insert_date = self.request.query_params.get("e_date", None)

        if from_insert_date is None or to_insert_date is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_objects = Q(insertDate__gte=from_insert_date) & Q(
            insertDate__lte=to_insert_date)

        if group == "team":
            return Manifest.objects.filter(q_objects).values("team").annotate(count=Count('team'))

        return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

    def partial_update(self, request, *args, **kwargs):
        try:
            manifest = get_object_or_404(Manifest, hawbNo=kwargs['pk'])

            q_objects = Q(consignee__exact=manifest.consignee)
            queryset = Manifest.objects.filter(
                q_objects)
            
            queryset.update(team=manifest.team)
            
            return JsonResponse(status=200, data={'code': 200, 'message': 'Updated'}, safe=False)
        except Exception as ex:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


class ManifestFlightViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestFlightSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        group = self.request.query_params.get("group", None)
        from_insert_date = self.request.query_params.get("s_date", None)
        to_insert_date = self.request.query_params.get("e_date", None)

        if from_insert_date is None or to_insert_date is None:
            return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)

        q_objects = Q(insertDate__gte=from_insert_date) & Q(
            insertDate__lte=to_insert_date)

        if group == "flight":
            return Manifest.objects.filter(q_objects).values("flight").annotate(Count('flight'))

        return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)


class ManifestInsertDateViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.all()
    serializer_class = ManifestInsertDateSerializer

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        group = self.request.query_params.get("group", None)

        if group == "insert_date":
            return Manifest.objects.values("insertDate").annotate(Count('insertDate')).order_by("-insertDate")[:30]

        return JsonResponse(status=400, data={'code': 400, 'message': 'Bad Request'}, safe=False)
