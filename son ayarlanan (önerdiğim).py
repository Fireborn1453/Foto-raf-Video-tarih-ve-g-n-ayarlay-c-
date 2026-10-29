from datetime import datetime
import os
import random
import shutil
import subprocess
import sys

# 1. BAŞLANGIÇTA KÜTÜPHANELERİ GÜNCELLE / KONTROL ET
print('Sistem ve kütüphaneler kontrol ediliyor, lütfen bekleyin...')
try:
  subprocess.check_call(
      [sys.executable, '-m', 'pip', 'install', '--upgrade', 'Pillow'],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
  )
except Exception:
  pass

from PIL import Image, UnidentifiedImageError

# Desteklenen resim, genişletilmiş video ve tüm ana marka RAW uzantıları
IMAGE_EXTENSIONS = (
    '.jpg',
    '.jpeg',
    '.png',
    '.heic',
    '.webp',
    '.mp4',
    '.MP4',
    '.mov',
    '.MOV',
    '.avi',
    '.mkv',  # Genişletilmiş video formatları
    '.cr3',
    '.CR3',
    '.hif',
    '.HIF',
    '.arw',
    '.ARW',  # Sony
    '.nef',
    '.NEF',  # Nikon
    '.raf',
    '.RAF',  # Fujifilm
    '.srf',
    '.sr2',
    '.nrw',
)

# Tespit edilip TXT'ye yazılacak arşiv uzantıları
ARCHIVE_EXTENSIONS = (
    '.rar',
    '.zip',
    '.7z',
    '.tar',
    '.gz',
    '.RAR',
    '.ZIP',
    '.7Z',
)


def get_image_date(file_path):
  """Dosyanın EXIF çekim tarihini almaya çalışır.

  Bulamazsa veya RAW/Video formatlarındaysa dosya tarihini döner.
  """
  if file_path.lower().endswith(
      (
          '.cr3',
          '.arw',
          '.nef',
          '.raf',
          '.srf',
          '.sr2',
          '.nrw',
          '.mp4',
          '.mov',
          '.avi',
          '.mkv',
      )
  ):
    try:
      timestamp = os.path.getmtime(file_path)
      return datetime.fromtimestamp(timestamp)
    except Exception:
      pass

  try:
    with Image.open(file_path) as img:
      exif_data = img._getexif()
      if exif_data:
        for tag_id, value in exif_data.items():
          if tag_id == 36867:  # DateTimeOriginal
            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
  except (AttributeError, KeyError, IndexError, UnidentifiedImageError, IOError):
    pass

  try:
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)
  except Exception:
    return None


