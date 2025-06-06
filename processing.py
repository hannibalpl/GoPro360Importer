# processing.py
import os
import sys
import csv
import math
import datetime
import subprocess
import tempfile

plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)
sys.path.insert(0, os.path.join(plugin_dir, 'geopy'))
sys.path.insert(0, os.path.join(plugin_dir, 'geographiclib'))
sys.path.insert(0, os.path.join(plugin_dir, 'piexif'))

# Dodanie ścieżki do gopro2gpx
gopro2gpx_dir = os.path.join(plugin_dir, 'gopro2gpx')
sys.path.insert(0, gopro2gpx_dir)

from osgeo import ogr, osr
from geopy.distance import geodesic
import piexif
from PIL import Image

def log(message, log_widget=None):
    print(message)
    if log_widget:
        log_widget(message)
        
# Import gopro2gpx - bezpośredni import modułu jako skryptu
try:
    # Importujemy gopro2gpx.py jako moduł
    import importlib.util
    gopro2gpx_path = os.path.join(gopro2gpx_dir, 'gopro2gpx.py')
    
    log(f"[DEBUG] Trying to load gopro2gpx from: {gopro2gpx_path}")
    log(f"[DEBUG] File exists: {os.path.exists(gopro2gpx_path)}")
    
    if not os.path.exists(gopro2gpx_path):
        raise FileNotFoundError(f"gopro2gpx.py not found at {gopro2gpx_path}")
    
    spec = importlib.util.spec_from_file_location("gopro2gpx", gopro2gpx_path)
    gopro2gpx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gopro2gpx)
    
    # Sprawdzenie czy potrzebne biblioteki są dostępne w folderze gopro2gpx
    gopro2gpx_available = True
    log(f"[DEBUG] gopro2gpx loaded successfully")
    
except Exception as e:
    log(f"Error importing gopro2gpx: {e}")
    gopro2gpx = None
    gopro2gpx_available = False

FFMPEG_BIN = os.path.join(plugin_dir, 'ffmpeg', 'ffmpeg.exe')
FFPROBE_BIN = os.path.join(plugin_dir, 'ffmpeg', 'ffprobe.exe')
CREATE_NO_WINDOW = 0x08000000


def convert_360_to_mov(input_360_path, output_mov_path, log_widget=None):
    """Konwertuje plik .360 do .mov używając ffmpeg"""
    # Normalizacja ścieżek do Windows
    input_360_path = os.path.normpath(input_360_path)
    output_mov_path = os.path.normpath(output_mov_path)
    
    log(f"[CONVERT] Converting {input_360_path} to {output_mov_path}", log_widget)
    
    cmd = [FFMPEG_BIN, '-hide_banner', '-loglevel', 'info',
           '-i', input_360_path,
           '-c:v', 'copy',  # Kopiuj strumień video bez rekodowania
           '-c:a', 'copy',  # Kopiuj strumień audio bez rekodowania
           '-movflags', '+faststart',  # Optymalizacja dla streamingu
           output_mov_path]
    
    log(f"[FFMPEG] {' '.join(cmd)}", log_widget)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, creationflags=CREATE_NO_WINDOW)
    
    if proc.returncode != 0:
        log(f"[CONVERT][ERROR] {proc.stderr}", log_widget)
        raise RuntimeError(f"Error converting .360 to .mov: {proc.stderr}")
    
    if not os.path.isfile(output_mov_path):
        raise RuntimeError(f"Conversion failed - output file not created: {output_mov_path}")
    
    log(f"[CONVERT] Success: {output_mov_path}", log_widget)
    return output_mov_path

