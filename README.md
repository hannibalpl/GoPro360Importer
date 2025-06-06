# gopro-qgis-telemetry

Wtyczka do QGIS do wyciągania strumieni telemetrii i wideo z plików `.360` GoPro i następnie przerabiania tych danych w docelowy widok StreetView w QGIS napisany w Pythonie.  
Docelowo: automatyczne przetwarzanie GPS i czasu, generowanie zdjęć 360 stopni, przypisywanie geotagów i znaczników czasowych, generowanie miejsc na mapie na podstawie tych danych. 
Generalnie STREETVIEW ale na twoich materiałach.
Obecnie: **zbiór notatek, testów i błędnych decyzji życiowych. Boże czemu to ciągnę...**

## Status

🟠   Publiczne repozytorium, ale na bardzo wczesnym etapie.  

⚠️   Kod jest brudnopisem, wiele rzeczy jeszcze nie działa lub działa nie tak, jak powinno.  
      Na razie mam dość, później pewnie do tego wrócę.
      
👨‍🔧   Jeśli tu trafiłeś przypadkiem: nie oceniaj — każdy projekt kiedyś wyglądał jak chaos. A ja na razie jestem w dupie. Pytanie tylko czy spodoba mi się to na tyle by się tu zacząć urządzać.

## Aktualne problemy:
- Problem ze zdjęciami - przy generowaniu chamsko filmu .360 przez ffmpeg  wychodzi 180 stopniowe zdjęcie (chyba nawet 130*, dunno, coś ucina), a czemu? FFmpeg wyciąga tylko jeden strumień i to taki na jaki natrafi pierwszy.
  Pliki .360 to 5 strumieni danych: przód i tył kamerki, dalej telemetria. QGIS ma to do siebie że pracuje w Pythonie, więc i wszelkie narzędzia muszą być w Pythonie a najlepiej to jako biblioteka standalone.
  Jest dosyć ciekawa biblioteka gpmf_parser, ale nie opanowałem jej na tyle by to parsować i konwertować przez Pythona, może za głupi jestem
- Aby ominąć problem FFmpega i wyciągnąć ze strumieni ładniejsze zdjęcia jednocześnie nie żyłując procesora, trzeba by film wyeksportować do .mov. Oba strumienie skleić i wypluć. Ale drugi strumień jest
  obrócony o 90* i leży jak ten po tamtym (boże... za co...). Obrócenie każdej klatki pali procesor. 
- Konwersja 360->mov sprawia że film traci telemetrię, ale zyskuje 360. ALE: wciąż brak efektów przy konwersji. No nie idzie.
- Przy okazji telemetrii wracamy do gpmf_parsera - ma wyciągać ją do pliku csv, ale nie umiem odpowiednio zbudować parseram i konwertera który przecież jest pisany w c oryginalnie.
- TAK, MOŻEMY TO ROBIĆ ZA POMOCĄ APKI od GoPro, eksportować jak te neandertaluchy .360 do .mov, dalej przez strony online robić z telemetrii csv (głównie gps i czas) i dopiero na tak przygotowanej paczce pracować, ale chcę mieć narzędzie
  ,,Kliknij i zapomnij" w QGISie, gdzie zwykły użyszkodnik wybiera sobie z nagrań te swoje kilkadziesiąt filmów, klika ,,Konwertuj do GPKG" i za godzinę ma gotowe pół miasta w StreetView bo był na wycieczce z kamerką 360 stopni.
- Patrzyłem na inne rozwiązania i biblioteki, pytałem tą trójkę debili (Copilot w VS'ie, Claude, ChatGPTv(ale copilot to chgpt w sumie), na Geminiego nawet nie patrze bo to debil wśród debili) ale zacinają się i stękają przy problemie
  rozbijania strumieni i wyciągania danych.
  Nie wiem, może wypróbuję Deepblue jak znajdę motywację.

  
  Generalnie jak wyciągnę telemetrię do .csv i jak wyeksportuję plik .360 do .mov'a to reszta kodu działa - ffmpeg tnie na zdjęcia, python te zdjęcia geotaguje z właściwą datą, robimy z tego geopaczkę i włala. Za pomocą narzędzia QgisGLViewer możemy
  podglądać wtedy kolejne punkty naszej trasy i mamy własne StreetView. Chyba że już tak namieszałem w kolejnych wersjach że i to już nie działa. Ale to jest betka, poprawi się.
  
## Cele projektu

- [ ] Wyodrębnienie strumieni telemetrycznych z gps i czasem z pliku `.360` do .csv
- [ ] Scalenie 2 strumieni wideo (180stopni) z pliku .360 do jednego filmu .mov z dobrą jakością
- [x] Pocięcie filmu na klatki w .jpeg
- [x] Geotagowanie klatek wideo z danymi GPS
- [x] Zebranie do kupy całości wygenerowanego materiału do paczki .gpkg 
- [x] Integracja z QGIS jako narzędzie obszarowe
- [ ] Właściwe ustalenie punktu początkowego zdjęcia do poprawnego wyświetlania przez QgisGLViewer, niby do północy ale to jakoś nie działa

## Wymagania

- Python 3.10+
- QGIS 3.28+ (dla pluginu)
- ffmpeg + ffprobe (z PATH)
- geographiclib
- geopy
- 🟠 gopro2gpx
- piexif
- 🟠 py_gpmf_parser (golas jest w c, mam skonwertowany parser do py, ale tam nic nie ma)
- ⚠️ jakakolwiek sprawna biblioteka do parsowania i konwersji danych z gopro - polecajki?
- QgisGLViewer jako osobna wtyczka

## Użycie (tymczasowe):
Zaimportuj do QGISa zawartość jako paczkę zip. Ot i dalej kombinuj. Mnie w to nie mieszaj chyba że masz rozwiązanie.

## Ostrzeżenie
    Ten projekt nie działa. Ma problemy.
    MA PROBLEMY.
    HGW czy coś mi boty nie spieprzyły w kolejnie iterowanych krokach w kodzie (ot, kłania się praca w kodzie na N++ zamiast w jakimś IDE, dopiero teraz wymyśliłem wersjonowanie w gicie, więc w sumie od tej wersji można to sprzątać) 
    Nie pracuje nad tym na razie (06.2025) bo i tak mam problem z pierwszymi podpunktami więc to idzie na dalszy plan.
    Ten projekt to na razie notes z walki o sens robienia tego niż gotowe rozwiązanie.
    Ściągasz to na własne ryzyko. Nie odpowiadam za rwanie włosów z czupryny. 
    
