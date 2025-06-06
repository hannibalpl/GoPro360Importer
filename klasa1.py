<<<<<<< HEAD
from processing import process_gopro_360_video


if __name__ == "__main__":
    # Przyk³adowe wartoœci - podmieñ na w³asne œcie¿ki i parametry
    input_360_path = r"C:\Praca\_miasta\KPO\Mechowo\Wizja\CIESLAW.360"
    output_folder = r"C:\Praca\_miasta\KPO\Mechowo\Wizja\v3"
    distance_m = 10  # co ile metrów wyci¹gaæ klatki

def log_widget(msg):
        print(msg)

=======
from processing import process_gopro_360_video


if __name__ == "__main__":
    # Przyk³adowe wartoœci - podmieñ na w³asne œcie¿ki i parametry
    input_360_path = r"C:\Praca\_miasta\KPO\Mechowo\Wizja\CIESLAW.360"
    output_folder = r"C:\Praca\_miasta\KPO\Mechowo\Wizja\v3"
    distance_m = 10  # co ile metrów wyci¹gaæ klatki

def log_widget(msg):
        print(msg)

>>>>>>> 20ecb62abf398cf1b723644dfbdf5bfce6de8521
process_gopro_360_video(input_360_path, output_folder, distance_m, log_widget)