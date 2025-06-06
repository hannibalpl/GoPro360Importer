from processing import process_gopro_360_video


if __name__ == "__main__":
    # Przyk�adowe warto�ci - podmie� na w�asne �cie�ki i parametry
    input_360_path = r"C:\Praca\_miasta\KPO\Mechowo\Wizja\CIESLAW.360"
    output_folder = r"C:\Praca\_miasta\KPO\Mechowo\Wizja\v3"
    distance_m = 10  # co ile metr�w wyci�ga� klatki

def log_widget(msg):
        print(msg)

process_gopro_360_video(input_360_path, output_folder, distance_m, log_widget)