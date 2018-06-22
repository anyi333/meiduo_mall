# _*_ coding:utf-8 _*_
from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers


class ImageCodeCheckSerializer(serializers.Serializer):
    '''图片验证码序列化器'''
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    # validate:可以跨字段检验   validate_:对特定字段进行校验
    def validate(self, attrs):
        '''校验'''
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        # 查询真实图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        # 删除redis中的图片验证码
        # 为了只比较一次,所以要先删除redis中的验证码,即使输入错误,下次会获取新的验证码
        redis_conn.delete('img_%s' % image_code_id)

        # 比较图片验证码
        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        # 判断是否在60s内
        # get_serializer方法在创建序列化器对象时,会自动生成context属性
        # context包含(request,format,view类视图对象)
        # 类视图对象中,kwargs属性保存了路径提取出来的参数
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')

        return attrs




