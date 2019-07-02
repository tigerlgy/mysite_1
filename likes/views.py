from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord

def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

# Create your views here.
def like_change(request):
    # receive data
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(400, 'You are not logged in, please log in to like this blog.')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, "The blog doesn't exsit anymore")
    # process data
    if request.GET.get('is_like') == 'true':
        # like
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, 
                                                               object_id=object_id, user=user)
        if created:
            # not liked before
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, 
                                                               object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            # liked, cannot like again
            return ErrorResponse(402 ,'You have already liked this blog.')
    else:
        # unlike
        if LikeRecord.objects.filter(content_type=content_type, 
                                     object_id=object_id, user=user).exists():
            like_record = LikeRecord.objects.get(content_type=content_type, 
                                                 object_id=object_id, user=user)
            like_record.delete()
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, 
                                                               object_id=object_id)
            if not created:
                like_count.liked_num -=1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(404, 'information not found')
        else:
            return ErrorResponse(403, "You haven't liked this blog")

