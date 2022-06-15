import qrcode

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('1H59GKH2BT7Q2K')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

with open('qrcode6.png', 'wb') as f:
    img.save(f)