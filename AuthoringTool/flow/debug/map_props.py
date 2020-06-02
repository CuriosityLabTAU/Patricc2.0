prop_to_rfid = {
    'goat': ['A08D64A2', 'D0C771A2', '7C96AC00'],
    'donkey' : ['704076A2', '804575A2', '69D9AC00'],
    'rooster' : ['D06468A2', 'FED3AC00'],
    'sheep' : ['10F58950', '70F26AA2', '802E71A2', 'EBEEAC00'],
    'fish' : ['509667A2', '0DE3AC00'],
    'avocado': ['E0A172A2', 'F08D73A2'],
    'banana': ['40AE69A2', 'A0C464A2'],
    'lemon': ['00326CA2', '80F374A2', '53E5AC00', '07E4AC00'],
    'leaf': ['701376A2','E5BDAC00'],
    'strawberry': ['904069A2', '43AAAC00', '2802AD00'],
    'blue_ball' : ['A05473A2'],
    'green_ball': ['408D6CA2'],
    'blue_car': ['80CF68A2'],
    'yellow_sun': ['30FF62A2'],
    'purple_flower': ['B00D79A2'],
    'carrot': ['A04A65A2'],
    'mouse': ['40CE74A2'],
    'horse': ['70F675A2','B0066AA2'],
    'bird': ['307379A2', '206464A2'],
    'cat': ['C04274A2', '006473A2', 'BDEDAC00'],
    'big_tomato': ['D0C566A2', 'B07A8D50', '2F91AC00'],
    'big_orange': ['D0FF72A2', 'F01469A2', 'F721AD00'],
    'little_orange': ['400770A2', '80F969A2'],
    'little_tomato': ['405B79A2', '100073A2'],
    'orange': ['F721AD00', 'E8C3AC00'],
    'tomato': ['2F91AC00', '6D62AC00'],
    'duck': ['200674A2', '401A6DA2', 'DEE3AC00'],
    'cucumber': ['E06A68A2', '807263A2', '4736AD00', '19A3AC00'],
    'cow': ['00F667A2', 'F06B73A2', '24B9AC00'],
}

rfid_to_prop = {}
for k, v in prop_to_rfid.items():
    for i in v:
        rfid_to_prop[i] = k