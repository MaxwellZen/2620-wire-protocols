
def encode_request(request):
    return

def decode_request(request):
    ind = request.find(' ')
    command = request[:ind]
    request = request[ind+1:]
    args = [command]
    arg = ""
    ind = 0
    while ind < len(request):
        if request[ind] == '[':
            ind += 1
        elif request[ind] == ']':
            args.append(arg)
            arg = ""
            ind += 3
        elif request[ind] == '\\':
            arg += request[ind+1]
            ind += 2
        else:
            arg += request[ind]
            ind += 1
    return args

def test_decode_request():
    assert(decode_request("abc [def] [ghi]") == ["abc", "def", "ghi"])
    assert(decode_request("abc [\[\]\]\]\[\\\\]") == ["abc", "[]]][\\"])
    print("decode_request tests passed")

if __name__ == "__main__":
    test_decode_request()