def extract_telemetry_from_gopro(video_path, output_csv_path, log_widget=None):
    """Wyciąga telemetrię z pliku GoPro używając gopro2gpx"""
    if not gopro2gpx_available:
        log("[TELEMETRY][ERROR] gopro2gpx module not available", log_widget)
        log(f"[TELEMETRY][ERROR] gopro2gpx_dir: {gopro2gpx_dir}", log_widget)
        log(f"[TELEMETRY][ERROR] Directory exists: {os.path.exists(gopro2gpx_dir)}", log_widget)
        if os.path.exists(gopro2gpx_dir):
            files = os.listdir(gopro2gpx_dir)
            log(f"[TELEMETRY][ERROR] Files in gopro2gpx dir: {files}", log_widget)
        raise RuntimeError("gopro2gpx module not available")
    
    # Normalizacja ścieżek
    video_path = os.path.normpath(video_path)
    output_csv_path = os.path.normpath(output_csv_path)
    
    log(f"[TELEMETRY] Extracting from: {video_path}", log_widget)
    log(f"[TELEMETRY] Output CSV: {output_csv_path}", log_widget)
    
    try:
        # Przygotowanie argumentów dla gopro2gpx - symulujemy argparse
        class Args:
            def __init__(self):
                self.verbose = 1
                self.binary = False
                self.skip = True
                self.skip_dop = True
                self.dop_limit = 2000
                self.time_shift = 0
                self.gpx = False
                self.kml = False
                self.csv = True
                self.gui = True
                self.files = [video_path]
                self.outputfile = os.path.splitext(output_csv_path)[0]
        
        args = Args()
        log(f"[TELEMETRY] Args prepared: files={args.files}, outputfile={args.outputfile}", log_widget)
        
        # Wywołanie funkcji main_core z gopro2gpx
        log("[TELEMETRY] Calling gopro2gpx.main_core", log_widget)
        gopro2gpx.main_core(args)
        log("[TELEMETRY] gopro2gpx.main_core completed", log_widget)
        
        # Sprawdzenie czy plik CSV został utworzony
        if os.path.exists(output_csv_path):
            log(f"[TELEMETRY] CSV saved: {output_csv_path}", log_widget)
            return output_csv_path
        else:
            log(f"[TELEMETRY][ERROR] CSV file was not created at: {output_csv_path}", log_widget)
            # Sprawdź czy został utworzony w innej lokalizacji
            expected_csv = args.outputfile + ".csv"
            if os.path.exists(expected_csv):
                log(f"[TELEMETRY] Found CSV at: {expected_csv}", log_widget)
                # Przenieś do oczekiwanej lokalizacji
                import shutil
                shutil.move(expected_csv, output_csv_path)
                log(f"[TELEMETRY] Moved CSV to: {output_csv_path}", log_widget)
                return output_csv_path
            raise RuntimeError("CSV file was not created")
        
    except Exception as e:
        log(f"[TELEMETRY][ERROR] {str(e)}", log_widget)
        import traceback
        log(f"[TELEMETRY][ERROR] Traceback: {traceback.format_exc()}", log_widget)
        raise RuntimeError(f"Error extracting telemetry: {str(e)}")

