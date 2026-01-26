from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.user.serializers.profile import MeSerializer, DeleteUserSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="내 정보 조회",
        description="로그인한 사용자의 정보를 조회합니다. email은 읽기 전용입니다.",
        responses={
            200: MeSerializer,
            401: OpenApiResponse(description="인증되지 않은 사용자"),
        },
    )
    def get(self, request):
        """
        내 정보 조회
        """
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="내 정보 전체 수정",
        description="nickname, name, gender 필드를 전체 수정합니다. email과 password는 수정 불가합니다. 비밀번호를 인증용으로 입력해야 합니다.",
        request=MeSerializer,
        responses={
            200: MeSerializer,
            400: OpenApiResponse(
                description="유효하지 않은 데이터 또는 비밀번호 불일치"
            ),
            401: OpenApiResponse(description="인증되지 않은 사용자"),
        },
    )
    def put(self, request):
        """
        내 정보 전체 수정 + 비밀번호 인증
        """
        serializer = MeSerializer(
            request.user,
            data=request.data,
            context={"request": request},
            partial=False,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="내 정보 부분 수정",
        description="nickname, name, gender 필드 중 일부만 수정 가능합니다. email과 password는 수정 불가합니다. 비밀번호를 인증용으로 입력해야 합니다.",
        request=MeSerializer,
        responses={
            200: MeSerializer,
            400: OpenApiResponse(
                description="유효하지 않은 데이터 또는 비밀번호 불일치"
            ),
            401: OpenApiResponse(description="인증되지 않은 사용자"),
        },
    )
    def patch(self, request):
        """
        내 정보 부분 수정 + 비밀번호 인증
        """
        serializer = MeSerializer(
            request.user,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="회원 탈퇴",
        description="로그인한 사용자의 비밀번호 확인 후 soft delete 처리합니다.",
        request=DeleteUserSerializer,
        responses={
            204: OpenApiResponse(description="회원 탈퇴 완료"),
            400: OpenApiResponse(description="비밀번호 불일치"),
            401: OpenApiResponse(description="인증되지 않은 사용자"),
        },
        methods=["DELETE"],
    )
    def delete(self, request):
        import json

        try:
            data = request.data
            if not data:
                data = json.loads(request.body.decode("utf-8"))
        except Exception:
            data = {}

        serializer = DeleteUserSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        request.user.is_active = False
        request.user.save(update_fields=["is_active"])

        return Response(
            {"message": "회원 탈퇴가 완료되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )
