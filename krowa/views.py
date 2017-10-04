from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder

import json, re

# Create your views here.
def index(request):
    context = {}
    return render(
        request,
        'krowa/index.html',
        context,
    )

def search_krowa_sequence(request):
    seq_start = -1
    seq_length = -1
    sequences = {}
    input_data = ""

    patterns = [request.POST['patterns_text']][0].encode('utf-8').split()

    # read patterns from 1. cli, 2. file
    if request.FILES['patterns_file'] is not None:
        patterns += request.FILES['patterns_file'].read().splitlines()

    patterns = list(filter(None, patterns))

    if request.FILES['patterns_file'] is None:
        res_dict = {
            'result' : 'no sequences'
        }
        return HttpResponse(
            content=DjangoJSONEncoder().encode(res_dict),
            content_type='application/json',
            status=400)

    for line in request.FILES['sequences']:
        _l = line.strip().decode('utf-8')
        _l = re.sub(' +',' ',_l)
        l = _l.split(" ")
        l_t = "".join(l[1:])
        input_data += l_t
        sequences[l[0]] = " ".join(l[1:])
        if seq_start == -1:
            seq_start = int(l[0])
            seq_length = len(l[1])

    line_step = 0
    k = list(sequences.keys())
    v = list(sequences.values())

    if len(k) > 1:
        line_step = int(k[1]) - int(k[0])

    search_res = ""

    for p in patterns:
        p = p.decode('utf-8')
        search_res += "\n\nPattern: {:s}\n".format(p.strip())
        pos = 0
        rex = re.compile(p.strip(), flags=re.IGNORECASE)
        cnt = 0
        while True:
            res = rex.search(input_data, pos)

            if res is None:
                if cnt == 0:
                    search_res += "No match for this pattern\n"
                break

            cnt += 1

            sta = res.start()
            sto = res.end()
            pos = sta+1

            idx_sta = int( (sta - seq_start + 1)/line_step )
            idx_sto = int( (sto - seq_start + 1)/line_step )

            marker = sta - int(k[idx_sta]) + 1
            breaks_cnt = int((marker) / seq_length)
            search_res += k[idx_sta] + " {:s}|".format("-"*(marker+breaks_cnt)) + "\n"

            for idx in range(idx_sta, idx_sto+1):
                search_res += k[idx] + " " + v[idx] + "\n"

            marker = sto - int(k[idx_sto])
            breaks_cnt = int((marker) / seq_length)
            search_res += k[idx_sto] + " {:s}|<".format(" "*(marker+breaks_cnt))
            search_res += "\n\n"

    res_dict = {
        'result' : 'OK',
        'data': search_res
    }

    return HttpResponse(
        content=DjangoJSONEncoder().encode(res_dict),
        content_type='application/json',
        status=200)
