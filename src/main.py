from data_selection import get_files
from text_selection import get_text
from KB_generation import get_kb
from graph_generation import get_graph


def main() :
    files = get_files()
    text = get_text(files)
    kb = get_kb(text)
    graph = get_graph(kb)
    print(f"graph generated as html file.")


if __name__ == "__main__" :
    main()
