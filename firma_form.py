from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import QSettings

class FirmaAyarlariDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("TevkifatApp", "BildirimFormu")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        self.setWindowTitle('Firma Bilgileri')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form layout
        form_layout = QFormLayout()
        
        # VKN
        self.txt_vkn = QLineEdit()
        self.txt_vkn.setMaxLength(10)
        self.txt_vkn.setPlaceholderText('10 haneli vergi kimlik numarası')
        form_layout.addRow('Vergi Kimlik Numarası:', self.txt_vkn)
        
        # Unvan
        self.txt_unvan = QLineEdit()
        self.txt_unvan.setMaxLength(150)
        self.txt_unvan.setPlaceholderText('Firma unvanı')
        form_layout.addRow('Firma Unvanı:', self.txt_unvan)
        
        # Adres
        self.txt_adres = QLineEdit()
        self.txt_adres.setMaxLength(100)
        self.txt_adres.setPlaceholderText('Firma adresi (maksimum 100 karakter)')
        form_layout.addRow('Firma Adresi:', self.txt_adres)
        
        # Tahakkuk Fiş Numarası - YENİ
        self.txt_thkFisNo = QLineEdit()
        self.txt_thkFisNo.setMaxLength(20)
        self.txt_thkFisNo.setPlaceholderText('Tahakkuk Fiş Numarası (20 karakter)')
        form_layout.addRow('Tahakkuk Fiş No:', self.txt_thkFisNo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_kaydet = QPushButton('Kaydet')
        self.btn_kaydet.clicked.connect(self.kaydet)
        
        self.btn_iptal = QPushButton('İptal')
        self.btn_iptal.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_iptal)
        button_layout.addWidget(self.btn_kaydet)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Kaydedilmiş firma bilgilerini yükler"""
        if self.settings.value('firma_vkn'):
            self.txt_vkn.setText(self.settings.value('firma_vkn'))
        
        if self.settings.value('firma_unvan'):
            self.txt_unvan.setText(self.settings.value('firma_unvan'))
        
        if self.settings.value('firma_adres'):
            self.txt_adres.setText(self.settings.value('firma_adres'))
            
        if self.settings.value('firma_thkFisNo'):
            self.txt_thkFisNo.setText(self.settings.value('firma_thkFisNo'))
    
    def kaydet(self):
        """Firma bilgilerini kontrol eder ve kaydeder"""
        vkn = self.txt_vkn.text().strip()
        unvan = self.txt_unvan.text().strip()
        adres = self.txt_adres.text().strip()
        thkFisNo = self.txt_thkFisNo.text().strip()
        
        # VKN kontrolü
        if not vkn or len(vkn) != 10 or not vkn.isdigit():
            QMessageBox.warning(self, 'Hata', 'Vergi Kimlik Numarası 10 haneli rakam olmalıdır.')
            return
        
        # Unvan kontrolü
        if not unvan or len(unvan) < 2:
            QMessageBox.warning(self, 'Hata', 'Firma unvanı en az 2 karakter olmalıdır.')
            return
        
        # Adres kontrolü
        if not adres:
            QMessageBox.warning(self, 'Hata', 'Firma adresi boş olamaz.')
            return
        
        if len(adres) > 100:
            QMessageBox.warning(self, 'Hata', 'Firma adresi en fazla 100 karakter olabilir.')
            return
        
        # Tahakkuk Fiş No kontrolü
        if thkFisNo and len(thkFisNo) != 20:
            QMessageBox.warning(self, 'Hata', 'Tahakkuk Fiş Numarası 20 karakter olmalıdır.')
            return
        
        # Bilgileri kaydet
        self.settings.setValue('firma_vkn', vkn)
        self.settings.setValue('firma_unvan', unvan)
        self.settings.setValue('firma_adres', adres)
        self.settings.setValue('firma_thkFisNo', thkFisNo)
        
        QMessageBox.information(self, 'Bilgi', 'Firma bilgileri başarıyla kaydedildi.')
        self.accept()