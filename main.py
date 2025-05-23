import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QAbstractItemView, QFileDialog)
from PyQt5.QtCore import QSettings, Qt
from datetime import datetime

from firma_form import FirmaAyarlariDialog
from kisi_form import KisiEklemeDialog

class TevkifatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("TevkifatApp", "BildirimFormu")
        self.tevkifat_verileri = []
        self.toplam_gayrisafi = 0.0
        self.toplam_tevkifat = 0.0
        
        self.init_ui()
        self.check_firma_bilgileri()
        
    def init_ui(self):
        self.setWindowTitle('Tevkifata Tabi Ödemeler Bildirim Formu')
        self.setGeometry(100, 100, 900, 600)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Başlık
        baslik = QLabel('TEVKİFATA TABİ ÖDEMELER BİLDİRİM FORMU')
        baslik.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        baslik.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(baslik)
        
        # Butonlar için layout
        button_layout = QHBoxLayout()
        
        # Firma bilgileri butonu
        self.btn_firma = QPushButton('Firma Bilgileri')
        self.btn_firma.clicked.connect(self.firma_bilgileri_goster)
        button_layout.addWidget(self.btn_firma)
        
        # Kişi ekleme butonu
        self.btn_ekle = QPushButton('Kişi/Firma Ekle')
        self.btn_ekle.clicked.connect(self.kisi_ekle)
        button_layout.addWidget(self.btn_ekle)
        
        # Kişi düzenleme butonu
        self.btn_duzenle = QPushButton('Düzenle')
        self.btn_duzenle.clicked.connect(self.kisi_duzenle)
        button_layout.addWidget(self.btn_duzenle)
        
        # Kişi silme butonu
        self.btn_sil = QPushButton('Sil')
        self.btn_sil.clicked.connect(self.kisi_sil)
        button_layout.addWidget(self.btn_sil)
        
        # XML oluşturma butonu
        self.btn_xml = QPushButton('XML Oluştur')
        self.btn_xml.clicked.connect(self.xml_olustur)
        button_layout.addWidget(self.btn_xml)
        
        main_layout.addLayout(button_layout)
        
        # Tablo oluşturma
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Kimlik Türü', 'VKN/TCKN', 'Unvan/Ad Soyad', 
            'Vergi Dairesi', 'Tevkifat Matrahı', 'Tevkifat Oranı', 'Tevkifat Tutarı'
        ])
        
        # Tablo ayarları
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)
        
        # Özet bilgi alanı
        info_layout = QHBoxLayout()
        
        self.lbl_kayit_sayisi = QLabel('Kayıt Sayısı: 0')
        info_layout.addWidget(self.lbl_kayit_sayisi)
        
        self.lbl_toplam_matrah = QLabel('Toplam Gayrisafi Tutar: 0.00 TL')
        info_layout.addWidget(self.lbl_toplam_matrah)
        
        self.lbl_toplam_tevkifat = QLabel('Toplam Tevkifat Tutarı: 0.00 TL')
        info_layout.addWidget(self.lbl_toplam_tevkifat)
        
        main_layout.addLayout(info_layout)
    
    def check_firma_bilgileri(self):
        """Firma bilgilerinin girilip girilmediğini kontrol eder"""
        if not self.settings.value('firma_vkn') or not self.settings.value('firma_unvan'):
            QMessageBox.information(self, 'Bilgilendirme', 
                                    'Lütfen önce firma bilgilerini giriniz.')
            self.firma_bilgileri_goster()
    
    def firma_bilgileri_goster(self):
        """Firma bilgileri formunu açar"""
        dialog = FirmaAyarlariDialog(self)
        if dialog.exec_():
            vkn = self.settings.value('firma_vkn')
            unvan = self.settings.value('firma_unvan')
            QMessageBox.information(self, 'Bilgi', f'Firma bilgileri kaydedildi: {unvan} (VKN: {vkn})')
    
    def kisi_ekle(self):
        """Yeni kişi/firma ekleme formunu açar"""
        dialog = KisiEklemeDialog(self)
        if dialog.exec_():
            veri = dialog.get_data()
            self.tevkifat_verileri.append(veri)
            
            # Toplamları güncelle
            self.toplam_gayrisafi += veri['tevkifat_matrahi']
            self.toplam_tevkifat += veri['tevkifat_tutari']
            
            # Tabloyu güncelle
            self.update_table()
            self.update_summary()
    
    def kisi_duzenle(self):
        """Seçili kişi/firma bilgilerini düzenler"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlemek istediğiniz kaydı seçin.')
            return
        
        dialog = KisiEklemeDialog(self, self.tevkifat_verileri[selected_row])
        if dialog.exec_():
            # Eski değerleri toplamlardan çıkar
            self.toplam_gayrisafi -= self.tevkifat_verileri[selected_row]['tevkifat_matrahi']
            self.toplam_tevkifat -= self.tevkifat_verileri[selected_row]['tevkifat_tutari']
            
            # Yeni verileri al
            veri = dialog.get_data()
            self.tevkifat_verileri[selected_row] = veri
            
            # Yeni değerleri toplamlaraa ekle
            self.toplam_gayrisafi += veri['tevkifat_matrahi']
            self.toplam_tevkifat += veri['tevkifat_tutari']
            
            # Tabloyu güncelle
            self.update_table()
            self.update_summary()
    
    def kisi_sil(self):
        """Seçili kişi/firma kaydını siler"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silmek istediğiniz kaydı seçin.')
            return
        
        reply = QMessageBox.question(self, 'Onay', 'Seçili kaydı silmek istediğinizden emin misiniz?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Silinecek kaydın değerlerini toplamlardan çıkar
            self.toplam_gayrisafi -= self.tevkifat_verileri[selected_row]['tevkifat_matrahi']
            self.toplam_tevkifat -= self.tevkifat_verileri[selected_row]['tevkifat_tutari']
            
            # Kaydı listeden çıkar
            del self.tevkifat_verileri[selected_row]
            
            # Tabloyu güncelle
            self.update_table()
            self.update_summary()
    
    def update_table(self):
        """Tabloyu güncel verilerle doldurur"""
        self.table.setRowCount(0)  # Tabloyu temizle
        
        for row, veri in enumerate(self.tevkifat_verileri):
            self.table.insertRow(row)
            
            # Verileri tabloya ekle
            self.table.setItem(row, 0, QTableWidgetItem(veri['kimlik_turu']))
            self.table.setItem(row, 1, QTableWidgetItem(veri['kimlik_no']))
            self.table.setItem(row, 2, QTableWidgetItem(veri['unvan_ad_soyad']))
            self.table.setItem(row, 3, QTableWidgetItem(veri['vergi_dairesi']))
            
            # Sayısal değerleri tabloya formatlı şekilde ekle
            self.table.setItem(row, 4, QTableWidgetItem(f"{veri['tevkifat_matrahi']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{veri['tevkifat_orani']:.3f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{veri['tevkifat_tutari']:.2f}"))
    
    def update_summary(self):
        """Özet bilgileri günceller"""
        self.lbl_kayit_sayisi.setText(f'Kayıt Sayısı: {len(self.tevkifat_verileri)}')
        self.lbl_toplam_matrah.setText(f'Toplam Gayrisafi Tutar: {self.toplam_gayrisafi:.2f} TL')
        self.lbl_toplam_tevkifat.setText(f'Toplam Tevkifat Tutarı: {self.toplam_tevkifat:.2f} TL')
    
    def xml_olustur(self):
        """XML dosyası oluşturur"""
        if not self.tevkifat_verileri:
            QMessageBox.warning(self, 'Uyarı', 'XML oluşturmak için en az bir kayıt eklemelisiniz.')
            return
        
        if not self.settings.value('firma_vkn') or not self.settings.value('firma_unvan'):
            QMessageBox.warning(self, 'Uyarı', 'Firma bilgileri eksik. Lütfen önce firma bilgilerini giriniz.')
            self.firma_bilgileri_goster()
            return
        
        # Dönem bilgisi iste
        ay = datetime.now().month
        yil = datetime.now().year

        if ay == 1:
            bir_onceki_ay = 12
        
        else:
            bir_onceki_ay = ay - 1
        

        donem = f"{yil}{bir_onceki_ay:02d}-{yil}{bir_onceki_ay:02d}"  # Örnek: 202501-202501
        
        # XML oluştur ve kaydet
        dosya_adi = QFileDialog.getSaveFileName(self, 'XML Dosyasını Kaydet', 
                                               f'tevkifat_{donem.replace("-", "_")}.xml', 
                                               'XML Dosyaları (*.xml)')
        
        if dosya_adi[0]:
            try:
                self.xml_kaydet(dosya_adi[0], donem)
                QMessageBox.information(self, 'Başarılı', 'XML dosyası başarıyla oluşturuldu.')
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'XML dosyası oluşturulurken hata oluştu: {str(e)}')
    
    def xml_kaydet(self, dosya_yolu, donem):
        """XML içeriğini oluşturur ve dosyaya kaydeder"""
        import xml.dom.minidom as minidom
        
        # XML belgesi oluştur
        doc = minidom.getDOMImplementation().createDocument(None, "vimveritransferi", None)
        root = doc.documentElement
        
        # XML şema tanımları
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.setAttribute("xsi:noNamespaceSchemaLocation", "ahs_tevkifata_tabi_olanlar_v2.xsd")
        
        # Protokol bölümü
        protokol = doc.createElement("protokol")
        root.appendChild(protokol)
        
        # Genel protokol bilgileri
        genel = doc.createElement("genel")
        genel.setAttribute("kuruluskodu", "330")
        protokol.appendChild(genel)
        
        vkn = doc.createElement("vkn")
        vkn_text = doc.createTextNode(self.settings.value('firma_vkn'))
        vkn.appendChild(vkn_text)
        genel.appendChild(vkn)
        
        unvan = doc.createElement("unvan")
        unvan_text = doc.createTextNode(self.settings.value('firma_unvan'))
        unvan.appendChild(unvan_text)
        genel.appendChild(unvan)
        
        adres = doc.createElement("adres")
        adres_text = doc.createTextNode(self.settings.value('firma_adres'))
        adres.appendChild(adres_text)
        genel.appendChild(adres)
        
        # Tahakkuk Fiş Numarası - Yeni eklenen alan
        thkFisNo = doc.createElement("thkFisNo")
        thkFisNo_text = doc.createTextNode(self.settings.value('firma_thkFisNo', ''))
        thkFisNo.appendChild(thkFisNo_text)
        genel.appendChild(thkFisNo)
        
        # Özel protokol bilgileri
        ozel = doc.createElement("ozel")
        protokol.appendChild(ozel)
        
        bilgidonem = doc.createElement("bilgidonem")
        bilgidonem_text = doc.createTextNode(donem)
        bilgidonem.appendChild(bilgidonem_text)
        ozel.appendChild(bilgidonem)
        
        bilgiTarihi = doc.createElement("bilgiTarihi")
        bilgiTarihi_text = doc.createTextNode(datetime.now().strftime("%Y%m%d"))
        bilgiTarihi.appendChild(bilgiTarihi_text)
        ozel.appendChild(bilgiTarihi)
        
        dosyano = doc.createElement("dosyano")
        dosyano_text = doc.createTextNode("001")
        dosyano.appendChild(dosyano_text)
        ozel.appendChild(dosyano)
        
        tutar = doc.createElement("tutar")
        tutar_text = doc.createTextNode(f"{self.toplam_gayrisafi:.2f}".replace(",", "."))
        tutar.appendChild(tutar_text)
        ozel.appendChild(tutar)
        
        vergitutari = doc.createElement("vergitutari")
        vergitutari_text = doc.createTextNode(f"{self.toplam_tevkifat:.2f}".replace(",", "."))
        vergitutari.appendChild(vergitutari_text)
        ozel.appendChild(vergitutari)
        
        kayitSayisi = doc.createElement("kayitSayisi")
        kayitSayisi_text = doc.createTextNode(str(len(self.tevkifat_verileri)))
        kayitSayisi.appendChild(kayitSayisi_text)
        ozel.appendChild(kayitSayisi)
        
        # İşlemler bölümü
        islemler = doc.createElement("islemler")
        root.appendChild(islemler)
        
        # Dönem ayı (YYYYAA)
        donem_ay = donem.split("-")[0]
        
        # Her bir kayıt için işlem bilgisi ekle
        for veri in self.tevkifat_verileri:
            islem = doc.createElement("islem")
            islemler.appendChild(islem)
            
            # Kimlik bilgileri - Yeni şemaya göre güncellendi
            kimlikBilgileri = doc.createElement("kimlikBilgileri")
            islem.appendChild(kimlikBilgileri)
            
            # GercekTuzelKisi yapısı - Yeni eklendi
            gercekTuzelKisi = doc.createElement("gercekTuzelKisi")
            kimlikBilgileri.appendChild(gercekTuzelKisi)
            
            if veri['kimlik_turu'] == 'Tüzel Kişi':
                vkn_element = doc.createElement("vkn")
                vkn_text = doc.createTextNode(veri['kimlik_no'])
                vkn_element.appendChild(vkn_text)
                gercekTuzelKisi.appendChild(vkn_element)
                
                unvan_element = doc.createElement("unvan")
                unvan_text = doc.createTextNode(veri['unvan_ad_soyad'])
                unvan_element.appendChild(unvan_text)
                gercekTuzelKisi.appendChild(unvan_element)
            else:  # Gerçek Kişi
                tckn = doc.createElement("tckn")
                tckn_text = doc.createTextNode(veri['kimlik_no'])
                tckn.appendChild(tckn_text)
                gercekTuzelKisi.appendChild(tckn)
                
                # Ad-Soyad'ı bölerek Ad ve Soyad olarak ekleyelim
                ad_soyad = veri['unvan_ad_soyad']
                if " " in ad_soyad:
                    parts = ad_soyad.split()
                    ad = " ".join(parts[:-1])  # Son eleman dışındaki her şey ad
                    soyad = parts[-1]  # Son eleman soyad
                else:
                    # Eğer boşluk yoksa, tamamını ad olarak kabul et
                    ad = ad_soyad
                    soyad = ""
                
                ad_element = doc.createElement("ad")
                ad_text = doc.createTextNode(ad)
                ad_element.appendChild(ad_text)
                gercekTuzelKisi.appendChild(ad_element)
                
                soyad_element = doc.createElement("soyad")
                soyad_text = doc.createTextNode(soyad)
                soyad_element.appendChild(soyad_text)
                gercekTuzelKisi.appendChild(soyad_element)
            
            # Adres alanı (opsiyonel) - Kişi adresini eklemiyoruz
            
            # Vergi dairesi
            vergiDairesiAdi = doc.createElement("vergiDairesiAdi")
            vergiDairesiAdi_text = doc.createTextNode(veri['vergi_dairesi'])
            vergiDairesiAdi.appendChild(vergiDairesiAdi_text)
            kimlikBilgileri.appendChild(vergiDairesiAdi)
            
            # İşlem bilgisi
            islemBilgisi = doc.createElement("islemBilgisi")
            islem.appendChild(islemBilgisi)
            
            # TurKodu - Yeni eklendi
            turKodu = doc.createElement("turKodu")
            turKodu_text = doc.createTextNode(veri.get('tur_kodu', '153'))  # Varsayılan olarak 153 kullanılıyor
            turKodu.appendChild(turKodu_text)
            islemBilgisi.appendChild(turKodu)
            
            kesintiAyi = doc.createElement("kesintiAyi")
            kesintiAyi_text = doc.createTextNode(donem_ay)
            kesintiAyi.appendChild(kesintiAyi_text)
            islemBilgisi.appendChild(kesintiAyi)
            
            tutarbilgisi = doc.createElement("tutarbilgisi")
            islemBilgisi.appendChild(tutarbilgisi)
            
            tevkifatMatrahi = doc.createElement("tevkifatMatrahi")
            tevkifatMatrahi_text = doc.createTextNode(f"{veri['tevkifat_matrahi']:.2f}".replace(",", "."))
            tevkifatMatrahi.appendChild(tevkifatMatrahi_text)
            tutarbilgisi.appendChild(tevkifatMatrahi)
            
            kdvHaricSatisBedeli = doc.createElement("kdvHaricSatisBedeli")
            kdvHaricSatisBedeli_text = doc.createTextNode(f"{veri['tevkifat_matrahi']:.2f}".replace(",", "."))
            kdvHaricSatisBedeli.appendChild(kdvHaricSatisBedeli_text)
            tutarbilgisi.appendChild(kdvHaricSatisBedeli)
            
            # Diğer ödemeler tutarı (opsiyonel)
            if 'diger_odemeler_tutar' in veri and veri['diger_odemeler_tutar'] > 0:
                digerOdemelerTutar = doc.createElement("digerOdemelerTutar")
                digerOdemelerTutar_text = doc.createTextNode(f"{veri['diger_odemeler_tutar']:.2f}".replace(",", "."))
                digerOdemelerTutar.appendChild(digerOdemelerTutar_text)
                tutarbilgisi.appendChild(digerOdemelerTutar)
            
            tevkifatOrani = doc.createElement("tevkifatOrani")
            tevkifatOrani_text = doc.createTextNode(f"{veri['tevkifat_orani']:.3f}".replace(",", "."))
            tevkifatOrani.appendChild(tevkifatOrani_text)
            islemBilgisi.appendChild(tevkifatOrani)
            
            tevkifEdilenTutar = doc.createElement("tevkifEdilenTutar")
            tevkifEdilenTutar_text = doc.createTextNode(f"{veri['tevkifat_tutari']:.2f}".replace(",", "."))
            tevkifEdilenTutar.appendChild(tevkifEdilenTutar_text)
            islemBilgisi.appendChild(tevkifEdilenTutar)
        
        # XML içeriği
        xml_string = doc.toprettyxml(indent="  ", encoding="utf-8")
        
        # UTF-8 with BOM olarak kaydet
        with open(dosya_yolu, 'wb') as f:
            # BOM ekle
            f.write(b'\xef\xbb\xbf')
            # XML içeriğini yaz
            f.write(xml_string)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TevkifatApp()
    window.show()
    sys.exit(app.exec_())