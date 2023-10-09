import os
def readme(dirpath):
    with open('README.md', 'w', encoding='utf-8') as f_:
        for i in os.listdir(dirpath):
            if os.path.isdir(i):
                readme(os.path.join(dirpath, i))
            if os.path.join(dirpath, i) != __file__ and os.path.splitext(i)[1][1:] in ['html', 'js', 'css', 'py']:
                with open(os.path.join(dirpath, i), 'r', encoding='utf-8') as f:
                    content = f.read()
                    f_.write(f'{i}:\n```{os.path.splitext(i)[1][1:]}\n{content}\n```\n')
readme(os.getcwd())
