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

def get_selection(k, v, seq_start, seq_length, sta, sto, step):
    search_res = ""

    idx_sta = 0
    idx_sto = 0

    if step > 0:
        idx_sta = int( (sta - seq_start + 1)/step )
        idx_sto = int( (sto - seq_start + 1)/step )

    marker = sta - int(k[idx_sta]) + 1
    breaks_cnt = int((marker) / seq_length)
    search_res += k[idx_sta] + " {:s}|".format("-"*(marker+breaks_cnt)) + "\n"

    for idx in range(idx_sta, idx_sto+1):
        search_res += k[idx] + " " + v[idx] + "\n"

    marker = sto - int(k[idx_sto])
    breaks_cnt = int((marker) / seq_length)
    search_res += k[idx_sto] + " {:s}|<".format(" "*(marker+breaks_cnt))
    search_res += "\n\n"
    return search_res

def fast_search(seq_start, seq_length, sequences, patterns, input_data, v, k, acc_r, acc_n):
    line_step = 0
    if len(k) > 1:
        line_step = int(k[1]) - int(k[0])

    search_res = ""

    for p in patterns:
        p = p.decode('utf-8')
        search_res += "Pattern: {:s}\n".format(p.strip())
        pos = 0
        rex = re.compile(p.strip(), flags=re.IGNORECASE)
        cnt = 0
        while True:
            res = rex.search(input_data, pos)

            if res is None:
                if cnt == 0:
                    search_res += "No match for this pattern\n\n"
                break

            cnt += 1

            sta = res.start()
            sto = res.end()
            pos = sta+1

            search_res += get_selection(k, v, seq_start, seq_length, sta, sto, line_step)

    res_dict = {
        'result' : 'OK',
        'data': search_res
    }

    return HttpResponse(
        content=DjangoJSONEncoder().encode(res_dict),
        content_type='application/json',
        status=200)

def slow_search(seq_start, seq_length, sequences, patterns, input_data, v, k, acc_r, acc_n):
    line_step = 0

    if len(k) > 1:
        line_step = int(k[1]) - int(k[0])

    search_res = ""
    i_d = input_data.lower()
    i_d_len = len(i_d)

    for p in patterns:
        p = p.decode('utf-8').strip()
        search_res += "Pattern: {:s}\n".format(p)
        pos = 0
        cnt = 0

        p_cnt = 0
        p_len = len(p)

        p_lower = p.lower()
        while True:
            pos = i_d.find(p_lower[0], pos)
            if pos == -1:
                if cnt == 0:
                    search_res += "No match for this pattern\n\n"
                break

            got_it = True
            for i in range(1, p_len):
                if pos+i >= i_d_len:
                    got_it = False
                    break;

                if i_d[pos+i] == p_lower[i]:
                    continue
                if acc_n and i_d[pos+i] == 'n':
                    continue
                if acc_r and i_d[pos+i] == 'r':
                    continue

                got_it = False
                break;

            if got_it is False:
                pos += 1
                continue;

            cnt += 1

            sta = pos
            sto = pos+p_len
            pos += 1

            search_res += get_selection(k, v, seq_start, seq_length, sta, sto, line_step)

    res_dict = {
        'result' : 'OK',
        'data': search_res
    }

    return HttpResponse(
        content=DjangoJSONEncoder().encode(res_dict),
        content_type='application/json',
        status=200)


def search_krowa_sequence(request):
    seq_start = -1
    seq_length = -1
    sequences = {}
    patterns = []
    input_data = ""

    file_format = 0 # 1 == genbank
    filter_header = True

    patterns = [request.POST['patterns_text']][0].encode('utf-8').split()

    # read patterns from 1. cli, 2. file
    if 'patterns_file' in request.FILES and request.FILES['patterns_file'] is not None:
        patterns += request.FILES['patterns_file'].read().splitlines()

    patterns = list(filter(None, patterns))

    for line in request.FILES['sequences']:
        _l = line.strip().decode('utf-8')
        _l = re.sub(' +',' ',_l)
        l = _l.split(" ")

        # check for file format
        if file_format == 0:
            try:
                int(l[0])
                filter_header = False
            except:
                if l[0] == 'LOCUS':
                    file_format = 1

        # header filet for genbank
        if file_format == 1:
            if filter_header == True:
                if l[0] == 'ORIGIN':
                    filter_header = False
                continue
            if filter_header == False:
                if l[0] == '//':
                    break

        l_t = "".join(l[1:])
        input_data += l_t
        sequences[l[0]] = " ".join(l[1:])
        if seq_start == -1:
            seq_start = int(l[0])
            seq_length = len(l[1])

    line_step = 0
    k = list(sequences.keys())
    v = list(sequences.values())

    if request.FILES['sequences'] is None:
        res_dict = {
            'result' : 'no sequences'
        }
        return HttpResponse(
            content=DjangoJSONEncoder().encode(res_dict),
            content_type='application/json',
            status=400)

    acc_r = 'accept_r' in request.POST
    acc_n = 'accept_n' in request.POST

    if (not acc_r and not acc_n):
        return fast_search(seq_start, seq_length, sequences, patterns, input_data, v, k, acc_r, acc_n)
    else:
        return slow_search(seq_start, seq_length, sequences, patterns, input_data, v, k, acc_r, acc_n)