def get_video_metadata(video_path, log_widget=None):
    fps_cmd = [FFPROBE_BIN, '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=r_frame_rate',
               '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    proc = subprocess.run(fps_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, creationflags=CREATE_NO_WINDOW)
    if proc.returncode != 0:
        log(f"[FPS][ERROR] {proc.stderr}", log_widget)
        raise RuntimeError(f"Error fetching FPS: {proc.stderr}")
    rate = proc.stdout.strip()
    fps = float(rate) if '/' not in rate else float(rate.split('/')[0]) / float(rate.split('/')[1])
    log(f"[FPS] {fps}", log_widget)

    dur_cmd = [FFPROBE_BIN, '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    proc = subprocess.run(dur_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, creationflags=CREATE_NO_WINDOW)
    if proc.returncode != 0:
        log(f"[DUR][ERROR] {proc.stderr}", log_widget)
        raise RuntimeError(f"Error fetching duration: {proc.stderr}")
    duration = float(proc.stdout.strip())
    log(f"[DUR] {duration}s", log_widget)
    return fps, duration

def parse_csv_telemetry(csv_path, log_widget=None):
    log(f"[CSV] Loading: {csv_path}", log_widget)
    coords = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = datetime.datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
            coords.append({'timestamp': dt.timestamp(), 'datetime': dt,
                           'lat': float(row['GPS (Lat.) [deg]']),
                           'lon': float(row['GPS (Long.) [deg]'])})
    log(f"[CSV] Points: {len(coords)}", log_widget)
    return coords

def _deg_to_dmsRational(deg):
    d = int(deg); m_full = (deg-d)*60; m = int(m_full)
    sec = int((m_full-m)*60*100)
    return ((d,1),(m,1),(sec,100))

def haversine_bearing(lat1, lon1, lat2, lon2):
    phi1,phi2 = math.radians(lat1),math.radians(lat2)
    dl = math.radians(lon2-lon1)
    x = math.sin(dl)*math.cos(phi2)
    y = math.cos(phi1)*math.sin(phi2)-math.sin(phi1)*math.cos(phi2)*math.cos(dl)
    return (math.degrees(math.atan2(x,y))+360)%360

def extract_frames(video_path, telemetry_data, out_folder, distance_m, log_widget=None):
    if not telemetry_data:
        log("[FRAME] No telemetry.", log_widget)
        return []
    sampled = [telemetry_data[0]]; last = sampled[0]
    for pt in telemetry_data[1:]:
        if geodesic((last['lat'], last['lon']), (pt['lat'], pt['lon'])).meters >= distance_m:
            sampled.append(pt); last = pt
    log(f"[FRAME] Sampled {len(sampled)} points", log_widget)

    fps, duration = get_video_metadata(video_path, log_widget)
    first_ts = sampled[0]['timestamp']
    base = os.path.splitext(os.path.basename(video_path))[0]
    records = []

    for idx, pt in enumerate(sampled):
        offset = pt['timestamp'] - first_ts
        if offset > duration:
            log(f"[FRAME] Skipping {pt['datetime']} offset>duration", log_widget)
            continue
        dt = pt['datetime']; ts_str = dt.strftime('%Y-%m-%d_%H-%M-%S_%f')[:-3]
        img_name = f"{base}_{ts_str}.jpg"; img_path = os.path.join(out_folder, img_name)

        # North aligned full equirectangular frame
        cmd = [FFMPEG_BIN, '-hide_banner', '-loglevel', 'info',
               '-ss', str(offset), '-i', video_path,
               '-vf', 'v360=input=equirect:output=equirect:yaw=-90:pitch=0:roll=0',
               '-frames:v', '1', '-q:v', '2', img_path]                   
        log(f"[FFMPEG] {' '.join(cmd)}", log_widget)
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, creationflags=CREATE_NO_WINDOW)
        if proc.returncode != 0:
            log(f"[FFMPEG ERR] {proc.stderr}", log_widget)
            continue
        if not os.path.isfile(img_path):
            log(f"[FRAME] Missing {img_name}", log_widget)
            continue

        if idx < len(sampled)-1:
            nxt = sampled[idx+1]
            direction = haversine_bearing(pt['lat'], pt['lon'], nxt['lat'], nxt['lon'])
        else:
            direction = 0.0

        log(f"[EXIF] {img_name}", log_widget)
        exif = {'0th':{}, 'Exif':{}, 'GPS':{}, '1st':{}, 'thumbnail':None}
        exif_time = dt.strftime('%Y:%m:%d %H:%M:%S')
        exif['0th'][piexif.ImageIFD.DateTime] = exif_time
        exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_time
        lat, lon = pt['lat'], pt['lon']
        exif['GPS'][piexif.GPSIFD.GPSLatitudeRef] = 'N' if lat>=0 else 'S'
        exif['GPS'][piexif.GPSIFD.GPSLongitudeRef] = 'E' if lon>=0 else 'W'
        exif['GPS'][piexif.GPSIFD.GPSLatitude] = _deg_to_dmsRational(abs(lat))
        exif['GPS'][piexif.GPSIFD.GPSLongitude] = _deg_to_dmsRational(abs(lon))
        exif_path = img_path.replace(os.sep, '/')
        piexif.insert(piexif.dump(exif), exif_path)
        records.append({'lat':pt['lat'], 'lon':pt['lon'], 'timestamp':pt['timestamp'],
                        'datetime':exif_time, 'path':img_path, 'direction':direction})
    log("[FRAME] Extraction finished", log_widget)
    return records

def process_video_with_csv(video_path, telemetry_csv_path, output_folder, distance_m, log_widget=None):
    """Reszta funkcji bez zmian - tylko nazwa pozostaje"""
    import os
    import datetime
    from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY
    from qgis.core import QgsVectorFileWriter, QgsCoordinateTransformContext
    from PyQt5.QtCore import QVariant, QDate

    os.makedirs(output_folder, exist_ok=True)
    log("[START] process_video_with_csv", log_widget)

    data = parse_csv_telemetry(telemetry_csv_path, log_widget)
    records = extract_frames(video_path, data, output_folder, distance_m, log_widget)

    gpkg_path = os.path.join(output_folder, f"gopro_photos_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.gpkg")
    layer = QgsVectorLayer('Point?crs=epsg:4326', 'photos', 'memory')
    prov = layer.dataProvider()
    prov.addAttributes([
        QgsField('DATE', QVariant.Date),
        QgsField('PATH', QVariant.String),
        QgsField('DIRECTION', QVariant.Double)
    ])
    layer.updateFields()

    feats = []
    for rec in records:
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(rec['lon'], rec['lat'])))
        feat.setFields(layer.fields())

        # Konwersja datetime string -> QDate
        dt_obj = datetime.datetime.strptime(rec['datetime'], '%Y:%m:%d %H:%M:%S')
        qdate = QDate(dt_obj.year, dt_obj.month, dt_obj.day)

        # Użycie pełnej ścieżki z konwersją do formatu Windows-compatible
        win_path = os.path.normpath(rec['path'])

        feat['DATE'] = qdate
        feat['PATH'] = win_path
        feat['DIRECTION'] = rec['direction']
        feats.append(feat)

    prov.addFeatures(feats)

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = 'GPKG'
    options.fileEncoding = 'UTF-8'
    options.layerName = 'photos'

    res, err = QgsVectorFileWriter.writeAsVectorFormatV2(
        layer, gpkg_path, QgsCoordinateTransformContext(), options
    )
    if res != QgsVectorFileWriter.NoError:
        raise RuntimeError(f"Error writing GeoPackage: {err}")

    log(f"[GPKG] Saved: {gpkg_path}", log_widget)
    return gpkg_path

