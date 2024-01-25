def open_txt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        r = f.read()
        return r


def write_txt(filename, s):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(s)


def get_demo_code(filename):
    demo = open_txt(filename)

    k = 'root:'
    assert k not in demo

    return demo


def main():
    # print(demo, type(demo))
    demo = get_demo_code('temp.py')
    readme = open_txt('./gen_txt_raw/README.md')
    readme = readme.format(demo=demo)
    write_txt('README.md', readme)

    initfile = open_txt('./gen_txt_raw/raw-__init__.py')
    initfile = initfile.format(demo=demo)
    write_txt('./inventory_manager/__init__.py', initfile)


if __name__ == '__main__':
    main()
