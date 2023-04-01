from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    @classmethod
    # database에서 조회된 user의 정보가 user로 들어오게 된다. (요청한 user의 정보)
    def get_token(cls, user):
        # 가지고 온 user의 정보를 바탕으로 token을 생성한다.
        token = super().get_token(user)

        # 로그인한 사용자의 클레임 설정하기.
        token['id'] = user.id
        token['username'] = user.username
        token['email'] = user.email

        return token
    """
    # response 커스텀
    default_error_messages = {
        'no_active_account': {'message': 'username or password is incorrect!',
                              'success': False,
                              'status': 401}
    }
    # 유효성 검사

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        # response에 추가하고 싶은 key값들 추가

        data['user'] = {"userName": self.user.username,
                        "isSuperUser": self.user.is_superuser,
                        "isStaff": self.user.is_staff}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['success'] = True

        return data
