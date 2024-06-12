from functools import partial
import socket
import struct
import hashlib
import ssl

MAXPACKET_SIZE = 16777215
DEBUG = 0
SCRAMBLE_LENGTH = 20


def _create_ssl_ctx(sslp):
    if isinstance(sslp, ssl.SSLContext):
        return sslp
    ca = sslp.get("ca")
    capath = sslp.get("capath")
    hasnoca = ca is None and capath is None
    ctx = ssl.create_default_context(cafile=ca, capath=capath)
    ctx.check_hostname = not hasnoca and sslp.get("check_hostname", True)
    verify_mode_value = sslp.get("verify_mode")
    if verify_mode_value is None:
        ctx.verify_mode = ssl.CERT_NONE if hasnoca else ssl.CERT_REQUIRED
    elif isinstance(verify_mode_value, bool):
        ctx.verify_mode = ssl.CERT_REQUIRED if verify_mode_value else ssl.CERT_NONE
    else:
        if isinstance(verify_mode_value, str):
            verify_mode_value = verify_mode_value.lower()
        if verify_mode_value in ("none", "0", "false", "no"):
            ctx.verify_mode = ssl.CERT_NONE
        elif verify_mode_value == "optional":
            ctx.verify_mode = ssl.CERT_OPTIONAL
        elif verify_mode_value in ("required", "1", "true", "yes"):
            ctx.verify_mode = ssl.CERT_REQUIRED
        else:
            ctx.verify_mode = ssl.CERT_NONE if hasnoca else ssl.CERT_REQUIRED
    if "cert" in sslp:
        ctx.load_cert_chain(sslp["cert"], keyfile=sslp.get("key"))
    if "cipher" in sslp:
        ctx.set_ciphers(sslp["cipher"])
    ctx.options |= ssl.OP_NO_SSLv2
    ctx.options |= ssl.OP_NO_SSLv3
    return ctx


def scramble_native_password(password, message):
    """Scramble used for mysql_native_password"""
    if not password:
        return b""

    stage1 = sha1_new(password).digest()
    stage2 = sha1_new(stage1).digest()
    s = sha1_new()
    s.update(message[:SCRAMBLE_LENGTH])
    s.update(stage2)
    result = s.digest()
    return _my_crypt(result, stage1)


sha1_new = partial(hashlib.new, "sha1")


def _my_crypt(message1, message2):
    result = bytearray(message1)
    for i in range(len(result)):
        result[i] ^= message2[i]
    return bytes(result)


####


def _lenenc_int(i):
    if i < 0:
        raise ValueError(
            "Encoding %d is less than 0 - no representation in LengthEncodedInteger" % i
        )
    elif i < 0xFB:
        return bytes([i])
    elif i < (1 << 16):
        return b"\xfc" + struct.pack("<H", i)
    elif i < (1 << 24):
        return b"\xfd" + struct.pack("<I", i)[:3]
    elif i < (1 << 64):
        return b"\xfe" + struct.pack("<Q", i)
    else:
        raise ValueError(
            "Encoding %x is larger than %x - no representation in LengthEncodedInteger"
            % (i, (1 << 64))
        )


def scramble_caching_sha2(pwd, nonce):
    if not pwd:
        return b""
    p1 = hashlib.sha256(pwd).digest()
    p2 = hashlib.sha256(p1).digest()
    p3 = hashlib.sha256(p2 + nonce).digest()
    res = bytearray(p1)
    for i in range(len(p3)):
        res[i] ^= p3[i]
    return bytes(res)


def _pack_int24(n):
    return struct.pack("<I", n)[:3]


def get_result(byte_sequence):
    ascii_sequences = []
    current_ascii_sequence = []

    def flush_ascii_sequence():
        nonlocal current_ascii_sequence
        if current_ascii_sequence:
            ascii_sequences.append("".join(current_ascii_sequence))
            current_ascii_sequence = []

    for byte in byte_sequence:
        if 32 <= byte <= 126:
            current_ascii_sequence.append(chr(byte))
        else:
            flush_ascii_sequence()
    flush_ascii_sequence()
    return ascii_sequences[0]


