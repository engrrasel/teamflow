from django.http import JsonResponse
from .models import District, Thana, PostOffice


def load_districts(request):
    division_id = request.GET.get('division')
    data = District.objects.filter(
        division_id=division_id
    ).values('id', 'name')
    return JsonResponse(list(data), safe=False)


def load_thanas(request):
    district_id = request.GET.get('district')
    data = Thana.objects.filter(
        district_id=district_id
    ).values('id', 'name')
    return JsonResponse(list(data), safe=False)


def load_post_offices(request):
    thana_id = request.GET.get('thana')
    data = PostOffice.objects.filter(
        thana_id=thana_id
    ).values('id', 'name', 'post_code')
    return JsonResponse(list(data), safe=False)
