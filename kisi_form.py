from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFormLayout, QRadioButton,
                             QGroupBox, QWidget, QDoubleSpinBox, QComboBox)
from PyQt5.QtCore import Qt

class KisiEklemeDialog(QDialog):
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.edit_data = edit_data  # Düzenleme modu için veriler
        self.init_ui()
        
        if self.edit_data:
            self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('Kişi/Firma Ekle')
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Kimlik tipi seçimi
        kimlik_grup = QGroupBox("Kimlik Türü")
        kimlik_layout = QHBoxLayout()
        
        self.rb_tuzel = QRadioButton("Tüzel Kişi")
        self.rb_tuzel.setChecked(True)
        self.rb_tuzel.toggled.connect(self.kimlik_turu_degisti)
        
        self.rb_gercek = QRadioButton("Gerçek Kişi")
        
        kimlik_layout.addWidget(self.rb_tuzel)
        kimlik_layout.addWidget(self.rb_gercek)
        kimlik_grup.setLayout(kimlik_layout)
        
        layout.addWidget(kimlik_grup)
        
        # Tüzel kişi formu
        self.tuzel_widget = QWidget()
        tuzel_form = QFormLayout()
        self.tuzel_widget.setLayout(tuzel_form)
        
        self.txt_vkn = QLineEdit()
        self.txt_vkn.setMaxLength(10)
        self.txt_vkn.setPlaceholderText('10 haneli vergi kimlik numarası')
        tuzel_form.addRow('Vergi Kimlik Numarası:', self.txt_vkn)
        
        self.txt_unvan = QLineEdit()
        self.txt_unvan.setMaxLength(150)
        tuzel_form.addRow('Unvan:', self.txt_unvan)
        
        layout.addWidget(self.tuzel_widget)
        
        # Gerçek kişi formu
        self.gercek_widget = QWidget()
        gercek_form = QFormLayout()
        self.gercek_widget.setLayout(gercek_form)
        
        self.txt_tckn = QLineEdit()
        self.txt_tckn.setMaxLength(11)
        self.txt_tckn.setPlaceholderText('11 haneli TC kimlik numarası')
        gercek_form.addRow('TC Kimlik Numarası:', self.txt_tckn)
        
        self.txt_ad_soyad = QLineEdit()
        self.txt_ad_soyad.setMaxLength(100)
        gercek_form.addRow('Ad Soyad:', self.txt_ad_soyad)
        
        layout.addWidget(self.gercek_widget)
        self.gercek_widget.setVisible(False)
        
        # Ortak form alanları
        common_form = QFormLayout()
        
        self.txt_vergi_dairesi = QLineEdit()
        self.txt_vergi_dairesi.setMaxLength(50)
        common_form.addRow('Vergi Dairesi:', self.txt_vergi_dairesi)
        
        # Tür Kodu seçimi - YENİ
        self.cmb_tur_kodu = QComboBox()
        self.cmb_tur_kodu.addItem("153", "153")
        self.cmb_tur_kodu.addItem("154", "154")
        self.cmb_tur_kodu.addItem("155", "155")
        common_form.addRow('Tür Kodu:', self.cmb_tur_kodu)
        
        # Tevkifat bilgileri
        self.spn_tevkifat_matrahi = QDoubleSpinBox()
        self.spn_tevkifat_matrahi.setRange(0.01, 99999999.99)
        self.spn_tevkifat_matrahi.setDecimals(2)
        self.spn_tevkifat_matrahi.setSingleStep(100)
        self.spn_tevkifat_matrahi.valueChanged.connect(self.calculate_tevkifat)
        common_form.addRow('Tevkifat Matrahı (TL):', self.spn_tevkifat_matrahi)
        
        # KDV Hariç Satış Bedeli - Otomatik olarak tevkifat matrahı ile aynı değer kullanılıyor
        
        # Diğer Ödemeler Tutarı - YENİ
        self.spn_diger_odemeler = QDoubleSpinBox()
        self.spn_diger_odemeler.setRange(0.00, 99999999.99)
        self.spn_diger_odemeler.setDecimals(2)
        self.spn_diger_odemeler.setSingleStep(100)
        common_form.addRow('Diğer Ödemeler Tutarı (TL):', self.spn_diger_odemeler)
        
        self.spn_tevkifat_orani = QDoubleSpinBox()
        self.spn_tevkifat_orani.setRange(0.001, 0.999)
        self.spn_tevkifat_orani.setDecimals(3)
        self.spn_tevkifat_orani.setSingleStep(0.001)
        self.spn_tevkifat_orani.setValue(0.010)  # Varsayılan %1
        self.spn_tevkifat_orani.valueChanged.connect(self.calculate_tevkifat)
        common_form.addRow('Tevkifat Oranı:', self.spn_tevkifat_orani)
        
        self.spn_tevkifat_tutari = QDoubleSpinBox()
        self.spn_tevkifat_tutari.setRange(0.01, 999999.99)
        self.spn_tevkifat_tutari.setDecimals(2)
        self.spn_tevkifat_tutari.setReadOnly(True)
        common_form.addRow('Tevkifat Tutarı (TL):', self.spn_tevkifat_tutari)
        
        layout.addLayout(common_form)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.btn_iptal = QPushButton('İptal')
        self.btn_iptal.clicked.connect(self.reject)
        
        self.btn_kaydet = QPushButton('Kaydet')
        self.btn_kaydet.clicked.connect(self.kaydet)
        
        button_layout.addWidget(self.btn_iptal)
        button_layout.addWidget(self.btn_kaydet)
        
        layout.addLayout(button_layout)
        
        # İlk hesaplama
        self.calculate_tevkifat()
    
    def kimlik_turu_degisti(self, checked):
        """Kimlik türü değiştiğinde görünümü günceller"""
        if checked:  # Tüzel kişi seçildi
            self.tuzel_widget.setVisible(True)
            self.gercek_widget.setVisible(False)
        else:  # Gerçek kişi seçildi
            self.tuzel_widget.setVisible(False)
            self.gercek_widget.setVisible(True)
    
    def calculate_tevkifat(self):
        """Tevkifat tutarını hesaplar"""
        matrahi = self.spn_tevkifat_matrahi.value()
        oran = self.spn_tevkifat_orani.value()
        
        tevkifat_tutari = matrahi * oran
        self.spn_tevkifat_tutari.setValue(tevkifat_tutari)
    
    def load_data(self):
        """Düzenleme için verileri forma yükler"""
        if self.edit_data['kimlik_turu'] == 'Tüzel Kişi':
            self.rb_tuzel.setChecked(True)
            self.txt_vkn.setText(self.edit_data['kimlik_no'])
            self.txt_unvan.setText(self.edit_data['unvan_ad_soyad'])
        else:
            self.rb_gercek.setChecked(True)
            self.txt_tckn.setText(self.edit_data['kimlik_no'])
            self.txt_ad_soyad.setText(self.edit_data['unvan_ad_soyad'])
        
        self.txt_vergi_dairesi.setText(self.edit_data['vergi_dairesi'])
        self.spn_tevkifat_matrahi.setValue(self.edit_data['tevkifat_matrahi'])
        self.spn_tevkifat_orani.setValue(self.edit_data['tevkifat_orani'])
        
        # Yeni alanların verileri - varsa yükle
        if 'tur_kodu' in self.edit_data:
            index = self.cmb_tur_kodu.findData(self.edit_data['tur_kodu'])
            if index >= 0:
                self.cmb_tur_kodu.setCurrentIndex(index)
        
        if 'diger_odemeler_tutar' in self.edit_data:
            self.spn_diger_odemeler.setValue(self.edit_data['diger_odemeler_tutar'])
    
    def get_data(self):
        """Form verilerini sözlük olarak döndürür"""
        data = {}
        
        if self.rb_tuzel.isChecked():
            data['kimlik_turu'] = 'Tüzel Kişi'
            data['kimlik_no'] = self.txt_vkn.text()
            data['unvan_ad_soyad'] = self.txt_unvan.text()
        else:
            data['kimlik_turu'] = 'Gerçek Kişi'
            data['kimlik_no'] = self.txt_tckn.text()
            data['unvan_ad_soyad'] = self.txt_ad_soyad.text()
        
        data['vergi_dairesi'] = self.txt_vergi_dairesi.text()
        data['tevkifat_matrahi'] = self.spn_tevkifat_matrahi.value()
        data['tevkifat_orani'] = self.spn_tevkifat_orani.value()
        data['tevkifat_tutari'] = self.spn_tevkifat_tutari.value()
        
        # Yeni alanlar
        data['tur_kodu'] = self.cmb_tur_kodu.currentData()
        data['diger_odemeler_tutar'] = self.spn_diger_odemeler.value()
        
        return data
    
    def kaydet(self):
        """Form verilerini kontrol eder ve kaydeder"""
        if self.rb_tuzel.isChecked():
            # Tüzel kişi kontrolü
            vkn = self.txt_vkn.text().strip()
            unvan = self.txt_unvan.text().strip()
            
            if not vkn or len(vkn) != 10 or not vkn.isdigit():
                QMessageBox.warning(self, 'Hata', 'Vergi Kimlik Numarası 10 haneli rakam olmalıdır.')
                return
            
            if not unvan or len(unvan) < 2:
                QMessageBox.warning(self, 'Hata', 'Unvan en az 2 karakter olmalıdır.')
                return
        else:
            # Gerçek kişi kontrolü
            tckn = self.txt_tckn.text().strip()
            ad_soyad = self.txt_ad_soyad.text().strip()
            
            if not tckn or len(tckn) != 11 or not tckn.isdigit():
                QMessageBox.warning(self, 'Hata', 'TC Kimlik Numarası 11 haneli rakam olmalıdır.')
                return
            
            if not ad_soyad or len(ad_soyad) < 3:
                QMessageBox.warning(self, 'Hata', 'Ad Soyad en az 3 karakter olmalıdır.')
                return
                
        # Vergi dairesi kontrolü
        vergi_dairesi = self.txt_vergi_dairesi.text().strip()
        if not vergi_dairesi:
            QMessageBox.warning(self, 'Hata', 'Vergi Dairesi alanı boş olamaz.')
            return
        
        # Tevkifat matrahı kontrolü
        if self.spn_tevkifat_matrahi.value() <= 0:
            QMessageBox.warning(self, 'Hata', 'Tevkifat Matrahı 0\'dan büyük olmalıdır.')
            return
        
        # Tevkifat oranı kontrolü
        if self.spn_tevkifat_orani.value() <= 0:
            QMessageBox.warning(self, 'Hata', 'Tevkifat Oranı 0\'dan büyük olmalıdır.')
            return
        
        # Kaydet
        self.accept()