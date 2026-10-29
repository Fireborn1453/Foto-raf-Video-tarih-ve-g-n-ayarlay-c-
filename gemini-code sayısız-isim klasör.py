import os
import shutil

def sarkilari_klasorle():
    hedef_dizin = os.getcwd()
    print(f"Taranan dizin: {hedef_dizin}\n")

    dosyalar = os.listdir(hedef_dizin)
    tasinan_sayisi = 0
    
    for dosya in dosyalar:
        if dosya.lower().endswith('.mp3'):
            sanatci = ""
            
            # Tire (-) işareti var mı kontrol et
            if '-' in dosya:
                parcalar = dosya.split('-', 1)
                sanatci = parcalar[0].strip()
            else:
                # Tire olmayanlar için ortak bir klasör belirle
                sanatci = "Diger_Sarkilar"
                
            # Windows/Linux dosya adlarında sorun çıkarabilecek yasaklı karakterleri temizle
            for karakter in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                sanatci = sanatci.replace(karakter, '')
            sanatci = sanatci.strip()
            
            if sanatci:
                sanatci_klasoru = os.path.join(hedef_dizin, sanatci)
                
                if not os.path.exists(sanatci_klasoru):
                    os.makedirs(sanatci_klasoru)
                    
                eski_yol = os.path.join(hedef_dizin, dosya)
                yeni_yol = os.path.join(sanatci_klasoru, dosya)
                
                shutil.move(eski_yol, yeni_yol)
                print(f"Taşındı: {dosya} -> {sanatci}/")
                tasinan_sayisi += 1

    print(f"\nİşlem bitti! Toplam {tasinan_sayisi} şarkı klasörlerine yerleştirildi.")

if __name__ == "__main__":
    onay = input("Tüm MP3'ler sanatçı adlarına göre klasörlenecek (Tiresizler 'Diger_Sarkilar' klasörüne gidecek). Onaylıyor musun? (e/h): ")
    if onay.lower() == 'e':
        sarkilari_klasorle()
    else:
        print("İşlem iptal edildi.")