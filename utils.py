
def encode_request(command, args):
    request = command
    for arg in args:
        arg2 = ""
        for i in range(len(arg)):
            if arg[i] in "[]\\":
                arg2 += "\\"
            arg2 += arg[i]
        request += " [" + arg2 + "]"
    return request

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

def test_encode_request():
    assert(encode_request("abc", ["def", "ghi"]) == "abc [def] [ghi]")
    assert(encode_request("abc", ["[][]\\\\"]) == "abc [\[\]\[\]\\\\\\\\]")
    print("encode_request tests passed")

def test_decode_request():
    assert(decode_request("abc [def] [ghi]") == ["abc", "def", "ghi"])
    assert(decode_request("abc [\[\]\]\]\[\\\\]") == ["abc", "[]]][\\"])
    print("decode_request tests passed")

if __name__ == "__main__":
    test_encode_request()
    test_decode_request()