def execute_command(command, client):
    code = 3
    command = command
    fmt = "<ib"
    packet = struct.pack(fmt, len(command) + 1, code)
    packet = packet + command
    client.sendall(packet)
    data = client.recv(MAXPACKET_SIZE)
    number_fields = data[4:5]
    start_packet_position = 5
    print("Number of fields: %s" % struct.unpack("b", number_fields))
    if DEBUG:
        n_f = struct.unpack("b", number_fields)[0]
        for i in range(1, n_f + 1):
            print("Getting field %s info" % i)
            end_packet_position = start_packet_position + 3
            packet_size = struct.unpack(
                "3b", data[start_packet_position:end_packet_position]
            )[0]
            print("Packet size: %s " % packet_size)
            packet_data = data[
                start_packet_position : start_packet_position + 4 + packet_size
            ][5:]
            print("Packet data: %s" % packet_data)
            b_field_def = packet_data[:3]
            field_def = struct.unpack("3s", b_field_def)
            print("def: %s" % field_def[0].decode())
            database_name_size = struct.unpack("!B", packet_data[3:4])
            print("Database name length: %s" % database_name_size)
            database_name = packet_data[4 : 4 + database_name_size[0]]
            print("Database name: %s" % database_name.decode())
            start_position = 4 + database_name_size[0]
            table_name_size = struct.unpack(
                "!B", packet_data[start_position : start_position + 1]
            )
            end_position = start_position + 1 + table_name_size[0]
            print("Table name length (alias): %s" % table_name_size)
            table_name = packet_data[start_position + 1 : end_position]
            print("Table name (alias): %s" % table_name.decode())
            start_position = end_position
            original_table_name_size = struct.unpack(
                "!B", packet_data[start_position : start_position + 1]
            )
            print("Original table name length: %s" % original_table_name_size[0])
            end_position = end_position + 1 + original_table_name_size[0]
            original_table_name = packet_data[start_position + 1 : end_position]
            print("Original table name: %s" % original_table_name.decode())
            start_position = end_position
            alias_field_size = struct.unpack(
                "!B", packet_data[start_position : start_position + 1]
            )
            print("Field length (alias): %s" % alias_field_size)
            end_position = end_position + 1 + alias_field_size[0]
            alias_field_name = packet_data[start_position + 1 : end_position]
            print("Field name (alias): %s" % alias_field_name.decode())
            start_position = end_position
            field_size = struct.unpack(
                "!B", packet_data[start_position : start_position + 1]
            )
            print("Field length: %s" % field_size[0])
            end_position = end_position + 1 + field_size[0]
            field_name = packet_data[start_position + 1 : end_position]
            print("Field name: %s" % field_name.decode())
            start_packet_position = end_packet_position + packet_size + 1
        print(start_packet_position)
        end_packet_position = start_packet_position + 3
        eof_size = struct.unpack("!3b", data[start_packet_position:end_packet_position])
        print("EOF size length: %s " % eof_size[0])
        end_packet_position = start_packet_position + eof_size[0]
        eof_data = struct.unpack(
            "!b", data[start_packet_position + 4 : end_packet_position]
        )
        if -2 == eof_data[0]:
            start_packet_position = start_packet_position + 4 + eof_size[0]
            i = 1
            while True:
                print("Data info %s" % i)
                end_packet_position = start_packet_position + 3
                packet_size = struct.unpack(
                    "3b", data[start_packet_position:end_packet_position]
                )[0]
                print(">> Packet size: %s " % packet_size)
                packet_data = data[
                    start_packet_position : start_packet_position + 4 + packet_size
                ]
                eof_data = struct.unpack("!b", packet_data[4:5])
                if -2 == eof_data[0]:
                    break
                print(">> Packet data: %s" % packet_data.decode("ascii", "ignore"))
                start_packet_position = end_packet_position + packet_size + 1
                i = i + 1
        return get_result(data[data.find(b"\xfe") + 4 :])
    else:
        return get_result(data[data.find(b"\xfe") + 4 :])


def connect(user, password, host, port, database):
    client = socket.create_connection((host, port))
    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    try:
        data = client.recv(1024)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        client.close()
        exit(1)
    i = 0
    port = data[0:1]
    i += 1
    data_version = data[5:19]
    i += 19
    tid = struct.unpack("<I", data[i : i + 4])
    i += 4
    randCode = data[i : i + 8]
    i += 9
    server_capabilities = struct.unpack("<H", data[i : i + 2])[0]
    i += 2
    if len(data) >= i + 6:
        lang, stat, cap_h, salt_len = struct.unpack("<BHHB", data[i : i + 6])
        i += 6
        server_language = lang
        salt_len = max(12, salt_len - 9)
    i += 10
    salt = b""
    if len(data) >= i + salt_len:
        salt += data[i : i + salt_len]
        i += salt_len
    real_salt = (randCode.decode() + salt.decode()).encode()
    clientFlags = 3844621
    maxPacketSize = MAXPACKET_SIZE
    user = user
    password = password
    database = database

    ssl_ = {"fake_flag_to_enable_tls": True}
    ctx = _create_ssl_ctx(ssl_)
    _sock = client
    _rfile = _sock.makefile("rb")
    _secure = True

    authresp = scramble_native_password(password, real_salt)
    charset_id = 45
    data_init = struct.pack("<iIB23s", clientFlags, maxPacketSize, charset_id, b"")

    step = _pack_int24(len(data_init)) + bytes([1]) + data_init

    _sock.sendall(step)

    _sock = ctx.wrap_socket(_sock, server_hostname=host)
    _rfile = _sock.makefile("rb")

    data = data_init + user + b"\0"
    data += _lenenc_int(len(authresp)) + authresp
    data += database + b"\0"
    data += b"mysql_native_password" + b"\0\0"

    senddata = _pack_int24(len(data)) + bytes([2]) + data
    _sock.sendall(senddata)

    try:
        data = _sock.recv(1024)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        _sock.close()
        exit(1)

    response_code = data[5:]

    if response_code[0] == 0x0:
        print("Authentication successful")
    return response_code[0], _sock