def organize_photos(source_dir, target_dir, copy_mode):
  print(
      f'Arşivleme işlemi başlatıldı... (Mod:'
      f" {'KOPYALA (Güvenli)' if copy_mode else 'TAŞI (Orijinali silinir)'})\n"
  )

  if not os.path.exists(source_dir):
    print(f'Hata: Klasör bulunamadı: {source_dir}')
    return

  if not os.path.exists(target_dir):
    os.makedirs(target_dir)

  processed_count = 0
  skipped_count = 0
  archive_list = []

  script_name = os.path.basename(sys.argv[0])

  for root, _, files in os.walk(source_dir):
    for file in files:
      if file == script_name:
        continue

      file_path = os.path.join(root, file)

      # Hedef klasörün (`_Duzenli_Arsiv`) kendisini taramaya dahil etme
      if os.path.abspath(target_dir) in os.path.abspath(file_path):
        continue

      # 1. Arşiv dosyalarını (rar, zip vb.) yakala ve rapora ekle
      if file.lower().endswith(ARCHIVE_EXTENSIONS):
        archive_list.append(file_path)
        continue

      # 2. Resim ve Video dosyalarını işle
      if file.lower().endswith(IMAGE_EXTENSIONS):
        file_date = get_image_date(file_path)

        if not file_date:
          print(f'Emin olunamadı / Atlandı: {file}')
          skipped_count += 1
          continue

        year_folder = file_date.strftime('%Y')
        month_day_folder = file_date.strftime('%m-%d')

        dest_sub_dir = os.path.join(target_dir, year_folder, month_day_folder)
        os.makedirs(dest_sub_dir, exist_ok=True)

        dest_file_path = os.path.join(dest_sub_dir, file)

        # İsim çakışması kontrolü ve rastgele sayı ekleme
        base, ext = os.path.splitext(file)
        is_skipped = False

        while os.path.exists(dest_file_path):
          try:
            if os.path.getsize(file_path) == os.path.getsize(dest_file_path):
              print(f'Aynı dosya mevcut, dokunulmadı: {file}')
              skipped_count += 1
              is_skipped = True
              break
          except Exception:
            pass

          rnd_num = random.randint(1000, 9999)
          dest_file_path = os.path.join(dest_sub_dir, f'{base}_{rnd_num}{ext}')

        if is_skipped:
          continue

        try:
          if copy_mode:
            shutil.copy2(file_path, dest_file_path)
            print(f'Kopyalandı: {file} -> {year_folder}/{month_day_folder}/')
          else:
            shutil.move(file_path, dest_file_path)
            print(f'Taşındı: {file} -> {year_folder}/{month_day_folder}/')
          processed_count += 1
        except Exception as e:
          print(f'Hata ({file}): {e}')
          skipped_count += 1

  # Bulunan arşivleri hedef klasörün içine TXT olarak kaydet
  if archive_list:
    txt_report_path = os.path.join(target_dir, '_Bulunan_Arsivler_Raporu.txt')
    try:
      with open(txt_report_path, 'w', encoding='utf-8') as f:
        f.write(
            '--- TARAMA SIRASINDA BULUNAN ZIP / RAR / ARŞİV DOSYALARI ---\n\n'
        )
        for arc in archive_list:
          f.write(f'{arc}\n')
      print(
          f'\n[!] {len(archive_list)} adet arşiv dosyası bulundu ve'
          ' "_Bulunan_Arsivler_Raporu.txt" dosyasına kaydedildi.'
      )
    except Exception:
      pass

  print('\n' + '=' * 40)
  print(' İŞLEM BAŞARIYLA TAMAMLANDI!')
  print('=' * 40)
  print(f' İşlem Yapılan Dosya Sayısı     : {processed_count}')
  print(f' Atlanan / Dokunulmayan Dosya   : {skipped_count}')
  print(f' Tespit Edilen Arşiv Dosyası    : {len(archive_list)}')
  print(f' Hedef Arşiv Klasörü          : {target_dir}')
  print('=' * 40)


if __name__ == '__main__':
  CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
  TARGET_DIRECTORY = os.path.join(CURRENT_DIR, '_Duzenli_Arsiv')

  print('=' * 50)
  print(' FOTOĞRAF VE MEDYA ARŞİVLEME ARACI')
  print('=' * 50)
  print('1 -> Kopyala (Orijinalleri yerinde bırakır - GÜVENLİ)')
  print('2 -> Taşı (Orijinalleri siler, hedefe taşır)')
  print('=' * 50)

  secim = input(
      'Lütfen bir mod seçin (1 veya 2, varsayılan 1): '
  ).strip()

  if secim == '2':
    copy_mode = False
    print('\n--> TAŞIMA MODU seçildi. Dosyalar hedefe taşınacak.\n')
  else:
    copy_mode = True
    print(
        '\n--> KOPYALAMA MODU seçildi. Orijinallerine dokunulmayacak'
        ' (Güvenli).\n'
    )

  organize_photos(CURRENT_DIR, TARGET_DIRECTORY, copy_mode=copy_mode)

  print('\nKapatmak için klavyeden herhangi bir tuşa basabilirsiniz...')
  os.system('pause >nul')