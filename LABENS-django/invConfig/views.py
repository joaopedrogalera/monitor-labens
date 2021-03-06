from .models import InvConfig
from .models import InvConfigTokens
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect

def getInvConfig(request):
    jsonReturn = []
    if (not 'campus' in request.GET.keys() and not 'inv' in request.GET.keys()):
        inverters = InvConfig.objects.all()
    elif 'campus' in request.GET.keys() and not request.GET['campus'] == "":

        if 'inv' in request.GET.keys() and not request.GET['inv'] == "":
            inverters = InvConfig.objects.filter(campus=request.GET['campus']).filter(nome=request.GET['inv'])
        else:
            inverters = InvConfig.objects.filter(campus=request.GET['campus'])
    else:
        return JsonResponse({'Error':'Missing Query Parameters'},status=400)

    if not inverters:
        return JsonResponse({'Error':'No inverters found'},status=404)

    for inverter in inverters:
        invParam = dict()
        invParam = {
                    'campus_cod':inverter.campus,
                    'inv_name':inverter.nome,
                    'inv_description':inverter.descri,
                    'power_factor':inverter.fp,
                    'power_limit':inverter.limPot,
                    'update_time':inverter.UpdateTime.strftime("%Y-%m-%d %H:%M:%S"),
                    'status':inverter.get_UpdateStatus_display()
                    }

        if not inverter.fp == 1.0:
            invParam['pf_type'] = inverter.get_fpTipo_display()
        else:
            invParam['pf_type'] = "Unitary"

        jsonReturn.append(invParam)

    return JsonResponse(jsonReturn,safe=False)

@csrf_exempt
def updateInvConfig(request):
    if request.method == "POST":
        if not 'content-type' in request.headers or not request.headers['content-type'] == 'application/json':
            return HttpResponse("Content type must be application/json", status=400)
        if  not 'labens-token' in request.headers:
            return HttpResponse("Auth token not present", status=401)

        content = json.loads(request.body.decode('utf-8'))

        if not type(content) is dict:
            return HttpResponse("Invalid json format. The format must be dict", status=400)

        if not 'campus' in content.keys() or content['campus'] == "" or not 'inv' in content.keys() or content['inv'] == "" or not 'power_factor' in content.keys() or content['power_factor'] == "" or not 'power_limit' in content.keys() or content['power_limit'] == "":
            return HttpResponse("Missing Parameters. 'campus', 'inv', 'power_factor', and 'power_limit' must be present", status=400)

        if not content['power_factor'] == 1.0 and (not 'pf_type' in content.keys() or content['pf_type'] == ""):
            return HttpResponse("Missing Parameters. 'pf_type' must be present when power_factor!=1.0", status=400)

        token = InvConfigTokens.objects.filter(token=request.headers['labens-token']).filter(inverters__campus=content["campus"]).filter(inverters__nome=content["inv"])

        if not token:
            return HttpResponse("Unauthorized", status=401)

        inverter = InvConfig.objects.filter(campus=content['campus']).filter(nome=content['inv'])
        inv = inverter[0]

        inv.fp = content['power_factor']
        inv.limPot = content['power_limit']
        inv.UpdateStatus = "A"

        if not content['power_factor'] == 1.0 and content['pf_type'] == "Inductive":
            inv.fpTipo = "D"
        elif not content['power_factor'] == 1.0 and content['pf_type'] == "Capacitive":
            inv.fpTipo = "A"
        elif not content['power_factor'] == 1.0:
            return HttpResponse("Invalid pf_type",status=400)

        inv.save()

        return HttpResponse('')

    else:
        return redirect('/')
