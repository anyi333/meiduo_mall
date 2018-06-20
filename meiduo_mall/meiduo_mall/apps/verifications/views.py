import random
from django.contrib.messages import constants
from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from verifications import serializers

# Create your views here.

class ImageCodeView(APIView):
    '''图片验证码'''
    def get(self, request, image_code_id, captcha=None):
        # 生成图片验证码
        text,image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s' % image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image,content_type='images/jpg')

class SMSCodeView(GenericAPIView):
    '''短信验证码'''

    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self,request,mobile):
        '''创建短信验证码'''
        # 判断图片验证码, 判断是否在60s内
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 发送短信验证码
        sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        ccp = CCP()
        ccp.send_template_sms(mobile, [code, expires], SMS_CODE_TEMP_ID)

        return Response({'message':'OK'})

