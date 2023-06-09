from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from accounts.jwt_claim_serializer import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# TokenObtainPairView : urls.py에서 import했고, 토큰을 발급받기 위해 사용

class CustomTokenObtainPairView(TokenObtainPairView):
    # serializer_class에 커스터마이징된 시리얼라이저를 넣어 준다.
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom Refresh token View
    """
    serializer_class = CustomTokenRefreshSerializer
    
    

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_200_OK, data={'code': 200, 'message': 'Successful Logout'})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'code': 400, 'message': 'Failed Logout'})


            
"""
class UserView(APIView):

    # DONE 회원 정보 조회
    def get(self, request):
        data = UserModel.objects.get(id=request.user.id)
        return Response(UserSerializer(data).data, status=status.HTTP_200_OK)

    # DONE 회원가입
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DONE 회원 정보 수정
    def put(self, request):
        user = UserModel.objects.get(id=request.user.id)
        user_serializer = UserSerializer(user, data=request.data, partial=True)

        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DONE 회원 탈퇴
    def delete(self, request):
        user = UserModel.objects.get(id=request.user.id)
        if user:
            user.delete()
            return Response({"message": "회원탈퇴 성공"}, status=status.HTTP_200_OK)
        return Response({"message": "회원탈퇴 실패"}, status=status.HTTP_400_BAD_REQUEST)

"""

