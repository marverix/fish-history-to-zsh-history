#!/usr/bin/env python3

import os
import re


regexp_fish_history_entries = re.compile(r"^[ -] cmd: (?P<cmd>.+)\s+when: (?P<when>[0-9]+)", re.MULTILINE)
ZSH_HISTORY_ENTRY = ": {}:0;{}\n"
MIGRATE_STRATEGY = ["abort", "overwrite", "merge"]


def convert_fish_cmd_to_zsh_cmd(cmd: str) -> str:
    """
    Convert given fish cmd to zsh cmd
    :param cmd: Fish cmd
    :return: Zsh cmd
    """
    return cmd.replace('; and ', '&&').replace('; or ', '||')


def convert_fish_history_to_zsh_history(fish_history: str) -> (str, int):
    """
    Convert given fish history content to zsh history format
    :param fish_history: Fish history
    :return: Zsh history
    """
    iter_fish_history_entries = regexp_fish_history_entries.finditer(fish_history)
    entries_num = 0
    zsh_history = ""
    for entry in iter_fish_history_entries:
        entries_num += 1
        zsh_history += ZSH_HISTORY_ENTRY.format(entry.group("when"), convert_fish_cmd_to_zsh_cmd(entry.group("cmd")))

    return zsh_history, entries_num


def _write_and_overwrite(zsh_dst: str, zsh_history: str):
    """
    @private
    Write zsh_history to zsh_dst, and overwrite if exists
    :param zsh_dst:
    :param zsh_history:
    :return:
    """
    try:
        with open(zsh_dst, "w") as zs:
            zs.write(zsh_history)
    except Exception as err:
        print(f"Fatal error while writing data: {err}")
        exit(1)


def _write_or_abort(zsh_dst: str, zsh_history: str):
    """
    @private
    Write zsh_history to zsh_dst, or abort if exists
    :param zsh_dst:
    :param zsh_history:
    :return:
    """
    if os.path.exists(zsh_dst):
        print(f"'{zsh_dst}' already exists. Aborting.")
        return

    _write_and_overwrite(zsh_dst, zsh_history)


def _write_and_merge(zsh_dst: str, zsh_history: str):
    """
    @private
    Write zsh_history to zsh_dst, and merge content if exists
    :param zsh_dst:
    :param zsh_history:
    :return:
    """
    current_content = ""

    if os.path.exists(zsh_dst):
        try:
            with open(zsh_dst, "r") as zs:
                current_content = zs.read()
        except Exception:
            print(f"Could not read '{zsh_dst}' to merge")
            exit(1)

    merged_content = current_content.split("\n") + zsh_history.split("\n")
    merged_content = list(set(merged_content))
    merged_content.sort()

    if merged_content[0] == "":
        merged_content.pop(0)

    merged_content.append("")

    merged_zsh_history = "\n".join(merged_content)

    _write_and_overwrite(zsh_dst, merged_zsh_history)


def migrate(fish_src: str, zsh_dst: str, strategy: str):
    """
    Migrate fish_history in fish_src, to zsh_history in zsh_dst, with given migrate strategy
    :param fish_src: fish_history src path
    :param zsh_dst: zsh_history dst path
    :param strategy: Migrate strategy
    :return:
    """
    if strategy not in MIGRATE_STRATEGY:
        print(f"Unsupported merge strategy '{strategy}'")
        exit(1)

    print(f"Reading '{fish_src}' ...")
    try:
        with open(fish_src, "r") as fs:
            fish_history = fs.read()
    except Exception:
        print(f"Could not read '{fish_src}'")
        exit(1)

    print("Looking for fish_history entries ...")
    zsh_history, entries_num = convert_fish_history_to_zsh_history(fish_history)

    if entries_num == 0:
        print("No entries found. zsh_history not created")
        exit(0)

    print(f"{entries_num} entries found. Saving to '{zsh_dst}'")

    if strategy == MIGRATE_STRATEGY[0]:
        _write_or_abort(zsh_dst, zsh_history)
    elif strategy == MIGRATE_STRATEGY[1]:
        _write_and_overwrite(zsh_dst, zsh_history)
    elif strategy == MIGRATE_STRATEGY[2]:
        _write_and_merge(zsh_dst, zsh_history)
    else:
        print(f"Unsupported migrate strategy '{strategy}'")
        exit(1)

    print("Finished")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="fish_history to zsh_history")
    parser.add_argument('-f', '--fish-src', default="~/.local/share/fish/fish_history",
                        help='fish_history location | Default: ~/.local/share/fish/fish_history')
    parser.add_argument('-z', '--zsh-dst', default="~/.zsh_history",
                        help='zsh_history location | Default: ~/.zsh_history')
    parser.add_argument('-s', '--strategy', choices=MIGRATE_STRATEGY, default=MIGRATE_STRATEGY[0],
                        help='Migrate strategy. What to do when zsh_dst is existing and is not empty?'
                             ' | abort - Abort migration (Default)'
                             ' | overwrite - Overwrite file'
                             ' | merge - Merge existing and the new content')
    args = parser.parse_args()

    migrate(args.fish_src, args.zsh_dst, args.strategy)