def process_gopro_360_video(input_360_path, output_folder, distance_m, log_widget=None):
    """Główna funkcja do przetwarzania plików .360 GoPro"""
    # Normalizacja ścieżek do Windows
    input_360_path = os.path.normpath(input_360_path)
    output_folder = os.path.normpath(output_folder)
    
    os.makedirs(output_folder, exist_ok=True)
    log("[START] process_gopro_360_video", log_widget)
    log(f"[START] Input: {input_360_path}", log_widget)
    log(f"[START] Output folder: {output_folder}", log_widget)
    
    # Krok 1: Konwersja .360 do .mov
    temp_mov_path = os.path.normpath(os.path.join(output_folder, "temp_converted.mov"))
    temp_csv_path = os.path.normpath(os.path.join(output_folder, "temp_telemetry.csv"))
    
    try:
        convert_360_to_mov(input_360_path, temp_mov_path, log_widget)
        
        # Krok 2: Wyciągnięcie telemetrii
        extract_telemetry_from_gopro(temp_mov_path, temp_csv_path, log_widget)
        
        # Krok 3: Przetworzenie wideo z telemetrią
        result = process_video_with_csv(temp_mov_path, temp_csv_path, output_folder, distance_m, log_widget)
        
        # Czyszczenie plików tymczasowych
        try:
            if os.path.exists(temp_mov_path):
                os.remove(temp_mov_path)
                log(f"[CLEANUP] Removed: {temp_mov_path}", log_widget)
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
                log(f"[CLEANUP] Removed: {temp_csv_path}", log_widget)
        except Exception as cleanup_error:
            log(f"[CLEANUP] Warning: {cleanup_error}", log_widget)
        
        return result
        
    except Exception as e:
        log(f"[ERROR] process_gopro_360_video failed: {str(e)}", log_widget)
        # Czyszczenie w przypadku błędu
        try:
            if os.path.exists(temp_mov_path):
                os.remove(temp_mov_path)
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
        except:
            pass
        raise e

