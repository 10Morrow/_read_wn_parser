import signal
from services import is_valid_url, create_folder_if_not_exists, write_data_to_file,\
    load_state, save_state, create_pickle
from novel_parser import generate_chapters_link_list
from chapter_parser import parse_data_from_chapter
from category_parser import create_category_links_list, parse_novels_from_category


def enter_link():
    link = input("enter link: ")
    if not is_valid_url(link):
        print("might you enter wrong link, try again!")
        enter_link()
    return link


def handle_interrupt(signal, frame):
    raise Exception("The program was interrupted.")



def choose_mode():
    try:
        chosen_mode = int(input("""
                hi, chose needed mode:
            1. you need to parse one novel (send nevel link)
            2. you need to parse all novels in category (send category link)
            """))
    except:
        print("you enter wrong number, try again!")
        choose_mode()
    return chosen_mode


def main(state):
    if "chosen_mode" in state:
        chosen_mode = state["chosen_mode"]
    else:
        chosen_mode = choose_mode()
        state["chosen_mode"] = chosen_mode

    if "entered_link" in state:
        link = state["entered_link"]
    else:
        link = enter_link()
        state["entered_link"] = link

    if chosen_mode == 1:
        if "links_data" in state:
            data = state["links_data"]
        else:
            data = generate_chapters_link_list(link)
            state["links_data"] = data
        name = data['name']
        if "last_chapter_link" in state:
            chapters = data['chapters'][state["last_chapter_link"]+1:]
        else:
            chapters = data['chapters']
        create_folder_if_not_exists(name)
        for i, link in enumerate(chapters):
            if "links" in state:
                if link in state["links"]:
                    data = state["links"][link]
                else:
                    data = parse_data_from_chapter(link)
                    if data:
                        state["links"][link] = data
            else:
                data = parse_data_from_chapter(link)
                if data:
                    state["links"] = {link: data}
            if data:
                state["last_chapter_link"] = i
                write_data_to_file(name, i,  data)
    else:

        if "page_links" in state:
            page_links = state["page_links"]
        else:
            page_links = create_category_links_list(link)
            state["page_links"] = page_links
        if "last_page" in state:
            page_links = page_links[state["last_page"]+1:]

        for page_id, page_with_novels in enumerate(page_links):
            if "novel_data" in state:
                if page_with_novels in state["novel_data"]:
                    novels_list = state["novel_data"][page_with_novels]
                else:
                    novels_list = parse_novels_from_category(page_with_novels)
                    state["novel_data"][page_with_novels] = novels_list
            else:
                novels_list = parse_novels_from_category(page_with_novels)
                state["novel_data"] = {page_with_novels: novels_list}
            if "last_novel" in state:
                novels_list = novels_list[state["last_novel"]+1:]
            for novel_id, one_novel in enumerate(novels_list):
                if "chapter_data" in state:
                    if one_novel in state["chapter_data"]:
                        novel_data = state["chapter_data"][one_novel]
                    else:
                        novel_data = generate_chapters_link_list(one_novel)
                        state["chapter_data"][one_novel] = novel_data
                else:
                    novel_data = generate_chapters_link_list(one_novel)
                    state["chapter_data"] = {one_novel: novel_data}
                name = novel_data['name']
                chapters = novel_data['chapters']
                create_folder_if_not_exists(name)
                if "last_chapter" in state:
                    chapters = chapters[state["last_chapter"]+1:]
                for chapter_id, link in enumerate(chapters):
                    if "links" in state:

                        if link in state["links"]:
                            data = state["links"][link]
                            real_chapter_id = data["chapter_id"]
                            real_data = data["data"]
                        else:
                            data = parse_data_from_chapter(link)
                            real_chapter_id = data["chapter_id"]
                            real_data = data["data"]
                            if data:
                                state["links"][link] = data
                    else:
                        data = parse_data_from_chapter(link)
                        real_chapter_id = data["chapter_id"]
                        real_data = data["data"]
                        if data:
                            state["links"] = {link: data}
                    if data:
                        write_data_to_file(name, real_chapter_id, real_data)
                    state["last_chapter"] = chapter_id
                state["last_novel"] = novel_id
            state["last_page"] = page_id


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, handle_interrupt)
        create_pickle()
        state = load_state()
        main(state)
    except Exception as e:
        save_state(state)
        print(f"[e] error {e}")
        print("[+] state saved")