import os
import shutil


def main():
    # Confirmation
    confirm = input('Type "YES" to remove results and reset configurations')
    if confirm != 'YES':
        raise Exception('Program will not reset')
    # Make backup of stats folder
    current_user = os.getlogin()
    stats_path = rf'C:/Users/{current_user}/Documents/Deluxe Ski Jump 4/Stats'
    try:
        shutil.copytree(stats_path, './data/stats_copy')
    except FileExistsError:
        shutil.rmtree('./data/stats_copy')
        shutil.copytree(stats_path, './data/stats_copy')
    # Remove stats folder
    shutil.rmtree(stats_path)
    # Remove database
    os.remove('./data/results.db')
    # Remove classification
    os.remove('./data/classifications.xlsx')


if __name__ == '__main__':
    main()
