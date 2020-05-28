import qrcode


def generate( code ):
    codigo = qrcode.make( code )
    return codigo

