"""
Copyright (c) 2006, Gustavo Niemeyer <gustavo@niemeyer.net>

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


dumps_table = {}
loads_table = {}


def dumps(obj, _dt=None):
    if not _dt:
        _dt = dumps_table

    type_names = [type(obj)]
    for type_name in type_names:
        if type_name in _dt:
            return _dt[type_name](obj)

        type_names.extend(type_name.__bases__)

    raise ValueError("Unsupported type: %s" % type(obj))


def loads(str, _lt=loads_table):
    if not str:
        raise ValueError("Can't load empty string")
    try:
        return _lt[str[0]](str, 0)[0]
    except KeyError as e:
        raise ValueError("Unknown type character: %s" % e)
    except IndexError:
        raise ValueError("Corrupted data")


def dumps_bool(obj):
    return ("b%d" % int(obj)).encode("ascii")


def dumps_int(obj):
    return ("i%s;" % obj).encode("ascii")


def dumps_float(obj):
    return ("f%r;" % obj).encode("ascii")


def dumps_bytes(obj):
    return ("c%s:" % len(obj)).encode("ascii") + obj


def dumps_str(obj):
    obj = obj.encode("utf-8")
    return ("s%s:" % len(obj)).encode("ascii") + obj


def dumps_list(obj, _dt=None):
    return b"l" + b"".join([dumps(val, _dt) for val in obj]) + b";"


def dumps_tuple(obj, _dt=None):
    return b"t" + b"".join([dumps(val, _dt) for val in obj]) + b";"


def dumps_dict(obj, _dt=None):
    res = []
    keys = sorted(obj.keys())
    append = res.append
    for key in keys:
        val = obj[key]
        append(dumps(key, _dt))
        append(dumps(val, _dt))
    return b"d" + b"".join(res) + b";"


def dumps_none(obj):
    return b"n"


def loads_bool(str, pos):
    return bool(int(chr(str[pos + 1]))), pos + 2


def loads_int(str, pos):
    endpos = str.index(b";", pos)
    return int(str[pos + 1:endpos]), endpos + 1


def loads_float(str, pos):
    endpos = str.index(b";", pos)
    return float(str[pos + 1:endpos]), endpos + 1


def loads_bytes(str, pos):
    startpos = str.index(b":", pos) + 1
    endpos = startpos + int(str[pos + 1:startpos - 1])
    return str[startpos:endpos], endpos


def loads_str(str, pos):
    startpos = str.index(b":", pos) + 1
    endpos = startpos + int(str[pos + 1:startpos - 1])
    return str[startpos:endpos].decode("utf-8"), endpos


def loads_list(str, pos, _lt=loads_table):
    pos += 1
    res = []
    append = res.append
    while str[pos] != ord(";"):
        obj, pos = _lt[str[pos]](str, pos)
        append(obj)
    return res, pos + 1


def loads_tuple(str, pos, _lt=loads_table):
    pos += 1
    res = []
    append = res.append
    while str[pos] != ord(";"):
        obj, pos = _lt[str[pos]](str, pos)
        append(obj)
    return tuple(res), pos + 1


def loads_dict(str, pos, _lt=loads_table):
    pos += 1
    res = {}
    while str[pos] != ord(";"):
        key, pos = _lt[str[pos]](str, pos)
        val, pos = _lt[str[pos]](str, pos)
        res[key] = val
    return res, pos + 1


def loads_none(str, pos):
    return None, pos + 1


dumps_table.update({
    bool: dumps_bool,
    int: dumps_int,
    float: dumps_float,
    bytes: dumps_bytes,
    str: dumps_str,
    list: dumps_list,
    tuple: dumps_tuple,
    dict: dumps_dict,
    type(None): dumps_none,
    })

loads_table.update({
    ord("b"): loads_bool,
    ord("i"): loads_int,
    ord("f"): loads_float,
    ord("c"): loads_str,
    ord("s"): loads_str,
    ord("u"): loads_str,
    ord("l"): loads_list,
    ord("t"): loads_tuple,
    ord("d"): loads_dict,
    ord("n"): loads_none,
    })
