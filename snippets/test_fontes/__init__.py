from PySide2.QtWidgets import QApplication, QLabel
from PySide2.QtGui import QFont, QFontInfo

app = QApplication([])

label = QLabel('Texte en gras')
font = QFont("Latin Modern Math", 20)
font.setBold(True)  # Forcer le gras
label.setFont(font)

label.show()

label2 = QLabel('Texte pas en gras')
font2 = QFont("Latin Modern Math", 20)
# font2.setBold(True)  # Forcer le gras
label2.setFont(font2)

label2.show()


# Obtenir des informations sur la fonte utilisée
font_info = QFontInfo(label.font())

# Afficher les détails de la fonte réellement utilisée
print("Fonte demandée :", font.family())
print("Fonte utilisée :", font_info.family(), font_info.bold())


app.exec_()
