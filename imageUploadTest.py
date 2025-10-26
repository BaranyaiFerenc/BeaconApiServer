import BeaconShell


images = [
    './testing/test_images/1.png',
    './testing/test_images/2.png',
    './testing/test_images/3.png',
    './testing/test_images/4.png',
]


for img in images:
    input("Press enter to send the image...")
    BeaconShell.SendImage(username="admin", password="Titok123", imagePath=img)
