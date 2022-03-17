# Migrate fish_history to zsh_history

## Usage

### With curl

```sh
python3 -c "$(curl -fsSL https://raw.github.com/marverix/fish-history-to-zsh-history/master/fish-history-to-zsh-history.py)"
```

### With wget

```sh
python3 -c "$(wget https://raw.github.com/marverix/fish-history-to-zsh-history/master/fish-history-to-zsh-history.py -qO -)"
```

## Options

```sh
❯ ./fish-history-to-zsh-history.py --help
usage: fish_history to zsh_history [-h] [-f FISH_SRC] [-z ZSH_DST] [-s {abort,overwrite,merge}]

optional arguments:
  -h, --help            show this help message and exit
  -f FISH_SRC, --fish-src FISH_SRC
                        fish_history location
                        | Default: ~/.local/share/fish/fish_history
  -z ZSH_DST, --zsh-dst ZSH_DST
                        zsh_history location
                        | Default: ~/.zsh_history
  -s {abort,overwrite,merge}, --strategy {abort,overwrite,merge}
                        Migrate strategy. What to do when zsh_dst is existing and is not empty?
                        | abort - Abort migration (Default)
                        | overwrite - Overwrite file
                        | merge - Merge existing and the new content
```
