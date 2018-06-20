# _*_ coding:utf-8 _*_
from django.db.migrations import serializer
from django_redis import get_redis_connection

from meiduo_mall.utils.exceptions import logger


class ImageCodeCheckSerializer(serializer.Serializer):
    '''图片验证码校验序列化器'''

    image_code_id = serializer.UUIDSerializer()
    text = serializer.CharField(max_lenth=4,min_lenth=4)

    def validate(self,attrs):
        '''检验'''

        image_code_id = attrs['image_code_id']
        text = attrs['text']
        # 查询真是图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id)
        if not real_image_code_text:
            raise serializer.ValidationError('图片验证码无效')

        # 删除图片验证码
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except Exception as e:
            logger.error(e)

            # 比较图片验证码
            real_image_code_text = real_image_code_text.decode()
            if real_image_code_text.lower() != text.lower():
                raise serializer.ValidationError('图片验证码无效')

            # 判断是否在60s之内
            mobile = self.context['view'].kwargs['mobile']
            send_flag = redis_conn.get('send_flag_%s' % mobile)
            if send_flag:
                raise serializer.ValidationError('请求次数频繁')

            return attrs





