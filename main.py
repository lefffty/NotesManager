import os
import json
import zipfile
import csv
import datetime
import platform
import shutil
import logging
import matplotlib.pyplot as plt
from enum import Enum
from collections import defaultdict, Counter
from send2trash import send2trash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


NOTES_DIR = 'notes'
BACKUP_DIR = 'backups'
CSV_DIR = 'csv'
JSON_DIR = 'json'
PDF_DIR = 'pdf'
ACTIONS_FILE = 'actions.txt'
TXT_EXTENSION = '.txt'
PLOTS_DIR = 'plots'


class Actions(Enum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3


def ensure_directory_exists() -> None:
    """
    To check dirs
    """
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)


def setup_logging():
    logging.basicConfig(
        filename='logs/basic_logging.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def log_note_action(action, note_title):
    logging.info(f'Action: {action} | Note: {note_title}')


def list_notes() -> None:
    """
    List of notes
    """
    notes = [f.lower() for f in os.listdir(NOTES_DIR)
             if f.endswith(TXT_EXTENSION)]
    if not notes:
        print('There is no saved notes')
    else:
        print('===================')
        print('Existing notes:')
        for index, note in enumerate(notes):
            print(f'  {index + 1} - {note[:-4]}')
        print('===================')


def search_note_by_keyword() -> None:
    """
    To search note by entered keyword
    """
    keyword: str = input('  Enter keyword: ').lower()
    found: bool = False

    for note in os.listdir(NOTES_DIR):
        if note.endswith(TXT_EXTENSION):
            with open(os.path.join(NOTES_DIR, note), 'r') as file:
                text = ''.join([line.lower() for line in file.readlines()])
                if keyword in text:
                    print(
                        (f'  Keyword "{keyword}" was found in '
                         f'"{note.removesuffix(TXT_EXTENSION)}" '
                         f'note: {text.count(keyword.lower())}'))
                    found = True

    if not found:
        print('There is no notes which includes entered keyword!')


def create_note():
    """
    Создание новой заметки
    """
    title = input('  Enter note title: ')
    content = input('  Enter note content: ')

    filename = os.path.join(NOTES_DIR, f'{title}.txt')

    if os.path.exists(filename):
        print('  Note with that title already exists!')

    with open(filename, 'w') as file:
        file.write(content)

    log_note_action(Actions.CREATE, title)


def update_note() -> None:
    """
    Update note
    """
    list_notes()
    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [file for file in os.listdir(
            NOTES_DIR) if file.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            old_filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            new_title = input('  Enter new note title: ')
            new_content = input('  Enter new note content: ')
            new_filename = os.path.join(NOTES_DIR, f'{new_title}.txt')
            os.rename(old_filename, new_filename)
            with open(new_filename, 'w') as file:
                file.write(new_content)
            log_note_action(Actions.UPDATE, new_title)
    except ValueError:
        print('  Entered number is not integer!')


def delete_note() -> None:
    """
    To delete note
    """
    list_notes()
    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [file for file in os.listdir(NOTES_DIR)]
        if 1 <= note_num <= len(notes):
            filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            os.remove(filename)
            log_note_action(Actions.DELETE.name, notes[note_num - 1])
    except ValueError:
        print('  Entered number is not integer!')


def send_note_to_trash():
    list_notes()

    note_number = input('  Enter note number: ')

    try:
        note_num = int(note_number)
        notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            filename = os.path.join(NOTES_DIR, notes[note_num - 1])
            if platform.system() == 'Windows':
                send2trash(filename)
            else:
                trash_path = os.path.expanduser("~/.local/share/Trash/files/")
                os.makedirs(trash_path, exist_ok=True)
                shutil.move(filename, trash_path)
            print(f'  {filename} was sent to trash!')
        else:
            print(f'Note number should be in ({1}, {len(notes)})')
    except ValueError:
        print('Note number should be integer!')


def create_backup() -> None:
    """
    Create note`s backup
    """
    timestamp = datetime.datetime.now().date()
    backup_filename = os.path.join(BACKUP_DIR, f'notes_backup_{timestamp}.zip')

    with zipfile.ZipFile(backup_filename, 'w') as zip_file:
        for note in os.listdir(NOTES_DIR):
            if note.endswith(TXT_EXTENSION):
                zip_file.write(os.path.join(NOTES_DIR, note), arcname=note)

    print(f'  Backup {backup_filename} was created!')


def delete_old_backups() -> None:
    """
    Deleting old backups
    """
    now = datetime.datetime.now().date()

    for file in os.listdir(BACKUP_DIR):
        full_path = os.path.join(BACKUP_DIR, file)
        creation_time = os.path.getctime(full_path)
        creation_date = datetime.datetime.fromtimestamp(creation_time).date()
        if (now - creation_date).days >= 1:
            os.remove(full_path)

    print('  Old backups was deleted!')


def export_to_csv():
    """
    Exporting notes info CSV
    """
    timestamp = datetime.datetime.now().date()
    FILENAME = os.path.join(CSV_DIR, f'{timestamp}.csv')

    notes = []
    for _file in os.listdir(NOTES_DIR):
        if _file.endswith(TXT_EXTENSION):
            full_path = os.path.join(NOTES_DIR, _file)
            with open(full_path, 'r') as file:
                note_dict = defaultdict(str)
                note_dict['title'] = _file
                note_dict['content'] = file.read()
            notes.append(note_dict)

    with open(FILENAME, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['title', 'content'])
        for note in notes:
            writer.writerow(note)

    print('  Notes was exported into CSV')


def export_to_json():
    """
    Exporting notes info JSON
    """
    timestamp = datetime.datetime.now().date()
    FILENAME = os.path.join(JSON_DIR, f'{timestamp}.json')

    notes = defaultdict(str)
    for _file in os.listdir(NOTES_DIR):
        if _file.endswith(TXT_EXTENSION):
            with open(os.path.join(NOTES_DIR, _file), 'r') as file:
                notes[_file] = file.read()

    with open(FILENAME, 'w') as json_file:
        json.dump(notes, json_file, indent=4, ensure_ascii=False)

    print('  Notes was exported into JSON')


def words_frequency(buffer: str) -> defaultdict[str, int]:
    words_dict: defaultdict[str, int] = defaultdict(int)
    words = buffer.split(' ')
    for word in words:
        words_dict[word] += 1
    return words_dict


def semantic_analysis():
    list_notes()
    note_number = input('  Enter number of note you want to analyze: ')

    try:
        note_num = int(note_number)
        notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
        if 1 <= note_num <= len(notes):
            full_path = os.path.join(NOTES_DIR, notes[note_num - 1])
            title = notes[note_num - 1].removesuffix(TXT_EXTENSION)
            with open(full_path, 'r') as file:
                content = file.read()
            print(content)
            words_freq = words_frequency(content)
            return words_freq, title
        else:
            print(f'  Your number should be in range ({1}, {len(notes)})')
    except ValueError:
        print('  Your number should be integer!')


def export_to_pdf():
    timestamp = datetime.datetime.now().date()
    filename = os.path.join(PDF_DIR, f'{timestamp}.pdf')
    canv = canvas.Canvas(filename, pagesize=A4)

    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith('.txt')]

    x = 15
    y = 780
    dy = 40
    for note in notes:
        with open(os.path.join(NOTES_DIR, note)) as file:
            title = note.removesuffix(TXT_EXTENSION)
            content = file.read()
        canv.drawString(x, y, text=f'Title: {title}')
        canv.drawString(x, y+dy, text=f'Content: {content}')
        y += dy

    canv.save()


def statistics_by_date() -> Counter:
    notes = [f for f in os.listdir(NOTES_DIR) if f.endswith(TXT_EXTENSION)]
    dates = []
    for note in notes:
        path = os.path.join(NOTES_DIR, note)
        creation_date = datetime.datetime.fromtimestamp(
            os.path.getctime(path)).date()
        dates.append(str(creation_date))
    counter = Counter(dates)
    return counter


def plot_semantic_analysis():
    words_freq, title = semantic_analysis()
    plt.figure(figsize=(200, 100))
    plt.bar(words_freq.keys(), words_freq.values())
    plt.title(f'{title} analysis')
    plt.ylabel('Количество вхождений')
    plt.xlabel('Слово')
    plt.show()


def plot_user_statistics():
    statistics = statistics_by_date()
    TITLE = 'User activity'
    XLABEL = 'Date'
    YLABEL = 'Created notes'
    plt.bar(statistics.keys(), statistics.values())
    plt.title(TITLE)
    plt.xlabel(XLABEL)
    plt.ylabel(YLABEL)
    plt.show()


def main():
    ensure_directory_exists()
    setup_logging()
    while True:
        print('1 - list of notes')
        print('2 - search note by keyword')
        print('3 - create note')
        print('4 - delete note permanently')
        print('5 - send note to trash')
        print('6 - update note')
        print('7 - create new backup')
        print('8 - delete old backups')
        print('9 - export to JSON')
        print('10 - export to CSV')
        print('11 - export to PDF')
        print('12 - note semantic analysis')
        print('13 - activity diagram')
        print('14 - EXIT')

        choice = (input('Enter your choice: '))
        try:
            choice = int(choice)
        except ValueError:
            print('Your choice should be integer!')

        match choice:
            case 1:
                list_notes()
            case 2:
                search_note_by_keyword()
            case 3:
                create_note()
            case 4:
                delete_note()
            case 5:
                send_note_to_trash()
            case 6:
                update_note()
            case 7:
                create_backup()
            case 8:
                delete_old_backups()
            case 9:
                export_to_json()
            case 10:
                export_to_csv()
            case 11:
                export_to_pdf()
            case 12:
                plot_semantic_analysis()
            case 13:
                plot_user_statistics()
            case 14:
                break
    print('Program has finished!')


if __name__ == '__main__':
    main()
